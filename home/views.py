from django.shortcuts import render

# Create your views here.
from django.utils.text import slugify
from rest_framework import generics, permissions

from home.models import Note
from home.permissions import IsOwner
from home.serializers import NoteSerializer

class UserNotes(generics.ListCreateAPIView):
    #permission_classes = (permissions.IsAuthenticated,)
    queryset = Note.objects.all()
    serializer_class=NoteSerializer
    # def get_queryset(self):
    #     user=self.request.user
    #     return Note.objects.filter(owner=user)
    #
    # def perform_create(self, serializer):
    #     slug=slugify(serializer.validated_data.get('heading'))
    #     serializer.save(owner=self.request.user,slug=slug)


class NoteDetails(generics.RetrieveAPIView):
    #permission_classes = (IsOwner,)
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
