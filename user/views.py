from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from .modules import Account, SendInvocation
from .forms import Get, SendInvocation as SendInvocationForm
from typing import Any
from pages.views import _contacts_page
import json

async def _account(request) -> Any:
    status = 500

    try:
        method = request.method
        if method != 'POST':
            status = 405
            raise Exception(f'Використання методу {method} неможливе.')
        
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
    
async def _send_invocation(request) -> Any:
    status = 500
    response_json = {'status': 'error', 'err_description': ''}

    try:
        method = request.method
        if method != 'POST':
            status = 405
            raise Exception(f'Використання методу {method} неможливе.')
        
        form = SendInvocationForm(request.POST)
        if not form.is_valid():
            status = 422
            raise Exception('Некоректно заповнена форма.')

        data = form.to_json()
        async with SendInvocation() as module:
            response_json.update(
                await module.send_invocation(data)
            )
        
        status = 200
        response_json['status'] = 'success'

    except (Exception, ) as e:
        response_json['err_description'] = str(e)
    
    finally:
        response = HttpResponseRedirect('/contacts')
        response.set_cookie(
            'send_invocation_response',
            json.dumps(response_json)
        )
        return response
