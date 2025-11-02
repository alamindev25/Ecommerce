from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from .serializers import OrderSerializer, OrderCreateSerializer
from .models import Order


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer

    def get_queryset(self):
        queryset = Order.objects.all()

        shop_id = self.request.query_params.get('shop_id', None)
        if shop_id is not None:
            queryset = queryset.filter(shop_id=shop_id)

        return queryset.order_by('-order_date')

    @action(detail=False, methods=['get'])
    def sales_summary(self, request):
        """
        Get sales summary by time period (today, week, month, year)
        Query parameters:
        - shop_id: Filter by specific shop (required)
        - period: 'today', 'week', 'month', 'year' (default: 'today')
        """
        shop_id = request.query_params.get('shop_id')
        period = request.query_params.get('period', 'today')

        if not shop_id:
            return Response({'error': 'shop_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Get date range based on period
        today = timezone.now().date()

        if period == 'today':
            start_date = today
            end_date = today
            period_name = "Today"
        elif period == 'week':
            start_date = today - timedelta(days=today.weekday())  # Monday of current week
            end_date = start_date + timedelta(days=6)  # Sunday of current week
            period_name = "This Week"
        elif period == 'month':
            start_date = today.replace(day=1)  # First day of current month
            if today.month == 12:
                end_date = today.replace(year=today.year+1, month=1, day=1) - timedelta(days=1)
            else:
                end_date = today.replace(month=today.month+1, day=1) - timedelta(days=1)
            period_name = "This Month"
        elif period == 'year':
            start_date = today.replace(month=1, day=1)  # First day of current year
            end_date = today.replace(month=12, day=31)  # Last day of current year
            period_name = "This Year"
        else:
            return Response({'error': 'Invalid period. Use: today, week, month, year'},
                          status=status.HTTP_400_BAD_REQUEST)

        # Filter orders by shop and date range
        orders = Order.objects.filter(
            shop_id=shop_id,
            order_date__date__gte=start_date,
            order_date__date__lte=end_date
        )

        # Calculate summary statistics
        summary = orders.aggregate(
            total_sales=Sum('final_total'),
            total_orders=Count('id'),
            total_subtotal=Sum('subtotal'),
            total_discount=Sum('discount_total'),
            total_due=Sum('due_amount')
        )

        # Get payment method breakdown
        payment_breakdown = orders.values('payment_method').annotate(
            count=Count('id'),
            total_amount=Sum('final_total')
        ).order_by('payment_method')

        return Response({
            'period': period_name,
            'date_range': {
                'start_date': start_date,
                'end_date': end_date
            },
            'summary': {
                'total_orders': summary['total_orders'] or 0,
                'total_sales': float(summary['total_sales'] or 0),
                'total_subtotal': float(summary['total_subtotal'] or 0),
                'total_discount': float(summary['total_discount'] or 0),
                'total_due': float(summary['total_due'] or 0),
            },
        })