from django.forms import Form, IntegerField

class DeleteVacancy(Form):
    vacancy_id = IntegerField(label='ID вакансії в БД')

    def to_json(self):
        return {
            'vacancy_id': self.cleaned_data['vacancy_id'],
        }