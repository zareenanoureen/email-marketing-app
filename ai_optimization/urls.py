from django.urls import path
from .views import *

urlpatterns = [
    path('generate-email-template/', generate_email_template, name='generate_email_template'),
    path('view-template/', view_template, name='view_template'),
    path('create-campaign/', create_campaign, name='create_campaign'),
    path('campaigns/', campaign_list, name='campaign_list'),
    path('campaigns/<int:campaign_id>/', campaign_detail, name='campaign_detail'),
    path('sent_mail/<int:mail_id>/', sent_mail_detail, name='sent_mail_detail'),
    path('respond_email/<int:mail_id>/', respond_email, name='respond_email'),
]
