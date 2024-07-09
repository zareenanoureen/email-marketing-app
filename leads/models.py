from django.db import models

class Lead(models.Model):
    name = models.CharField(max_length=200)
    contact_no = models.TextField()
    industry = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    address = models. TextField()
    notes = models.TextField(blank=True, null=True)


class ShopifyStoresDetails(models.Model):
    link = models.URLField()
    brand_summary = models.TextField()
    traffic_analysis = models.TextField()
    seo_score = models.TextField()
    tech_stacks = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)