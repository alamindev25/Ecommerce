from django.db import models
from shop.models import Shop


class CostCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class CostHistory(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    cost_category = models.ForeignKey(CostCategory, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    date = models.DateField()

    def __str__(self):
        return f"{self.shop.name} - {self.cost_category.name} - {self.amount} on {self.date}"