from django.forms import Form, CharField, ChoiceField, Select, TextInput, Textarea
from zhilservice.enums import Messangers

class SendInvocation(Form):
    fullname = CharField(
        label='Ваше повне ім\'я', 
        min_length=1, 
        required=True, 
        widget=TextInput(
            attrs={'class': 'form-control mb-3 fullname'}
        )
    )

    phone = CharField(label='Номер телефона', 
        min_length=13,
        max_length=13, 
        required=True, 
        widget=TextInput(
            attrs={'class': 'form-control mb-3 phone', 'value': '+380'}
        )
    )

    messanger = ChoiceField(
        label='Мессенджер для зв\'язку',
        choices=[(item.value, item.value) for item in Messangers],
        required=True,
        widget=Select(
            attrs={'class': 'form-select mb-3 messanger'}
        )
    )

    text = CharField(
        label='Опишіть причину звернення', 
        min_length=1, 
        required=True, 
        widget=Textarea(
            attrs={'class': 'form-control mb-3 text', 'rows': '7', 'cols': '10', 'style': 'resize:none;'}
        )
    )

    def to_json(self):
        return {
            'fullname': self.cleaned_data['fullname'],
            'phone': self.cleaned_data['phone'],
            'messanger': self.cleaned_data['messanger'],
            'text': self.cleaned_data['text']
        }