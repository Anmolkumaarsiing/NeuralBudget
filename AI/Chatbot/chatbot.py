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
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFaceEndpoint, ChatHuggingFace
from langchain_chroma import Chroma

# Suppress FutureWarning for cleaner output
warnings.filterwarnings("ignore", category=FutureWarning)

# --- Project Path Setup ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

# --- Firestore Client ---
from apps.common_utils.firebase_config import db

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
def index_user_transactions(user_id: str, force_reindex=False):
    print(f"Starting indexing for user: {user_id} (force_reindex={force_reindex})...")
    try:
        queries_to_try = [
            ("userId", "=="),
            ("user_id", "==")
        ]

        docs = []
        for field_name, op in queries_to_try:
            try:
                q = db.collection("transactions").where(field_name, op, user_id)
                docs = list(q.stream())
                if docs:
                    print(f"✅ Found {len(docs)} transaction(s) using field '{field_name}'.")
                    break
                else:
                    print(f"DEBUG: No results for field '{field_name}'.")
            except Exception as e:
                print(f"DEBUG: Query with field '{field_name}' failed: {e}")

        if not docs:
            print("DEBUG: Falling back to client-side filter (scanning all transactions).")
            all_docs = list(db.collection("transactions").stream())
            for d in all_docs:
                dd = d.to_dict() or {}
                root_user_id = dd.get("userId") or dd.get("user_id") or dd.get("id")
                nested = dd.get("transaction") or {}
                nested_user_id = nested.get("userId") or nested.get("user_id")
                if root_user_id == user_id or nested_user_id == user_id:
                    docs.append(d)
            print(f"DEBUG: Matched {len(docs)} docs after client-side scanning.")

        documents_to_index = []
        doc_count = len(docs)
        if doc_count == 0:
            print(f"No new transactions to index for user: {user_id} (Found {doc_count} documents)")
            return False

        print(f"Processing {doc_count} transaction doc(s)...")
        for doc in docs:
            try:
                raw = doc.to_dict() or {}
                tx_payload = raw.get("transaction") if isinstance(raw.get("transaction"), dict) else raw
                required_fields = ["amount", "category", "date"]
                missing = [f for f in required_fields if f not in tx_payload]
                if missing:
                    print(f"❌ Doc {doc.id} missing fields: {missing}. Full doc keys: {list(raw.keys())}")
                    continue
                category_raw = tx_payload.get("category", "")
                category_norm = category_raw.strip().lower()

                compact_content = (
                    f"amount: {tx_payload['amount']}, "
                    f"category: {category_norm}, "
                    f"date: {tx_payload['date']}"
                )

                doc_to_add = Document(
                    page_content=compact_content,
                    metadata={
                        "user_id": user_id,
                        "source_transaction_id": doc.id,
                        "amount": tx_payload['amount'],
                        "category": category_norm,
                        "date": tx_payload['date']
                    }
                )
                documents_to_index.append(doc_to_add)
            except Exception as e:
                print(f"❌ Error processing transaction {doc.id}: {e}")
                continue

        if not documents_to_index:
            print(f"No valid transactions to index after filtering for user: {user_id}")
            return False

        print("Generating test embedding to verify vector config...")
        try:
            test_embedding = embedding_service.embed_query(documents_to_index[0].page_content)
            print("✅ Sample embedding generated. Length:", len(test_embedding))
        except Exception as e:
            print(f"❌ Error generating test embedding: {e}")
            return False

        print(f"Adding {len(documents_to_index)} document(s) to '{VECTOR_COLLECTION_NAME}'...")
        vector_store.add_documents(documents=documents_to_index)
        try:
            if hasattr(vector_store, "persist"):
                vector_store.persist()
        except Exception:
            pass

        print(f"✅ Indexing complete for user: {user_id}")
        return True

    except GoogleAPIError as e:
        print(f"❌ Firestore error during indexing: {e}")
        print("Check Firestore permissions and ensure the 'transactions' collection exists.")
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
        You are "Neural Budget", a financial assistant.
        Sum the 'amount' for transactions where 'category' matches the category mentioned in the question: {question} (case-insensitive, treat 'food' and 'Groceries' as equivalent).
        Answer in Indian Rupees (₹), e.g., "You spent ₹X.XX."
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
