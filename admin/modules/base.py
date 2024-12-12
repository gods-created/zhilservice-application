from .singleton import Singleton
from abc import ABC, abstractmethod
from string import ascii_letters, digits
from random import choice
from os import getenv
from boto3 import client, resource
from copy import deepcopy

class CompareClass(Singleton, ABC):
    pass

class Base(CompareClass):
    def __init__(self):
        self.response_json = {
            'status': 'error',
            'err_description': ''
        }
        self.s3_client = None
        self.s3_client = None
        self.aws_bucket_name = None

    def __enter__(self):
        aws_access_key_id = getenv('AWS_ACCESS_KEY_ID')
        aws_secret_access_key = getenv('AWS_SECRET_ACCESS_KEY')
        aws_bucket_name = getenv('AWS_BUCKET_NAME')
        if all((aws_access_key_id, aws_secret_access_key, aws_bucket_name)):
            self.aws_bucket_name = aws_bucket_name

            self.s3_client = client(
                's3',
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                region_name='us-east-1'
            )

            self.s3_bucket = resource(
                's3',
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                region_name='us-east-1'
            ).Bucket(aws_bucket_name)

        return self

    def _generate_string(self) -> str:
        return ''.join(choice(ascii_letters + digits) for _ in range(15)) 

    def _delete_from_s3(self, dir: str = 'news', filename: str = None) -> dict:
        response_json = deepcopy(self.response_json)

        try:
            s3_client = self.s3_client
            if not s3_client:
                raise Exception('Не вдалося виконати видалення через відсутнє з\'єднання з S3.')

            bucket_name = self.aws_bucket_name
            list_objects = s3_client.list_objects(
                Bucket=bucket_name,
                Prefix=f'{dir}/'
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

    @abstractmethod
    async def _executing_process(self) -> dict:
        pass