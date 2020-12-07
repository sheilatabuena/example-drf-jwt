""" Database models for message bus. """

from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Message(models.Model):
    """ model for a message """

    id = models.AutoField(primary_key=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False)
    message = models.CharField(max_length=1000, null=False, default='', blank=False)


    @classmethod
    def get_field_names(cls):
        """ return field names only array """
        return [field.name for field in Message._meta.fields]

    class Meta:
        managed = True
