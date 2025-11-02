from .models import *
from rest_framework import serializers

class PersonalNotesSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonalNotes
        fields = '__all__'
        read_only_fields = ['user_id','created_at', 'updated_at']