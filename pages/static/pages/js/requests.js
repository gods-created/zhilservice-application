import { HREF, BASE_URL, CLOSE_MODAL_BUTTON, edit_button_state, show_alert } from './app.js';

const HEADERS = { 
    'Content-Type': 'multipart/form-data' 
};

export function _account() {
    const GET_INFO_BUTTON = $('.get-info-button');
    const GET_INFO_BUTTON_TEXT = GET_INFO_BUTTON.text();

    GET_INFO_BUTTON.off('click').on('click', async (e) => {
        e.preventDefault();

        const FORM = $('#get-account-info');
        const EMAIL_INPUT = FORM.find('.email');
        const CURRENT_ACCOUNT_NUMBER = FORM.find('.current-account-number');
        const LOCALITY = FORM.find('.locality');

        const email_value = EMAIL_INPUT.val()?.trim();
        const current_account_number = CURRENT_ACCOUNT_NUMBER.val();
        const locality = LOCALITY.val();
        if (
            validator.isEmail(email_value) &&
            Number(current_account_number) > 0 &&
            ['Зарічне', 'Черкаське'].includes(locality)
        ) {
            edit_button_state(GET_INFO_BUTTON);

            let status, description;

            try {
                const formData = new FormData();
                formData.append('email', email_value);
                formData.append('current_account_number', current_account_number);
                formData.append('locality', locality);

                const request = await axios.post(`${BASE_URL}/api/user/account`, formData, { HEADERS });
                const response = request.data;

                status = response.status;
                description = status === 'error' ? response.err_description : 'Повідомлення відправлено на Вашу пошту!';

                // console.log(response);
            } catch (err) {
                status = 'error';
                description = err.message;
            }

            edit_button_state(GET_INFO_BUTTON, false, GET_INFO_BUTTON_TEXT);

            CLOSE_MODAL_BUTTON.click();
            show_alert(status, description);
        } 

        return;
    });
}

export function _auth_admin() {
    const ADMIN_AUTH_BUTTON = $('.admin-auth-button');
    const ADMIN_AUTH_BUTTON_TEXT = ADMIN_AUTH_BUTTON.text();

    ADMIN_AUTH_BUTTON.off('click').on('click', async (e) => {
        e.preventDefault();

        const EMAIL_INPUT = $('#admin-email');
        const PASSWORD_INPUT = $('#admin-password');
        const SECRET_KEY_INPUT = $('#app-secret-key');
        const REMEMBER_CHECKED = $('#flex-check-default');

        const email_value = EMAIL_INPUT.val()?.trim();
        const password_value = PASSWORD_INPUT.val()?.trim();
        const secret_key_value = SECRET_KEY_INPUT.val()?.trim();
        
        if (
            validator.isEmail(email_value) &&
            password_value.length >= 8
        ) {
            edit_button_state(ADMIN_AUTH_BUTTON);
            let status, err_description, response_data;
            const data = JSON.stringify({
                'email': email_value,
                'password': password_value
            })

            const jwt = KJUR.jws.JWS.sign(null, { alg: 'HS256', typ: 'JWT' }, data, secret_key_value);
            
            try {
                const formData = new FormData();
                formData.append('jwt', jwt);

                const request = await axios.post(`${BASE_URL}/api/admin/auth`, formData, { HEADERS });
                const response = request.data;

                status = response.status;
                err_description = response.err_description;
                response_data = response.data;

                console.log(response);
            } catch (err) {
                status = 'error';
                err_description = err.message;
            }

            if (status == 'success') {
                let session_token = response_data.session_token; 
                Cookies.set('session_token', session_token);

                if (REMEMBER_CHECKED.is(':checked')) {
                    Cookies.set('email', email_value);
                    Cookies.set('password', password_value);
                }

                return window.location.reload();
            }

            edit_button_state(ADMIN_AUTH_BUTTON, false, ADMIN_AUTH_BUTTON_TEXT)
            show_alert(status, err_description);
            return;
        } 

        return;
    })
}

