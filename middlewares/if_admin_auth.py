from django.http import HttpResponseRedirect
from admin.modules import AdminAuth
from time import time
from loguru import logger
from asgiref.sync import iscoroutinefunction, markcoroutinefunction

class IfAdminAuthMiddleware:
    async_capable = True
    sync_capable = False

    def __init__(self, get_response):
        self.get_response = get_response
        if iscoroutinefunction(self.get_response):
            markcoroutinefunction(self)

    async def __call__(self, request):
        path = request.path
        session_token_from_cookie = request.COOKIES.get('session_token', '')

        if path.startswith('/admin'):
            is_authenticated = await self._check_admin_auth()
            if_token = await self._check_session_token(session_token_from_cookie)

            if not all((is_authenticated, if_token)):
                if '/auth' not in path:
                    return HttpResponseRedirect('/admin/auth/')
            else:
                if '/auth' in path:
                    return HttpResponseRedirect('/admin')

        return await self.get_response(request)

    async def _check_session_token(self, session_token_from_cookie: str) -> bool:
        async with AdminAuth() as module:
            response_json = await module.select_session_token()

        session_token = response_json.get('data', {}).get('session_token', '')
        expired_time = response_json.get('data', {}).get('expired_time', 0)

        if (session_token and (session_token != session_token_from_cookie or int(time() * 1000) - expired_time > 1200000)) or not session_token:
            async with AdminAuth() as module:
                drop_session_response = await module.drop_session()

            if drop_session_response.get('status', 'error') == 'error':
                logger.error(
                    drop_session_response.get('err_description', '')
                )
                
            return False
            
        async with AdminAuth() as module:
            refresh_expired_time_response = await module.refresh_expired_time()

        if refresh_expired_time_response.get('status', 'error') == 'error':
            logger.error(
                refresh_expired_time_response.get('err_description', '')
            )
        
        return True

    async def _check_admin_auth(self) -> bool:
        try:
            async with AdminAuth() as module:
                response_json = await module.select_session_token()

            if response_json.get('status') == 'error':
                logger.error(response_json.get('err_description', 'Неизвестная ошибка'))
                return False

            data = response_json.get('data', {})
            session_token = data.get('session_token', '')
            expired_time = data.get('expired_time', 0)

            if session_token and (time() - expired_time) <= 1200000:
                return True

            return False
        except Exception as e:
            logger.error(f"Ошибка при проверке авторизации администратора: {str(e)}")
            return False