from django.conf import settings
from django.db import models


class ChatIA(models.Model):
  user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, null=True, blank=True)
  name = models.CharField(max_length=255)
  description = models.TextField(blank=True)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  def __str__(self):
    return self.name

class Message(models.Model):
  chatia = models.ForeignKey('ChatIA', on_delete=models.CASCADE)
  content = models.TextField()
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  def __str__(self):
    return self.content