import os
import sys
import warnings
import logging
from datetime import datetime
from dotenv import load_dotenv
from requests.exceptions import ReadTimeout
from google.api_core.exceptions import GoogleAPIError
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

# --- Firebase Service ---
from apps.common_utils.firebase_service import get_transactions

# --- CONFIGURATION ---
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('chatbot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
LLM_REPO_ID = "mistralai/Mixtral-8x7B-Instruct-v0.1"
FALLBACK_LLM_REPO_ID = "HuggingFaceH4/zephyr-7b-beta"
VECTOR_COLLECTION_NAME = "user_transaction_vectors"
CHROMA_PERSIST_DIR = "./chroma_db"

_initialized_services = {
    "embedding_service": None,
    "llm": None,
    "vector_store": None
}

def _initialize_ai_services():
    """Initialize AI services with proper error handling and logging"""
    global _initialized_services

    if all(_initialized_services.values()):
        print("AI services already initialized. Reusing existing instances.")
        return _initialized_services["embedding_service"], _initialized_services["llm"], _initialized_services["vector_store"]

    print("Initializing AI services...")
    start_time = datetime.now()

    # Initialize Embedding Service
    try:
        embedding_service = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
        _initialized_services["embedding_service"] = embedding_service
        print(f"✅ Embedding service initialized: {EMBEDDING_MODEL_NAME}")
    except Exception as e:
        logger.error(f"❌ Failed to initialize embedding service: {e}")
        raise RuntimeError(f"Embedding service initialization failed: {e}")

    # Initialize LLM
    try:
        llm_endpoint = HuggingFaceEndpoint(
            repo_id=LLM_REPO_ID,
            huggingfacehub_api_token=os.getenv("HUGGINGFACEHUB_API_TOKEN"),
            max_new_tokens=512,
            temperature=0.1,
            timeout=60,
        )
        llm = ChatHuggingFace(llm=llm_endpoint)
        _initialized_services["llm"] = llm
        print(f"✅ Primary LLM initialized: {LLM_REPO_ID}")
    except Exception as e:
        logger.warning(f"⚠️ Primary LLM failed: {e}. Trying fallback...")
        try:
            llm_endpoint = HuggingFaceEndpoint(
                repo_id=FALLBACK_LLM_REPO_ID,
                huggingfacehub_api_token=os.getenv("HUGGINGFACEHUB_API_TOKEN"),
                max_new_tokens=512,
                temperature=0.1,
                timeout=60,
            )
            llm = ChatHuggingFace(llm=llm_endpoint)
            _initialized_services["llm"] = llm
            print(f"✅ Fallback LLM initialized: {FALLBACK_LLM_REPO_ID}")
        except Exception as fallback_e:
            logger.error(f"❌ Both primary and fallback LLM failed: {fallback_e}")
            raise RuntimeError(f"LLM initialization failed: {fallback_e}")

    # Initialize Vector Store
    try:
        vector_store = Chroma(
            collection_name=VECTOR_COLLECTION_NAME,
            embedding_function=embedding_service,
            persist_directory=CHROMA_PERSIST_DIR
        )
        _initialized_services["vector_store"] = vector_store
        print(f"✅ Vector store initialized: {VECTOR_COLLECTION_NAME}")
    except Exception as e:
        logger.error(f"❌ Vector store initialization failed: {e}")
        raise RuntimeError(f"Vector store initialization failed: {e}")

    init_time = (datetime.now() - start_time).total_seconds()
    print(f"✅ All AI services initialized successfully in {init_time:.2f}s")

    return embedding_service, llm, vector_store

def clear_user_data_from_vector_store(user_id: str, vector_store):
    """Clear existing user data to prevent duplicates"""
    try:
        # Use the correct Chroma filter syntax with $eq operator
        existing_docs = vector_store.get(where={"user_id": {"$eq": user_id}})
        if existing_docs and existing_docs.get('ids'):
            vector_store.delete(ids=existing_docs['ids'])
            print(f"Cleared {len(existing_docs['ids'])} existing documents for user {user_id}")
    except Exception as e:
        logger.warning(f"Could not clear existing data for user {user_id}: {e}")

def index_user_transactions(user_id: str, embedding_service, vector_store, force_reindex=False):
    """Index user transactions and income data with comprehensive logging and no duplicates"""
    print(f"Starting indexing for user: {user_id} (force_reindex={force_reindex})")
    start_time = datetime.now()

    try:
        # Clear existing user data to prevent duplicates
        clear_user_data_from_vector_store(user_id, vector_store)

        # Fetch transactions (expenses) and incomes for this user
        transactions_data = get_transactions(user_id, "expenses", limit=1000)
        income_data = get_transactions(user_id, "incomes", limit=1000)
        print(f"Retrieved {len(transactions_data)} expense(s) and {len(income_data)} income(s)")

        all_docs = []

        # Process expenses
        for tx in transactions_data:
            tx_id = tx.get('id') or tx.get('source_transaction_id') or f'tx_{datetime.now().timestamp()}'
            all_docs.append({'data': tx, 'collection': 'expenses', 'doc_id': tx_id})

        # Process incomes  
        for inc in income_data:
            inc_id = inc.get('id') or inc.get('source_transaction_id') or f'inc_{datetime.now().timestamp()}'
            all_docs.append({'data': inc, 'collection': 'incomes', 'doc_id': inc_id})

        if not all_docs:
            print(f"No documents found for user: {user_id}")
            return False

        documents_to_index = []
        processed_count = 0
        skipped_count = 0

        print(f"Processing {len(all_docs)} document(s)...")

        for item in all_docs:
            raw = item['data']
            doc_id = item['doc_id']
            collection_type = item['collection']
            
            try:
                if collection_type == 'expenses':
                    required_fields = ["name", "category", "amount", "date", "status"]
                    missing = []
                    for field in required_fields:
                        if field not in raw or raw[field] in [None, "", 0]:
                            missing.append(field)
                    
                    if missing:
                        logger.warning(f"Expense document {doc_id} missing fields: {missing}, skipping")
                        skipped_count += 1
                        continue

                    compact_content = (
                        f"Expense: {raw['name']} "
                        f"Amount: ₹{raw['amount']} "
                        f"Category: {raw['category']} "
                        f"Date: {raw['date']} "
                        f"Status: {raw['status']} "
                        f"Type: expense"
                    )
                    
                    metadata = {
                        "user_id": user_id,
                        "source_document_id": doc_id,
                        "type": "expense",
                        "amount": float(raw['amount']),
                        "date": str(raw['date']),
                        "category": raw['category'],
                        "name": raw['name'],
                        "status": raw['status']
                    }

                else:  # incomes
                    required_fields = ["source", "amount", "date", "status"]
                    missing = []
                    for field in required_fields:
                        if field not in raw or raw[field] in [None, "", 0]:
                            missing.append(field)
                    
                    if missing:
                        logger.warning(f"Income document {doc_id} missing fields: {missing}, skipping")
                        skipped_count += 1
                        continue

                    compact_content = (
                        f"Income Source: {raw['source']} "
                        f"Amount: ₹{raw['amount']} "
                        f"Date: {raw['date']} "
                        f"Status: {raw['status']} "
                        f"Type: income"
                    )
                    
                    metadata = {
                        "user_id": user_id,
                        "source_document_id": doc_id,
                        "type": "income",
                        "amount": float(raw['amount']),
                        "date": str(raw['date']),
                        "source": raw['source'],
                        "status": raw['status']
                    }

                doc_to_add = Document(
                    page_content=compact_content,
                    metadata=metadata
                )
                documents_to_index.append(doc_to_add)
                processed_count += 1

            except Exception as e:
                logger.error(f"Error processing document {doc_id} from {collection_type}: {e}")
                skipped_count += 1
                continue

        if not documents_to_index:
            logger.warning(f"No valid documents to index for user: {user_id}")
            return False

        # Filter complex metadata and add to vector store
        filtered_documents = filter_complex_metadata(documents_to_index)
        print(f"Adding {len(filtered_documents)} documents to vector store")
        
        vector_store.add_documents(documents=filtered_documents)
        
        # Persist if supported
        try:
            if hasattr(vector_store, "persist"):
                vector_store.persist()
        except Exception as persist_e:
            logger.warning(f"Vector store persist failed: {persist_e}")

        index_time = (datetime.now() - start_time).total_seconds()
        print(f"✅ Indexing complete for user: {user_id} "
                    f"(Processed: {processed_count}, Skipped: {skipped_count}, Time: {index_time:.2f}s)")
        
        return True

    except Exception as e:
        logger.error(f"❌ Indexing failed for user {user_id}: {e}")
        return False

def create_rag_chain_for_user(user_id: str, vector_store, llm):
    """Create RAG chain with very strict prompting to prevent hallucination."""
    try:
        retriever = vector_store.as_retriever(
            search_kwargs={
                "k": 20,  # Get more documents
                "filter": {"user_id": user_id}
            }
        )

        # Ultra-strict prompt template to prevent hallucination
        template = """You are Neural Budget, a financial assistant. 

Context Data:
{context}

Question: {question}

IMPORTANT INSTRUCTIONS:
- Look at ALL the context data above
- For income questions: Find entries that contain "Type: income" and give the EXACT amounts shown
- For expense questions: Find entries that contain "Type: expense" and give EXACT amounts/categories
- When asked about "this month" or current month, include ALL records from August 2025
- Always use the actual amounts from the context, never estimate
- Keep answers concise and to the point


Example: If context shows "Income Source: Pocket Money Amount: ₹1000.0 Date: 2025-08-27 Status: Completed Type: income"
Then for income questions, answer: "You have ₹1000 income from Pocket Money this month."

Answer based on the context:"""


        prompt = ChatPromptTemplate.from_template(template)

        rag_chain = (
            {"context": retriever, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )

        print(f"RAG chain created successfully for user: {user_id}")
        return rag_chain
    except Exception as e:
        logger.error(f"Failed to create RAG chain for user {user_id}: {e}")
        return None

def get_chatbot_response(user_id: str, message: str) -> str:
    """
    Main function to get chatbot response with improved accuracy.
    """
    print(f"Processing query for user {user_id}: '{message[:50]}...' ")
    start_time = datetime.now()

    try:
        # Initialize AI services
        embedding_service, llm, vector_store = _initialize_ai_services()
        test_retriever = vector_store.as_retriever(
            search_kwargs={"k": 10, "filter": {"user_id": user_id}}
        )
        retrieved_docs = test_retriever.get_relevant_documents(message)
        
        print(f"[DEBUG] Retrieved {len(retrieved_docs)} documents for query: {message}")
        # Index user transactions (force fresh data)
        indexing_success = index_user_transactions(user_id, embedding_service, vector_store, force_reindex=True)
        if not indexing_success:
            logger.warning(f"Indexing failed for user {user_id}")
            return "Sorry, I couldn't load your financial data. Please try again."

        # Create RAG chain
        user_rag_chain = create_rag_chain_for_user(user_id=user_id, vector_store=vector_store, llm=llm)
        if not user_rag_chain:
            return "Failed to initialize the financial assistant. Please try again later."

        # Get response from chain
        response = user_rag_chain.invoke(message)

        if isinstance(response, str):
            response = response.strip()

        response_time = (datetime.now() - start_time).total_seconds()
        print(f"✅ Response generated for user {user_id} in {response_time:.2f}s")

        return response

    except ReadTimeout as e:
        error_msg = "I'm experiencing a timeout. Please try again in a moment."
        logger.error(f"ReadTimeout for user {user_id}: {e}")
        return error_msg

    except Exception as e:
        error_msg = f"I encountered an error processing your request. Please try again later."
        logger.error(f"Unexpected error for user {user_id}: {e}")
        return error_msg

# --- STANDALONE TESTING ---
if __name__ == '__main__':
    # Use your actual test user ID
    test_user_id = "PZWaO69zDjfivyIwPX4wi1KK6Pp2"

    print("=== Starting Chatbot Service Test ===")

    try:
        print("\n" + "="*50)
        print("TESTING INCOME QUERIES")
        print("="*50)
        
        # Test various income questions
        test_queries = [
            "How much income do I have this month?",
            "What's my total income?", 
            "How much pocket money did I receive?",
            "Show me my income sources",
            "What income do I have?"
        ]
        
        for query in test_queries:
            print(f"\n🔸 Q: {query}")
            response = get_chatbot_response(test_user_id, query)
            print(f"🔹 A: {response}")

    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        print(f"❌ Test failed: {e}")

    print("=== Test Complete ===")
