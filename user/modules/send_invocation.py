from .base import Base
from copy import deepcopy
from ..tasks import send_message_to_mail

class SendInvocation(Base):
    def __init__(self):
        super().__init__()

    async def __aenter__(self):
        return self 
    
    async def send_invocation(self, data: dict) -> dict:
        response_json = deepcopy(self.response_json)

        try:
            data = (
                data.get('fullname', ''),
                data.get('phone', ''),
                data.get('messanger', ''),
                data.get('text', ''),
            )

            if not all(data):
                raise ValueError('Некоректно заповнена форма.')

            send_message_to_mail.apply_async(
                data,
                {'action': 'invocation'},
                queue='high_priority'
            )
            response_json['status'] = 'success'

        except (ValueError, Exception, ) as e:
            response_json['err_description'] = str(e)

        finally:
            return response_json
    
    async def __aexit__(self, *args, **kwargs):
        pass