from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()
from subscription_plans.models import SubscriptionPlans


class Agent(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='agents')
    agent_id = models.AutoField(primary_key=True)
    referrals_count = models.IntegerField(default=0)
    valid_referrals_count = models.IntegerField(default=0)
    current_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Agent {self.agent_id} - {self.user_id.phone}"