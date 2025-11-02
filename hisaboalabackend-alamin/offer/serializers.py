from rest_framework import serializers
from .models import PromoCode

class PromoCodeSerializer(serializers.ModelSerializer):
    plan_name = serializers.CharField(source='plan_id.plan_name', read_only=True)
    discount_display = serializers.SerializerMethodField()

    class Meta:
        model = PromoCode
        fields = ['id', 'promo_code', 'plan_name', 'discount_display']

    def get_discount_display(self, obj):
        if obj.discount_type == 'percentage':
            return f"{obj.discount_value}%"
        else:
            return f"{obj.discount_value} TK"