from django.urls import path
from .views import *

urlpatterns = [
    path('generate-email-template/', generate_email_template, name='generate_email_template'),
    path('view-template/', view_template, name='view_template'),
]
