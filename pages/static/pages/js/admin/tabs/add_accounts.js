import { edit_button_state } from '../../app.js';
import { _add_accounts } from '../../requests.js';

const SUBMIT = $('.add-accounts-submit');
const SUBMIT_TEXT = SUBMIT.text()
SUBMIT.off('click').on('click', async (e) => {
    e.preventDefault();

    const FORM = $('.add-accounts-form');
    const LOCALITY = FORM.find('.locality');
    const DOCUMENT = FORM.find('.document');

    const locality_value = LOCALITY.val();
    const document_files = DOCUMENT[0].files;

    if (!['Зарічне', 'Черкаське'].includes(locality_value) || document_files.length === 0) {
        return;
    }

    const document_value = document_files[0];

    edit_button_state(SUBMIT);
    await _add_accounts(locality_value, document_value);
    edit_button_state(SUBMIT, false, SUBMIT_TEXT);
})