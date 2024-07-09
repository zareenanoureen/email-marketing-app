from django.urls import path
from .views import *

urlpatterns = [
    path('v1/send', send_mail, name='send_mail'),
    path('v1/receive', receive_mail, name='receive_mail'),
    path('v1/reply', reply_to_email, name='reply_to_email'),
    path('v1/add_domain', add_domain, name='add_domain'),
    path('v1/verify_domain', verify_domain, name='verify_domain'),
    path('v1/sent_emails', get_sent_emails, name='get_sent_emails'),
    path('v1/received_emails', get_received_emails, name='get_received_emails'),
]