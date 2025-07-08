from home.utils.python.firebase_service import get_transactions
from home.utils.python.ml_util import preprocess_data, predict_future_income, categorize_spending, generate_visualizations

def generate_visualizations_data(user_id):
    incomes = get_transactions(user_id, 'transaction', 100)
    df = preprocess_data(incomes)
    future_income = predict_future_income(df)
    df = categorize_spending(df)
    visualizations = generate_visualizations(df, future_income)
    return visualizations
