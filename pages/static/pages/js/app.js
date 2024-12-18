import { _account } from './requests.js';

export const BASE_URL = `${window.location.protocol}//${window.location.host}`;
export const PATHNAME = window.location.pathname;
export const HREF = window.location.href;

export const CLOSE_MODAL_BUTTON = $('.btn-close');

const OPEN_DEBT_MODAL_BUTTON = $('.open-debt-modal');
const MORE_INFO_BUTTON = $('.more-info-button');
const DESCRIPTION_ITEMS = $('.description-item');

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

function correct_phone_input() {
    const FORM = $('.send-invocation-form');
    if (FORM === null) {
        return;
    };

    const PHONE_INPUT = FORM.find('.phone');
    PHONE_INPUT.on('input', function () {
        let phone_value = $(this).val().replace(/(?!^)\+|[^\d+]/g, '');

        if (phone_value.length < 4) {
            phone_value = '+380';
        }

        if (phone_value.length > 13) {
            phone_value = phone_value.slice(0, 13)
        }

        $(this).val(
            phone_value
        );
    })
}

function edit_description_items() {
    if (DESCRIPTION_ITEMS.length > 0) {
        DESCRIPTION_ITEMS.each(function(index, elem) {
            const content = $(elem).text();
            $(elem).empty();
            $(elem).html(
                content
            )
        })
    }
}

function make_news_image_bigger() {
    function window_builder(link) {
        if (!link) return;

        const mainDiv = document.createElement('div');
        mainDiv.classList.add('modal', 'd-block', 'news-image-bigger');
        mainDiv.addEventListener('click', (e) => {
            const target = e.currentTarget;
            target.remove();
        })

        const dialogBlock = document.createElement('div');
        dialogBlock.classList.add('modal-dialog', 'modal-dialog-centered', 'modal-dialog-scrollable');

        const contentBlock = document.createElement('div');
        contentBlock.classList.add('modal-content');

        const bodyBlock = document.createElement('div');
        bodyBlock.classList.add('modal-body');

        const imageBlock = document.createElement('img');
        imageBlock.src = link;
        imageBlock.classList.add('img-fluid');
        
        bodyBlock.appendChild(imageBlock);
        contentBlock.appendChild(bodyBlock);
        dialogBlock.appendChild(contentBlock);
        mainDiv.appendChild(dialogBlock);

        document.body.appendChild(mainDiv);
    }

    const blocks = $('.news-image');
    if (blocks.length > 0) {
        blocks.off('click').on('click', (e) => {
            const target = e.currentTarget;
            const link = $(target).attr('src');
            window_builder(link)
        })
    }
}

$(document).ready(async () => {
    load_current_year();
    underline_active_tab();
    correct_phone_input();
    edit_description_items();
    make_news_image_bigger();

    OPEN_DEBT_MODAL_BUTTON.off('click').on('click', () => {
        open_debt_modal();
    });

    MORE_INFO_BUTTON.off('click').on('click', function (e) {
        e.preventDefault();
        
        const parent = $(this).parent().parent();
        const description_item = parent.find('span.description-item');

        if (description_item.hasClass('d-block')) {
            description_item.addClass('d-none').removeClass('d-block');
            $(this).text('Детальніше');
        } else {
            description_item.addClass('d-block').removeClass('d-none');
            $(this).text('Заховати');
        }

        return;
    });
})