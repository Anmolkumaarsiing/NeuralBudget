from apps.common_utils.firebase_service import get_user_categories, add_transaction, get_transactions

def get_categories(user_id):
    return get_user_categories(user_id)

def set_budget(user_id, category, budget):
    add_transaction(user_id, {"category": category, "budget": budget}, "budgets")

def get_budgets(user_id):
    return get_transactions(user_id, "budgets")
