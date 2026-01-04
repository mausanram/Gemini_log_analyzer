# 🤖 Gemini Log Analyzer (GenAI)

This project implements an automated pipeline for server log classification and analysis using Large Language Models (LLMs), 
specifically **Google Gemini 2.5 Flash**. The system processes raw log files (`.txt`), applies prompt engineering to extract 
semantic context, and generates a structured output (`.json`) ready to be consumed by dashboards or monitoring systems.

## Project Overview
This script is an automated log analyzer that leverages a Google Large Language Model (LLM) to classify records. 
It specifically uses the Gemini 2.5 Flash model (or 2.0 Flash for testing). The script performs the following steps:

1.  **Secure Configuration:** Reads the `GEMINI_API_KEY` from a `.env` file to avoid exposing sensitive credentials.
2.  **Ingestion:** Opens `logs.txt` and parses each line as an individual log record, ignoring empty lines.
3.  **API Integration:** Iterates through each identified log and contacts the Google Gemini API.
4.  **Prompt Engineering:** Sends a specialized prompt instructing the model to act as an expert analyst and return thematic tags 
                            (e.g., `["SQL-query",  "timeout-error"]`) in a strict JSON format.
5.  **Rate Limiting:** Implements a strategic pause (`time.sleep()`) between calls to prevent API saturation (see "Technical Decisions" for details).
6.  **Aggregation:** Upon completion, aggregates all results and saves them to `output.json`, formatted with the log ID, 
                     original text, and AI-generated tags.

## Prerequisites
* **Python Version:** Python 3.10.12 or higher.
* **Google AI Studio API Key:** Required to execute the script. You can generate one at: **[Google AI Studio](https://aistudio.google.com/app/apikey)**.

### Installation & Execution

1.  **Clone the repository and create a virtual environment:**
    ```bash
    python -m venv venv
    ```

2.  **Activate the virtual environment (Linux/macOS):**
    ```bash
    source venv/bin/activate
    ```
    *(For Windows: `.\venv\Scripts\Activate.ps1`)*

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure credentials:** Create a `.env` file in the project root and add your key:
    ```ini
    GEMINI_API_KEY="YOUR_API_KEY_HERE"
    ```

5.  **Run the script:**
    ```bash
    python3 main.py
    ```

### Usage Example

The script accepts log blocks in `.txt` format, as shown below:
```text
[2025-10-20 09:13:42] [INFO] Agent DBConnector initialized. Awaiting query request.
[2025-10-20 09:13:45] [USER INPUT] "Muéstrame los cursos disponibles de Power BI con certificación."
[2025-10-20 09:13:45] [DEBUG] Building SQL query...
[2025-10-20 09:13:46] [SQL] SELECT nombre, certificacion, disponible FROM cursos WHERE tecnologia_id = 'Power BI';
[2025-10-20 09:13:47] [INFO] Query executed successfully. 12 records retrieved.
[2025-10-20 09:13:48] [LLM RESPONSE] “Encontré 12 cursos disponibles con certificación Power BI.”
```

Subsequently, the script processes each line, queries the Gemini API, and generates a standardized JSON structure where each 
log block is classified with a maximum of 3 standardized tags, as shown below:
```json
[
  {
    "log_id": 1,
    "timestamp": "2023-11-05 08:30:15",
    "tags": ["performance-issue", "sql-query", "high-latency"],
    "analysis": "Query executing smoothly but exceeding latency threshold."
  }
]
```


### Technical Decisions

**Model Selection:**
The **Gemini 2.5 Flash** model was selected despite Gemini 2.0 Flash offering a higher Requests Per Minute (RPM) limit (10 RPM vs. 15 RPM). 
The rationale is that for a log classification task, tag quality and precision are the primary objectives. Since 2.5 Flash is a newer 
generation model with superior reasoning capabilities, it provides more intelligent and useful log classification. This project prioritized 
high-quality results over marginally faster execution.

**RPM Management (Rate Limiting):**
The Gemini free tier API imposes strict frequency limits that must be managed to avoid failures. For the 2.5 Flash model, the free tier has 
a limit of 10 Requests Per Minute (RPM); therefore, a simple loop would fail with a `429 Too Many Requests` error after the tenth log.
To ensure the script processes logs 100% robustly, a fixed `time.sleep(6.1)` was implemented between every API call. This delay ensures a rate 
of ~9.8 requests per minute, operating safely within the limit. This strategy guarantees correct execution on any machine, regardless of network 
speed or Google server latency variables.

> **Note:** The delay required for the 2.0 Flash model (with 15 RPM) is 4.1 seconds. Considering the Requests Per Day (RPD) limit is 250 for 2.5 Flash and 200 for 2.0 Flash, the time difference when analyzing 200 logs is around 7 minutes, which is not a significant duration at this scale. This further supports the decision to use 2.5 Flash.

**Secure Credential Management (python-dotenv):**
To avoid exposing sensitive credentials (the API Key) directly in the source code, the `python-dotenv` library is used to load the `GEMINI_API_KEY` from a local `.env` file. This `.env` file is excluded from version control (via `.gitignore`), ensuring the secret key is never shared publicly on repositories like GitHub.

**Prompt Engineering:**
The prompt sent to the model was optimized to ensure more precise responses. It explicitly requests that tags be generated in English 
(matching the provided example) and limits the output to a maximum of 3 tags. This constraint forces the model to think and reason about the best 
options rather than simply extracting words found within the text itself. The model is also instructed to standardize its responses to avoid a proliferation of different tags for the same log feature. These measures reduce the risk of the model committing errors such as hallucinations.

## 👤 Author

**Mauricio Sánchez**
* [LinkedIn](https://www.linkedin.com/in/mauricio-s%C3%A1nchez-ram%C3%ADrez-497a92285)
* [GitHub](https://github.com/mausanram)

*This project was developed as part of a Data Engineering & AI portfolio.*

