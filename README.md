
# 🧠 Resume Analyzer — Azure AI-Powered Resume Insights

## 📋 Overview

**Resume Analyzer** is a serverless, AI-powered application that analyzes resumes to extract key insights such as skills, keywords, and candidate information.  
It leverages **Azure Cognitive Services**, **Azure Functions**, **Azure Blob Storage**, and **Azure Cosmos DB** to provide an end-to-end automated pipeline.

### 🔍 High-Level Flow

1. **Upload Resume** — User uploads a resume PDF using a REST API.
2. **Blob Trigger Activation** — The upload triggers an **Azure Function (Blob Trigger)**.
3. **AI Processing** — The function calls **Azure Cognitive Services** to extract text and analyze insights.
4. **Storage** — Extracted information (filename, candidate name, keywords, insights) is stored in **Azure Cosmos DB**.
5. **Insights Retrieval** — A second API allows users to fetch the analysis results using the filename.

---

## 🧩 Architecture

```

User → HTTP API → Blob Storage → Blob Trigger → Cognitive Services → Cosmos DB → HTTP API → User

````

**Components Involved:**
- **HTTP Function 1** — Uploads the resume to Blob Storage.
- **Blob Trigger Function** — Activates automatically on upload, extracts text using Cognitive Services, and stores insights in Cosmos DB.
- **HTTP Function 2** — Retrieves insights by querying Cosmos DB with the resume filename.

---

## ⚙️ Azure Resources Used

| Resource | Purpose | Description |
|-----------|----------|-------------|
| **Resource Group** | Container for related resources | Logical grouping for easier management |
| **Storage Account (Blob)** | Store uploaded resumes | Resumes uploaded via API are stored here |
| **Azure Cognitive Services** | Resume text extraction and analysis | Uses Form Recognizer and Language AI models |
| **Azure Cosmos DB** | Store resume insights | Stores structured data like keywords, candidate name, filename |
| **Azure Function App** | Host serverless APIs | Contains upload, blob-trigger, and insights-retrieval functions |

---

## 🧱 Setup Instructions

### 1️⃣ Login to Azure
```bash
az login
````

### 2️⃣ Set the Active Subscription

```bash
az account set --subscription "<subscription-id>"
```

### 3️⃣ Create a Resource Group

```bash
az group create -n <resource-group-name> -l <location>
```

### 4️⃣ Create Storage Account (Blob)

```bash
az storage account create -n ${PREFIX}storage -g $RG -l $LOC --sku Standard_LRS
```

### 5️⃣ Create a Blob Container

```bash
AZ_STORAGE_KEY=$(az storage account keys list -g $RG -n ${PREFIX}storage --query "[0].value" -o tsv)
az storage container create --name resumes --account-name ${PREFIX}storage --account-key $AZ_STORAGE_KEY
```
<img width="1911" height="963" alt="Screenshot 2025-11-11 195505" src="https://github.com/user-attachments/assets/483f963e-effd-468c-ba31-f7773147715f" />

### 6️⃣ Create Cognitive Services Account

```bash
az cognitiveservices account create \
  --name ${PREFIX}cog \
  --resource-group $RG \
  --kind CognitiveServices \
  --sku S0 \
  --location $LOC \
  --yes
```
<img width="1914" height="928" alt="Screenshot 2025-11-11 195625" src="https://github.com/user-attachments/assets/f06cbd6b-3036-4157-ae2f-35f9a4b28f5a" />


### 7️⃣ Deploy the Function App

```bash
az functionapp create \
  --resource-group <resource-group-name> \
  --consumption-plan-location <location> \
  --name resumeanalyzerfunc \
  --storage-account <storage-account-name> \
  --runtime python \
  --functions-version 4 \
  --os-type Linux \
  --linux-fx-version "Python|3.12"
```
<img width="1904" height="972" alt="Screenshot 2025-11-11 195705" src="https://github.com/user-attachments/assets/f11cd9ed-22d6-417a-b633-fa7af1789a02" />

