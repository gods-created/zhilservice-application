from .singleton import Singleton
from abc import ABC, abstractmethod
from string import ascii_letters, digits
from random import choice
from os import getenv

class CompareClass(Singleton, ABC):
    pass

class Base(CompareClass):
    def __init__(self):
        self.response_json = {
            'status': 'error',
            'err_description': ''
        }
        self.aws_bucket_name = getenv('AWS_BUCKET_NAME')

    def _generate_string(self) -> str:
        return ''.join(choice(ascii_letters + digits) for _ in range(15)) 

    @abstractmethod
    async def _executing_process(self) -> dict:
        pass