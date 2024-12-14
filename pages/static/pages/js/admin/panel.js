import { HREF, logout } from '../app.js';

const LOGOUT_BTN = $('.logout');
const TEXTAREA_CLASS = 'div.description.editor';
export var QUILL = null;

function underline_active_tab() {
    let add_accounts_block = $('.add-accounts-block');
    let news_actions_block = $('.news-actions-block');
    let vacancies_actions_block = $('.vacancies-actions-block');
    let purchases_actions_block = $('.purchases-actions-block');

    let target_link;

    if (HREF.includes('tab=news_actions')) {
        target_link = news_actions_block;
    } else if (HREF.includes('tab=vacancies_actions')) {
        target_link = vacancies_actions_block;
    } else if (HREF.includes('tab=purchases_actions')) {
        target_link = purchases_actions_block;
    } else {
        target_link = add_accounts_block;
    }

    target_link.each(function () {
        let text = $(this).text();
        $(this).text('');
        
        $(this).append(`
            <span class="text-decoration-underline">
                ${text}
            </span> 
        `)
    });

    return;
}

$(document).ready(async () => {
    underline_active_tab();
    LOGOUT_BTN.off('click').on('click', () => {
        return logout();
    })

    if ($(TEXTAREA_CLASS).length !== 0) {
        QUILL = new Quill(TEXTAREA_CLASS, {
            theme: 'snow'
        });
    }
})