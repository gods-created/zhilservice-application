import { _auth_admin } from '../requests.js';
// import { _check_session }  from '../requests.js';

function form_completing() {
    const email = Cookies.get('email');
    const password = Cookies.get('password');
    const not_allowed = [null, undefined];
    
    const EMAIL_INPUT = $('#admin-email');
    const PASSWORD_INPUT = $('#admin-password');

    [email, password].forEach((value, index) => {
        if (!not_allowed.includes(value)) {
            if (index == 0) {
                EMAIL_INPUT.val(email);
            } else {
                PASSWORD_INPUT.val(password)
            }
        }
    })

    return;
}

$(document).ready(async () => {
    // await _check_session();
    _auth_admin();
    form_completing();
})