from django.db import models

class SentEmail(models.Model):
    recipient = models.EmailField()
    recipient_name = models.TextField()
    subject = models.CharField(max_length=255)
    html_body = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

class ReceivedEmail(models.Model):
    sender = models.EmailField()
    sender_name = models.TextField()
    subject = models.CharField(max_length=255)
    content = models.TextField()
    received_at = models.DateTimeField(auto_now_add=True)