export async function _add_accounts(locality, document) {
    let status, description;
    
    try {
        const formData = new FormData();
        formData.append('locality', locality);
        formData.append('documents', document);

        const request = await axios.post(`${BASE_URL}/api/admin/add_accounts`, formData, { HEADERS });
        const response = request.data;

        status = response.status;
        const err_description = response.err_description;

        description = status !== 'success' ? err_description : 'Файл успішно завантажено!';
    } catch (err) {
        status = 'error';
        description = err.message;
    }

    show_alert(status, description);
    return;
}

export async function _delete_news(news_id) {
    let status, description;
    
    try {
        const formData = new FormData();
        formData.append('news_id', news_id);

        const request = await axios.post(`${BASE_URL}/api/admin/delete_news`, formData, { HEADERS });
        const response = request.data;

        status = response.status;
        const err_description = response.err_description;

        description = status !== 'success' ? err_description : 'Новину успішно видалено!';
    } catch (err) {
        status = 'error';
        description = err.message;
    }

    if (status === 'success') {
        window.location.href = HREF;
        return;
    }

    return show_alert(status, description);
}

export async function _add_news(title, image, news_description) {
    let status, description;
    
    try {
        const formData = new FormData();
        formData.append('title', title);
        formData.append('description', news_description);
        formData.append('image', image);

        const request = await axios.post(`${BASE_URL}/api/admin/add_news`, formData, { HEADERS });
        const response = request.data;

        status = response.status;
        const err_description = response.err_description;

        description = status !== 'success' ? err_description : 'Новина успішно завантажена!';
    } catch (err) {
        status = 'error';
        description = err.message;
    }

    if (status === 'success') {
        window.location.href = HREF;
        return;
    }

    return show_alert(status, description);
}

export async function _add_vacancy(title, vacancy_description) {
    let status, description;
    
    try {
        const formData = new FormData();
        formData.append('title', title);
        formData.append('description', vacancy_description);

        const request = await axios.post(`${BASE_URL}/api/admin/add_vacancy`, formData, { HEADERS });
        const response = request.data;

        status = response.status;
        const err_description = response.err_description;

        description = status !== 'success' ? err_description : 'Вакансія успішно завантажена!';
    } catch (err) {
        status = 'error';
        description = err.message;
    }

    if (status === 'success') {
        window.location.href = HREF;
        return;
    }

    return show_alert(status, description);
}

export async function _delete_vacancy(vacancy_id) {
    let status, description;
    
    try {
        const formData = new FormData();
        formData.append('vacancy_id', vacancy_id);

        const request = await axios.post(`${BASE_URL}/api/admin/delete_vacancy`, formData, { HEADERS });
        const response = request.data;

        status = response.status;
        const err_description = response.err_description;

        description = status !== 'success' ? err_description : 'Вакансію успішно видалено!';
    } catch (err) {
        status = 'error';
        description = err.message;
    }

    if (status === 'success') {
        window.location.href = HREF;
        return;
    }

    return show_alert(status, description);
}

export async function _add_purchase(short_description, file) {
    let status, description;
    
    try {
        const formData = new FormData();
        formData.append('short_description', short_description);
        formData.append('file', file);

        const request = await axios.post(`${BASE_URL}/api/admin/add_purchase`, formData, { HEADERS });
        const response = request.data;

        status = response.status;
        const err_description = response.err_description;

        description = status !== 'success' ? err_description : 'Закупівля успішно завантажена!';
    } catch (err) {
        status = 'error';
        description = err.message;
    }

    if (status === 'success') {
        window.location.href = HREF;
        return;
    }

    return show_alert(status, description);
}

export async function _delete_purchase(purchases_id) {
    let status, description;
    
    try {
        const formData = new FormData();
        formData.append('purchases_id', purchases_id);

        const request = await axios.post(`${BASE_URL}/api/admin/delete_purchase`, formData, { HEADERS });
        const response = request.data;

        status = response.status;
        const err_description = response.err_description;

        description = status !== 'success' ? err_description : 'Закупівлю успішно видалено!';
    } catch (err) {
        status = 'error';
        description = err.message;
    }

    if (status === 'success') {
        window.location.href = HREF;
        return;
    }

    return show_alert(status, description);
}