import os
import sys
import warnings
from dotenv import load_dotenv
from requests.exceptions import ReadTimeout
from google.cloud.firestore import Client
from google.api_core.exceptions import GoogleAPIError
from google.cloud.firestore_v1 import FieldFilter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
from langchain_community.vectorstores.utils import filter_complex_metadata
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFaceEndpoint, ChatHuggingFace
from langchain_chroma import Chroma

# Suppress FutureWarning for cleaner output
warnings.filterwarnings("ignore", category=FutureWarning)

# --- Project Path Setup ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

# --- Firestore Client ---
from apps.common_utils.firebase_config import db
from apps.common_utils.firebase_service import get_transactions

# --- CONFIGURATION ---
load_dotenv()

EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
LLM_REPO_ID = "mistralai/Mixtral-8x7B-Instruct-v0.1"
FALLBACK_LLM_REPO_ID = "HuggingFaceH4/zephyr-7b-beta"
VECTOR_COLLECTION_NAME = "user_transaction_vectors"
CHROMA_PERSIST_DIR = "./chroma_db"

# --- INIT SERVICES ---
print("Initializing AI services...")

try:
    embedding_service = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    print("✅ Embedding service initialized.")
except Exception as e:
    print(f"❌ Error initializing embedding service: {e}")
    sys.exit(1)

try:
    llm_endpoint = HuggingFaceEndpoint(
        repo_id=LLM_REPO_ID,
        huggingfacehub_api_token=os.getenv("HUGGINGFACEHUB_API_TOKEN"),
        max_new_tokens=128,
        temperature=0.1,
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
            huggingfacehub_api_token=os.getenv("HUGGINGFACEHUB_API_TOKEN"),
            max_new_tokens=128,
            temperature=0.1,
            timeout=60,
        )
        llm = ChatHuggingFace(llm=llm_endpoint)
        print("✅ LLM initialized with ChatHuggingFace.")
    except Exception as e:
        print(f"❌ Error initializing fallback LLM: {e}")
        print("Ensure your HUGGINGFACEHUB_API_TOKEN is set and the model is available.")
        sys.exit(1)

try:
    print("Testing Firestore connection...")
    test_doc = db.collection("test").document("connection_test").set({"test": "ok"})
    print("✅ Firestore connection test successful.")
    vector_store = Chroma(
        collection_name=VECTOR_COLLECTION_NAME,
        embedding_function=embedding_service,
        persist_directory=CHROMA_PERSIST_DIR
    )
    print(f"✅ Vector store initialized in '{VECTOR_COLLECTION_NAME}' collection.")
except GoogleAPIError as e:
    print(f"❌ Firestore error: {e}")
    print("Check your Firebase service account key (firebase_key.json) and permissions.")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error initializing Chroma vector store: {e}")
    sys.exit(1)

print("Services initialized.")

# --- INDEXING ---
# --- INDEXING ---
def index_user_transactions(user_id: str, force_reindex=False):
    print(f"Starting indexing for user: {user_id} (force_reindex={force_reindex})...")
    try:
        # Fetch transactions and income using get_transactions
        transactions_data = get_transactions(user_id, "expenses", limit=1000) # Increased limit for comprehensive indexing
        income_data = get_transactions(user_id, "incomes", limit=1000) # Assuming an "income" collection

        all_docs = []
        # Process transactions
        for tx in transactions_data:
            # Ensure 'id' is present for Document creation
            if 'id' not in tx:
                tx['id'] = tx.get('source_transaction_id', 'unknown_id') # Fallback if 'id' is missing
            all_docs.append({'data': tx, 'collection': 'transactions'})

        # Process income
        for inc in income_data:
            if 'id' not in inc:
                inc['id'] = inc.get('source_transaction_id', 'unknown_id') # Fallback if 'id' is missing
            all_docs.append({'data': inc, 'collection': 'income'})

        documents_to_index = []
        doc_count = len(all_docs)
        if doc_count == 0:
            print(f"No new transactions or income to index for user: {user_id} (Found {doc_count} documents)")
            return False

        print(f"Processing {doc_count} transaction/income doc(s)...")
        for item in all_docs:
            raw = item['data']
            collection_type = item['collection']
            doc_id = raw.get('id')

            try:
                tx_payload = raw.get("transaction") if isinstance(raw.get("transaction"), dict) else raw
                required_fields = ["amount", "category", "date"] if collection_type == 'transactions' else ["amount", "source", "date"]
                missing = [f for f in required_fields if f not in tx_payload]
                if missing:
                    print(f"❌ Doc {doc_id} from {collection_type} missing fields: {missing}. Full doc keys: {list(raw.keys())}")
                    continue

                amount = tx_payload.get('amount')
                date = tx_payload.get('date')

                if collection_type == 'transactions':
                    category_raw = tx_payload.get("category", "")
                    category_norm = category_raw.strip().lower()
                    transaction_name = tx_payload.get("name", "").strip()
                    compact_content = (
                        f"type: expense, amount: {amount}, "
                        f"category: {category_norm}, date: {date}, "
                        f"name: {transaction_name}"
                    )
                    metadata_type = "expense"
                    metadata_category = category_norm
                    metadata_source = None
                    metadata_name = transaction_name
                else: # income
                    source_raw = tx_payload.get("source", "")
                    source_norm = source_raw.strip().lower()
                    transaction_name = tx_payload.get("name", "").strip()
                    compact_content = (
                        f"type: income, amount: {amount}, "
                        f"source: {source_norm}, date: {date}, "
                        f"name: {transaction_name}"
                    )
                    metadata_type = "income"
                    metadata_category = None
                    metadata_source = source_norm
                    metadata_name = transaction_name

                doc_to_add = Document(
                    page_content=compact_content,
                    metadata={
                        "user_id": user_id,
                        "source_document_id": doc_id,
                        "type": metadata_type,
                        "amount": amount,
                        "date": date,
                        "category": metadata_category,
                        "source": metadata_source,
                        "name": metadata_name # Add the transaction name to metadata
                    }
                )
                documents_to_index.append(doc_to_add)
            except Exception as e:
                print(f"❌ Error processing document {doc_id} from {collection_type}: {e}")
                continue

        if not documents_to_index:
            print(f"No valid documents to index after filtering for user: {user_id}")
            return False

        # Filter complex metadata before adding to vector store
        filtered_documents_to_index = filter_complex_metadata(documents_to_index)

        print("Generating test embedding to verify vector config...")
        try:
            test_embedding = embedding_service.embed_query(filtered_documents_to_index[0].page_content)
            print("✅ Sample embedding generated. Length:", len(test_embedding))
        except Exception as e:
            print(f"❌ Error generating test embedding: {e}")
            return False

        print(f"Adding {len(filtered_documents_to_index)} document(s) to '{VECTOR_COLLECTION_NAME}'...")
        vector_store.add_documents(documents=filtered_documents_to_index)
        try:
            if hasattr(vector_store, "persist"):
                vector_store.persist()
        except Exception:
            pass

        print(f"✅ Indexing complete for user: {user_id}")
        return True

    except GoogleAPIError as e:
        print(f"❌ Firestore error during indexing: {e}")
        print("Check Firestore permissions and ensure the 'transactions' and 'income' collections exist.")
        return False
    except Exception as e:
        print(f"❌ Error during indexing: {e}")
        return False

