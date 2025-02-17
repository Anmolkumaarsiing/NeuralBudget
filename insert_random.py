import firebase_admin
from firebase_admin import credentials, firestore
import random
from datetime import datetime, timedelta

# Initialize Firebase
cred = credentials.Certificate("firebase_key.json")  # Replace with your service account key
firebase_admin.initialize_app(cred)

# Get Firestore client
db = firestore.client()

# User ID for whom the data will be inserted
USER_ID = "xX0DXk4FvTV2ULCyKF3kQQ6kizO2"  # Replace with the actual user ID

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
        "userId": USER_ID,
        "source": random.choice(INCOME_SOURCES),
        "amount": generate_random_amount(),
        "date": generate_random_date(),
        "status": random.choice(STATUSES),
    }

def insert_random_data(num_records=200):
    """Insert random transactions into Firestore."""
    incomes_ref = db.collection("incomes")

    for i in range(num_records):
        transaction = generate_random_transaction()
        incomes_ref.add(transaction)
        print(f"Inserted transaction {i + 1}: {transaction}")

    print(f"Successfully inserted {num_records} random transactions for user {USER_ID}.")

if __name__ == "__main__":
    insert_random_data()