### 8.Deply Cosmosdb account
```bash
az cosmosdb create \
  --name resume-anaylzerdb \
  --resource-group ResumeAnalyser-rg \
  --kind GlobalDocumentDB \
  --locations regionName="West US 2" failoverPriority=0 isZoneRedundant=false \
  --default-consistency-level Session \
  --enable-automatic-failover true \
  --enable-multiple-write-locations false \
  --capabilities EnableServerless \
  --backup-policy-type Periodic \
  --backup-interval 240 \
  --backup-retention 8 \
  --backup-storage-redundancy Geo \
  --public-network-access Enabled \
  --enable-free-tier false \
  --tags "defaultExperience=Core (SQL)" "hidden-workload-type=Development/Testing" \
  --api-version 2023-03-01-preview
```

### 9. Create cosmosdb db and container

```bash
# Create database
az cosmosdb sql database create \
  --account-name resume-anaylzerdb \
  --name ResumeDB \
  --resource-group ResumeAnalyser-rg

# Create container
az cosmosdb sql container create \
  --account-name resume-anaylzerdb \
  --database-name resumesDB \
  --name resumesdata \
  --partition-key-path "/name" \
  --resource-group ResumeAnalyser-rg
```

<img width="1914" height="930" alt="Screenshot 2025-11-11 195809" src="https://github.com/user-attachments/assets/e967c780-1b2e-4b01-955f-63ac355050b7" />

---

## 🌐 API Endpoints

### 1️⃣ Upload Resume

Uploads the resume to Blob Storage and triggers processing.

```bash
curl.exe -X POST "https://resumeanalyzerfunc.azurewebsites.net/api/uploadresume" \
  -F "file=@<path-to-resume.pdf>" -v
```

### 2️⃣ Get Resume Insights

Retrieves keywords and extracted data from Cosmos DB.

```bash
curl.exe "https://resumeanalyzerfunc.azurewebsites.net/api/GetResumeInsights?filename=<filename.pdf>" -v
```

---

## 🧠 Behind the Scenes

* The **Upload API** stores the resume in **Blob Storage**.
* A **Blob Trigger Function** activates automatically and:

  * Calls **Azure Cognitive Services** (Form Recognizer + Language API) to extract text and identify key skills.
  * Processes and structures the extracted data.
  * Saves the structured insights into **Cosmos DB**.
* The **Get API** queries **Cosmos DB** using the filename and returns JSON insights.

---


# 🧠 Azure Cognitive Services — Overview

**Azure Cognitive Services** is a **cloud-based suite of AI APIs and services** that allows developers to easily integrate **artificial intelligence capabilities** into their applications — **without needing to build or train AI models from scratch**.

It provides **pre-trained AI models** for:

* **Vision** – understanding images and documents
* **Speech** – recognizing and generating spoken language
* **Language** – analyzing and interpreting text
* **Decision** – making intelligent recommendations
* **Search** – enabling knowledge discovery

---

## 💡 Key Idea

You can think of Cognitive Services as *AI as a Service* — where Microsoft has already trained powerful AI models that you can call using a simple REST API or SDK.
You send data (text, image, audio, etc.), and the service returns structured insights.

---

## 🧩 Core Categories

| Category     | Examples                                                                  | Used For                                                     |
| ------------ | ------------------------------------------------------------------------- | ------------------------------------------------------------ |
| **Vision**   | Computer Vision, Form Recognizer, Face API                                | Extract text, recognize faces, identify objects              |
| **Language** | Text Analytics, Translator, Language Understanding (LUIS), Speech-to-Text | Extract meaning, sentiment, entities, and keywords from text |
| **Speech**   | Speech to Text, Text to Speech, Speech Translation                        | Convert spoken words to text or vice versa                   |
| **Decision** | Personalizer, Anomaly Detector                                            | Recommendations, pattern detection                           |
| **Search**   | Bing Search APIs                                                          | Web and knowledge search                                     |

---

## ⚙️ How It Works

1. **You create a Cognitive Services resource** in Azure.
   This gives you an endpoint URL and an API key.

2. **Your application calls the service API**

   * e.g., Upload a document → Cognitive Service processes it.

3. **Azure AI model analyzes the input**

   * For text: identifies entities, keywords, summaries, and sentiment.
   * For documents: extracts text and structure (tables, key-value pairs).

