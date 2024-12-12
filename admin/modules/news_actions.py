from .base import Base
from copy import deepcopy
from ..models import News
from asgiref.sync import sync_to_async
from os import remove

class NewsActions(Base):
    def __init__(self):
        super().__init__()

    async def __aenter__(self):
        super().__enter__()
        return self
    
    def __delete_from_s3(self, filename: str = None) -> dict:
        response_json = deepcopy(self.response_json)

        try:
            s3_client = self.s3_client
            if not s3_client:
                raise Exception('Не вдалося видалити новину через відсутнє з\'єднання з S3.')

            bucket_name = self.aws_bucket_name
            list_objects = s3_client.list_objects(
                Bucket=bucket_name,
                Prefix='news/'
            )

            contents = list_objects.get('Contents', [])
            keys = [item.get('Key') for item in contents]

            if filename:
                for key in keys:
                    if key in filename:
                        s3_client.delete_object(
                            Bucket=bucket_name,
                            Key=key
                        )

                        break
                    else:
                        continue
            
            else:
                for key in keys:
                    s3_client.delete_object(
                        Bucket=bucket_name,
                        Key=key
                    )


            response_json['status'] = 'success'

        except (Exception, ) as e:
            response_json['err_description'] = str(e)

        finally:
            return response_json
    
    @sync_to_async
    def __add_news(self, title: str, image: bytearray, description: str) -> dict:
        response_json = deepcopy(self.response_json)

        try:
            s3_bucket = self.s3_bucket
            if not s3_bucket:
                raise Exception('Не вдалося зберегти новостворену новину через відсутнє з\'єднання з S3.')

            if not image.name.endswith(('.png', '.jpg', '.svg')):
                raise ValueError(f'Титульне зображення новини некоректного формату.')

            news, _ = News.objects.get_or_create(
                title=title
            )
            
            imagename = f'{news.id}.png'
            news.description = description
            news.image_source = f'https://{self.aws_bucket_name}.s3.us-east-1.amazonaws.com/news/{imagename}'
            news.save()

            with open(imagename, "wb+") as destination:
                for chunk in image.chunks():
                    destination.write(chunk)
            
            with open(imagename, "rb") as destination:
                s3_bucket.upload_fileobj(destination, f'news/{imagename}')

            remove(imagename)

            response_json['status'] = 'success'

        except (Exception, ) as e:
            response_json['err_description'] = str(e)

        finally:
            return response_json
    
    @sync_to_async
    def __news(self) -> list:
        return list(News.objects.all().values('id', 'title', 'image_source', 'description'))
    
    @sync_to_async
    def __delete_news(self, news_id: int) -> None:
        response_json = deepcopy(self.response_json)

        try:
            news = News.objects.get(id=news_id)
            
            image_source = news.image_source
            delete_from_s3_response = self._delete_from_s3('news', image_source)
            if delete_from_s3_response.get('status', 'error') == 'error':
                raise Exception(
                    delete_from_s3_response.get('err_description', '')
                )

            news.delete()

            response_json['status'] = 'success'
        
        except News.DoesNotExist:
            response_json['err_description'] = 'Інформації щодо новини не знайдено.'

        except (Exception, ) as e:
            response_json['err_description'] = str(e)

        finally:
            return response_json
    
    @sync_to_async
    def __delete_all_news(self) -> None:
        delete_from_s3_response = self.__delete_from_s3()
        if delete_from_s3_response.get('status', 'error') == 'error':
            raise Exception(
                delete_from_s3_response.get('err_description', '')
            )
    
        News.objects.all().delete()
        return None

    async def _executing_process(self, *args, **kwargs) -> dict:
        response_json = deepcopy(self.response_json)

        try:
            action = kwargs.get('action')
            if not action:
                raise ValueError('Виконання запиту неможливе.')
            
            if action == 'add_news':
                if len(args) != 3:
                    raise ValueError('Некоректна кількість аргументів для виконання запиту.')
                
                title, image, description, *_ = args
                add_news_response = await self.__add_news(title, image, description)
                if add_news_response.get('status', 'error') == 'error':
                    raise Exception(
                        add_news_response.get('err_description', '')
                    )

            elif action == 'news':
                items = await self.__news()
                response_json['items'] = items

            elif action == 'delete':
                if len(args) != 1:
                    raise ValueError('Некоректна кількість аргументів для виконання запиту.')
                
                news_id, *_ = args
                delete_news_response = await self.__delete_news(news_id)
                if delete_news_response.get('status', 'error') == 'error':
                    raise Exception(
                        delete_news_response.get('err_description', '')
                    )

            elif action == 'delete_all':
                delete_news_response = await self.__delete_all_news()
                if delete_news_response.get('status', 'error') == 'error':
                    raise Exception(
                        delete_news_response.get('err_description', '')
                    )

            response_json['status'] = 'success'

        except (ValueError, Exception, ) as e:
            response_json['err_description'] = str(e)

        finally:
            return response_json
    
    async def news(self) -> dict:
        response_json = deepcopy(self.response_json)

        try:
            executing_process_response = await self._executing_process(action='news')
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
    
    async def add_news(self, data) -> dict:
        response_json = deepcopy(self.response_json)

        try:
            title, image, description = data.get('title', ''), data.get('image', None), data.get('description', '')
            if not all((title, image, description)):
                raise ValueError('Некоректно заповнена форма.')

            executing_process_response = await self._executing_process(title, image, description, action='add_news')
            if executing_process_response.get('status', 'error') == 'error':
                raise Exception(
                    executing_process_response.get('err_description', '')
                )

            response_json['status'] = 'success'

        except (ValueError, Exception, ) as e:
            response_json['err_description'] = str(e)

        finally:
            return response_json
 
    async def delete_news(self, data: dict) -> dict:
        response_json = deepcopy(self.response_json)

        try:
            news_id = data.get('news_id', '')
            if not news_id:
                raise ValueError('Не вказано ID новини.')

            executing_process_response = await self._executing_process(
                news_id,
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
    
    async def delete_all_news(self) -> dict:
        response_json = deepcopy(self.response_json)

        try:
            executing_process_response = await self._executing_process(
                action='delete_all'
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