from django.db import models
from authentication.models import CustomUser


class Domain(models.Model):
    user = models.OneToOneField(CustomUser,on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    is_valid = models.BooleanField(default=False)

class SentEmail(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    recipient = models.EmailField()
    recipient_name = models.TextField()
    subject = models.CharField(max_length=255)
    html_body = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

class ReceivedEmail(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    sender = models.EmailField()
    sender_name = models.TextField()
    subject = models.CharField(max_length=255)
    content = models.TextField()
    received_at = models.DateTimeField(auto_now_add=True)