4. **You get structured insights as JSON output.**

---

## 📘 Example in Resume Analyzer

In your **Resume Analyzer project**, two specific Cognitive Services capabilities can be leveraged:

### 🧾 1. Form Recognizer (under Vision)

* Extracts **text and structure** (tables, fields, paragraphs) from resumes (PDFs or images).
* Can identify **sections like name, education, skills, experience**, etc.
* Converts an unstructured resume into structured JSON output.

**Example output:**

```json
{
  "Name": "Archana Yadav",
  "Email": "archana@example.com",
  "Skills": ["Azure", "Python", "Machine Learning"]
}
```

---

### 💬 2. Language Service (under Language)

* Performs **keyword extraction**, **entity recognition**, **summarization**, and **sentiment analysis**.
* Helps identify the **most relevant skills, roles, and experience areas** in the resume.

**Example output:**

```json
{
  "KeyPhrases": ["Azure Purview", "data lineage", "ingestion service", "machine learning"],
  "Sentiment": "Positive",
  "Summary": "Experienced software engineer specializing in Azure data governance."
}
```

---

## 🧠 Why Use Cognitive Services Here?

| Need                                               | Cognitive Service Feature                   |
| -------------------------------------------------- | ------------------------------------------- |
| Extract text from resume PDFs                      | **Form Recognizer (Document Intelligence)** |
| Identify candidate details (name, contact, skills) | **Text Extraction + Entity Recognition**    |
| Extract top keywords                               | **Language API - Key Phrase Extraction**    |
| Generate quick summary                             | **Language API - Summarization**            |

This saves you from writing complex ML models or NLP pipelines.
You just connect these pre-trained services to your **Azure Function** using REST APIs or SDKs.

---

## 💸 Pricing and Scaling

* You pay **per API call** or **per page** (for document analysis).
* Can scale automatically with Function App.
* Offers **free tiers** for testing and small workloads.

---

## 🧩 Summary

| Aspect                 | Description                                       |
| ---------------------- | ------------------------------------------------- |
| **Service Type**       | Pre-built AI APIs                                 |
| **Main Features**      | Vision, Speech, Language, Decision                |
| **Used For**           | Resume parsing, keyword extraction, text analysis |
| **In Resume Analyzer** | Extract text, identify skills, generate insights  |
| **Advantage**          | No ML expertise needed; easy API integration      |


---


# 🚀 **Azure App Service — Overview**

### 🧩 **What It Is**

**Azure App Service** is a **fully managed platform** for building, deploying, and scaling **web apps, REST APIs, and backend services** — without managing any infrastructure.

It supports multiple runtimes:

* **.NET / .NET Core**
* **Node.js**
* **Python**
* **Java**
* **PHP**
* **Ruby**
* **Custom containers (Docker)**

It handles the hosting, scaling, security, load balancing, and updates for you.

---

### 🏗️ **Core Components**

| Component                            | Description                                                                                                                                |
| ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------ |
| **App Service Plan**                 | Defines the **region**, **VM size**, **pricing tier**, and **scaling options** for your app. Think of it as the “server” your app runs on. |
| **Web App / API App / Function App** | The actual app code you deploy. You can have multiple apps running on one App Service Plan.                                                |
| **Deployment Slots**                 | Allow **zero-downtime deployment** (e.g., `staging` and `production` slots).                                                               |
| **Kudu / SCM**                       | A built-in deployment and management console (reachable at `https://<appname>.scm.azurewebsites.net`).                                     |
| **App Settings**                     | Store **environment variables** like connection strings, API keys, or configuration values securely.                                       |

---

### ⚙️ **Key Features**

