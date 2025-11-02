from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from cost_book.views import CostCategoryListView, CostHistoryViewset
from user.views import *
from product.views import *
from shop.views import *
from transaction.views import *
from knox import views as knox_views
from global_reports.views import GlobalReportViewSet
from personal_notes.views import PersonalNotesViewSet
from lose_history.views import LoseHistoryViewset, LoseCategoryListView
from sale.views import OrderViewSet
from subscription_plans.views import CustomerSubscriptionsViewSet, SubscriptionPlansViewSet, SubscriptionOrderViewSet
from offer.views import PromoCodeViewSet

app_name = 'hisabwala'

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'subcategories', SubCategoryViewSet, basename='subcategory')
router.register(r'units', UnitViewSet, basename='unit')
router.register(r'shops', ShopViewSet, basename='shop')
router.register(r'shop-products', ShopProductViewSet, basename='shop-product')
router.register(r'product-prices', ProductPriceViewSet, basename='product-price')
router.register(r'transactions', TransactionViewSet, basename='transaction')


router.register(r'global-reports', GlobalReportViewSet, basename='global-reports')
router.register(r'personal-notes', PersonalNotesViewSet, basename= 'personal-notes')
router.register(r'subscription-plans', SubscriptionPlansViewSet, basename='subscription-plans')
router.register(r'promo-codes', PromoCodeViewSet, basename='promo-codes')
router.register(r'user-subscriptions', CustomerSubscriptionsViewSet, basename='user-subscriptions')
router.register(r'subscription-orders', SubscriptionOrderViewSet, basename='subscription-orders')
# Cost Book
router.register(r'cost-history', CostHistoryViewset, basename='cost-history')
# Lose History
router.register(r'lose-history', LoseHistoryViewset, basename='lose-history')
# Sale/Order Management
router.register(r'orders', OrderViewSet, basename='orders')

urlpatterns = [
    path('', include(router.urls)),

    # Authentication Section
    path('validate_phone/', ValidatePhoneSentOTP.as_view()),
    path('validate_otp/', ValidateOTP.as_view()),
    path('register/', Register.as_view()),
    path('login/', LoginAPI.as_view()),
    path('logout/', knox_views.LogoutView.as_view()),

    # Custom API endpoints for relationships
    path('categories/<int:category_id>/subcategories/', CategorySubCategoriesAPIView.as_view(), name='category-subcategories'),
    path('categories/<int:category_id>/units/', CategoryUnitsAPIView.as_view(), name='category-units'),
    path('cost-categories/', CostCategoryListView.as_view(), name='cost-categories-list'),
    path('lose-categories/', LoseCategoryListView.as_view(), name='lose-categories-list'),
]