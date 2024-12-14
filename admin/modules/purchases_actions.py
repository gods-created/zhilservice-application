from .base import Base
from copy import deepcopy
from ..models import Purchases
from asgiref.sync import sync_to_async
from os import remove

class PurchasesActions(Base):
    def __init__(self):
        super().__init__()

    async def __aenter__(self):
        super().__enter__()
        return self

    @sync_to_async
    def __add_purchase(self, short_description: str, file: bytearray) -> dict:
        response_json = deepcopy(self.response_json)

        try:
            s3_bucket = self.s3_bucket
            if not s3_bucket:
                raise Exception('Не вдалося зберегти інформацію щодо закупівлі через відсутнє з\'єднання з S3.')

            uploaded_filename = file.name.lower()
            if not uploaded_filename.endswith(('.docx', '.doc', '.xlsx', '.xls')):
                raise ValueError(f'Файл некоректного формату.')

            purchase, _ = Purchases.objects.get_or_create(
                short_description=short_description
            )
            
            filename = f'{purchase.id}_{uploaded_filename}'
            purchase.file_source = f'https://{self.aws_bucket_name}.s3.us-east-1.amazonaws.com/purchases/{filename}'
            purchase.save()

            with open(filename, "wb+") as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
            
            with open(filename, "rb") as destination:
                s3_bucket.upload_fileobj(destination, f'purchases/{filename}')

            remove(filename)

            response_json['status'] = 'success'

        except (Exception, ) as e:
            response_json['err_description'] = str(e)

        finally:
            return response_json
    
    @sync_to_async
    def __purchases(self) -> list:
        return list(Purchases.objects.all().values('id', 'short_description', 'file_source'))
    
    @sync_to_async
    def __delete_purchase(self, purchases_id: int) -> None:
        response_json = deepcopy(self.response_json)

        try:
            purchase = Purchases.objects.get(id=purchases_id)

            file_source = purchase.file_source
            
            delete_from_s3_response = self._delete_from_s3('purchases', file_source)
            if delete_from_s3_response.get('status', 'error') == 'error':
                raise Exception(
                    delete_from_s3_response.get('err_description', '')
                )

            purchase.delete()

            response_json['status'] = 'success'
        
        except Purchases.DoesNotExist:
            response_json['err_description'] = 'Інформації щодо закупівлі не знайдено.'
        
        except (Exception, ) as e:
            response_json['err_description'] = str(e)

        finally:
            return response_json

    async def _executing_process(self, *args, **kwargs) -> dict:
        response_json = deepcopy(self.response_json)

        try:
            action = kwargs.get('action')
            if not action:
                raise ValueError('Виконання запиту неможливе.')
            
            if action == 'add_purchase':
                if len(args) != 2:
                    raise ValueError('Некоректна кількість аргументів для виконання запиту.')
                
                short_description, file, *_ = args
                add_purchase_response = await self.__add_purchase(short_description, file)
                if add_purchase_response.get('status', 'error') == 'error':
                    raise Exception(
                        add_purchase_response.get('err_description', '')
                    )

            elif action == 'purchases':
                items = await self.__purchases()
                response_json['items'] = items

            elif action == 'delete':
                if len(args) != 1:
                    raise ValueError('Некоректна кількість аргументів для виконання запиту.')
                
                purchases_id, *_ = args
                delete_purchase_response = await self.__delete_purchase(purchases_id)
                if delete_purchase_response.get('status', 'error') == 'error':
                    raise Exception(
                        delete_purchase_response.get('err_description', '')
                    )

            response_json['status'] = 'success'

        except (ValueError, Exception, ) as e:
            response_json['err_description'] = str(e)

        finally:
            return response_json
    
    async def purchases(self) -> dict:
        response_json = deepcopy(self.response_json)

        try:
            executing_process_response = await self._executing_process(action='purchases')
            if executing_process_response.get('status', 'error') == 'error':
                raise Exception(
                    executing_process_response.get('err_description', '')
                )

            response_json['items'] = executing_process_response.get('items', [])
            response_json['status'] = 'success'

        except (Exception, ) as e:
            response_json['err_description'] = str(e)

        finally:
            return response_json
    
    async def add_purchase(self, data) -> dict:
        response_json = deepcopy(self.response_json)

        try:
            short_description, file = data.get('short_description', ''), data.get('file', None)
            if not all((short_description, file)):
                raise ValueError('Некоректно заповнена форма.')

            executing_process_response = await self._executing_process(short_description, file, action='add_purchase')
            if executing_process_response.get('status', 'error') == 'error':
                raise Exception(
                    executing_process_response.get('err_description', '')
                )

            response_json['status'] = 'success'

        except (ValueError, Exception, ) as e:
            response_json['err_description'] = str(e)

        finally:
            return response_json
 
    async def delete_purchase(self, data: dict) -> dict:
        response_json = deepcopy(self.response_json)

        try:
            purchases_id = data.get('purchases_id', '')
            if not purchases_id:
                raise ValueError('Не вказано ID закупівлі.')

            executing_process_response = await self._executing_process(
                purchases_id,
                action='delete'
            )

            if executing_process_response.get('status', 'error') == 'error':
                raise Exception(
                    executing_process_response.get('err_description', '')
                )
            
            response_json['status'] = 'success'

        except (Exception, ) as e:
            response_json['err_description'] = str(e)

        finally:
            return response_json
    
    async def __aexit__(self, *args, **kwargs):
        if self.s3_client:
            self.s3_client.close()