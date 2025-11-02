from rest_framework import serializers
from .models import *

class SubscriptionPlansSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlans
        exclude = ['is_active', 'agent_commission_percentage']


class CustomerSubscriptionsSerializer(serializers.ModelSerializer):
    plan_name = serializers.CharField(source='plan_id.plan_name', read_only=True)
    plan_description = serializers.CharField(source='plan_id.description', read_only=True)
    plan_duration = serializers.IntegerField(source='plan_id.duration', read_only=True)
    
    class Meta:
        model = CustomerSubscriptions
        fields = ['id', 'plan_name', 'plan_description', 'plan_duration', 'amount_paid', 
                 'start_date', 'end_date', 'status', 'subscription_mode','discount',
                 'created_at']
        read_only_fields = ['created_at', 'updated_at', 'status', 'subscription_mode', 'discount']


class SubscriptionOrderSerializer(serializers.ModelSerializer):
    plan_name = serializers.CharField(source='subscription_plan.plan_name', read_only=True)
    plan_price = serializers.DecimalField(source='subscription_plan.price', max_digits=10, decimal_places=2, read_only=True)
    plan_duration = serializers.IntegerField(source='subscription_plan.duration', read_only=True)
    
    class Meta:
        model = SubscriptionOrder
        fields = ['id', 'subscription_plan', 'plan_name', 'plan_price', 'plan_duration', 
                 'order_date', 'order_status', 'payment_status', 'reference_number', 'payment_method']
        read_only_fields = ['plan_name', 'plan_price', 'plan_duration', 'order_date','order_status', 'payment_status', 'created_at', 'updated_at', 'user_id', 'payment_method']