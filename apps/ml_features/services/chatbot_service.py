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

# Setup logging
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

# --- INIT SERVICES ---
_initialized_services = {
    "embedding_service": None,
    "llm": None,
    "vector_store": None
}

def _initialize_ai_services():
    """Initialize AI services with proper error handling and logging"""
    global _initialized_services
    
    if all(_initialized_services.values()):
        logger.info("AI services already initialized. Reusing existing instances.")
        return _initialized_services["embedding_service"], _initialized_services["llm"], _initialized_services["vector_store"]

    logger.info("Initializing AI services...")
    start_time = datetime.now()

    # Initialize Embedding Service
    try:
        embedding_service = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
        _initialized_services["embedding_service"] = embedding_service
        logger.info(f"✅ Embedding service initialized: {EMBEDDING_MODEL_NAME}")
    except Exception as e:
        logger.error(f"❌ Failed to initialize embedding service: {e}")
        raise RuntimeError(f"Embedding service initialization failed: {e}")

    # Initialize LLM
    try:
        llm_endpoint = HuggingFaceEndpoint(
            repo_id=LLM_REPO_ID,
            huggingfacehub_api_token=os.getenv("HUGGINGFACEHUB_API_TOKEN"),
            max_new_tokens=256,
            temperature=0.1,
            timeout=60,
        )
        llm = ChatHuggingFace(llm=llm_endpoint)
        _initialized_services["llm"] = llm
        logger.info(f"✅ Primary LLM initialized: {LLM_REPO_ID}")
    except Exception as e:
        logger.warning(f"⚠️ Primary LLM failed: {e}. Trying fallback...")
        try:
            llm_endpoint = HuggingFaceEndpoint(
                repo_id=FALLBACK_LLM_REPO_ID,
                huggingfacehub_api_token=os.getenv("HUGGINGFACEHUB_API_TOKEN"),
                max_new_tokens=256,
                temperature=0.1,
                timeout=60,
            )
            llm = ChatHuggingFace(llm=llm_endpoint)
            _initialized_services["llm"] = llm
            logger.info(f"✅ Fallback LLM initialized: {FALLBACK_LLM_REPO_ID}")
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
        logger.info(f"✅ Vector store initialized: {VECTOR_COLLECTION_NAME}")
    except Exception as e:
        logger.error(f"❌ Vector store initialization failed: {e}")
        raise RuntimeError(f"Vector store initialization failed: {e}")

    init_time = (datetime.now() - start_time).total_seconds()
    logger.info(f"✅ All AI services initialized successfully in {init_time:.2f}s")
    
    return embedding_service, llm, vector_store

def index_user_transactions(user_id: str, embedding_service, vector_store, force_reindex=False):
    """Index user transactions and income data with comprehensive logging"""
    logger.info(f"Starting indexing for user: {user_id} (force_reindex={force_reindex})")
    start_time = datetime.now()
    
    try:
        # Fetch transactions and income
        transactions_data = get_transactions(user_id, "expenses", limit=1000)
        income_data = get_transactions(user_id, "incomes", limit=1000)
        
        logger.info(f"Retrieved {len(transactions_data)} transactions and {len(income_data)} income records")

        all_docs = []
        
        # Process transactions
        for tx in transactions_data:
            if 'id' not in tx:
                tx['id'] = tx.get('source_transaction_id', f'tx_{datetime.now().timestamp()}')
            all_docs.append({'data': tx, 'collection': 'transactions'})

        # Process income
        for inc in income_data:
            if 'id' not in inc:
                inc['id'] = inc.get('source_transaction_id', f'inc_{datetime.now().timestamp()}')
            all_docs.append({'data': inc, 'collection': 'income'})

        if not all_docs:
            logger.info(f"No documents found for user: {user_id}")
            return False

        documents_to_index = []
        processed_count = 0
        skipped_count = 0

        logger.info(f"Processing {len(all_docs)} document(s)...")
        
        for item in all_docs:
            raw = item['data']
            collection_type = item['collection']
            doc_id = raw.get('id')

            try:
                tx_payload = raw.get("transaction") if isinstance(raw.get("transaction"), dict) else raw
                
                # Validate required fields
                if collection_type == 'transactions':
                    required_fields = ["amount", "category", "date"]
                    category_raw = tx_payload.get("category", "uncategorized")
                    category_norm = category_raw.strip().lower()
                    transaction_name = tx_payload.get("name", "").strip()
                    
                    compact_content = (
                        f"Transaction: {transaction_name or 'unnamed'} "
                        f"Amount: ₹{tx_payload.get('amount', 0)} "
                        f"Category: {category_norm} "
                        f"Date: {tx_payload.get('date', 'unknown')} "
                        f"Type: expense"
                    )
                    
                    metadata = {
                        "user_id": user_id,
                        "source_document_id": doc_id,
                        "type": "expense",
                        "amount": float(tx_payload.get('amount', 0)),
                        "date": tx_payload.get('date'),
                        "category": category_norm,
                        "source": None,
                        "name": transaction_name
                    }
                else:  # income
                    required_fields = ["amount", "source", "date"]
                    source_raw = tx_payload.get("source", "unknown")
                    source_norm = source_raw.strip().lower()
                    transaction_name = tx_payload.get("name", "").strip()
                    
                    compact_content = (
                        f"Income: {transaction_name or 'unnamed'} "
                        f"Amount: ₹{tx_payload.get('amount', 0)} "
                        f"Source: {source_norm} "
                        f"Date: {tx_payload.get('date', 'unknown')} "
                        f"Type: income"
                    )
                    
                    metadata = {
                        "user_id": user_id,
                        "source_document_id": doc_id,
                        "type": "income",
                        "amount": float(tx_payload.get('amount', 0)),
                        "date": tx_payload.get('date'),
                        "category": None,
                        "source": source_norm,
                        "name": transaction_name
                    }

                # Check for missing required fields
                missing = [f for f in required_fields if f not in tx_payload or not tx_payload[f]]
                if missing:
                    logger.warning(f"Document {doc_id} missing fields: {missing}, skipping")
                    skipped_count += 1
                    continue

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
        logger.info(f"Adding {len(filtered_documents)} documents to vector store")
        
        vector_store.add_documents(documents=filtered_documents)
        
        # Persist if supported
        try:
            if hasattr(vector_store, "persist"):
                vector_store.persist()
        except Exception as persist_e:
            logger.warning(f"Vector store persist failed: {persist_e}")

        index_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"✅ Indexing complete for user: {user_id} "
                   f"(Processed: {processed_count}, Skipped: {skipped_count}, Time: {index_time:.2f}s)")
        return True

    except Exception as e:
        logger.error(f"❌ Indexing failed for user {user_id}: {e}")
        return False

