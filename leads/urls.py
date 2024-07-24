from django.urls import path
from .views import *

urlpatterns = [
    path('generate_shopifystoresdetail/', generate_shopifystoresdetail, name='generate-shopifystoresdetail'),
    path('show-leads/', show_leads, name='all-leads'),
    path('lead/add/', add_lead, name='add-lead'),
    # path('lead/<int:id>/', get_or_update_lead, name='get-or-update-lead'),
    path('lead/find/', find_leads, name='find-leads'),
    path('lead/<int:id>/add_notes/', add_notes, name='add-notes'),
    path('lead/<int:lead_id>/', lead_detail, name='lead_detail'),
]
