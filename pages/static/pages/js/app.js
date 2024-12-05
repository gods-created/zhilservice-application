import { _account } from './requests.js';

export const BASE_URL = `${window.location.protocol}//${window.location.host}`;
export const PATHNAME = window.location.pathname;
export const HREF = window.location.href;

export const CLOSE_MODAL_BUTTON = $('.btn-close');

export function edit_button_state(obj, state=true, text='...') {
    obj.prop('disabled', state);
    obj.text(text);
}

export function show_alert(status='error', text='') {
    const alert_modal = $('.alert-modal');
    const alert_title = $('.alert-title');
    const alert_text = $('.alert-text');

    const title = status === 'error' ? 'Невдача!' : 'Успішно!';

    alert_title.text(title)
    alert_text.text(text)
    alert_modal.removeClass('d-none').addClass('d-block');
    
    close_modals();
    
    return;
}

export function logout() {
    Cookies.remove('session_token');
    return window.location.reload();
}

function load_current_year() {
    let span = $('.current-year');
    let year = new Date().getFullYear();
    span.text(year);
    return;
}

function underline_active_tab() {
    let news_link = $('.news');
    let purchases_link = $('.purchases');
    let vacancies_link = $('.vacancies');
    let contacts_link = $('.contacts');

    let target_link;

    if (PATHNAME.includes('purchases')) {
        target_link = purchases_link;
    } else if (PATHNAME.includes('vacancies')) {
        target_link = vacancies_link;
    } else if (PATHNAME.includes('contacts')) {
        target_link = contacts_link;
    } else if (PATHNAME.includes('news')) {
        target_link = news_link;
    } else {
        return;
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

function open_debt_modal() {
    const debt_modal = $('.debt-modal');
    debt_modal.removeClass('d-none').addClass('d-block');
    close_modals();
    _account();
    
    return;
}

function close_modals() {
    CLOSE_MODAL_BUTTON.off('click').on('click', () => {
        close_all_modals();
    });

    return;
}

function close_all_modals() {
    const modals = $('.modal');
    modals.each(function () {
        if ($(this).hasClass('d-block')) {
            $(this).removeClass('d-block').addClass('d-none');
        }
    })

    return;
}

$(document).ready(async () => {
    load_current_year();
    underline_active_tab();

    const OPEN_DEBT_MODAL_BUTTON = $('.open-debt-modal');

    OPEN_DEBT_MODAL_BUTTON.off('click').on('click', () => {
        open_debt_modal();
    });
})