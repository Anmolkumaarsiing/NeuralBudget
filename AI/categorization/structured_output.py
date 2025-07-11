from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from dotenv import load_dotenv
import os
import sys
import json
from home.firebase_config import db, get_categories, add_transaction, get_transactions, add_category
from google.cloud.firestore_v1.base_query import FieldFilter
from typing import List, Dict
from datetime import datetime

# Step 1: Load environment variables
load_dotenv()

# Step 2: Add OCR script path
sys.path.append(os.path.abspath("../text_recognition"))
from run_ocr import get_ocr_text

# Step 3: Get OCR text
image_path = "../image.png"
res_text = get_ocr_text(image_path)

# Step 4: Setup the LLM
llm = HuggingFaceEndpoint(
    repo_id="mistralai/Mistral-7B-Instruct-v0.3",
    task="text-generation",
    huggingfacehub_api_token=os.getenv("HUGGINGFACEHUB_API_TOKEN"),
    max_new_tokens=500,
    temperature=0.6,
)

# Step 5: Use Chat wrapper with your LLM
model = ChatHuggingFace(llm=llm)

# Step 6: Categorization rules
CATEGORY_KEYWORDS = {
    "Dining Out & Entertainment": ["restaurant", "cafe", "food", "zomato", "swiggy", "movie", "concert", "netflix", "spotify"],
    "Education & Self-Development": ["course", "udemy", "book", "training", "workshop", "education"],
    "Groceries & Essentials": ["grocery", "supermarket", "essentials", "milk", "vegetables"],
    "Healthcare & Insurance": ["hospital", "pharmacy", "medicine", "insurance", "doctor", "clinic"],
    "Housing": ["rent", "mortgage", "apartment", "housing", "property","home"],
    "Transportation": ["uber", "ola", "flight", "train", "bus", "taxi", "fuel"],
    "Utilities": ["electricity", "water", "internet", "phone", "gas"],
    "Other": []
}

def categorize_transaction(store_name: str, items: List[Dict]) -> str:
    store_name = store_name.lower()
    item_names = [item["name"].lower() for item in items] if items else []
    valid_categories = get_categories()  # Fetch valid categories from Firestore
    for category, keywords in CATEGORY_KEYWORDS.items():
        if category not in valid_categories:
            add_category(category)  # Add missing category to Firestore
        if any(keyword in store_name for keyword in keywords):
            return category
        for item_name in item_names:
            if any(keyword in item_name for keyword in keywords):
                return category
    return "Other"

# Step 7: Format prompt for structured JSON output
prompt = f"""
You are a helpful assistant that structures OCR text from UPI transactions.

Here is the unstructured OCR text:
\"\"\"{res_text}\"\"

Extract the information and return it in the following JSON format:
{{
  "store_name": "string",
  "date": "string (DD-MM-YYYY)",
  "total_amount": "string",
  "expense_type": "string (debit or credit)",
  "items": [
    {{
      "name": "string",
      "quantity": "string",
      "price": "string"
    }}
  ]
}}

- Ensure the date is in DD-MM-YYYY format.
- If items are not explicitly listed, set "items" to an empty list.
- Set "expense_type" to "debit" for UPI payments.
- Return only valid JSON.
"""

# Step 8: Invoke the model
response = model.invoke(prompt)

# Step 9: Parse and validate JSON output
try:
    structured_data = json.loads(response.content if hasattr(response, "content") else response)
except json.JSONDecodeError:
    print("Error: Model did not return valid JSON")
    structured_data = {
        "store_name": "",
        "date": "",
        "total_amount": "",
        "expense_type": "debit",
        "items": []
    }

# Step 10: Add category and timestamp to OCR data
structured_data["category"] = categorize_transaction(
    structured_data.get("store_name", ""),
    structured_data.get("items", [])
)
structured_data["timestamp"] = datetime.now().isoformat()

# Step 11: Save OCR data to Firestore
user_id = "example_user_id"  # Replace with actual user ID
add_transaction(user_id, structured_data, "transactions")

# Step 12: Fetch all transactions for the user
transactions = []
last_doc_id = None
while True:
    batch = get_transactions(user_id, "transactions", limit=100, start_after_doc_id=last_doc_id)
    if not batch:
        break
    transactions.extend(batch)
    last_doc_id = batch[-1]["id"] if batch else None

# Step 13: Categorize uncategorized transactions
valid_categories = get_categories()
for transaction in transactions:
    if not transaction.get("category") or transaction["category"] not in valid_categories:
        transaction["category"] = categorize_transaction(
            transaction.get("store_name", ""),
            transaction.get("items", [])
        )
        # Update Firestore with category
        db.collection("transactions").document(transaction["id"]).update({"category": transaction["category"]})

# Step 14: Save combined transactions to file
with open("transactions.json", "w") as f:
    json.dump(transactions, f, indent=2)

# Step 15: Print structured transactions
print("=== Structured Transactions ===")
print(json.dumps(transactions, indent=2))