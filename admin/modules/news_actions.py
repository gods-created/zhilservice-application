from .base import Base
from copy import deepcopy
from os import getenv, remove
from boto3 import resource, client
from uuid import uuid4
from ..migrations.news.models import NewsModel
from sqlalchemy import create_engine, select, delete
from sqlalchemy.orm import Session
from loguru import logger
from subprocess import run
from re import sub, search

class NewsActions(Base):
    def __init__(self):
        super().__init__()
        self.s3_bucket = None
        self.s3_client = None
        self.db = None

    async def __aenter__(self):
        aws_access_key_id = getenv('AWS_ACCESS_KEY_ID')
        aws_secret_access_key = getenv('AWS_SECRET_ACCESS_KEY')
        aws_bucket_name = self.aws_bucket_name

        if all((
            aws_access_key_id, aws_secret_access_key, aws_bucket_name
        )):
            self.s3_bucket = resource(
                's3',
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                region_name='us-east-1'
            ).Bucket(aws_bucket_name)

            self.s3_client = client(
                's3',
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                region_name='us-east-1'
            )

        news_db_string_connection = getenv('NEWS_DB_STRING_CONNECTION')
        if news_db_string_connection:
            self.db = Session(
                create_engine(
                    news_db_string_connection,
                    echo=False,
                    connect_args={'check_same_thread': False}
                )
            )

        return self
    
    def __convert_file(self, filename: str) -> str:
        new_filename = sub(r'\.(docx|doc)$', '.pdf', filename)
        soffice_run_command = getenv('SOFFICE_RUN_COMMAND', 'soffice')

        run([
            soffice_run_command,
            '--headless',
            '--convert-to', 'pdf',
            '--print-to-file', new_filename,
            filename
        ])
        
        remove(filename)
        return new_filename

    async def __get_objects_from_bucket(self) -> dict:
        response_json = deepcopy(self.response_json)

        try:
            s3_client = self.s3_client
            if not s3_client:
                raise Exception('Неможливо підключитися до клієнта для перевірки наявності файлу.')

            list_objects_response = s3_client.list_objects_v2(
                Bucket=self.aws_bucket_name,
                Prefix='news/'
            )

            filenames = [
                file.get('Key', '') for file in list_objects_response.get('Contents', [])
            ]

            response_json['filenames'] = filenames
            response_json['status'] = 'success'
        
        except (Exception, ) as e:
            response_json['err_description'] = str(e)

        finally:
            return response_json

    async def __if_file_exists_in_bucket(self, filename: str) -> dict:
        response_json = deepcopy(self.response_json)

        try:
            s3_client = self.s3_client
            if not s3_client:
                raise Exception('Неможливо підключитися до клієнта для перевірки наявності файлу.')

            get_objects_from_bucket_response = await self.__get_objects_from_bucket()
            if get_objects_from_bucket_response.get('status', 'error') == 'error':
                raise Exception(
                    get_objects_from_bucket_response.get('err_description', '')
                )

            filenames = get_objects_from_bucket_response.get('filenames', [])
            for each in filenames:
                if search(rf'news/\s*{filename}\s*', each):
                    filename = f'{self._generate_string()}_{filename}'
                    break
                continue

            response_json['filename'] = filename
            response_json['status'] = 'success'

        except Exception as e:
            response_json['err_description'] = str(e)

        finally:
            return response_json

    async def __saving_to_bucket(self, documents: list) -> dict:
        response_json = deepcopy(self.response_json)

        try:
            s3_bucket = self.s3_bucket
            if not s3_bucket:
                raise Exception('Неможливо підключитися до ресурсу для завантежння файлу.')
            
            response_json['documents'] = []

            for doc in documents:
                chunks, filename, *_ = doc
                destination = open(filename, mode='wb+')
                for chunk in chunks:
                    destination.write(chunk)

                destination.close()
                break
            
            filename = self.__convert_file(filename)
            if_file_exists_in_bucket_response = await self.__if_file_exists_in_bucket(filename)
            if if_file_exists_in_bucket_response.get('status', 'error') == 'error':
                remove(filename)
                raise Exception(
                    if_file_exists_in_bucket_response.get('err_description', '')
                )
            
            target_filename = if_file_exists_in_bucket_response.get('filename', filename)
            path = f'news/{target_filename}'
            s3_bucket.upload_file(
                filename,
                path,
                ExtraArgs={
                    'ContentType': 'application/pdf',
                    'ACL':'public-read'
                },
            )
    
            link = f'https://{self.aws_bucket_name}.s3.us-east-1.amazonaws.com/{path}'
            response_json['documents'].append(
                {
                    'filename': target_filename,
                    'link': link
                }
            )

            remove(filename)
            response_json['status'] = 'success'

        except (Exception, ) as e:
            response_json['err_description'] = str(e)

        finally:
            return response_json
        
    async def __saving_to_db(self, title: str, document_list: list) -> dict:
        response_json = deepcopy(self.response_json)
        db = self.db

        try:
            if not db:
                raise Exception('Не вдалося з\'єднатися с БД.')

            document, *_ = document_list
            filename, link = document.get('filename', ''), document.get('link', '')
            news_id = str(uuid4())

            new_row = NewsModel(
                news_id=news_id,
                title=title,
                filename=filename,
                link=link
            )

            db.add(new_row)
            db.commit()

            response_json['status'] = 'success'

        except (Exception, ) as e:
            if db:
                db.rollback()
            response_json['err_description'] = str(e)

        finally:
            return response_json
        
    async def __if_news_exists(self, news_id: str) -> dict:
        response_json = deepcopy(self.response_json)

        try:
            db = self.db

            if not db:
                raise Exception('Не вдалося з\'єднатися с БД.')

            stmt = select(NewsModel).where(NewsModel.news_id == news_id)
            row = db.scalars(statement=stmt).first()
            if not row:
                raise Exception(f'Новини з таким ID ({news_id}) не знайдено.')
            
            response_json['row'] = (row.title, row.filename, row.link)
            response_json['status'] = 'success'

        except (Exception, ) as e:
            response_json['err_description'] = str(e)

        finally:
            return response_json
        
    async def __drop_from_bucket(self, filename: str = '') -> None:
        try:
            s3_bucket = self.s3_bucket
            if not s3_bucket:
                raise Exception('Неможливо підключитися до ресурсу для видалення файлу.')
            
            filenames = []
            if not filename:
                get_objects_from_bucket_response = await self.__get_objects_from_bucket()
                if get_objects_from_bucket_response.get('status', 'error') == 'error':
                    raise Exception(
                        get_objects_from_bucket_response.get('err_description', '')
                    )
                print(get_objects_from_bucket_response)
                filenames = get_objects_from_bucket_response.get('filenames', [])
            else:
                filenames.append(f'news/{filename}')
            
            for filename in filenames:
                s3_bucket.delete_objects(
                    Delete={
                        'Objects': [
                            {
                                'Key': filename,
                            },
                        ],
                    }
                )

        except (Exception, ) as e:
            logger.error(f'Не вдале видалення старого файлу з S3. Опис помилки: \'{str(e)}\'')
        
    async def __updating_in_db(self, news_id: str, title: str, document_list: list) -> dict:
        response_json = deepcopy(self.response_json)
        db = self.db

        try:
            if not db:
                raise Exception('Не вдалося з\'єднатися с БД.')

            filename, link = '', ''
            if document_list:
                document, *_ = document_list
                filename, link = document.get('filename', ''), document.get('link', '')

            if_news_exists_response = await self.__if_news_exists(news_id)
            if if_news_exists_response.get('status', 'error') == 'error':
                raise Exception(
                    if_news_exists_response.get('err_description', '')
                )

            row = if_news_exists_response.get('row', ())
            if not row:
                raise Exception(f'Новини з таким ID ({news_id}) не знайдено.')

            prev_title, prev_filename, prev_link, *_ = row

            if prev_filename != filename and filename:
                await self.__drop_from_bucket(prev_filename)

            for_updating = {
                'title': title if title else prev_title,
                'filename': filename if filename else prev_filename,
                'link': link if link else prev_link
            }

            db.query(NewsModel).filter(NewsModel.news_id == news_id).update(for_updating)
            db.commit()

            response_json['status'] = 'success'

        except (Exception, ) as e:
            if db:
                db.rollback()
            response_json['err_description'] = str(e)

        finally:
            return response_json
        
    async def __deleting_from_db(self, news_id: str = '', action: str ='delete') -> dict:
        response_json = deepcopy(self.response_json)
        db = self.db

        try:
            if not db:
                raise Exception('Не вдалося з\'єднатися с БД.')

            if action == 'delete_all':
                await self.__drop_from_bucket()
                db.query(NewsModel).delete()

            else:
                if_news_exists_response = await self.__if_news_exists(news_id)
                if if_news_exists_response.get('status', 'error') == 'error':
                    raise Exception(
                        if_news_exists_response.get('err_description', '')
                    )
                
                row =  if_news_exists_response.get('row')
                if row:
                    _, filename, *_ = row
                    await self.__drop_from_bucket(filename)

                stmt = delete(NewsModel).where(NewsModel.news_id == news_id)

                db.execute(stmt)

            db.commit()
            
            response_json['status'] = 'success'

        except (Exception, ) as e:
            if db:
                db.rollback()
            response_json['err_description'] = str(e)

        finally:
            return response_json

    async def __select_news(self, page: int = 1) -> dict:
        response_json = deepcopy(self.response_json)

        try:
            db = self.db
            if not db:
                raise Exception('Не вдалося з\'єднатися с БД.')
            
            stmt = select(NewsModel)
            if page:
                per_page = 12
                offset = (page - 1) * per_page 
                stmt.offset(offset).limit(per_page)
            
            news_list = []
            for row in db.scalars(stmt):
                news = row.to_json()
                news_list.append(
                    news
                )

            response_json['news'] = news_list
            response_json['status'] = 'success'

        except (Exception, ) as e:
            response_json['err_description'] = str(e)

        finally:
            return response_json

    async def _executing_process(self, title: str = '', documents: list = [], **kwargs) -> dict:
        response_json = deepcopy(self.response_json)

        try:
            document_list = []
            if documents:
                saving_to_bucket_response = await self.__saving_to_bucket(documents)
                if saving_to_bucket_response.get('status', 'error') == 'error':
                    raise Exception(
                        saving_to_bucket_response.get('err_description', '')
                    )
                
                document_list = saving_to_bucket_response.get('documents', [])
                if not document_list:
                    raise ValueError('Жодного файлу не було збережено.')

            news_id = kwargs.get('news_id', '')
            action = kwargs.get('action', '')

            if news_id or action:
                action_response = await self.__updating_in_db(news_id, title, document_list) if action == 'update' else await self.__deleting_from_db(news_id, action)
                if action_response.get('status', 'error') == 'error':
                    raise Exception(
                        action_response.get('err_description', '')
                    )
                
            elif document_list:
                saving_to_db_response = await self.__saving_to_db(title, document_list)
                if saving_to_db_response.get('status', 'error') == 'error':
                    raise Exception(
                        saving_to_db_response.get('err_description', '')
                    )
                
            else:
                raise Exception('Виконання запиту завершилося невдало.')

            response_json['status'] = 'success'

        except (ValueError, Exception, ) as e:
            response_json['err_description'] = str(e)

        finally:
            return response_json
    
    async def news(self, page: int = 1) -> dict:
        response_json = deepcopy(self.response_json)

        try:
            select_news_response = await self.__select_news(page) if page else await self.__select_news()
            if select_news_response.get('status', 'error') == 'error':
                raise Exception(
                    select_news_response.get('err_description', '')
                )
            
            news = select_news_response.get('news', [])

            response_json['items'] = news
            response_json['status'] = 'success'

        except (Exception, ) as e:
            response_json['err_description'] = str(e)

        finally:
            return response_json
    
    async def add_news(self, data) -> dict:
        response_json = deepcopy(self.response_json)

        try:
            title = data.get('title', '')
            documents = [(f.chunks(), f.name) for f in data.get('documents', []) if f.name.endswith(('.doc', '.docx'))]

            if not title:
                raise ValueError('Не вказано заголовок для новини.')
            
            if not documents:
                raise ValueError('Жодного файлу з розширенням \'.doc\' або \'.docx\' не було завантажено.')

            executing_process_response = await self._executing_process(title, documents)
            if executing_process_response.get('status', 'error') == 'error':
                raise Exception(
                    executing_process_response.get('err_description', '')
                )

            response_json['status'] = 'success'

        except (ValueError, Exception, ) as e:
            response_json['err_description'] = str(e)

        finally:
            return response_json
 
    async def update_news(self, data: dict) -> dict:
        response_json = deepcopy(self.response_json)

        try:
            news_id, title = data.get('news_id', ''), data.get('title', '')
            if not news_id:
                raise ValueError('Не вказано ID новини.')

            documents = [(f.chunks(), f.name) for f in data.get('documents', []) if f.name.endswith(('.doc', '.docx'))]

            executing_process_response = await self._executing_process(
                title, 
                documents,
                news_id=news_id,
                action='update'
            )

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
                news_id=news_id,
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
        if self.db:
            self.db.close()

        if self.s3_client:
            self.s3_client.close()