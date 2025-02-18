import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64

def preprocess_data(incomes):
    """Convert Firestore income data into a Pandas DataFrame."""
    
    data = []
    for income in incomes:
        data.append({
            "source": income["source"],
            "amount": income["amount"],
            "date": pd.to_datetime(income["date"]),
            "status": income["status"],
        })
    df = pd.DataFrame(data)
    df.sort_values(by="date", inplace=True)

    return df

def predict_future_income(df):
    """Predict future income using linear regression."""
    # Feature engineering
    df["day_of_year"] = df["date"].dt.dayofyear  # Use day of year as a feature
    X = df[["day_of_year"]]
    y = df["amount"]

    # Train a linear regression model
    model = LinearRegression()
    model.fit(X, y)

    # Predict for the next 30 days
    future_days = pd.DataFrame({"day_of_year": range(1, 366)})
    future_days["predicted_amount"] = model.predict(future_days[["day_of_year"]])

    return future_days

def categorize_spending(df):
    """Categorize spending into high, medium, low using KMeans clustering."""
    kmeans = KMeans(n_clusters=3, random_state=42,n_init=10)
    df["spending_category"] = kmeans.fit_predict(df[["amount"]])
    return df

def generate_visualizations(df, future_income):
    """Generate visualizations and return them as base64-encoded images."""
    plt.switch_backend("Agg")  # Use a non-interactive backend for Matplotlib

    # Visualization 1: Income Over Time
    plt.figure(figsize=(10, 6))
    sns.lineplot(x="date", y="amount", data=df, label="Actual Income")
    plt.title("Income Over Time")
    plt.xlabel("Date")
    plt.ylabel("Amount")
    plt.xticks(rotation=45)
    plt.tight_layout()
    income_over_time = plot_to_base64(plt)
    plt.close()

    # Visualization 2: Predicted Future Income
    plt.figure(figsize=(10, 6))
    sns.lineplot(x="day_of_year", y="predicted_amount", data=future_income, label="Predicted Income")
    plt.title("Predicted Future Income")
    plt.xlabel("Day of Year")
    plt.ylabel("Predicted Amount")
    plt.tight_layout()
    predicted_income = plot_to_base64(plt)
    plt.close()

    # Visualization 3: Spending Categories
    plt.figure(figsize=(10, 6))
    sns.countplot(x="spending_category", data=df, hue="spending_category", palette="viridis", legend=False)
    plt.title("Spending Categories")
    plt.xlabel("Category")
    plt.ylabel("Count")
    plt.tight_layout()
    spending_categories = plot_to_base64(plt)
    plt.close()

    return {
        "income_over_time": income_over_time,
        "predicted_income": predicted_income,
        "spending_categories": spending_categories,
    }

def plot_to_base64(plt):
    """Convert a Matplotlib plot to a base64-encoded image."""
    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode("utf-8")