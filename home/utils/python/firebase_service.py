from home.firebase_config import db

def get_categories():
    """Fetch categories from Firestore."""
    categories_ref = db.collection("categories")
    docs = categories_ref.stream()
    return [doc.to_dict()["name"] for doc in docs]

def add_transaction(user_id, transaction_data):
    """Add a transaction to Firestore."""
    transactions_ref = db.collection("transactions")
    transactions_ref.add({
        "userId": user_id,
        **transaction_data
    })

def get_transactions(user_id,limit=10,collection='transactions'):
    try:
        transactions_ref = db.collection(collection)
    except Exception as e:
        print(e)
        return []
    
    query = transactions_ref.where("userId", "==", user_id).limit(limit).get()
    transactions = []
    for doc in query:
        transaction = doc.to_dict()
        transaction["id"] = doc.id
        transactions.append(transaction)
    return transactions

def add_category(category_name):
    """Add a category to Firestore."""
    categories_ref = db.collection("categories")
    categories_ref.add({
        "name": category_name
    })
