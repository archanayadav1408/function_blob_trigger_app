
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

## 🧠 9. Common Issues

| Error                               | Fix                                                              |
| ----------------------------------- | ---------------------------------------------------------------- |
| `ModuleNotFoundError`               | Check `requirements.txt` and reinstall dependencies              |
| `Storage connection string invalid` | Regenerate keys from Azure Portal                                |
| `503 Site Unavailable`              | Restart your Function App from Azure Portal                      |
| `NameError: json not defined`       | Add `import json` at the top of your function                    |
| `Access Denied (Blob)`              | Ensure SAS tokens are generated properly with `read` permissions |

---


