from django.forms import Form, EmailField, CharField, ChoiceField
from zhilservice.enums import Localities

class Get(Form):
    email = EmailField(label='Ваша пошта')
    current_account_number = CharField(label='Ваш розрахунковий рахунок')
    locality = ChoiceField(
        label='Ваш населений пункт',
        choices=[(loc.value, loc.value) for loc in Localities]
    )

    def to_json(self):
        return {
            'email': self.cleaned_data['email'],
            'current_account_number': self.cleaned_data['current_account_number'],
            'locality': self.cleaned_data['locality'],
        }