def create_rag_chain_for_user(user_id: str, vector_store, llm):
    """Create RAG chain with concise prompting"""
    try:
        retriever = vector_store.as_retriever(
            search_kwargs={
                "k": 8,
                "filter": {"user_id": user_id}
            }
        )

        # Concise prompt template
        template = """You are "Neural Budget", a helpful AI financial assistant.

RESPONSE RULES:
1. For greetings ONLY (Hi, Hello, Hey, etc.): Respond with "Hello! How can I help with your finances today?" - DO NOT include any transaction data.
2. For spending questions: Give the amount in ₹ format + one short tip (max 25 words).
3. If no data found: Say "No [category] expenses found in your records."
4. Keep responses under 3 sentences total.
5. Always respond in a friendly and professional tone.
6. If the user is argueing or rude, stay calm and polite.
7. If you don't know the answer, say "I'm not sure about that" and offer a financial advice.

EXAMPLES:
- "You've spent ₹1,500 on laundry. Consider bulk washing to save money."
- "No dining expenses found in your records."
- "Hello! How can I help with your finances today?"

CONTEXT: {context}
QUESTION: {question}

RESPONSE:"""

        prompt = ChatPromptTemplate.from_template(template)

        rag_chain = (
            {"context": retriever, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )
        
        logger.info(f"RAG chain created successfully for user: {user_id}")
        return rag_chain
        
    except Exception as e:
        logger.error(f"Failed to create RAG chain for user {user_id}: {e}")
        return None

def get_chatbot_response(user_id: str, message: str) -> str:
    """
    Main function to get chatbot response with comprehensive logging
    """
    logger.info(f"Processing query for user {user_id}: '{message[:50]}...' ")
    start_time = datetime.now()
    
    try:
        # Initialize AI services
        embedding_service, llm, vector_store = _initialize_ai_services()
        
        # Index user transactions
        indexing_success = index_user_transactions(user_id, embedding_service, vector_store)
        if not indexing_success:
            logger.warning(f"Indexing failed for user {user_id}, proceeding with existing data")

        # Create RAG chain
        user_rag_chain = create_rag_chain_for_user(user_id=user_id, vector_store=vector_store, llm=llm)
        
        if not user_rag_chain:
            error_msg = "Failed to initialize the financial assistant. Please try again later."
            logger.error(f"RAG chain creation failed for user {user_id}")
            return error_msg

        # Get response
        response = user_rag_chain.invoke(message)
        
        # Clean up response
        if isinstance(response, str):
            response = response.strip()
        
        response_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"✅ Response generated for user {user_id} in {response_time:.2f}s")
        
        return response

    except ReadTimeout as e:
        error_msg = "I'm experiencing a timeout. Please check your internet connection or try again in a moment."
        logger.error(f"ReadTimeout for user {user_id}: {e}")
        return error_msg
        
    except Exception as e:
        error_msg = f"I encountered an error while processing your request. Please try again later."
        logger.error(f"Unexpected error for user {user_id}: {e}")
        return error_msg

# --- STANDALONE TESTING ---
if __name__ == '__main__':
    # Test user ID
    test_user_id = "nQUxkJ1HkZZIPVboQytBLpbC4za2"
    
    logger.info("=== Starting Chatbot Service Test ===")
    
    try:
        # Initialize services
        embedding_service, llm, vector_store = _initialize_ai_services()
        
        # Index transactions
        index_success = index_user_transactions(test_user_id, embedding_service, vector_store, force_reindex=True)
        
        if index_success:
            # Create RAG chain
            user_rag_chain = create_rag_chain_for_user(user_id=test_user_id, vector_store=vector_store, llm=llm)
            
            if user_rag_chain:
                logger.info("=== Testing Sample Queries ===")
                
                test_queries = [
                    "Hello! How are you?",
                    "How much did I spend on groceries this month?",
                    "What's my total spending on transport?",
                    "Show me my entertainment expenses",
                    "How much income did I receive from salary?",
                    "What's my biggest expense category?"
                ]
                
                for query in test_queries:
                    logger.info(f"Testing query: {query}")
                    try:
                        response = user_rag_chain.invoke(query)
                        logger.info(f"Response: {response[:100]}...")
                        print(f"\n🔸 Q: {query}")
                        print(f"🔹 A: {response}\n")
                    except Exception as e:
                        logger.error(f"Query failed: {e}")
                        print(f"❌ Query failed: {e}")
            else:
                logger.error("Failed to create RAG chain")
        else:
            logger.error("Failed to index transactions")
            
    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        
    logger.info("=== Test Complete ===")
