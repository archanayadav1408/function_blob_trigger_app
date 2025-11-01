import os
import logging
import uuid
import json
import datetime
import azure.functions as func

from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from azure.cosmos import CosmosClient, PartitionKey

# Define the Function App
app = func.FunctionApp()

# Environment Variables
FORM_ENDPOINT = os.environ["FORM_ENDPOINT"]
FORM_KEY = os.environ["FORM_KEY"]
TEXT_ENDPOINT = os.environ["TEXT_ENDPOINT"]
TEXT_KEY = os.environ["TEXT_KEY"]
COSMOS_ENDPOINT = os.environ["COSMOS_DB_ENDPOINT"]
COSMOS_KEY = os.environ["COSMOS_DB_KEY"]
COSMOS_DB = os.environ["COSMOS_DB_DATABASE"]
COSMOS_CONTAINER = os.environ["COSMOS_DB_CONTAINER"]

# Initialize clients
form_client = DocumentAnalysisClient(endpoint=FORM_ENDPOINT, credential=AzureKeyCredential(FORM_KEY))
text_client = TextAnalyticsClient(endpoint=TEXT_ENDPOINT, credential=AzureKeyCredential(TEXT_KEY))


def generate_sas_url(container_name, blob_name):
    """Generate a temporary SAS URL for Form Recognizer to access the blob."""
    conn_str = os.environ["AzureWebJobsStorage"]
    blob_service_client = BlobServiceClient.from_connection_string(conn_str)
    account_name = blob_service_client.account_name

    account_key = None
    for kv in conn_str.split(';'):
        if kv.startswith("AccountKey="):
            account_key = kv.split('=', 1)[1]
            break
    if not account_key:
        raise ValueError("Account key not found in AzureWebJobsStorage")

    sas_token = generate_blob_sas(
        account_name=account_name,
        container_name=container_name,
        blob_name=blob_name,
        account_key=account_key,
        permission=BlobSasPermissions(read=True),
        expiry=datetime.datetime.utcnow() + datetime.timedelta(minutes=15),
    )

    return f"https://{account_name}.blob.core.windows.net/{container_name}/{blob_name}?{sas_token}"


def analyze_document(blob_url):
    """Extract text and key-value pairs from the uploaded resume."""
    poller = form_client.begin_analyze_document_from_url("prebuilt-document", blob_url)
    result = poller.result()

    text_content = " ".join([p.content for p in result.paragraphs])
    return text_content

def extract_entities(text):
    """Extract entities (skills, organizations, dates, people, etc.) from text."""
    response = text_client.recognize_entities([text])[0]
    entities = []
    person_name = None

    if not response.is_error:
        for ent in response.entities:
            entities.append({"text": ent.text, "category": ent.category})
            if ent.category == "Person" and not person_name:
                person_name = ent.text  # Pick first detected name

    # Fallback name if not found
    if not person_name:
        person_name = "Unknown"

    return person_name, entities

def extract_key_phrases(text):
    resp = text_client.extract_key_phrases([text])
    return resp[0].key_phrases if not resp[0].is_error else []

def extract_summary(text):
    try:
        # Start the summarization job and wait for completion
        poller = text_client.begin_abstract_summary([text])
        result = poller.result()  # <-- this waits for completion internally
        summary_text = ""
        # Loop through results
        for doc in result:
            if not doc.is_error:
                for summary in doc.summaries:
                    summary_text += summary.text.strip() + " "
            else:
                raise Exception(f"Error in summary: {doc.error.code} - {doc.error.message}")
        return summary_text.strip()
    except Exception as e:
        print(f"Error in extract_summary: {e}")
        return ""


def store_in_cosmos(person_name, entities, blob_name, key_phrases, summary):
    """Store extracted info in Cosmos DB (auto-generated ID)."""
    client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)
    database = client.create_database_if_not_exists(id=COSMOS_DB)
    guid = str(uuid.uuid4())
    container = database.create_container_if_not_exists(
        id=COSMOS_CONTAINER,
        partition_key=PartitionKey(path="/name")
    )

    doc = {
        "id":guid,
        "fileName": blob_name,
        "summary": summary,
        "name": person_name,
        "key_phrases": key_phrases,
        "entities": entities,
        "uploadTime": datetime.datetime.utcnow().isoformat()
    }

    container.create_item(doc)
    logging.info(f"✅ Stored resume info for {person_name} in Cosmos DB")


