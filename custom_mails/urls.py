from django.urls import path
from .views import *

urlpatterns = [
    path('v1/send', send_mail, name='send_mail'),
    path('v1/receive', receive_mail, name='receive_mail'),
    path('reply_email/<int:email_id>/', reply_email, name='reply_email'),
    path('reply_sent_email/<int:email_id>/', reply_sent_email, name='reply_sent_email'),
    path('v1/add_domain', add_domain, name='add_domain'),
    path('v1/verify_domain', verify_domain, name='verify_domain'),
    path('v1/sent_emails', get_sent_emails, name='get_sent_emails'),
    path('v1/received_emails', get_received_emails, name='get_received_emails'),
    path('read_email/<int:email_id>/', read_email, name='read_email'),
    path('read_sent_mail/<int:email_id>/', read_sent_email, name='read_sent_mail'),
    path('v1/configure-receive-endpoint', configure_receive_endpoint_view, name='configure_receive_endpoint'),
]