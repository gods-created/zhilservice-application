from django.forms import Form, CharField, FileField

class AddNews(Form):
    title = CharField(label='Заголовок для новини')
    description = CharField(label='Опис новини')
    image = FileField(label='Титульне зображення')

    def to_json(self):
        return {
            'title': self.cleaned_data['title'],
            'description': self.cleaned_data['description'],
            'image': self.cleaned_data['image']
        }