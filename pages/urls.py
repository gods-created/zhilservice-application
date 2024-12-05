from django.urls import path
from .views import (
    _main_page,
    _vacancies_page, 
    _admin_auth, 
    _admin_panel
)

urlpatterns = [
    path('news', _main_page),
    path('vacancies', _vacancies_page),
    
    path('admin/auth', _admin_auth),
    path('admin', _admin_panel)
]
