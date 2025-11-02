from django.db import models

class Supplier(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=14)
    address = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.phone}"

    class Meta:
        verbose_name_plural = 'Suppliers'
        ordering = ['name']


class Customer(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=14)
    address = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.phone}"