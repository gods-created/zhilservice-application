from django.forms import Form, CharField
from ..multiple_file_field import MultipleFileField

class UpdateNews(Form):
    news_id = CharField(label='ID новини')
    title = CharField(label='Новий заголовок', empty_value=True)
    documents = MultipleFileField()

    def to_json(self):
        return {
            'news_id': self.cleaned_data['news_id'],
            'title': self.cleaned_data['title'],
            'documents': self.cleaned_data['documents']
        }