import os
import sys
import json
import google.generativeai as genai
from dotenv import load_dotenv
import time 

def api_key_load():
    """
    Loads the Google API Key from the .env file.
    """
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("ERROR: GEMINI_API_KEY variable not found.")
        print("Make sure to create a .env file with your API key.")
        sys.exit(1)
        
    print("API Key loaded successfully.")
    return api_key

def configure_gemini_model(api_key):
    """
    Configures the Google API and returns the Gemini 2.5 model ready for use.
    """
    try:
        genai.configure(api_key=api_key)

        # Gemini 2.5 Flash Model (10 RPM) (preferred for quality)
        model = genai.GenerativeModel('gemini-2.5-flash') # Using 2.5 Flash model

        # Gemini 2.0 Flash Model (15 RPM) (for testing purposes)
        # model = genai.GenerativeModel('gemini-2.0-flash') # Using 2.0 Flash model

        print("Gemini 2.5 Flash model configured successfully.")
        return model
    
    except Exception as e: 
        print(f"An error occurred while configuring the Gemini model: {e}")
        sys.exit(1)

def read_logs(file_path):
    """
    Reads the log file and returns a list of blocks. Each block is separated by a 
    blank line.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            full_content = f.read()

            list_blocks = full_content.split('\n\n')

            logs = [block.strip() for block in list_blocks if block.strip()]
        return logs
    
    except FileNotFoundError:  
        print(f"ERROR: File not found at {file_path}")
        sys.exit(1)

    except Exception as e: 
        print(f"An error occurred while reading the file: {e}")
        sys.exit(1)

def analyze_log(model, log_text):
    """
    Sends a log to Gemini, requests tags in JSON format, and measures response time.
    Returns: (list_of_tags, api_duration_seconds)
    """

    prompt = f"""
            Act as an expert Log Analyst. Your task is to analyze the following log entry and 
            generate key thematic tags that classify the operation performed.

            Strict Rules:
            1. Generate a MAXIMUM of 3 tags.
            2. Focus on the main ACTION (e.g., 'SQL update', 'cache cleanup') and the OUTCOME (e.g., 'success', 'permission denied').
            3. Avoid generic tags like 'LLM response' or 'user input' unless they are the direct cause of an error.
            4. Your response must be *strictly* a valid JSON object containing a single key "tags".
            5. Standardize all tags and output them in English only.
            
            Example of desired output:
            {{"tags": ["SQL query", "timeout error", "success"]}}

            Log entry to analyze:
            ---
            {log_text}
            ---
            """
    
    try:
        start_time = time.time()
        response = model.generate_content(prompt)
        end_time = time.time()
        api_duration = end_time - start_time
        
        # Clean the response in case Gemini adds "```json"
        clean_response = response.text.strip().replace("```json", "").replace("```", "")
        
        # Use json.loads() to convert the response string into a dictionary
        json_data = json.loads(clean_response)
        
        # Validate that the JSON has the requested structure
        if "tags" in json_data and isinstance(json_data["tags"], list):
            return json_data["tags"], api_duration
        
        else:
            print(f"WARNING: Received JSON does not have the expected format: {clean_response}")
            return ["error-parsing"], api_duration

    except json.JSONDecodeError: # The model did not return valid JSON
        print(f"WARNING: Could not decode JSON from response: {response.text}")
        return ["error-json"], 0.0
    
    except Exception as e: # Another error occurred
        print(f"ERROR calling Gemini API: {e}")
        return ["error-api"], 0.0

def main():
    """
    Main execution function of the script.
    """

    # ===== Configuration ===== ##
    api_key = api_key_load()
    model = configure_gemini_model(api_key)
    
    # ===== File Paths ===== ##
    logs_file = "logs.txt"
    json_file = "output.json"
    
    # ===== Read Log File ==== # 
    blocks_to_process = read_logs(logs_file)
    print(f"\nRead {len(blocks_to_process)} blocks. Starting processing...")
    
    # ===== Processing Start ===== #
    list_outputs = []
    list_api_times = []
    
    for i, log in enumerate(blocks_to_process):        

        tags, api_time = analyze_log(model, log) 

        if api_time > 0:
            list_api_times.append(api_time)
        
        result = {
            "log_id": i + 1,
            "original_text": log, 
            "tags": tags          
        }

        list_outputs.append(result)
        
        # A delay must be applied between API calls to avoid saturation (Rate Limiting).
        # Optimization based on RPM: 4.1s for 2.0 Flash or 6.1s for 2.5 Flash.
        time.sleep(6.1)

        print(f"Blocks analyzed: {i+1}/{len(blocks_to_process)}", end="\r")

    # ===== Save Tags to JSON File ===== #
    try:
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(list_outputs, f, indent=4, ensure_ascii=False)
            
        print(f"\nProcess COMPLETED. Results successfully saved to {json_file}")
        
    except Exception as e:
        print(f"\nError saving JSON file: {e}")

    # === Print Average Response Time === #
    if list_api_times:
        mean_time = sum(list_api_times) / len(list_api_times)
        print(f"Average API response time: {mean_time:.2f} sec")

if __name__ == "__main__":
    main()