| Feature                               | Description                                                                                        |
| ------------------------------------- | -------------------------------------------------------------------------------------------------- |
| 🧰 **Continuous Deployment (CI/CD)**  | Integrates with **GitHub**, **Azure DevOps**, **Bitbucket**, or **local Git** for auto-deployment. |
| ☁️ **Scalability**                    | Supports **manual** and **auto-scaling** (based on CPU, memory, schedule, or request count).       |
| 🔐 **Authentication / Authorization** | Built-in “Easy Auth” integrates with **Azure AD**, **Microsoft**, **Google**, **GitHub**, etc.     |
| 📊 **Monitoring**                     | Deep integration with **Application Insights** for performance, logs, and telemetry.               |
| 🕒 **Custom Domains + SSL**           | Add your own domain (`www.yourapp.com`) and manage free SSL certificates.                          |
| 🧱 **VNet Integration**               | Securely connect your app to Azure resources or on-premises systems.                               |

---

### 🧠 **App Service vs. Azure Functions**

| Feature  | Azure App Service (Web/API App)   | Azure Functions                                |
| -------- | --------------------------------- | ---------------------------------------------- |
| Hosting  | Always running                    | Event-driven (triggers like HTTP, Timer, Blob) |
| Pricing  | Based on compute size & uptime    | Based on execution count & duration            |
| Best For | Web apps, APIs, long-running apps | Lightweight event-driven code, background jobs |

---

### 🧰 **Typical Workflow**

1. **Develop** locally (e.g., using VS Code + Azure Functions Core Tools).
2. **Deploy** using:

   * VS Code “Deploy to Azure”
   * Azure CLI (`az functionapp deployment source config-zip`)
   * GitHub Actions / Azure DevOps
3. **Configure Settings** in Azure Portal → App Service → **Configuration**

   * Store secrets like `FORM_KEY`, `TEXT_KEY`, etc.
4. **Monitor** logs via:

   * Portal → “Log Stream”
   * Application Insights

---

## ⚡ **What Are Azure Function Triggers?**

A **trigger** is what *starts* the execution of an Azure Function.
Each function **must have exactly one trigger**, and you can think of it as *"when this event happens → run my code."*

Azure Functions supports many types of triggers — here are the most common:

| Trigger Type                       | What It Does                                                                     | Example Use Case                                     |
| ---------------------------------- | -------------------------------------------------------------------------------- | ---------------------------------------------------- |
| **HTTP Trigger**                   | Runs when an HTTP request is made to the endpoint.                               | Building APIs, webhooks, or web apps.                |
| **Blob Trigger**                   | Runs when a file (blob) is uploaded, modified, or deleted in Azure Blob Storage. | Processing uploaded files (images, PDFs, resumes).   |
| **Timer Trigger**                  | Runs on a schedule (like a cron job).                                            | Scheduled cleanups, health checks, periodic reports. |
| **Queue Trigger**                  | Runs when a message is added to an Azure Storage Queue.                          | Background job processing or decoupled workflows.    |
| **Event Grid / Event Hub Trigger** | Runs on Azure events or streaming data.                                          | Real-time analytics or monitoring.                   |
| **Cosmos DB Trigger**              | Runs when changes occur in a Cosmos DB container.                                | Sync or react to DB updates automatically.           |
| **Service Bus Trigger**            | Runs when messages are posted to Azure Service Bus topics or queues.             | Enterprise messaging, ordered job processing.        |

---

## 🧠 **Triggers Used in Your Resume Analyzer Project**

Your code uses **two triggers**:

| Trigger          | Function                                | Description                                                                                             |
| ---------------- | --------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| **HTTP Trigger** | `upload_resume` and `GetResumeInsights` | Runs when someone calls your API endpoint via HTTP (`POST` or `GET`).                                   |
| **Blob Trigger** | `BlobTrigger`                           | Runs automatically when a new resume file is uploaded to your blob storage container named `"resumes"`. |

Let’s break that down in detail 👇

---

### 🔹 1. **HTTP Trigger**

```python
@app.route(route="uploadresume", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def upload_resume(req: func.HttpRequest) -> func.HttpResponse:
```

**When does it run?**
→ Whenever a user calls the API:

```bash
curl.exe -X POST "https://resumeanalyzerfunc.azurewebsites.net/api/uploadresume" \
     -F "file=@C:\Path\Resume.pdf"
```

**What it does:**

1. Accepts an uploaded file (`resume.pdf`).
2. Uploads that file to **Azure Blob Storage** (`resumes` container).
3. Returns a success message.

