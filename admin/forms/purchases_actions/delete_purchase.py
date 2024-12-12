from django.forms import Form, IntegerField

class DeletePurchase(Form):
    purchases_id = IntegerField(min_value=1, label='ID закупівлі')


    def to_json(self):
        return {
            'purchases_id': self.cleaned_data['purchases_id'],
        }