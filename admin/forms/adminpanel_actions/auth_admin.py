from django.forms import Form, CharField

class AuthAdmin(Form):
    jwt = CharField(label='JWT')

    def to_json(self):
        return {
            'jwt': self.cleaned_data['jwt']
        }