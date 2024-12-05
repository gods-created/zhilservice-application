from django.forms import Form, ChoiceField
from ..multiple_file_field import MultipleFileField
from zhilservice.enums import Localities

class AddAccounts(Form):
    locality = ChoiceField(
        label='Населений пункт',
        choices=[(loc.value, loc.value) for loc in Localities]
    )
    documents = MultipleFileField()


    def to_json(self):
        return {
            'locality': self.cleaned_data['locality'],
            'documents': self.cleaned_data['documents']
        }