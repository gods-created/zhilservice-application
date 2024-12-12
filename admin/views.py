from django.shortcuts import render
from typing import Any
from .modules import NewsActions, VacanciesActions, AdminAuth, PurchasesActions
from django.http import HttpResponse, JsonResponse
from .forms import *

async def _add_accounts(request) -> Any:
    status = 500 

    try:
        method = request.method
        if method != 'POST':
            status = 405
            raise Exception(f'Використання методу {method} неможливе.')
        
        form = AddAccounts(request.POST, request.FILES)
        if not form.is_valid():
            status = 422
            raise Exception('Некоректно заповнена форма.')
        
        data = form.to_json()
        async with AdminAuth() as module:
            response_json = await module.add_accounts(data)

        status = 200
        return JsonResponse(
            response_json,
            status=status
        )

    except (Exception, ) as e:
        return HttpResponse(
            content=str(e),
            content_type='text/html; charset=utf-8',
            status=status
        )



async def _vacancies(request) -> Any:
    status = 500 

    try:
        method = request.method
        if method != 'GET':
            status = 405
            raise Exception(f'Використання методу {method} неможливе.')

        page = int(
            request.GET.get('page', '1')
        )

        async with VacanciesActions() as module:
            response_json = await module.select_all_vacancies(page)

        status = 200
        return JsonResponse(
            response_json,
            status=status
        )

    except (Exception, ) as e:
        return HttpResponse(
            content=str(e),
            content_type='',
            status=status
        )

async def _add_vacancy(request) -> Any:
    status = 500 

    try:
        method = request.method
        if method != 'POST':
            status = 405
            raise Exception(f'Використання методу {method} неможливе.')
        
        form = AddVacancy(request.POST)
        if not form.is_valid():
            status = 422
            raise Exception('Некоректно заповнена форма.')
        
        data = form.to_json()
        async with VacanciesActions() as module:
            response_json = await module.add_vacancy(data)

        status = 200
        return JsonResponse(
            response_json,
            status=status
        )

    except (Exception, ) as e:
        return HttpResponse(
            str(e),
            content_type='text/html; charset=utf-8',
            status=status
        )

async def _delete_vacancy(request) -> Any:
    status = 500 

    try:
        method = request.method
        if method != 'POST':
            status = 405
            raise Exception(f'Використання методу {method} неможливе.')
        
        form = DeleteVacancy(request.POST)
        if not form.is_valid():
            status = 422
            raise Exception('Некоректно заповнена форма.')
        
        data = form.to_json()
        async with VacanciesActions() as module:
            response_json = await module.delete_vacancy(data)

        status = 200
        return JsonResponse(
            response_json,
            status=status
        )

    except (Exception, ) as e:
        return HttpResponse(
            str(e),
            content_type='text/html; charset=utf-8',
            status=status
        )

async def _delete_all_vacancies(request) -> Any:
    status = 500 

    try:
        method = request.method
        if method != 'GET':
            status = 405
            raise Exception(f'Використання методу {method} неможливе.')

        async with VacanciesActions() as module:
            response_json = await module.delete_all_vacancies()

        status = 200
        return JsonResponse(
            response_json,
            status=status
        )

    except (Exception, ) as e:
        return HttpResponse(
            content=str(e),
            content_type='',
            status=status
        )



async def _news(request) -> Any:
    status = 500

    try:
        method = request.method
        if method != 'GET':
            status = 405
            raise Exception(f'Використання методу {method} неможливе.')

        async with NewsActions() as module:
            response_json = await module.news()

        status = 200
        return JsonResponse(
            response_json,
            status=status
        )

    except (Exception, ) as e:
        return HttpResponse(
            str(e),
            content_type='text/html; charset=utf-8',
            status=status
        )

