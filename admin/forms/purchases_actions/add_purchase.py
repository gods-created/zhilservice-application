from django.forms import Form, CharField, FileField

class AddPurchase(Form):
    short_description = CharField(min_length=1, label='Короткий опис змісту файла')
    file = FileField(label='Файл з даними щодо закупівлі')

    def to_json(self):
        return {
            'short_description': self.cleaned_data['short_description'],
            'file': self.cleaned_data['file']
        }