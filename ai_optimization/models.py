from django.db import models

class EmailTemplate(models.Model):
    subject = models.CharField(max_length=255)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject

class Campaign(models.Model):
    name = models.CharField(max_length=255)
    no_of_target_leads = models.PositiveBigIntegerField()
    products = models.TextField()
    my_brand = models.CharField(max_length=255)
    
    def __str__(self):
        return self.name

class AISentMails(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject