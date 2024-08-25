from django.db import models
import re
# Create your models here.
class Lead(models.Model):
    name = models.CharField(max_length=200, null=True, blank=True)
    contact_no = models.TextField(null=True, blank=True)
    email = models.CharField(max_length=200, null=True, blank=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    phone_number = models.CharField(max_length=200, null=True, blank=True)
    industry = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    notes = models.TextField(blank=True, null=True)
    link = models.URLField()
    brand_summary = models.TextField()
    traffic_analysis = models.TextField()
    seo_score = models.TextField()
    tech_stacks = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def get_seo_scores(self):
        scores = re.findall(r'(.*)\((\d+)/10\)\s*=\s*(\d+)', self.seo_score)
        labels = [score[0].strip() for score in scores]
        data = [int(score[1]) for score in scores]
        return labels, data