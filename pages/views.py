from django.shortcuts import render
from django.http import HttpRequest
from django.core.paginator import Paginator
from admin.modules.news_actions import NewsActions
from admin.modules.vacancies_actions import VacanciesActions
from admin.modules.purchases_actions import PurchasesActions
from user.forms import SendInvocation as SendInvocationForm
from typing import Any 
from os import getenv
import json

async def get_elements(items: str = 'news') -> list:
    response_json = {}

    if items == 'news':
        async with NewsActions() as module:
            response_json.update(
                await module.news()
            )

    elif items == 'vacancies':
        async with VacanciesActions() as module:
            response_json.update(
                await module.select_all_vacancies()
            )

    elif items == 'purchases':
        async with PurchasesActions() as module:
            response_json.update(
                await module.purchases()
            )

    if response_json.get('status', 'error') == 'error':
        raise Exception(
            response_json.get('err_description', '')
        )

    all_items = response_json.get('items', [])
    if len(all_items) > 0:
        all_items = all_items[::-1]
        
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

        all_news = await get_elements('news')
        paginator = Paginator(all_news, 12)
        news = paginator.get_page(page)

        return render(request, 'pages/user/main.html', {'news': news})

    except (Exception, ) as e:
        return HttpRequest(
            str(e),
            content_type='text/html; charset=utf-8',
            status=status
        )

async def _purchases_page(request) -> Any:
    status = 500 

    try:
        method = request.method
        if method != 'GET':
            status=405
            raise Exception(f'Використання методу {method} неможливе.')

        page = int(
            request.GET.get('page', '1')
        )

        all_items = await get_elements('purchases')
        paginator = Paginator(all_items, 12)
        purchases = paginator.get_page(page)

        status = 200
        return render(request, 'pages/user/purchases.html', {
            'purchases': purchases
        })

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

        all_vacancies = await get_elements('vacancies')
        paginator = Paginator(all_vacancies, 12)
        vacancies = paginator.get_page(page) 
        tel = getenv('HR_TELEPHONE_NUMBER', '+')

        return render(request, 'pages/user/vacancies.html', {'vacancies': vacancies, 'tel': tel})

    except (Exception, ) as e:
        return HttpRequest(
            str(e),
            content_type='text/html; charset=utf-8',
            status=status
        )

async def _contacts_page(request) -> Any:
    status = 500

    try:
        method = request.method
        if method != 'GET':
            status = 405
            raise Exception(f'Використання методу {method} неможливе.')

        send_invocation_response = json.loads(request.COOKIES.get('send_invocation_response', '{}'))
            
        response = render(
            request, 'pages/user/contacts.html', {
                'form': SendInvocationForm,
                'response': send_invocation_response,
                'dispetcher_telephone_number': getenv('DISPETCHER_TELEPHONE_NUMBER', '+'),
                'cherkaske_accounter_telephone_number': getenv('CHERKASKE_ACCOUNTER_TELEPHONE_NUMBER', '+'),
                'zarichne_accounter_telephone_number': getenv('ZARICHNE_ACCOUNTER_TELEPHONE_NUMBER', '+'),
                'company_email': getenv('COMPANY_EMAIL', ''),
            }
        )

        if send_invocation_response:
            response.delete_cookie(
                'send_invocation_response'
            )

        return response

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

            elements = ''
            if tab == 'news_actions':
                elements = 'news'
            elif tab == 'purchases_actions':
                elements = 'purchases'
            elif tab == 'vacancies_actions':
                elements = 'vacancies'

            all_news = await get_elements(elements)
            paginator = Paginator(all_news, 12)
            items = paginator.get_page(page)

            data[elements] = items
            
        return render(request, 'pages/admin/panel.html', data)
    
    except (Exception, ) as e:
        return HttpRequest(
            str(e),
            content_type='text/html; charset=utf-8',
            status=status
        )