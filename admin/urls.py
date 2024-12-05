"""
URL configuration for zhilservice project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from .views import (
    _news, _add_news, _update_news, 
    _delete_news, _delete_all_news, _auth_admin, 
    _add_accounts, _add_vacancy, _vacancies, 
    _delete_vacancy, _delete_all_vacancies
)

urlpatterns = [
    path('news', _news),
    path('add_news', _add_news),
    path('update_news', _update_news),
    path('delete_news', _delete_news),
    path('delete_all_news', _delete_all_news),

    path('auth', _auth_admin),

    path('add_accounts', _add_accounts),

    path('vacancies', _vacancies),
    path('add_vacancy', _add_vacancy),
    path('delete_vacancy', _delete_vacancy),
    path('delete_all_vacancies', _delete_all_vacancies)
]