# LLM-TextAnalyzer

**LLM-TextAnalyzer** is a fully deployable system designed for automated text analysis using state-of-the-art Large Language Models (LLMs). It supports processing text from JSON or CSV files, executing queries based on predefined questions, and storing the results in a NoSQL database. The project integrates multiple cutting-edge LLMs, allowing dynamic model selection and efficient text processing. Thanks to its Docker-based architecture, **LLM-TextAnalyzer** is easily deployable and scalable, ensuring a robust and flexible solution for various text analysis needs.


## Main Features:  
- **Data ingestion from JSON or CSV files**: The system processes files containing a collection of texts (e.g., abstracts of scientific papers).  
- **Automated query execution**: A predefined set of questions is automatically submitted to each text, leveraging LLMs to perform tasks such as:  
  - Keyword extraction  
  - Summarization  
  - Consistency checking with a specific topic  
- **Result storage**: Query results are stored in a NoSQL database for future analysis and retrieval.  
- **Scalable architecture**: The system is designed to support distributed environments, enabling content distribution via Kafka through connectors like [Kafka Connect File Pulse](https://github.com/streamthoughts/kafka-connect-file-pulse).  
- **Support for multiple cutting-edge LLM solutions**: The project is compatible with various on-premise LLM deployments, including [OnPrem LLM](https://github.com/amaiya/onprem), allowing flexibility in model selection and execution.  
- **Dynamic model downloading and management**: The system automatically downloads LLM models based on a configuration file, ensuring the right models are available for analysis. Downloads are resumable, allowing for interruption handling and efficient model retrieval.  


## Requirements

Here is the **Requirements** section for your README:

---

## Requirements  

To deploy and run **LLM-TextAnalyzer**, ensure you have the following prerequisites installed:

### **System Requirements**  
- A **64-bit OS** (Linux, Windows, macOS)  
- At least **4 CPU cores** (recommended: 8+)  
- Minimum **8GB RAM** (recommended: 16GB+)  
- **10GB+ free disk space** for model storage and logs  

### **Software Requirements**  
- [Docker](https://docs.docker.com/get-docker/) 

### **Environment Variables**  
Ensure that you have a `.env` file in the project root with the required environment variables. The application relies on environment variables to configure services such as CouchDB and Fluentd.

```bash
COUCHDB_URL=couchdb:5984
COUCHDB_USER=your_username  
COUCHDB_PASSWORD=your_password  
MODEL_DIR=/datasets/llm_model

DOCKER_BUILDKIT=1
COMPOSE_DOCKER_CLI_BUILD=1
``` 

Modify the `.env` file as needed, particularly setting database credentials and paths.

These services are orchestrated via **Docker Compose**, ensuring seamless deployment and scalability.  

## Getting Started

### 1. Clone the Repository  
First, clone the repository and navigate into the project directory:

```bash
git clone https://github.com/menga28/LLM-TextAnalyzer/git
cd LLM-TextAnalyzer
``` 

### 2. Model Selection & Management (Optional)
The system dynamically downloads and manages LLM models based on the **`onprem/config.py`** file. You can modify this file to:
- **Add or remove models**
- **Change the default model**
- **Adjust prompt templates for specific models**

#### **Example `config.py` File:**
```python
import os

MODEL_DIR = os.path.join("datasets", "llm_model")
ACTUAL_MODEL = "DeepSeek-R1-8B"  # Change this to use a different default model

MODELS = [
    {
        "id": "mistral-7b",
        "filename": "mistral-7b-instruct-v0.2.Q4_K_M.gguf",
        "path": os.path.join(MODEL_DIR, "mistral-7b-instruct-v0.2.Q4_K_M.gguf"),
        "url": "https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf",
        "hash_md5": "d98804ecfe3f274b46aed70d9257945e",
        "prompt_template": f"""[INST] {COMMON_SYSTEM_PROMPT}\n{{prompt}} [/INST]"""
    },
    {
        "id": "llama-3.2-3b",
        "filename": "Llama-3.2-3B-Instruct-uncensored-Q8_0.gguf",
        "path": os.path.join(MODEL_DIR, "Llama-3.2-3B-Instruct-uncensored-Q8_0.gguf"),
        "url": "https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-uncensored-GGUF/resolve/main/Llama-3.2-3B-Instruct-uncensored-Q8_0.gguf",
        "hash_md5": "08dd494d754c926afddc737400ab6c91",
        "prompt_template": (
            "<|begin_of_text|>"
            "<|start_header_id|>system<|end_header_id|>\n\n"
            f"{COMMON_SYSTEM_PROMPT}<|eot_id|>"
            "<|start_header_id|>user<|end_header_id|>\n\n"
            "{prompt}<|eot_id|>"
            "<|start_header_id|>assistant<|end_header_id|>\n\n"
        )
    },
    {
        "id": "DeepSeek-R1-8B",
        "filename": "DeepSeek-R1-Distill-Llama-8B-Q4_K_M.gguf",
        "path": os.path.join(MODEL_DIR, "DeepSeek-R1-Distill-Llama-8B-Q4_K_M.gguf"),
        "url": "https://huggingface.co/unsloth/DeepSeek-R1-Distill-Llama-8B-GGUF/resolve/main/DeepSeek-R1-Distill-Llama-8B-Q4_K_M.gguf",
        "hash_md5": "3bf955d9c842acc1211326046a1275c8",
        "prompt_template": """<|begin_of_text|><|start_header_id|>system<|end_header_id|>
                            You are a concise assistant. Provide only the direct answer to the question, without explanations, reasoning, or additional context.
                            <|eot_id|><|start_header_id|>user<|end_header_id|>
                            {prompt}
                            <|eot_id|><|start_header_id|>assistant<|end_header_id|>
                            """
    }
]
```
To **disable a model**, simply remove or comment it out from the `MODELS` list.

If you do not modify this file, the system will download and use the default models listed in `config.py`.  

> ⚡ **Download Resumption**: If a model download is interrupted, the system will automatically resume it on the next execution.

### 3. Start the System  
To deploy all services, simply run:

```bash
docker-compose up -d
```

This will:
- Build and start the required containers.  
- Automatically download and set up the required LLM models (if not already present).  
- Initialize the database and services.  

## Usage

### 1. **Providing Input Data**
To use **LLM-TextAnalyzer**, you must structure your data using XML files stored in the `datasets/` directory. The system processes three types of XML files:

- **`content.xml`**: Contains the abstracts of academic papers or other textual content for analysis.
- **`query.xml`**: Defines a set of questions to be asked about each text in `content.xml`.
- **`result.xml`**: Stores the responses generated by the LLM.

Each file must be placed inside the `datasets/` directory before starting the system. The system continuously monitors these files and processes new inputs automatically.

---

### 2. **Example of Input Files**
#### **1. `content.xml` (Abstracts)**
Each `content.xml` file contains a list of textual items to analyze. The system will process these texts and generate responses based on predefined queries.

```xml
<xml>
    <search>
        <query>
            "digital twin platform" OR "DT Platform"
        </query>
        <items>
            <item>
                <uuid>044897fa-5520-4e41-8a61-dd9a89f91ba8</uuid>
                <title>Evaluating carbon emissions from the operation of historic dwellings in cities</title>
                <abstract>Historic dwellings in cities are considered an important resource for carbon neutrality due to their potential for low-carbon renewal...</abstract>
            </item>
            <item>
                <uuid>26b70aa6-0a69-4058-b58f-9156402386d5</uuid>
                <title>A digital twin-based adaptive optimization approach</title>
                <abstract>Renewable-dominated power grids require industries to adjust operations based on energy availability. This research presents a digital twin platform for optimization...</abstract>
            </item>
        </items>
    </search>
</xml>
```

#### **2. `query.xml` (Questions)**
Defines the set of queries applied to each text in `content.xml`.

```xml
<xml>
    <questions>
        <question>
            <id>5dbd3c18-b7ac-4dfd-accb-97294f731bea</id>
            <text>Does the text mention open-source? Respond yes or no.</text>
        </question>
        <question>
            <id>0832d05a-662c-49c0-8bbf-4a950fe9787c</id>
            <text>Does the text describe the development of a digital twin platform?</text>
        </question>
    </questions>
</xml>
```

---

### 3. **Processing the Data**
Once `content.xml` and `query.xml` are placed in the `datasets/` directory, the system will automatically:
1. **Parse** the files.
2. **Use the LLM model** to answer the questions.
3. **Store the results** in `result.xml`.

---

### 4. **Retrieving Results**
After processing, the system generates `result.xml` containing the responses:

```xml
<xml>
    <results>
        <result content_id="044897fa-5520-4e41-8a61-dd9a89f91ba8">
            <answers>
                <answer id="5dbd3c18-b7ac-4dfd-accb-97294f731bea">
                    <text>no</text>
                </answer>
                <answer id="0832d05a-662c-49c0-8bbf-4a950fe9787c">
                    <text>Yes, the text mentions the development of a digital twin management platform as part of the proposed approach for evaluating carbon emissions.</text>
                </answer>
            </answers>
        </result>
        <result content_id="26b70aa6-0a69-4058-b58f-9156402386d5">
            <answers>
                <answer id="5dbd3c18-b7ac-4dfd-accb-97294f731bea">
                    <text>no</text>
                </answer>
                <answer id="0832d05a-662c-49c0-8bbf-4a950fe9787c">
                    <text>Yes, the text describes the implementation and experimental evaluation of micro-services on a standardized digital twin platform.</text>
                </answer>
            </answers>
        </result>
    </results>
</xml>
```

## Architecture  

The architecture of **LLM-TextAnalyzer** is designed for modularity, scalability, and efficient text processing using Large Language Models (LLMs). The system is composed of multiple interconnected services managed via **Docker Compose**, ensuring a seamless deployment experience.  

---

### **Core Components**  

### **1. Data Ingestion & Processing**  
- **Fluentd**  
  - Monitors the `datasets/` directory for new XML files.  
  - Extracts structured content from `content.xml` and `query.xml`.  
  - Prepares and forwards processed data to CouchDB for storage.  

- **Spark**  
  - Provides scalable and distributed processing for handling large-scale text data.  
  - Ensures efficient computation when working with a high volume of queries.  

---

### **2. Storage & Data Management**  
- **CouchDB**  
  - Stores processed texts, queries, and generated results.  
  - Provides a NoSQL document-based storage system for efficient retrieval and analysis.  

- **Datasets Volume** (`datasets/`)  
  - Serves as a shared storage for raw text inputs, queries, and results.  
  - Holds dynamically downloaded LLM models used for inference.  

---

### **3. Model Inference & LLM Execution**  
- **OnPrem LLM Server**  
  - Runs inference using dynamically downloaded LLM models.  
  - Supports multiple models defined in `onprem/config.py`.  
  - Provides an API for handling queries and returning responses.  

- **Model Management**  
  - Automatically downloads LLM models based on `config.py`.  
  - Supports resuming downloads in case of interruptions.  

---

### **4. API & User Interaction**  
- **Flask Application**  
  - Exposes REST API endpoints for submitting text queries and retrieving results.  
  - Communicates with the OnPrem LLM service to process queries dynamically.  

- **Result Storage**  
  - The system generates `result.xml`, storing answers for each processed query.  
  - Users can fetch structured responses directly via the API or from CouchDB.  

Services interact seamlessly through predefined networking and volume configurations.  

---
### **Port Mappings**
  - `5001` → OnPrem LLM Server  
  - `5984` → CouchDB Admin Panel  
---

### **Component Interactions**  

| Component       | Function |
|----------------|----------|
| **Fluentd**    | Monitors XML files, extracts data, forwards to CouchDB |
| **Spark**      | Enables distributed text processing for large datasets |
| **CouchDB**    | Stores input texts, queries, and results |
| **OnPrem LLM** | Executes inference with selected LLM models |
| **Flask API**  | Provides endpoints for submitting queries and retrieving results |

## Acknowledgments  

This project was developed as part of the **"Technologies for Big Data Management"** course at the [University of Camerino](http://www.didattica.cs.unicam.it/doku.php?id=start).  

### **Creators**  
- [Michele Mengascini](https://github.com/menga28)  
- [Simone Micarelli](https://github.com/Elmicass)  
