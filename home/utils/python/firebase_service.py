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

def get_transactions(user_id):
    transactions_ref = db.collection("transactions")
    query = transactions_ref.where("userId", "==", user_id).stream()
    transactions = []
    for doc in query:
        transaction = doc.to_dict()
        transaction["id"] = doc.id  # Include document ID
        transactions.append(transaction)
    return transactions

def add_category(category_name):
    """Add a category to Firestore."""
    categories_ref = db.collection("categories")
    categories_ref.add({
        "name": category_name
    })