@app.blob_trigger(arg_name="myblob", path="resumes/{name}", connection="AzureWebJobsStorage")
def BlobTrigger(myblob: func.InputStream):
    logging.info(f"📄 Processing blob: {myblob.name}, Size: {myblob.length} bytes")

    container_name = "resumes"
    blob_name = myblob.name.replace("resumes/", "")
    blob_url = generate_sas_url(container_name, blob_name)

    # Step 1: Extract text from resume
    text_content = analyze_document(blob_url)

    # Step 2: Extract entities & auto-detect person name
    person_name, entities = extract_entities(text_content)
    key_phrases = extract_key_phrases(text_content)
    summary = extract_summary(text_content)
    logging.info(str(key_phrases))

    # Step 3: Store results in Cosmos DB
    store_in_cosmos(person_name, entities, blob_name,key_phrases, summary)


@app.route(route="GetResumeInsights", auth_level=func.AuthLevel.ANONYMOUS)
def GetResumeInsights(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    filename = req.params.get('filename')
    if not filename:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('filename')

    if filename:
        client = CosmosClient(COSMOS_ENDPOINT, credential=COSMOS_KEY)
        database = client.get_database_client(COSMOS_DB)
        container = database.get_container_client(COSMOS_CONTAINER)

        # Query for this file
        query = "SELECT * FROM c WHERE c.fileName=@filename"
        items = list(container.query_items(
            query=query,
            parameters=[{"name": "@filename", "value": filename}],
            enable_cross_partition_query=True
        ))
        if not items:
            return func.HttpResponse(
                f"No data found for file '{filename}'", status_code=404
            )
        doc = items[0]
        name = doc.get("name", "Unknown")
        summary = doc.get("summary", "Unknown")
        key_phrases = doc.get("key_phrases", "Unknown")
        entities = doc.get("entities", [])

        # Format into meaningful text
        skill_entities = [e['text'] for e in entities if e['category'] in ['Skill', 'Product']]
        org_entities = [e['text'] for e in entities if e['category'] == 'Organization']
        date_entities = [e['text'] for e in entities if e['category'] == 'DateTime']
        result = {
            "Name": name,
            "Summary": summary,
            "Skills": skill_entities,
            "Organizations": org_entities,
            "Dates": date_entities,
            "Key Phrases":key_phrases
        }

        return func.HttpResponse(
            json.dumps(result, indent=2),
            mimetype="application/json",
            status_code=200
        )
    else:
        if not filename:
            return func.HttpResponse(
                "Please pass the filename in the query string ?filename=",
                status_code=400
            )

@app.route(route="uploadresume", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def upload_resume(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Processing upload request...")

    try:
        # Get uploaded file
        file = req.files.get("file")
        if not file:
            return func.HttpResponse("No file uploaded. Please upload a file with key 'file'.", status_code=400)

        filename = file.filename
        file_bytes = file.stream.read()

        # Upload to blob storage
        conn_str = os.environ["AzureWebJobsStorage"]
        blob_service_client = BlobServiceClient.from_connection_string(conn_str)
        container_name = "resumes"

        container_client = blob_service_client.get_container_client(container_name)

        blob_client = container_client.get_blob_client(filename)
        blob_client.upload_blob(file_bytes, overwrite=True)

        # Generate SAS URL
        sas_url = generate_sas_url(container_name, filename)
        logging.info(f"Uploaded")

        return func.HttpResponse(
            f"File uploaded successfully!",
            mimetype="text/plain",
            status_code=200
        )

    except Exception as e:
        logging.error(f"Error during upload: {e}")
        return func.HttpResponse(f"Error: {e}", status_code=500)
