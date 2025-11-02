from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()


class SubscriptionPlans(models.Model):
    plan_name = models.CharField(max_length=100)
    duration = models.IntegerField(help_text="Duration in months")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    agent_commission_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)


    def __str__(self):
        return f'{self.plan_name} - {self.price}'
    
    class Meta:
        verbose_name_plural = 'Subscription Plans'
    

class CustomerSubscriptions(models.Model):
    STATUS = (
        ('active', 'Active'),
        ('inactive', 'Inactive')
    )

    SUBSCRIPTION_MODE = (
        ('trial', 'Trial'),
        ('regular', 'Regular'),
        ('loan', 'Loan'),
        ('free', 'Free'),
    )

    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    plan_id = models.ForeignKey(SubscriptionPlans, on_delete=models.CASCADE)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS, default='active')
    subscription_mode = models.CharField(max_length=10, choices=SUBSCRIPTION_MODE, default='regular')
    referred_by = models.IntegerField(null=True, blank=True)
    discount = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user_id} - {self.plan_id.plan_name} ({self.status})'
    
    class Meta:
        verbose_name_plural = 'Customer Subscriptions'
        unique_together = ('user_id', 'plan_id', 'start_date')
        ordering = ['-created_at']


class SubscriptionOrder(models.Model):
    PAYMENT_METHOD = (
        ('bank', 'Bank'),
        ('agent', 'Agent')
    )
    PAYMENT_STATUS = (
        ('paid', 'Paid'),
        ('unpaid', 'Unpaid')
    )

    ORDER_STATUS = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    )

    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    subscription_plan = models.ForeignKey(SubscriptionPlans, on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    order_status = models.CharField(max_length=10, choices=ORDER_STATUS, default='pending')
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS, default='unpaid')
    reference_number = models.CharField(max_length=8, null=True, blank=True)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD)

    def __str__(self):
        return f'Order {self.id} - {self.user_id}'

    class Meta:
        verbose_name_plural = 'Subscription Orders'
        ordering = ['-order_date']