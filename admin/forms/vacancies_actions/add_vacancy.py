from django.forms import Form, CharField

class AddVacancy(Form):
    title = CharField(label='Назва посади')
    description = CharField(label='Опис посади')

    def to_json(self):
        return {
            'title': self.cleaned_data['title'],
            'description': self.cleaned_data['description']
        }