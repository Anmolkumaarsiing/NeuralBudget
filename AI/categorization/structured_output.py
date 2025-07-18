from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from dotenv import load_dotenv
import os
import sys
import json
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

# Load env first
load_dotenv()

# Import Firestore client from centralized setup
from apps.common_utils.firebase_config import db

# Add OCR module path
sys.path.append(os.path.abspath("../text_recognition"))
from run_ocr import get_ocr_text

# === OCR Image ===
image_path = "../image.png"
res_text = get_ocr_text(image_path)

# === LLM Setup ===
llm = HuggingFaceEndpoint(
    repo_id="mistralai/Mistral-7B-Instruct-v0.3",
    task="text-generation",
    huggingfacehub_api_token=os.getenv("HUGGINGFACEHUB_API_TOKEN"),
    max_new_tokens=500,
    temperature=0.6,
)

model = ChatHuggingFace(llm=llm)

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

def categorize_transaction(name: str) -> str:
    name = name.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in name for keyword in keywords):
            return category
    return "Other"

# === Prompt the model ===
prompt = f"""
You are an AI assistant that processes OCR UPI transaction data.

Here is the unstructured OCR text:
\"\"\"{res_text}\"\"\"

Extract and return the following JSON format:
{{
  "transaction": {{
    "amount": number,
    "category": "string (you can leave it empty)",
    "date": "YYYY-MM-DD",
    "name": "string (receiver/sender name)",
    "status": "Pending"
  }}
}}

- Always use "Pending" as status.
- Amount should be numeric (no ₹ or commas).
- Date format must be YYYY-MM-DD.
- Return only valid JSON.
"""

response = model.invoke(prompt)

# === Parse JSON ===
try:
    raw_data = json.loads(response.content if hasattr(response, "content") else response)
    transaction = raw_data.get("transaction", {})
except Exception as e:
    print("Error parsing response:", e)
    transaction = {
        "amount": 0,
        "category": "",
        "date": "1970-01-01",
        "name": "Unknown",
        "status": "Pending"
    }

transaction["category"] = categorize_transaction(transaction.get("name", ""))
transaction["timestamp"] = datetime.now().isoformat()

# === Save to Firestore ===
user_id = "demo_user"  # Replace this with dynamic user ID later
db.collection("transactions").document(user_id).set(transaction)

print("\nTransaction saved to Firestore!")
print(json.dumps(transaction, indent=2))
