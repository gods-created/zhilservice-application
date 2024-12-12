import { edit_button_state } from '../../app.js';
import { _add_vacancy, _delete_vacancy } from '../../requests.js';

const ADD_VACANCY_SUBMIT = $('.add-vacancy-submit');
const ADD_VACANCY_SUBMIT_TEXT = ADD_VACANCY_SUBMIT.text();

const DELETE_VACANCY_SUBMIT = $('.delete-vacancy-submit');

ADD_VACANCY_SUBMIT.off('click').on('click', async (e) => {
    e.preventDefault();

    const FORM = $('.add-vacancy-form');
    const TITLE = FORM.find('.title');
    const DESCRIPTION = FORM.find('.ql-editor');

    const title_value = TITLE.val()?.trim();
    const description_value = DESCRIPTION.html();
    
    if (
        title_value.length === 0 || $(description_value).text()?.trim().length === 0
    ) {
        return;
    }

    edit_button_state(ADD_VACANCY_SUBMIT);
    await _add_vacancy(title_value, description_value);
    edit_button_state(ADD_VACANCY_SUBMIT, false, ADD_VACANCY_SUBMIT_TEXT);
    return;
})

DELETE_VACANCY_SUBMIT.off('click').on('click', async (e) => {
    e.preventDefault();

    const vacancy_id = $(e.currentTarget).attr('vacancy_id');
    await _delete_vacancy(vacancy_id)
})