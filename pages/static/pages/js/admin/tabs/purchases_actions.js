import { _delete_purchase, _add_purchase } from '../../requests.js';
import { edit_button_state } from '../../app.js';

const DELETE_PURCHASE_SUBMIT = $('.delete-purchase-submit');
const ADD_PURCHASE_SUBMIT = $('.add-purchase-form > div > .add-purchase-submit')
const ADD_PURCHASE_SUBMIT_TEXT = ADD_PURCHASE_SUBMIT.text();

function short_description_input_validator() {
    $('.add-purchase-form > div > .short_description').on('input', function() {
        const value = $(this).val()?.trim();
        if (value.length > 30) {
            $(this).val(
                value.slice(0, 30)
            )
        }
    })
}

DELETE_PURCHASE_SUBMIT.off('click').on('click', async (e) => {
    e.preventDefault();

    const purchase_id = $(e.currentTarget).attr('purchase_id');
    await _delete_purchase(purchase_id);
})

ADD_PURCHASE_SUBMIT.on('click', async (e) => {
    e.preventDefault();

    const FORM = $('.add-purchase-form');
    const SHORT_DESCRIPTION = FORM.find('.short_description');
    const FILE = FORM.find('.file')[0].files;

    const short_description_value = SHORT_DESCRIPTION.val()?.trim();
    const file_length = FILE.length;

    if (short_description_value.length === 0 || file_length === 0) {
        return;
    }

    const file_value = FILE[0];

    edit_button_state(ADD_PURCHASE_SUBMIT);
    await _add_purchase(short_description_value, file_value);
    edit_button_state(ADD_PURCHASE_SUBMIT, false, ADD_PURCHASE_SUBMIT_TEXT);
})

$(document).ready(() => {
    short_description_input_validator();
})