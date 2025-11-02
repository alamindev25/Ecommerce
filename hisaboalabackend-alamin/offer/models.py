from django.db import models
from subscription_plans.models import SubscriptionPlans

class PromoCode(models.Model):
    DISCOUNT_TYPE_CHOICES = (
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount')
    )
    plan_id = models.ForeignKey(SubscriptionPlans, on_delete=models.CASCADE, related_name='promo_codes')
    promo_code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPE_CHOICES)
    discount_value = models.IntegerField(help_text="Discount value, percentage or fixed amount")
    is_active = models.BooleanField(default=True)
    max_uses = models.IntegerField(default=1)
    used_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.promo_code} - {self.plan_id.plan_name} - {self.created_at.strftime("%Y-%m-%d")}'
    class Meta:
        verbose_name = "Promo Code"
        verbose_name_plural = "Promo Codes"
