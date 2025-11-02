from .models import *
from .serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from knox.auth import TokenAuthentication as KnoxTokenAuthentication
from datetime import datetime, timedelta
import calendar

class SubscriptionPlansViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SubscriptionPlansSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        return SubscriptionPlans.objects.filter(is_active=True)
    

class CustomerSubscriptionsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CustomerSubscriptionsSerializer
    authentication_classes = [KnoxTokenAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return CustomerSubscriptions.objects.filter(user_id=self.request.user)


class SubscriptionOrderViewSet(viewsets.ModelViewSet):
    serializer_class = SubscriptionOrderSerializer
    authentication_classes = [KnoxTokenAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return SubscriptionOrder.objects.filter(user_id=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user_id=self.request.user)
    
    def perform_update(self, serializer):
        instance = serializer.save()
        
        # If payment status is changed to 'paid', complete the order and create subscription
        if instance.payment_status == 'paid' and instance.order_status == 'pending':
            # Update order status to completed
            instance.order_status = 'completed'
            instance.save()
            
            # Create CustomerSubscription
            plan = instance.subscription_plan
            start_date = datetime.now().date()
            
            # Calculate end date by adding months
            year = start_date.year
            month = start_date.month + plan.duration
            if month > 12:
                year += (month - 1) // 12
                month = (month - 1) % 12 + 1
            
            # Get the last day of the target month
            last_day = calendar.monthrange(year, month)[1]
            day = min(start_date.day, last_day)
            end_date = start_date.replace(year=year, month=month, day=day)
            
            CustomerSubscriptions.objects.create(
                user_id=instance.user_id,
                plan_id=plan,
                amount_paid=plan.price,
                start_date=start_date,
                end_date=end_date,
                status='active',
                subscription_mode='regular'
            )
