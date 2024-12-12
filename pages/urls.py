from django.urls import path, re_path
from .views import (
    _main_page,
    _vacancies_page,
    _purchases_page,
    _contacts_page, 
    _admin_auth, 
    _admin_panel
)

urlpatterns = [
    re_path(r'^news/?$', _main_page),
    re_path(r'^vacancies/?$', _vacancies_page),
    re_path(r'^purchases/?$', _purchases_page),
    re_path(r'^contacts/?$', _contacts_page),

    re_path(r'^admin/auth/?$', _admin_auth),
    re_path(r'^admin/?$', _admin_panel),
]
