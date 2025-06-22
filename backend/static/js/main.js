// backend/static/js/main.js

document.addEventListener('DOMContentLoaded', function() {
    console.log('Main JavaScript untuk aplikasi Kominfo Magang telah dimuat!');

    // --- Fungsi Toggle Password Visibility (lebih umum) ---
    function setupPasswordToggle(passwordFieldId, toggleButtonId) {
        const passwordField = document.getElementById(passwordFieldId);
        const toggleButton = document.getElementById(toggleButtonId);

        if (passwordField && toggleButton) {
            console.log(`Setting up toggle for field: ${passwordFieldId} with button: ${toggleButtonId}`); // Debugging
            toggleButton.addEventListener('click', function () {
                console.log(`Toggle button clicked for: ${passwordFieldId}`); // Debugging
                const type = passwordField.getAttribute('type');
                if (type === 'password') {
                    passwordField.setAttribute('type', 'text');
                    this.querySelector('i').classList.remove('bi-eye');
                    this.querySelector('i').classList.add('bi-eye-slash');
                } else {
                    passwordField.setAttribute('type', 'password');
                    this.querySelector('i').classList.remove('bi-eye-slash');
                    this.querySelector('i').classList.add('bi-eye');
                }
            });
        } else {
            console.warn(`Elements not found for password toggle: Field ID '${passwordFieldId}', Button ID '${toggleButtonId}'`); // Debugging
        }
    }

    // Panggil fungsi toggle untuk field password di halaman register
    // ID di register: password (input), togglePassword (button)
    //         confirm_password (input), toggleConfirmPassword (button)
    setupPasswordToggle('password', 'togglePassword'); // Register Password
    setupPasswordToggle('confirm_password', 'toggleConfirmPassword'); // Register Confirm Password

    // Panggil fungsi toggle untuk field password di halaman login
    // ID di login: loginPassword (input), toggleLoginPassword (button)
    setupPasswordToggle('loginPassword', 'toggleLoginPassword'); // <--- UBAH DI SINI


    // --- Validasi Register Form (hanya jika elemen register form ada di halaman) ---
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        // Karena ID password di register dan login berbeda, kita bisa langsung merujuk ke elemen register
        const passwordInputRegister = document.getElementById('password');
        const confirmPasswordInputRegister = document.getElementById('confirm_password');
        const passwordErrorDiv = document.getElementById('passwordError');
        const confirmPasswordErrorDiv = document.getElementById('confirmPasswordError');

        function validatePasswordRegister() {
            const password = passwordInputRegister.value;
            const messages = [];

            if (password.length < 10) {
                messages.push('Kata sandi minimal 10 karakter.');
            }

            const specialCharRegex = /[!@#$%^&*()_+{}\[\]:;"'<>,.?/~`]/;
            if (!specialCharRegex.test(password)) {
                messages.push('Harus mengandung setidaknya satu karakter khusus (contoh: @, #, $).');
            }

            const numberRegex = /\d/;
            if (!numberRegex.test(password)) {
                messages.push('Harus mengandung setidaknya satu angka.');
            }
            
            if (messages.length > 0) {
                passwordInputRegister.classList.add('is-invalid');
                passwordInputRegister.classList.remove('is-valid');
                passwordErrorDiv.innerHTML = messages.join('<br>');
                return false;
            } else {
                passwordInputRegister.classList.remove('is-invalid');
                passwordInputRegister.classList.add('is-valid');
                passwordErrorDiv.innerHTML = '';
                return true;
            }
        }

        function validateConfirmPasswordRegister() {
            const password = passwordInputRegister.value;
            const confirmPassword = confirmPasswordInputRegister.value;

            if (password !== confirmPassword) {
                confirmPasswordInputRegister.classList.add('is-invalid');
                confirmPasswordInputRegister.classList.remove('is-valid');
                confirmPasswordErrorDiv.textContent = 'Konfirmasi kata sandi tidak cocok!';
                return false;
            } else {
                confirmPasswordInputRegister.classList.remove('is-invalid');
                confirmPasswordInputRegister.classList.add('is-valid');
                confirmPasswordErrorDiv.textContent = '';
                return true;
            }
        }

        if (passwordInputRegister && confirmPasswordInputRegister) {
            passwordInputRegister.addEventListener('input', function() {
                validatePasswordRegister();
                validateConfirmPasswordRegister();
            });

            confirmPasswordInputRegister.addEventListener('input', validateConfirmPasswordRegister);
        }

        registerForm.addEventListener('submit', function(event) {
            const isPasswordValid = validatePasswordRegister();
            const isConfirmPasswordValid = validateConfirmPasswordRegister();

            if (!isPasswordValid || !isConfirmPasswordValid) {
                event.preventDefault();
            }
        });
    }


    // Untuk menyembunyikan flash message setelah beberapa detik
    const flashMessages = document.querySelectorAll('.alert');
    flashMessages.forEach(message => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(message);
            bsAlert.close();
        }, 5000);
    });
});