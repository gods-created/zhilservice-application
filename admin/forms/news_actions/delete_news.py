from django.forms import Form, CharField

class DeleteNews(Form):
    news_id = CharField(label='ID новини')

    def to_json(self):
        return {
            'news_id': self.cleaned_data['news_id'],
        }