✅ This is a **user-facing API** — the entry point for uploading resumes.

---

### 🔹 2. **Blob Trigger**

```python
@app.blob_trigger(arg_name="myblob", path="resumes/{name}", connection="AzureWebJobsStorage")
def BlobTrigger(myblob: func.InputStream):
```

**When does it run?**
→ Automatically triggered **when a new blob** (resume file) is uploaded to your container `resumes`.

**What it does:**

1. Reads the uploaded PDF.
2. Generates a **temporary SAS URL** for the blob.
3. Uses **Azure Form Recognizer** to extract text from the resume.
4. Uses **Azure Text Analytics** to:

   * Extract keywords, skills, organizations, etc.
   * Generate a summary.
5. Stores extracted information in **Cosmos DB** for later querying.

✅ This is your **automation trigger** — it processes files in the background as soon as they arrive.

---

### 🔹 3. **HTTP Trigger (for querying insights)**

```python
@app.route(route="GetResumeInsights", auth_level=func.AuthLevel.ANONYMOUS)
def GetResumeInsights(req: func.HttpRequest) -> func.HttpResponse:
```

**When does it run?**
→ When someone calls:

```bash
curl.exe "https://resumeanalyzerfunc.azurewebsites.net/api/GetResumeInsights?filename=<resume name>"
```

**What it does:**

* Fetches resume insights from **Cosmos DB** using the file name.
* Returns the extracted **Name**, **Skills**, **Organizations**, **Dates**, and **Summary**.

✅ This acts as the **retrieval API** for users to view the analysis results.

---

## 🧩 **Trigger Flow Summary**

Here’s how the triggers work together in your app:

```
(1) User uploads resume
     ↓
 [HTTP Trigger] → /uploadresume
     ↓
 File saved to Blob Storage
     ↓
 (2) Blob event fires automatically
     ↓
 [Blob Trigger] → Processes PDF → Form Recognizer + Text Analytics
     ↓
 Results stored in Cosmos DB
     ↓
 (3) User queries results
     ↓
 [HTTP Trigger] → /GetResumeInsights
     ↓
 Returns JSON with extracted info + summary
```

---

## 🌐 **Why This Design Is Efficient**

✅ **Decoupled architecture** — Upload and processing are independent.

✅ **Automatic processing** — Blob trigger ensures files are processed instantly.

✅ **Serverless scaling** — Both HTTP and Blob triggers scale automatically.

✅ **Cost-efficient** — You pay only for executions (no idle server cost).

---


Perfect ✅ — here’s a **step-by-step guide with commands** to **set up, run, and test your Azure Function App locally**, including all dependencies and environment variables for your Resume Analyzer project.

---

# 🧠 Setup 

---

## ⚙️ Prerequisites

Make sure you have the following installed:

