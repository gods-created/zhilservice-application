from celery import Celery
from typing import Any
from django.core.mail import send_mail
from os import environ
from loguru import logger

environ.setdefault('DJANGO_SETTINGS_MODULE', 'zhilservice.settings')

app = Celery('send_message_to_mail', broker='redis://localhost:6379')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.task_queues = {
    'high_priority': {
        'exchange': 'high_priority',
        'routing_key': 'high.#'
    }
}
app.autodiscover_tasks()

@app.task
def send_message_to_mail(current_account_number: str, email: str, data: list) -> Any:
    try:
        if len(data) == 4:
            data = list(map(lambda x: '0' if len(str(x).replace(' ', '')) == 0 else x, data))
            total, trash, flat, warming = data
        else:
            total = trash = flat = warming = '0'

        message = f'<h3>Обов\'язкові платежі по рахунку №{current_account_number}:</h3>' \
                f'<p style="margin:0px;">вивіз сміття: <span style="font-weight:bold;">{trash} грн.</span></p>' \
                f'<p style="margin:0px;">квартплата: <span style="font-weight:bold;">{flat} грн.</span></p>' \
                f'<p style="margin:0px;">теплопостачання: <span style="font-weight:bold;">{warming} грн.</span></p>' \
                f'<p style="margin:0px;">всього: <span style="font-weight:bold;">{total} грн.</span></p><br />' \
                f'<p style="margin:0px;">Дякуюємо, що Ви за нами і гарного дня! З повагою, КП "Жилсервіс".' 
        
        subject = 'Повідомлення від КП "Жилсервіс"'

        send_mail(
            subject=subject,
            message=message,
            from_email='tersk.bo@gmail.com',
            recipient_list=[email],
            html_message=message,
            fail_silently=False
        )

    except (ValueError, Exception, ) as e:
        logger.error(str(e))

    finally:
        return None