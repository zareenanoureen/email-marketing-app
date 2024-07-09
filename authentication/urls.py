from django.urls import path
from .views import *

urlpatterns = [
    path('signup/', signup, name='signup'),
    path('', signin, name='signin'),
    path('profile/', profile, name='profile'),
    path('tabs/', tabs_page, name='tabs_page'),
    path('dashboard/', dashboard, name='dashboard'),
]
