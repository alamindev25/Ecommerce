from django.contrib import admin
from .models import *

admin.site.register(SubscriptionPlans)
admin.site.register(CustomerSubscriptions)
admin.site.register(SubscriptionOrder)