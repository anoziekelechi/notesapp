from django.urls import path

from home.views import UserNotes, NoteDetails

urlpatterns = [
    path('notes/', UserNotes.as_view(),name="notes"),
    path('detail/<int:pk>/', NoteDetails.as_view(),name="detail"),
]