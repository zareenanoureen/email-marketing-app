from django.db import models
from authentication.models import CustomUser

class Lead(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    contact_no = models.TextField()
    industry = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    notes = models.TextField(blank=True, null=True)


class ShopifyStoresDetails(models.Model):
    lead = models.ForeignKey(Lead,on_delete=models.CASCADE)
    link = models.URLField()
    brand_summary = models.TextField()
    traffic_analysis = models.TextField()
    seo_score = models.TextField()
    tech_stacks = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)