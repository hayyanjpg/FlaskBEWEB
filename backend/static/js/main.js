// backend/static/js/main.js

document.addEventListener('DOMContentLoaded', function() {
    console.log('Main JavaScript untuk aplikasi Kominfo Magang telah dimuat!');

    const registerForm = document.getElementById('registerForm');
    const passwordInput = document.getElementById('password');
    const confirmPasswordInput = document.getElementById('confirm_password');
    const passwordErrorDiv = document.getElementById('passwordError');
    const confirmPasswordErrorDiv = document.getElementById('confirmPasswordError');

    // Fungsi validasi password
    function validatePassword() {
        const password = passwordInput.value;
        const messages = [];

        // Minimal 10 karakter
        if (password.length < 10) {
            messages.push('Kata sandi minimal 10 karakter.');
        }

        // Minimal 1 karakter khusus (contoh: @, #, $, %)
        const specialCharRegex = /[!@#$%^&*()_+{}\[\]:;"'<>,.?/~`]/;
        if (!specialCharRegex.test(password)) {
            messages.push('Harus mengandung setidaknya satu karakter khusus (contoh: @, #, $).');
        }

        // Minimal 1 angka
        const numberRegex = /\d/;
        if (!numberRegex.test(password)) {
            messages.push('Harus mengandung setidaknya satu angka.');
        }
        
        // Opsional: Minimal 1 huruf besar dan 1 huruf kecil
        // const upperCaseRegex = /[A-Z]/;
        // if (!upperCaseRegex.test(password)) {
        //     messages.push('Harus mengandung setidaknya satu huruf kapital.');
        // }
        // const lowerCaseRegex = /[a-z]/;
        // if (!lowerCaseRegex.test(password)) {
        //     messages.push('Harus mengandung setidaknya satu huruf kecil.');
        // }

        if (messages.length > 0) {
            passwordInput.classList.add('is-invalid');
            passwordInput.classList.remove('is-valid');
            passwordErrorDiv.innerHTML = messages.join('<br>');
            return false;
        } else {
            passwordInput.classList.remove('is-invalid');
            passwordInput.classList.add('is-valid');
            passwordErrorDiv.innerHTML = '';
            return true;
        }
    }

    // Fungsi validasi konfirmasi password
    function validateConfirmPassword() {
        const password = passwordInput.value;
        const confirmPassword = confirmPasswordInput.value;

        if (password !== confirmPassword) {
            confirmPasswordInput.classList.add('is-invalid');
            confirmPasswordInput.classList.remove('is-valid');
            confirmPasswordErrorDiv.textContent = 'Konfirmasi kata sandi tidak cocok!';
            return false;
        } else {
            confirmPasswordInput.classList.remove('is-invalid');
            confirmPasswordInput.classList.add('is-valid');
            confirmPasswordErrorDiv.textContent = '';
            return true;
        }
    }

    // Event listeners untuk validasi real-time
    if (passwordInput && confirmPasswordInput) {
        passwordInput.addEventListener('input', function() {
            validatePassword();
            validateConfirmPassword(); // Validasi konfirmasi juga saat password berubah
        });

        confirmPasswordInput.addEventListener('input', validateConfirmPassword);
    }

    // Event listener saat form disubmit
    if (registerForm) {
        registerForm.addEventListener('submit', function(event) {
            const isPasswordValid = validatePassword();
            const isConfirmPasswordValid = validateConfirmPassword();

            if (!isPasswordValid || !isConfirmPasswordValid) {
                event.preventDefault(); // Mencegah form dikirim jika ada error
            }
            // Jika semua validasi JS lolos, form akan dikirim ke backend
        });
    }

    // Untuk menyembunyikan flash message setelah beberapa detik
    const flashMessages = document.querySelectorAll('.alert');
    flashMessages.forEach(message => {
        setTimeout(() => {
            // Gunakan Bootstrap's built-in alert close
            const bsAlert = new bootstrap.Alert(message);
            bsAlert.close();
        }, 5000); // Pesan akan hilang setelah 5 detik
    });
});