from django.db import models

class Transaction(models.Model):
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    status = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name} - {self.category} - {self.amount}"
