""" Registering only model Message """

from django.contrib import admin

from .models import Message


class MessageAdmin(admin.ModelAdmin):
    """ This class configures admin display for Message """
    search_fields = ['message']

    list_display = ('id', 'user', 'message')
    list_filter = ['user']

# Register your models here.
admin.site.register(Message, MessageAdmin)
