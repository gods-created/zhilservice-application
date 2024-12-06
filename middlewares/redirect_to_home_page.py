from django.http import HttpResponseRedirect
from django.urls import resolve, Resolver404
from re import sub

class RedirectToHomePageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path.strip('/')
        print(path)
        try:
            resolve(request.path)
        except Resolver404:
            return HttpResponseRedirect('/news/')

        return self.get_response(request)