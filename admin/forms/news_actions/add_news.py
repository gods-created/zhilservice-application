from django.forms import Form, CharField
from ..multiple_file_field import MultipleFileField

class AddNews(Form):
    title = CharField(label='Заголовок для статті')
    documents = MultipleFileField()

    def to_json(self):
        return {
            'title': self.cleaned_data['title'],
            'documents': self.cleaned_data['documents']
        }