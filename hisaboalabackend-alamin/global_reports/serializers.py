from .models import *
from rest_framework import serializers

class GlobalReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = GlobalReport
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'user_id', 'status', 'response_content']
