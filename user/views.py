from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .modules import Account
from .forms import Get
from typing import Any

async def _account(request) -> Any:
    status = 500

    try:
        method = request.method
        if method != 'POST':
            status = 405
            raise Exception('Використання методу {method} неможливе.')
        
        form = Get(request.POST)
        if not form.is_valid():
            status = 422
            raise Exception('Некоректно заповнена форма.')

        data = form.to_json()
        async with Account() as module:
            response_json = await module.get(data)
        
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