from django.shortcuts import render
from django.http import HttpRequest
from django.core.paginator import Paginator
from admin.modules.news_actions import NewsActions
from admin.modules.vacancies_actions import VacanciesActions
from typing import Any 
from os import getenv 

async def get_elements(page: int = 1, items: str = 'news') -> list:
    response_json = {}

    if items == 'news':
        async with NewsActions() as module:
            response_json.update(
                await module.news(page)
            )
    elif items == 'vacancies':
        async with VacanciesActions() as module:
            response_json.update(
                await module.select_all_vacancies(page)
            )

    if response_json.get('status', 'error') == 'error':
        raise Exception(
            response_json.get('err_description', '')
        )

    all_items = response_json.get('items', [])

    if not all_items and page > 1:
        page -= 1
        return await get_elements(page)

    return all_items

async def _main_page(request) -> Any:
    status = 500 

    try:
        method = request.method
        if method != 'GET':
            status=405
            raise Exception(f'Використання методу {method} неможливе.')

        page = int(
            request.GET.get('page', '1')
        )

        all_news = await get_elements(page, 'news')
        paginator = Paginator(all_news, 12)
        news = paginator.get_page(page) 

        return render(request, 'pages/user/main.html', {'news': news})

    except (Exception, ) as e:
        return HttpRequest(
            str(e),
            content_type='text/html; charset=utf-8',
            status=status
        )

async def _vacancies_page(request) -> Any:
    status = 500 

    try:
        method = request.method
        if method != 'GET':
            status=405
            raise Exception(f'Використання методу {method} неможливе.')

        page = int(
            request.GET.get('page', '1')
        )

        all_vacancies = await get_elements(page, 'vacancies')
        paginator = Paginator(all_vacancies, 12)
        vacancies = paginator.get_page(page) 
        tel = getenv('COMPANY_TELEPHONE_NUMBER', '+')

        return render(request, 'pages/user/vacancies.html', {'vacancies': vacancies, 'tel': tel})

    except (Exception, ) as e:
        return HttpRequest(
            str(e),
            content_type='text/html; charset=utf-8',
            status=status
        )

async def _admin_auth(request) -> Any:
    status = 500 

    try:
        method = request.method
        if method != 'GET':
            status=405
            raise Exception(f'Використання методу {method} неможливе.')
        
        return render(request, 'pages/admin/auth.html', {
            'app_secret_key': getenv('APP_SECRET_KEY', '')
        })
    
    except (Exception, ) as e:
        return HttpRequest(
            str(e),
            content_type='text/html; charset=utf-8',
            status=status
        )
    
async def _admin_panel(request) -> Any:
    status = 500 

    try:
        method = request.method
        if method != 'GET':
            status=405
            raise Exception(f'Використання методу {method} неможливе.')
        
        tab = request.GET.get('tab', 'add_accounts')
        data = {
            'tab': tab
        }

        if tab != 'add_accounts':
            page = int(
                request.GET.get('page', '1')
            )

            if tab == 'news_actions':
                all_news =  await get_elements(page, 'news')
                paginator = Paginator(all_news, 12)
                news = paginator.get_page(page) 

                data['news'] = news

            elif tab == 'vacancies_actions':
                all_vacancies =  await get_elements(page, 'vacancies')
                paginator = Paginator(all_vacancies, 12)
                vacancies = paginator.get_page(page) 

                data['vacancies'] = vacancies

            else:
                pass

        return render(request, 'pages/admin/panel.html', data)
    
    except (Exception, ) as e:
        return HttpRequest(
            str(e),
            content_type='text/html; charset=utf-8',
            status=status
        )