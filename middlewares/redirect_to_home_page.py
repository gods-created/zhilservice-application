from django.http import HttpResponseRedirect
from admin.urls import urlpatterns as admin_urlpatterns
from user.urls import urlpatterns as user_urlpatterns
from pages.urls import urlpatterns as pages_urlpatterns

class RedirectToHomePageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        if_admin_path = any(path.endswith(str(url.pattern)) for url in admin_urlpatterns)
        if_user_path = any(path.endswith(str(url.pattern)) for url in user_urlpatterns)
        if_pages_path = any(path.endswith(str(url.pattern)) for url in pages_urlpatterns)
        
        if not any((if_admin_path, if_user_path, if_pages_path)) or path == '/':
            return HttpResponseRedirect('/news')

        return self.get_response(request)