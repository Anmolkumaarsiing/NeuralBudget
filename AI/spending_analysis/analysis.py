import os
import json
import sys
import warnings
from datetime import datetime
from dotenv import load_dotenv
from requests.exceptions import ReadTimeout
from google.cloud.firestore import Client
from google.api_core.exceptions import GoogleAPIError
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace

from google.cloud.firestore_v1 import SERVER_TIMESTAMP
from google.protobuf.timestamp_pb2 import Timestamp

# Suppress FutureWarning for cleaner output
warnings.filterwarnings("ignore", category=FutureWarning)

# --- Project Path Setup ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

# --- Firestore Client ---
from apps.common_utils.firebase_config import db  # Assumes same Firestore config as chatbot

# --- CONFIGURATION ---
load_dotenv()

LLM_REPO_ID = "mistralai/Mixtral-8x7B-Instruct-v0.1"  # Primary model (aligned with chatbot)
FALLBACK_LLM_REPO_ID = "HuggingFaceH4/zephyr-7b-beta"  # Fallback model
HUGGINGFACEHUB_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")

# --- INIT SERVICES ---
print("Initializing AI services for expense analysis...")

try:
    print("Testing Firestore connection...")
    test_doc = db.collection("test").document("connection_test").set({"test": "ok"})
    print("✅ Firestore connection test successful.")
except GoogleAPIError as e:
    print(f"❌ Firestore error: {e}")
    print("Check your Firebase service account key (firebase_key.json) and permissions.")
    sys.exit(1)

try:
    llm_endpoint = HuggingFaceEndpoint(
        repo_id=LLM_REPO_ID,
        huggingfacehub_api_token=HUGGINGFACEHUB_API_TOKEN,
        max_new_tokens=300,
        temperature=0.7,
        timeout=60,
    )
    llm = ChatHuggingFace(llm=llm_endpoint)
    print("✅ LLM initialized with ChatHuggingFace (Mixtral).")
except Exception as e:
    print(f"❌ Error initializing Mixtral LLM: {e}")
    print("Attempting fallback to zephyr-7b-beta...")
    try:
        llm_endpoint = HuggingFaceEndpoint(
            repo_id=FALLBACK_LLM_REPO_ID,
            huggingfacehub_api_token=HUGGINGFACEHUB_API_TOKEN,
            max_new_tokens=300,
            temperature=0.7,
            timeout=60,
        )
        llm = ChatHuggingFace(llm=llm_endpoint)
        print("✅ LLM initialized with ChatHuggingFace (Fallback).")
    except Exception as e:
        print(f"❌ Error initializing fallback LLM: {e}")
        print("Ensure your HUGGINGFACEHUB_API_TOKEN is set and the model is available.")
        sys.exit(1)

print("Services initialized.")

# --- DATA RETRIEVAL ---
def get_user_summary(user_id: str):
    print(f"Fetching transaction data for user: {user_id}...")
    try:
        transactions_ref = db.collection("transactions").where("userId", "==", user_id)
        docs = list(transactions_ref.stream())

        # Fallback if not found
        if not docs:
            transactions_ref = db.collection("transactions").where("id", "==", user_id)
            docs = list(transactions_ref.stream())


        monthly_totals, category_totals = {}, {}
        doc_count = 0

        for doc in docs:
            data = doc.to_dict()
            #print("📄 Raw doc:", data)

            txn = data.get("transaction", {})
            amount = float(txn.get("amount", 0))
            category = txn.get("category", "Other").strip().lower()
            date_val = txn.get("date")

            # --- Handle both string and Firestore Timestamp ---
            if isinstance(date_val, str):
                try:
                    date = datetime.strptime(date_val, "%Y-%m-%d")
                except ValueError:
                    print(f"❌ Invalid string date in {doc.id}: {date_val}")
                    continue
            else:
                try:
                    date = date_val.to_datetime()
                except Exception:
                    print(f"❌ Unsupported date format in {doc.id}: {date_val}")
                    continue

            # Monthly totals
            month_key = date.strftime("%Y-%m")
            monthly_totals[month_key] = monthly_totals.get(month_key, 0) + amount
            category_totals[category] = category_totals.get(category, 0) + amount

            doc_count += 1

        print(f"✅ Processed {doc_count} transaction(s) for user: {user_id}")
        return {"monthly_totals": monthly_totals, "categories": category_totals}

    except Exception as e:
        print(f"❌ Error processing transactions: {e}")
        return None

# ------------------- DEBUGGER -------------------------------  
    
def debug_user_ids():
    transactions_ref = db.collection("transactions")
    docs = list(transactions_ref.stream())
    user_ids = set()
    ids = set()

    for doc in docs:
        data = doc.to_dict()
        if "userId" in data:
            user_ids.add(data["userId"])
        if "id" in data:
            ids.add(data["id"])
    
    print("🔍 Distinct userIds in DB:", user_ids)
    print("🔍 Distinct ids in DB:", ids)




# --- RAG CHAIN FOR ANALYSIS ---
def create_analysis_chain():
    """Create a RAG chain for expense analysis and forecasting."""
    try:
        template = """
        You are "Neural Budget", a friendly financial coach. Analyze the user's spending data below and provide insights in Indian Rupees (₹).

        SPENDING DATA:
        {summary_json}

        TASKS:
        1. Analyze past spending trends (e.g., increasing/decreasing, overspending in specific months).
        2. Highlight the top 3 categories driving the most expenses.
        3. Predict the next month's total expenses based on trends (provide a range if possible).
        4. Suggest one practical improvement in a friendly, encouraging style with emojis 😊.

        ANSWER FORMAT:
        **Spending Trends**: <Your analysis>
        **Top Categories**: <List top 3 categories with amounts in ₹>
        **Next Month Prediction**: <Predicted range in ₹>
        **Tip for You**: <Practical suggestion>
        """
        prompt = ChatPromptTemplate.from_template(template)

        analysis_chain = (
            {"summary_json": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )
        return analysis_chain
    except Exception as e:
        print(f"❌ Error creating analysis chain: {e}")
        return None

# --- GENERATE ANALYSIS ---
def generate_expense_analysis(user_id: str):
    """Generate expense analysis and forecasting for a user."""
    print(f"Generating expense analysis for user: {user_id}...")
    summary = get_user_summary(user_id)
    if not summary:
        return "❌ Failed to retrieve user data. Please check Firestore configuration."

    summary_json = json.dumps(summary, indent=2)
    analysis_chain = create_analysis_chain()
    if not analysis_chain:
        return "❌ Failed to initialize analysis chain."

    try:
        response = analysis_chain.invoke(summary_json)
        print("✅ Analysis generated successfully.")
        return response
    except ReadTimeout as e:
        print(f"❌ ReadTimeoutError during analysis: {e}")
        return "❌ Analysis failed due to a timeout. Please try again later."
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        return "❌ Analysis failed. Please check LLM accessibility and try again."

# --- RUN ---
if __name__ == "__main__":
    test_user = "nQUxkJ1HkZZIPVboQytBLpbC4za2"  # Replace with your Firestore userId
    # print("Testing Firestore connection...")
    # debug_user_ids()
    print(f"\nRunning expense analysis for user: {test_user}")
    # insights = generate_expense_analysis(test_user)
    # print("\n💡 LLM Insights & Forecast:")
    # print(insights)
    
    insights = generate_expense_analysis(test_user)

    with open("analysis_output.txt", "w", encoding="utf-8") as f:
        f.write(insights)

    print("\n💡 LLM Insights & Forecast:\n")
    print(insights)
