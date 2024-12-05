import { _delete_news, _add_news } from '../../requests.js';
import { edit_button_state } from '../../app.js';

const DELETE_NEWS_SUBMIT = $('.delete-news-submit');

const ADD_NEWS_SUBMIT = $('.add-news-submit');
const ADD_NEWS_SUBMIT_TEXT = ADD_NEWS_SUBMIT.text();

DELETE_NEWS_SUBMIT.off('click').on('click', async (e) => {
    e.preventDefault();

    const news_id = $(e.currentTarget).attr('news_id');
    await _delete_news(news_id);
})

ADD_NEWS_SUBMIT.off('click').on('click', async (e) => {
    e.preventDefault();

    const FORM = $('.add-news-form');
    const TITLE = FORM.find('.title');
    const DOCUMENT = FORM.find('.document');
    
    const title_value = TITLE.val()?.trim();
    const document_files = DOCUMENT[0].files;

    if (title_value.length === 0 || document_files.length === 0) {
        return;
    }
    
    const document_value = document_files[0];

    edit_button_state(ADD_NEWS_SUBMIT);
    await _add_news(title_value, document_value);
    edit_button_state(ADD_NEWS_SUBMIT, false, ADD_NEWS_SUBMIT_TEXT);
})