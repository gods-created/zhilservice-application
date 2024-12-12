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
    const IMAGE = FORM.find('.image');
    const DESCRIPTION = FORM.find('.ql-editor');
    
    const title_value = TITLE.val()?.trim();
    const image_files = IMAGE[0].files;
    const description_value = DESCRIPTION.html();

    if (
        title_value.length === 0 || image_files.length !== 1 || $(description_value).text()?.trim().length === 0
    ) {
        return;
    }

    edit_button_state(ADD_NEWS_SUBMIT);
    await _add_news(title_value, image_files[0], description_value);
    edit_button_state(ADD_NEWS_SUBMIT, false, ADD_NEWS_SUBMIT_TEXT);
})
