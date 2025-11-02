from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from knox.auth import TokenAuthentication as KnoxTokenAuthentication
from .models import GlobalReport
from .serializers import GlobalReportSerializer

class GlobalReportViewSet(viewsets.ModelViewSet):
    queryset = GlobalReport.objects.all()
    serializer_class = GlobalReportSerializer
    authentication_classes = [KnoxTokenAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return GlobalReport.objects.filter(user_id=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user_id=self.request.user)