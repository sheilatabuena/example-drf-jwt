"""message_bus URL Configuration

Get only shows the messages that the authenticated user can see
Post either creates a new message, or edits an existing one
Delete only deletes a specified message
"""
from django.urls import path
from message_bus import views

urlpatterns = [
    path('messages/<int:mid>/', views.Messages.as_view()),
    path('messages/', views.Messages.as_view())
]
