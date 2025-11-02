from rest_framework import viewsets
from .models import PromoCode
from .serializers import PromoCodeSerializer
from django.db.models import F

class PromoCodeViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PromoCodeSerializer

    def get_queryset(self):
        return PromoCode.objects.filter(is_active=True, max_uses__gt=F('used_count'))
