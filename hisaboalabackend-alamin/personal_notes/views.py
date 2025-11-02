from .models import *
from .serializers import PersonalNotesSerializer
from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from knox.auth import TokenAuthentication as KnoxTokenAuthentication

class PersonalNotesViewSet(viewsets.ModelViewSet):
    queryset = PersonalNotes.objects.all()
    serializer_class = PersonalNotesSerializer
    authentication_classes = [KnoxTokenAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PersonalNotes.objects.filter(user_id=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user_id=self.request.user)