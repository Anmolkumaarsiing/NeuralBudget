import firebase_admin
from firebase_admin import credentials, firestore
import random
from datetime import datetime, timedelta

# Initialize Firebase
cred = credentials.Certificate("firebase_key.json")  # Replace with your service account key
firebase_admin.initialize_app(cred)

# Get Firestore client
db = firestore.client()

# List of possible income sources
INCOME_SOURCES = ["Salary", "Freelancing", "Business", "Investments", "Other"]

# List of possible statuses
STATUSES = ["Received", "Pending", "Failed"]

def generate_random_date():
    """Generate a random date within the last year."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    random_date = start_date + (end_date - start_date) * random.random()
    return random_date.strftime("%Y-%m-%d")

def generate_random_amount():
    """Generate a random amount between 100 and 10000."""
    return round(random.uniform(100, 10000), 2)

def generate_random_transaction():
    """Generate a random transaction."""    
    return {
        "name": 'Stuff',
        "category": random.choice(INCOME_SOURCES),
        "amount": generate_random_amount(),
        "date": generate_random_date(),
        "status": random.choice(STATUSES),   
    }

USER_ID = "PZWaO69zDjfivyIwPX4wi1KK6Pp2"  # User ID for deletion
collection = 'transactions'
def insert_random_data(user_id, num_records=20):
    """Insert random transactions into Firestore."""
    incomes_ref = db.collection(collection)

    for i in range(num_records):
        transaction = generate_random_transaction()
        incomes_ref.add({
            "userId" : user_id,
            "transaction" : {
                **transaction
            },
            "id":user_id
        })
        print(f"Inserted transaction {i + 1}: {transaction}")

    print(f"Successfully inserted {num_records} random transactions for user {user_id}.")

def delete_user_transactions(user_id):
    """Delete all transactions for a given user ID."""
    transactions_ref = db.collection(collection)
    query = transactions_ref.where("userId", "==", user_id).stream()

    deleted_count = 0
    for doc in query:
        doc.reference.delete()
        deleted_count += 1
    print(f"Successfully deleted {deleted_count} transactions for user {user_id}.")

if __name__ == "__main__":
    # Use the predefined USER_ID for deletion
    # delete_user_transactions(USER_ID)
    insert_random_data(USER_ID, 20)