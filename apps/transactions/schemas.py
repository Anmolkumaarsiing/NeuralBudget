import datetime

class TransactionSchema:
    """Defines the structure for a transaction document."""
    def __init__(self, name: str, category: str, amount: float, date: datetime.datetime, status: str, user_id: str):
        self.name = name
        self.category = category
        self.amount = amount
        self.date = date
        self.status = status
        self.user_id = user_id

    def to_dict(self):
        """Converts the object to a dictionary for Firestore."""
        return self.__dict__

class IncomeSchema:
    """Defines the structure for an income document."""
    STATUS_CHOICES = [
        "Received", "Pending", "Completed", "Failed", "Cancelled",
        "Partially Paid", "Due", "Processing", "On Hold", "Refunded", "Overdue",
    ]

    def __init__(self, source: str, amount: float, date: datetime.datetime, status: str, user_id: str):
        if status not in self.STATUS_CHOICES:
            raise ValueError(f"Invalid status: {status}")
        self.source = source
        self.amount = amount
        self.date = date
        self.status = status
        self.user_id = user_id

    def to_dict(self):
        """Converts the object to a dictionary for Firestore."""
        return self.__dict__