| Tool                               | Version             | Install Command                                                  |
| ---------------------------------- | ------------------- | ---------------------------------------------------------------- |
| **Python**                         | 3.12+               | [Download](https://www.python.org/downloads/)                    |
| **Azure Functions Core Tools**     | v4                  | `npm install -g azure-functions-core-tools@4 --unsafe-perm true` |
| **Azure CLI**                      | Latest              | [Download](https://aka.ms/installazurecliwindows)                |
| **VS Code**                        | (Recommended)       | [Download](https://code.visualstudio.com/)                       |
| **Azure Extension Pack (VS Code)** | Optional but useful | From VS Code Extensions panel                                    |

---

## 📦 1. Clone the Project

```bash
git clone https://github.com/<your-repo>/function_blob_trigger_app.git
cd function_blob_trigger_app
```

---

## 🧰 2. Create and Activate a Virtual Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (macOS/Linux)
source .venv/bin/activate
```

---

## 📚 3. Install Required Packages

```bash
pip install -r requirements.txt
```

If you don’t have a `requirements.txt`, create one with:

```bash
azure-functions
azure-ai-formrecognizer
azure-ai-textanalytics
azure-storage-blob
azure-core
azure-cosmos
```

Then install:

```bash
pip install -r requirements.txt
```

---

## 🔐 4. Set Up Local Environment Variables

Create a file named **`local.settings.json`** in the root of your project (if not already present):

```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "<your-storage-connection-string>",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "FORM_ENDPOINT": "<your-form-recognizer-endpoint>",
    "FORM_KEY": "<your-form-recognizer-key>",
    "TEXT_ENDPOINT": "<your-text-analytics-endpoint>",
    "TEXT_KEY": "<your-text-analytics-key>",
    "COSMOS_DB_ENDPOINT": "<your-cosmos-endpoint>",
    "COSMOS_DB_KEY": "<your-cosmos-key>",
    "COSMOS_DB_DATABASE": "ResumeAnalyzer",
    "COSMOS_DB_CONTAINER": "ResumeData"
  }
}
```

You can get these values from the **Azure Portal** under:

* **Storage Account → Access keys**
* **Cognitive Services → Keys and Endpoint**
* **Cosmos DB → Keys and Connection String**

---

## 🧩 5. Initialize Azure Function Project (if not already initialized)

If you’re starting fresh:

```bash
func init . --python
```

Then add your function:

```bash
func new --name BlobTrigger --template "Blob trigger"
func new --name GetResumeInsights --template "HTTP trigger"
func new --name uploadresume --template "HTTP trigger"
```

*(You already have these defined, so you can skip if code exists.)*

---

## ▶️ 6. Run the Function App Locally

Start your function runtime:

```bash
func start
```

If everything is configured correctly, you’ll see output like:

```
Found Python version 3.12.10
Functions:
    BlobTrigger: blobTrigger
    GetResumeInsights: [GET] http://localhost:7071/api/GetResumeInsights
    uploadresume: [POST] http://localhost:7071/api/uploadresume
```

---

## 🧪 7. Test the APIs Locally

### ✅ Upload a Resume (HTTP Trigger)

```bash
curl.exe -X POST "http://localhost:7071/api/uploadresume" `
     -F "file=@C:\Users\archanayadav\Documents\Latest_Archana_s_Resume.pdf" -v
```

After uploading, you’ll see your blob trigger automatically start processing.

### ✅ Get Resume Insights (HTTP Trigger)

```bash
curl.exe "http://localhost:7071/api/GetResumeInsights?filename=Latest_Archana_s_Resume.pdf" -v
```

Expected Output (JSON):

```json
{
  "Name": "Archana Yadav",
  "Skills": ["Python", "Azure", "Data Engineering"],
  "Organizations": ["Microsoft"],
  "Dates": ["2023", "2024"],
  "Summary": "Experienced engineer skilled in Azure and data ingestion services."
}
```

---

## ☁️ 8. Deploy to Azure

Once everything works locally:

```bash
# Login to Azure
az login

# Set your subscription
az account set --subscription "<your-subscription-id>"

# Deploy
func azure functionapp publish resumeanalyzerfunc
```

You’ll see:

```
Deployment successful.
App URL: https://resumeanalyzerfunc.azurewebsites.net
```

---

# 📘 API Documentation

## **Overview**

This API suite automates the extraction of insights from uploaded resumes using **Azure Cognitive Services** (Form Recognizer + Text Analytics), **Azure Blob Storage**, and **Cosmos DB**.
There are **three major functions** (APIs):

| Function Name       | Trigger Type        | Purpose                                              |
| ------------------- | ------------------- | ---------------------------------------------------- |
| `upload_resume`     | HTTP Trigger (POST) | Uploads a resume to Blob Storage                     |
| `BlobTrigger`       | Blob Trigger        | Processes uploaded resumes and stores extracted data |
| `GetResumeInsights` | HTTP Trigger (GET)  | Fetches processed insights from Cosmos DB            |

<img width="1902" height="915" alt="image" src="https://github.com/user-attachments/assets/8c0d3164-303b-44b0-a83e-24c33bf87968" />


---

## 🔹 **1. Upload Resume API**

### **Endpoint**

```
POST /api/uploadresume
```

### **Purpose**

Uploads a PDF resume to the Azure Blob Storage container `resumes`.
Once uploaded, the **Blob Trigger** automatically processes the file and extracts insights.

### **Headers**

| Key          | Value               |
| ------------ | ------------------- |
| Content-Type | multipart/form-data |

### **Request Payload**

**Form Data:**

| Field  | Type        | Required | Description           |
| ------ | ----------- | -------- | --------------------- |
| `file` | File (.pdf) | ✅        | Resume file to upload |

### **Example CURL Command**

```bash
curl -X POST "http://localhost:7071/api/uploadresume" \
  -F "file=@Ashish_Jha_Developer.pdf"
```
<img width="1896" height="788" alt="Screenshot 2025-11-11 200217" src="https://github.com/user-attachments/assets/6394a802-84f5-4efa-be5d-3fbd8b5df66a" />

### **Response (Success)**

```text
File uploaded successfully!
```

### **Response (Failure)**

```text
Error: Invalid file type or upload failure.
```
<img width="1919" height="979" alt="Screenshot 2025-11-11 200740" src="https://github.com/user-attachments/assets/f443d072-1088-457e-9204-8f05e45f15c7" />

---

## 🔹 **2. Blob Trigger (Automatic Processing)**

### **Trigger Type**

`Blob Trigger`

### **Trigger Path**

```
resumes/{name}
```

### **Purpose**

Automatically triggers when a new file is uploaded to the container `resumes`.

### **Processing Steps**

1. Generates a **SAS URL** for the uploaded blob.
2. Sends the blob to **Form Recognizer** (`prebuilt-document` model) to extract raw text.
3. Uses **Text Analytics** APIs to extract:

   * Named entities (skills, organizations, dates, etc.)
   * Key phrases
   * Summary text
4. Stores extracted data in **Cosmos DB** in the following format:

### **Document Schema (Cosmos DB)**

```json
{
  "id": "3f1c8b21-99ef-4db1-845f-89a0ad9f1e1d",
  "fileName": "Ashish_Jha_Developer.pdf",
  "summary": "Experienced Azure Developer with 3 years in cloud automation...",
  "name": "Ashish Jha",
  "key_phrases": ["Azure", "Python", "Microservices", "Cloud Security"],
  "entities": [
    {"text": "Microsoft", "category": "Organization"},
    {"text": "Python", "category": "Skill"}
  ],
  "uploadTime": "2025-11-01T17:00:00Z"
}
```
<img width="1919" height="995" alt="Screenshot 2025-11-11 200626" src="https://github.com/user-attachments/assets/12b6fdb7-5b12-4fb7-88ce-b21415c51e61" />



<img width="1512" height="958" alt="Screenshot 2025-11-11 201148" src="https://github.com/user-attachments/assets/79667937-cf64-4a47-bb6c-ade212e3050b" />


---

## 🔹 **3. Get Resume Insights API**

### **Endpoint**

```
GET /api/GetResumeInsights?filename={resume_file_name}
```

### **Purpose**

Retrieves the processed insights (summary, entities, skills, etc.) for the given uploaded resume from **Cosmos DB**.

### **Query Parameters**

| Parameter  | Required | Description                                                     |
| ---------- | -------- | --------------------------------------------------------------- |
| `filename` | ✅        | Name of the uploaded resume file (must exactly match file name) |

### **Example CURL Command**

```bash
curl "http://localhost:7071/api/GetResumeInsights?filename=Ashish_Jha_Developer.pdf"
```
<img width="1912" height="1126" alt="Screenshot 2025-11-11 200458" src="https://github.com/user-attachments/assets/b44fbd70-5cce-4584-8f0a-37e1258a098e" />

### **Example Response**

```json
{
  "Name": "Ashish Jha",
  "Summary": "Experienced Azure developer skilled in microservices, cloud automation, and AI integration.",
  "Skills": ["Azure", "Python", "AI", "Cloud"],
  "Organizations": ["Microsoft", "Tech Mahindra"],
  "Dates": ["2021", "2023"],
  "Key Phrases": ["Cloud Development", "AI-powered solutions", "Azure automation"]
}
```

### **Response Codes**

| Status Code | Description                   |
| ----------- | ----------------------------- |
| 200         | Success — data retrieved      |
| 404         | Resume not found in Cosmos DB |
| 400         | Missing filename parameter    |

<img width="1918" height="980" alt="Screenshot 2025-11-11 201048" src="https://github.com/user-attachments/assets/5bc5f6c4-0eab-4c17-8f35-2986d666a84c" />

---

## 🧩 **Supporting Functions**

### **Helper Function: `generate_sas_url(container_name, blob_name)`**

Generates a **15-minute temporary SAS URL** for Form Recognizer to read the uploaded blob.

### **Helper Function: `analyze_document(blob_url)`**

Uses **Form Recognizer** (`prebuilt-document`) to extract text and structure from the resume.

### **Helper Function: `extract_entities(text)`**

Extracts named entities (like Person, Skill, Organization) using **Text Analytics**.

### **Helper Function: `extract_summary(text)`**

Generates an abstract summary using **Azure Language Service** summarization feature.

### **Helper Function: `store_in_cosmos(...)`**

Persists extracted resume insights into **Cosmos DB**.

---

## ⚙️ **Environment Variables**

| Variable              | Description                        |
| --------------------- | ---------------------------------- |
| `FORM_ENDPOINT`       | Endpoint for Azure Form Recognizer |
| `FORM_KEY`            | Key for Azure Form Recognizer      |
| `TEXT_ENDPOINT`       | Endpoint for Text Analytics        |
| `TEXT_KEY`            | Key for Text Analytics             |
| `COSMOS_DB_ENDPOINT`  | Cosmos DB endpoint URL             |
| `COSMOS_DB_KEY`       | Cosmos DB primary key              |
| `COSMOS_DB_DATABASE`  | Cosmos DB database name            |
| `COSMOS_DB_CONTAINER` | Cosmos DB container name           |
| `AzureWebJobsStorage` | Connection string for Blob Storage |

---

# 🧠 **Common Issues**

| Error                               | Fix                                                              |
| ----------------------------------- | ---------------------------------------------------------------- |
| `ModuleNotFoundError`               | Check `requirements.txt` and reinstall dependencies              |
| `Storage connection string invalid` | Regenerate keys from Azure Portal                                |
| `503 Site Unavailable`              | Restart your Function App from Azure Portal                      |
| `NameError: json not defined`       | Add `import json` at the top of your function                    |
| `Access Denied (Blob)`              | Ensure SAS tokens are generated properly with `read` permissions |

---

# **Tools and Technologies Used**

| Tool / Service                                     | Purpose                                                                |
| -------------------------------------------------- | ---------------------------------------------------------------------- |
| **Azure Function App**                             | Serverless compute platform to host and run lightweight backend logic. |
| **Azure Blob Storage**                             | Stores uploaded resumes (PDF files).                                   |
| **Azure Cognitive Services (Language Service)**    | Extracts and summarizes text from resumes.                             |
| **Python (Function App runtime)**                  | Core language for writing business logic.                              |
| **Visual Studio Code + Azure Functions Extension** | Local development and debugging of the function app.                   |
| **Postman / Curl**                                 | For testing APIs locally.                                              |
| **Azure CLI**                                      | For setting up function app and resource connections.                  |

---

# **Challenges Faced**

| Challenge                               | Description                                               | Resolution                                                                |
| --------------------------------------- | --------------------------------------------------------- | ------------------------------------------------------------------------- |
| **File Type Validation**                | Need to ensure only `.pdf` files are uploaded.            | Added validation logic in the function; throw HTTP 400 error for non-PDF. |
| **Malformed URL errors**                | Issues with filenames containing spaces.                  | Used URL encoding (`%20`) or quotes around filenames.                     |
| **Azure Cognitive Services API errors** | Encountered `name 'ExtractSummaryAction' is not defined`. | Installed correct SDK version and imported from `azure.ai.textanalytics`. |
| **Authentication setup**                | Needed Cognitive Service endpoint and key.                | Stored them in local.settings.json for local dev.                         |



---

# **Future Enhancements**

* To provide more query option on resumes , more filters on name, time , skills.
* Store analysis results in **Cosmos DB** for querying and analytics.
* Build a **frontend (React/Azure Static Web App)** for user interaction.


---
