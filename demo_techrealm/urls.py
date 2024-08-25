from django.urls import path
from .views import *

urlpatterns = [
    path('landing/', index, name='index'),
    path('add-lead/', add_lead, name='add-lead'),
    path('', lead_iframe, name='add-lead'),
]