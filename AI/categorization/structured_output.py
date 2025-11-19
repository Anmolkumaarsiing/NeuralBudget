import google.generativeai as genai
import os
import json
from datetime import datetime
from dotenv import load_dotenv

# Load env first
load_dotenv()

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    api_key = os.getenv("GOOGLE_API_KEY")

if api_key:
    genai.configure(api_key=api_key)

# === Category Logic ===
CATEGORY_KEYWORDS = {
    "Dining Out & Entertainment": ["restaurant", "cafe", "food", "zomato", "swiggy", "movie", "concert", "netflix", "spotify"],
    "Education & Self-Development": ["course", "udemy", "book", "training", "workshop", "education"],
    "Groceries & Essentials": ["grocery", "supermarket", "essentials", "milk", "vegetables"],
    "Healthcare & Insurance": ["hospital", "pharmacy", "medicine", "insurance", "doctor", "clinic"],
    "Housing": ["rent", "mortgage", "apartment", "housing", "property", "home"],
    "Transportation": ["uber", "ola", "flight", "train", "bus", "taxi", "fuel"],
    "Utilities": ["electricity", "water", "internet", "phone", "gas"],
    "Other": []
}

def process_transaction_text(ocr_text: str, user_id: str) -> dict:
    # === Get Categories ===
    categories = list(CATEGORY_KEYWORDS.keys())

    # === Prompt the model ===
    prompt = f"""
    You are a specialized AI for converting raw text from a transaction receipt into a structured JSON object. 
    Your ONLY output should be a single, valid JSON object. Do not include any other text, explanations, or markdown.

    The user has provided the following text extracted from a transaction:
    ---
    {ocr_text}
    ---

    Analyze the text and extract the required information.

    Available categories for the "category" field are:
    {categories}

    **Instructions:**
    1.  **Parse the text:** Identify the transaction amount, date, and the name of the merchant or recipient.
    2.  **Categorize:** Assign the most appropriate category from the provided list. If no category fits, use "Other".
    3.  **Generate Name:** Create a short, descriptive name for the transaction based on its context (e.g., "Dinner at restaurant", "Monthly grocery shopping", "Taxi fare").
    4.  **Format Output:** Structure the data into the JSON format below.

    **JSON Output Format:**
    {{
      "transaction": {{
        "amount": <number>,
        "category": "<string, from the list>",
        "date": "YYYY-MM-DD",
        "name": "<string, descriptive name>",
        "status": "Pending"
      }}
    }}

    **IMPORTANT:**
    - If the provided text is empty, unreadable, or clearly not a financial transaction, you MUST return the following specific JSON object and nothing else:
      {{
        "error": "Invalid or unreadable transaction text."
      }}
    - The "amount" must be a number, without any currency symbols or commas.
    - The "date" must be in YYYY-MM-DD format.
    - The "category" MUST be one of the provided categories.
    - Your entire response must be ONLY the JSON object.
    """

    try:
        model = genai.GenerativeModel('gemini-flash-latest')
        response = model.generate_content(prompt)
        
        response_text = response.text
        # Clean up markdown if present
        if '```json' in response_text:
            response_text = response_text.split('```json')[1].split('```')[0]
        elif '```' in response_text:
            response_text = response_text.split('```')[1].split('```')[0]
        
        raw_data = json.loads(response_text.strip())

        # Check if the LLM returned a structured error
        if raw_data.get("error"):
            print(f"LLM returned a structured error: {raw_data['error']}")
            transaction = {
                "amount": 0,
                "category": "Other",
                "date": datetime.now().strftime('%Y-%m-%d'),
                "name": "Unreadable Transaction",
                "status": "Failed"
            }
        else:
            # Initialize with defaults to ensure structure
            transaction = {
                "amount": 0,
                "category": "Other",
                "date": datetime.now().strftime('%Y-%m-%d'),
                "name": "Unnamed Transaction",
                "status": "Pending"
            }
            llm_transaction = raw_data.get("transaction", {})
            
            # Ensure llm_transaction is a dict before updating
            if isinstance(llm_transaction, dict):
                transaction.update(llm_transaction)
            else:
                # Log if the transaction format is not a dict, and use defaults
                print(f"Warning: LLM returned 'transaction' but it was not a dictionary. Using defaults.")

    except Exception as e:
        print(f"Error parsing LLM response: {e}")
        transaction = {
            "amount": 0,
            "category": "Other",
            "date": datetime.now().strftime('%Y-%m-%d'),
            "name": "Processing Error",
            "status": "Failed"
        }

    # Final validation and timestamping
    if transaction.get("category") not in categories:
        transaction["category"] = "Other"
        
    transaction["timestamp"] = datetime.now().isoformat()

    return transaction