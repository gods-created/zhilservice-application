from .base import Base
from copy import deepcopy
from jwt import decode, PyJWTError
from os import getenv, remove
from boto3 import resource
from ..migrations.admin_auth.models import AdminAuthData
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from time import time 

class AdminAuth(Base):
    def __init__(self):
        super().__init__()
        self.app_secret_key = getenv('APP_SECRET_KEY')
        self.db = None

    async def __aenter__(self):
        super().__enter__()
        
        admin_auth_db_string_connection = getenv('ADMIN_AUTH_DB_STRING_CONNECTION')
        if admin_auth_db_string_connection:
            self.db = Session(
                create_engine(
                    admin_auth_db_string_connection,
                    echo=False,
                    connect_args={'check_same_thread': False}
                )
            )

        return self

    def __create_file(self, *args) -> None:
        filename, document, *_ = args
        with open(filename, 'wb+') as destination:
            for chunk in document:
                destination.write(chunk) 
        
        return None
    
    def __upload_file_to_bucket(self, filename: str) -> dict:
        response_json = deepcopy(self.response_json)

        try:
            s3_bucket = self.s3_bucket
            if not s3_bucket:
                raise Exception('Неможливо підключитися до ресурсу для завантежння файлу.')
            
            s3_bucket.upload_file(
                Key=filename,
                Filename=filename
            )

            response_json['status'] = 'success'

        except (ValueError, Exception, ) as e:
            response_json['err_description'] = str(e)

        finally:
            return response_json
    
    def __add_accounts(self, *args) -> dict:
        response_json = deepcopy(self.response_json)

        try:
            locality, documents, *_ = args
            for doc in documents:
                document_object = (doc.chunks(), doc.name)
                break
            
            document, document_filename = document_object
            document_filename = document_filename.lower()
            
            if not document_filename.endswith(('.xls', '.xlsx')):
                raise ValueError('Некоректний формат завантаженого файла.')

            extension = '.xls' if document_filename.endswith('.xls') else '.xlsx'
            filename = 'cherkaske' if locality == 'Черкаське' else 'zarichne'
            filename = f'{filename}{extension}'
            
            file = self.__create_file(filename, document)
            upload_file_to_bucket_response = self.__upload_file_to_bucket(filename)
            if upload_file_to_bucket_response.get('status', 'error') == 'error':
                raise Exception(
                    upload_file_to_bucket_response.get('err_description', '')
                )

            remove(filename)
            response_json['status'] = 'success'

        except (ValueError, Exception, ) as e:
            response_json['err_description'] = str(e)

        finally:
            return response_json
    
    def __decode_token(self, token: str) -> dict:
        response_json = deepcopy(self.response_json)

        try:
            data = decode(token, self.app_secret_key, algorithms=['HS256'])

            response_json['data'] = data
            response_json['status'] = 'success'

        except PyJWTError as e:
            response_json['err_description'] = 'Некоректний токен авторизації.'

        except Exception as e:
            response_json['err_description'] = str(e)

        finally:
            return response_json
        
    def __update(self, data: dict = {}) -> dict:
        response_json = deepcopy(self.response_json)
        db = self.db

        try:
            if not db:
                raise Exception('Не вдалося з\'єднатися с БД.')

            new_email, new_password, new_session_token = data.get('new_email', ''), data.get('new_password', ''), data.get('new_session_token', '')
            for_updating = {}
            if new_email:
                for_updating['email'] = new_email
            if new_password:
                for_updating['password'] = new_password
            
            for_updating['session_token'] = new_session_token
            for_updating['expired_time'] = int(time() * 1000) + 1200000
            db.query(AdminAuthData).filter(AdminAuthData.id == 1).update(for_updating)
            db.commit()

            response_json['status'] = 'success'

        except (Exception, ) as e:
            response_json['err_description'] = str(e)
            if db:
                db.rollback()

        finally:
            return response_json

    def __select(self, *args) -> dict:
        response_json = deepcopy(self.response_json)

        try:
            db = self.db
            if not db:
                raise Exception('Не вдалося з\'єднатися с БД.')

            if len(args) == 2:
                email, password, *_ = args
                stmt = select(AdminAuthData).where(
                    (AdminAuthData.email == email),
                    (AdminAuthData.password == password)
                )
            else:
                stmt = select(AdminAuthData)

            row = db.scalars(stmt).first()
            if not row:
                raise Exception('Не вірний пароль або пошта.')
            
            response_json['data'] = row.to_json()
            response_json['status'] = 'success'

        except (Exception, ) as e:
            response_json['err_description'] = str(e)

        finally:
            return response_json
        
    def __drop_session(self) -> dict:
        response_json = deepcopy(self.response_json)
        db = self.db

        try:
            if not db:
                raise Exception('Не вдалося з\'єднатися с БД.')

            update_response = self.__update({
                'new_session_token': ''
            })
            if update_response.get('status', 'error') == 'error':
                raise Exception(
                    update_response.get('err_description', '')
                )

            response_json['status'] = 'success'

        except (Exception, ) as e:
            response_json['err_description'] = str(e)

        finally:
            return response_json

    def __refresh_expired_time(self) -> dict:
        response_json = deepcopy(self.response_json)
        db = self.db
        
        try:
            if not db:
                raise Exception('Не вдалося з\'єднатися с БД.')

            select_response = self.__select()
            if select_response.get('status', 'error') == 'error':
                raise Exception(
                    select_response.get('err_description', '')
                )

            data = select_response.get('data', {})
            session_token = data.get('session_token')

            update_response = self.__update({
                'new_session_token': session_token
            })
            if update_response.get('status', 'error') == 'error':
                raise Exception(
                    update_response.get('err_description', '')
                )

            response_json['status'] = 'success'

        except (Exception, ) as e:
            response_json['err_description'] = str(e)

        finally:
            return response_json

    def __select_session_token(self) -> dict:
        response_json = deepcopy(self.response_json)

        try:
            db = self.db
            if not db:
                raise Exception('Не вдалося з\'єднатися с БД.')

            select_response = self.__select()
            if select_response.get('status', 'error') == 'error':
                raise Exception(
                    select_response.get('err_description', '')
                )

            data = select_response.get('data', {})
            data = {
                'session_token': data.get('session_token', ''),
                'expired_time': data.get('expired_time', '')
            }

            response_json['data'] = data
            response_json['status'] = 'success'

        except (Exception, ) as e:
            response_json['err_description'] = str(e)

        finally:
            return response_json

    def __auth(self, email: str, password: str) -> dict:
        response_json = deepcopy(self.response_json)

        try:
            db = self.db
            if not db:
                raise Exception('Не вдалося з\'єднатися с БД.')

            select_response = self.__select(email, password)
            if select_response.get('status', 'error') == 'error':
                raise Exception(
                    select_response.get('err_description', '')
                )

            session_token = self._generate_string()
            update_response = self.__update({
                'new_session_token': session_token
            })
            if update_response.get('status', 'error') == 'error':
                raise Exception(
                    update_response.get('err_description', '')
                )

            data = select_response.get('data', {})
            data['session_token'] = session_token

            response_json['data'] = data
            response_json['status'] = 'success'

        except (Exception, ) as e:
            response_json['err_description'] = str(e)

        finally:
            return response_json 
    
    async def _executing_process(self, *args, **kwargs) -> dict:
        response_json = deepcopy(self.response_json)

        try:
            action = kwargs.get('action', '')
            if not action:
                raise ValueError('Не вказано дію для виконання.')
            
            data = {}

            if action == 'auth':
                token, *_ = args
                decode_token_response = self.__decode_token(token)
                if decode_token_response.get('status', 'error') == 'error':
                    raise Exception(
                        decode_token_response.get('err_description', '')
                    )
                
                data = decode_token_response.get('data', {})

                email, password = data.get('email', ''), data.get('password', '')
                if not all((email, password)):
                    raise ValueError('Відсутні необхідні дані для авторизації.')
                
                auth_response = self.__auth(email, password)
                if auth_response.get('status', 'error') == 'error':
                    raise Exception(
                        auth_response.get('err_description', '')
                    )
                
                data = auth_response.get('data', {})

            elif action == 'select_session_token':
                select_session_token_response = self.__select_session_token()
                if select_session_token_response.get('status', 'error') == 'error':
                    raise Exception(
                        select_session_token_response.get('err_description', '')
                    )
                
                data = select_session_token_response.get('data', {})

            elif action == 'drop_session':
                drop_session_response = self.__drop_session()
                if drop_session_response.get('status', 'error') == 'error':
                    raise Exception(
                        drop_session_response.get('err_description', '')
                    )
                
            elif action == 'refresh_expired_time':
                refresh_expired_time_response = self.__refresh_expired_time()
                if refresh_expired_time_response.get('status', 'error') == 'error':
                    raise Exception(
                        refresh_expired_time_response.get('err_description', '')
                    )
            
            elif action == 'add_accounts':
                if len(args) != 2:
                    raise ValueError('Не вказано усі необхідні параметри для виконання запиту.')
                
                locality, documents, *_ = args
                add_accounts_response = self.__add_accounts(locality, documents)
                if add_accounts_response.get('status', 'error') == 'error':
                    raise Exception(
                        add_accounts_response.get('err_description', '')
                    )
            
            response_json['data'] = data
            response_json['status'] = 'success'

        except (ValueError, Exception, ) as e:
            response_json['err_description'] = str(e)

        finally:
            return response_json
        
    async def auth(self, data: dict) -> dict:
        response_json = deepcopy(self.response_json)

        try:
            token = data.get('jwt', '')
            if not token:
                raise ValueError('Не вказано токен авторизації.')
            
            executing_process_response = await self._executing_process(token, action='auth')
            if executing_process_response.get('status', 'error') == 'error':
                raise Exception(
                    executing_process_response.get('err_description', '')
                )

            data = executing_process_response.get('data', {})

            response_json['data'] = data
            response_json['status'] = 'success'

        except (Exception, ) as e:
            response_json['err_description'] = str(e)

        finally:
            return response_json 

    async def select_session_token(self) -> dict:
        response_json = deepcopy(self.response_json)

        try:
            executing_process_response = await self._executing_process(action='select_session_token')
            if executing_process_response.get('status', 'error') == 'error':
                raise Exception(
                    executing_process_response.get('err_description', '')
                )

            data = executing_process_response.get('data', {})

            response_json['data'] = data
            response_json['status'] = 'success'

        except (Exception, ) as e:
            response_json['err_description'] = str(e)

        finally:
            return response_json 
        
    async def drop_session(self) -> dict:
        response_json = deepcopy(self.response_json)

        try:
            executing_process_response = await self._executing_process(action='drop_session')
            if executing_process_response.get('status', 'error') == 'error':
                raise Exception(
                    executing_process_response.get('err_description', '')
                )
            
            response_json['status'] = 'success'

        except (Exception, ) as e:
            response_json['err_description'] = str(e)

        finally:
            return response_json 
        
    async def refresh_expired_time(self) -> dict:
        response_json = deepcopy(self.response_json)

        try:
            executing_process_response = await self._executing_process(action='refresh_expired_time')
            if executing_process_response.get('status', 'error') == 'error':
                raise Exception(
                    executing_process_response.get('err_description', '')
                )
            
            response_json['status'] = 'success'

        except (Exception, ) as e:
            response_json['err_description'] = str(e)

        finally:
            return response_json
        
    async def add_accounts(self, data: dict) -> dict:
        response_json = deepcopy(self.response_json)

        try:
            locality = data.get('locality')
            documents = data.get('documents', [])

            if not all((locality, documents)):
                raise ValueError('Не вказано усі необхідні параметри для виконання запиту.')
            
            executing_process_response = await self._executing_process(locality, documents, action='add_accounts')
            if executing_process_response.get('status', 'error') == 'error':
                raise Exception(
                    executing_process_response.get('err_description', '')
                )
            
            response_json['status'] = 'success'
            
        except (ValueError, Exception, ) as e:
            response_json['err_description'] = str(e)

        finally:
            return response_json
    
    async def __aexit__(self, *args, **kwargs):
        if not self.db:
            self.db.close()