async def _add_news(request) -> Any:
    status = 500

    try:
        method = request.method 
        if method != 'POST':
            status = 405
            raise Exception(f'Використання методу {method} неможливе.')
        
        form = AddNews(request.POST, request.FILES)
        if not form.is_valid():
            status = 422
            raise Exception('Некоректно заповнена форма.')
        
        data = form.to_json()
        async with NewsActions() as module:
            response_json = await module.add_news(data)

        status = 200
        return JsonResponse(
            response_json,
            status=status
        )

    except (Exception, ) as e:
        return HttpResponse(
            str(e),
            content_type='text/html; charset=utf-8',
            status=status
        )

async def _delete_news(request) -> Any:
    status = 500

    try:
        method = request.method 
        if method != 'POST':
            status = 405
            raise Exception(f'Використання методу {method} неможливе.')

        form = DeleteNews(request.POST)
        if not form.is_valid():
            status = 422
            raise Exception('Некоректно заповнена форма.')
        
        data = form.to_json()
        async with NewsActions() as module:
            response_json = await module.delete_news(data)

        status = 200
        return JsonResponse(
            response_json,
            status=status
        )

    except (Exception, ) as e:
        return HttpResponse(
            str(e),
            content_type='text/html; charset=utf-8',
            status=status
        )
    
async def _delete_all_news(request) -> Any:
    status = 500

    try:
        method = request.method 
        if method != 'POST':
            status = 405
            raise Exception(f'Використання методу {method} неможливе.')

        async with NewsActions() as module:
            response_json = await module.delete_all_news()

        status = 200
        return JsonResponse(
            response_json,
            status=status
        )

    except (Exception, ) as e:
        return HttpResponse(
            str(e),
            content_type='text/html; charset=utf-8',
            status=status
        )
    


async def _purchases(request) -> Any:
    status = 500

    try:
        method = request.method
        if method != 'GET':
            status = 405
            raise Exception(f'Використання методу {method} неможливе.')

        async with PurchasesActions() as module:
            response_json = await module.purchases()

        status = 200
        return JsonResponse(
            response_json,
            status=status
        )

    except (Exception, ) as e:
        return HttpResponse(
            str(e),
            content_type='text/html; charset=utf-8',
            status=status
        )

async def _add_purchase(request) -> Any:
    status = 500

    try:
        method = request.method 
        if method != 'POST':
            status = 405
            raise Exception(f'Використання методу {method} неможливе.')
        
        form = AddPurchase(request.POST, request.FILES)
        if not form.is_valid():
            status = 422
            raise Exception('Некоректно заповнена форма.')
        
        data = form.to_json()
        async with PurchasesActions() as module:
            response_json = await module.add_purchase(data)

        status = 200
        return JsonResponse(
            response_json,
            status=status
        )

    except (Exception, ) as e:
        return HttpResponse(
            str(e),
            content_type='text/html; charset=utf-8',
            status=status
        )

async def _delete_purchase(request) -> Any:
    status = 500

    try:
        method = request.method 
        if method != 'POST':
            status = 405
            raise Exception(f'Використання методу {method} неможливе.')

        form = DeletePurchase(request.POST)
        if not form.is_valid():
            status = 422
            raise Exception('Некоректно заповнена форма.')
        
        data = form.to_json()
        async with PurchasesActions() as module:
            response_json = await module.delete_purchase(data)

        status = 200
        return JsonResponse(
            response_json,
            status=status
        )

    except (Exception, ) as e:
        return HttpResponse(
            str(e),
            content_type='text/html; charset=utf-8',
            status=status
        )
    


async def _auth_admin(request) -> Any:
    status = 500

    try:
        method = request.method 
        if method != 'POST':
            status = 405
            raise Exception(f'Використання методу {method} неможливе.')

        form = AuthAdmin(request.POST)
        if not form.is_valid():
            status = 422
            raise Exception('Некоректно заповнена форма.')

        data = form.to_json()
        async with AdminAuth() as module:
            response_json = await module.auth(data)

        status = 200
        return JsonResponse(
            response_json,
            status=status
        )

    except (Exception, ) as e:
        return HttpResponse(
            str(e),
            content_type='text/html; charset=utf-8',
            status=status
        )