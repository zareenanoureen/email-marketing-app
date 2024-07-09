from django.urls import path
from .views import *

urlpatterns = [
    path('find_shopify_stores/', find_shopify_stores, name='find-shopify'),
    path('all-leads/', all_leads, name='all-leads'),
    path('lead/add/', add_lead, name='add-lead'),
    path('lead/<int:id>/', get_or_update_lead, name='get-or-update-lead'),
    path('lead/find/', find_leads, name='find-leads'),
    path('lead/<int:id>/add_notes/', add_notes, name='add-notes'),
]
