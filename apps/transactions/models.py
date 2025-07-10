from django.db import models

class Transaction(models.Model):
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    status = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name} - {self.category} - {self.amount}"


from django.db import models

class Income(models.Model):
    STATUS_CHOICES = [
        ("Received", "Received"),
        ("Pending", "Pending"),
        ("Completed", "Completed"),
        ("Failed", "Failed"),
        ("Cancelled", "Cancelled"),
        ("Partially Paid", "Partially Paid"),
        ("Due", "Due"),
        ("Processing", "Processing"),
        ("On Hold", "On Hold"),
        ("Refunded", "Refunded"),
        ("Overdue", "Overdue"),
    ]
    
    source = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)

    def __str__(self):
        return f"{self.source} - {self.amount} ({self.status})"