# --- RAG ---
def create_rag_chain_for_user(user_id: str):
    try:
        retriever = vector_store.as_retriever(
            search_kwargs={
                "k": 5,
                "filter": {"user_id": user_id}
            }
        )

        template = """
        You are "Neural Budget", a friendly financial assistant.
        If the user's query is a greeting (e.g., "Hi", "Hello", "How are you?"), respond with a friendly welcome message like "Hello! How can I help you with your finances today?".
        Otherwise, sum the 'amount' for transactions where 'category' or 'name' matches the category or name mentioned in the question: {question} (case-insensitive, treat 'food' and 'Groceries' as equivalent).
        Provide the answer concisely in Indian Rupees (₹), e.g., "You've spent ₹X.XX on [category/name] so far. Remember to keep track of your spending to stay on budget!" Do NOT include document IDs, metadata, or detailed breakdowns unless specifically asked.
        If no relevant transactions are found, say: "I don't have enough information to answer."

        CONTEXT:
        {context}

        QUESTION:
        {question}

        ANSWER:
        """
        prompt = ChatPromptTemplate.from_template(template)

        rag_chain = (
            {"context": retriever, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )
        return rag_chain
    except Exception as e:
        print(f"❌ Error creating RAG chain: {e}")
        return None

# --- RUN ---
def get_chatbot_response(user_id: str, message: str) -> str:
    """
    Provides a chatbot response based on user query and indexed transactions.
    """
    try:
        # Ensure user transactions are indexed
        index_user_transactions(user_id)

        # Create RAG chain for the user
        user_rag_chain = create_rag_chain_for_user(user_id=user_id)

        if user_rag_chain:
            response = user_rag_chain.invoke(message)
            return response
        else:
            return "I'm sorry, I couldn't initialize the financial assistant. Please try again later."
    except ReadTimeout as e:
        return f"I'm experiencing a timeout. Please check your internet connection or try again later. Error: {e}"
    except Exception as e:
        return f"An error occurred while processing your request: {e}"

# --- RUN ---
if __name__ == '__main__':
    current_user_id = "nQUxkJ1HkZZIPVboQytBLpbC4za2"

    index_user_transactions(current_user_id, force_reindex=True)

    print(f"\nCreating RAG chain for user: {current_user_id}")
    user_rag_chain = create_rag_chain_for_user(user_id=current_user_id)

    if user_rag_chain:
        print("--- Ready to Chat ---")
        questions = [
            "How much did I spend on Groceries?",
            "How much did I spend on Transport?",
            "How much did I spend on Entertainment?",
            "How much did I spend on Utilities?",
            "How much did I spend on Dining?"
        ]
        for question in questions:
            print(f"Q: {question}")
            try:
                response = user_rag_chain.invoke(question)
                print(f"A: {response}\n")
            except ReadTimeout as e:
                print(f"❌ ReadTimeoutError processing question: {e}")
                print(f"Check your network connection or increase the timeout in HuggingFaceEndpoint.")
            except Exception as e:
                print(f"❌ Error processing question: {e}")
                print(f"Check if LLM is accessible with your API token.")
                print(f"Using fallback LLM: {FALLBACK_LLM_REPO_ID}.")
    else:
        print("❌ Failed to create RAG chain. Cannot process questions.")
