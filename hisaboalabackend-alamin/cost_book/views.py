from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from cost_book.serializers import CostHistorySerializer, CostCategorySerializer
from cost_book.models import CostHistory, CostCategory

class CostCategoryListView(ListAPIView):
    queryset = CostCategory.objects.all()
    serializer_class = CostCategorySerializer

class CostHistoryViewset(viewsets.ModelViewSet):
    queryset = CostHistory.objects.all()
    serializer_class = CostHistorySerializer
    
    def get_queryset(self):
        queryset = CostHistory.objects.all()
        
        # Filter by shop
        shop_id = self.request.query_params.get('shop_id', None)
        if shop_id is not None:
            queryset = queryset.filter(shop_id=shop_id)
        
        # Filter by category
        category_id = self.request.query_params.get('category_id', None)
        if category_id is not None:
            queryset = queryset.filter(cost_category_id=category_id)
        
        return queryset

    @action(detail=False, methods=['get'])
    def cost_summary(self, request):
        """
        Get cost summary by time period (today, week, month, year)
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
        
        # Filter costs by shop and date range
        costs = CostHistory.objects.filter(
            shop_id=shop_id,
            date__gte=start_date,
            date__lte=end_date
        )
        
        # Calculate total cost
        total_cost = costs.aggregate(total=Sum('amount'))['total'] or 0
        
        return Response({
            'period': period_name,
            'date_range': {
                'start_date': start_date,
                'end_date': end_date
            },
            'total_cost': float(total_cost),
            'total_entries': costs.count()
        })