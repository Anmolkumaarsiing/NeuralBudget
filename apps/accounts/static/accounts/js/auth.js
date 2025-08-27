import { clearError, displayError, getCookie } from '/static/core/js/help.js';

const csrftoken = getCookie('csrftoken');

// Google Sign-In Callback
window.handleGoogleCredentialResponse = function(response) {
    console.log("Encoded JWT ID token: " + response.credential);
    const errorDiv = document.getElementById('loginError'); // Assuming a common error div
    clearError(errorDiv);

    // GOOGLE_LOGIN_URL is expected to be a global variable from login.html
    fetch(GOOGLE_LOGIN_URL, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({ id_token: response.credential })
    })
    .then(async response => {
        const data = await response.json();
        if (response.ok) {
            console.log("Google login successful! Redirecting...");
            localStorage.setItem("uid", data.uid);
            window.location.href = data.redirect_url;
        } else {
            throw new Error(data.error || 'Google login failed');
        }
    })
    .catch(error => {
        console.error("Google login error:", error);
        displayError(errorDiv, error.message);
    });
};

document.addEventListener('DOMContentLoaded', function() {
    const googleSignInBtn = document.getElementById('google-signin-btn');
    const googleSignUpBtn = document.getElementById('google-signup-btn');

    // Attach Google Sign-In to the existing icons
    if (googleSignInBtn) {
        googleSignInBtn.addEventListener('click', function(e) {
            e.preventDefault();
            google.accounts.id.prompt(); // Display the One Tap / Google Sign-In dialog
        });
    }

    if (googleSignUpBtn) {
        googleSignUpBtn.addEventListener('click', function(e) {
            e.preventDefault();
            google.accounts.id.prompt(); // Display the One Tap / Google Sign-In dialog
        });
    }
});

export function login(email, password) {
    console.log("Login function called");
    const errorDiv = document.getElementById('loginError');
    clearError(errorDiv);

    // console.log("Attempting login with:", { email, password });

    fetch('/accounts/login/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({ email, password })
    })
        .then(async response => {
            const text = await response.text();
            if (!response.ok) {
                let errorMessage = 'Login failed';
                try {
                    const errorData = JSON.parse(text);
                    errorMessage = errorData.error || errorMessage;
                } catch (e) {
                    errorMessage = text || errorMessage;
                }
                throw new Error(errorMessage);
            }
            return JSON.parse(text);
        })
        .then(data => {
            console.log("Login response data:", data);
            if (data.message === 'Login successful') {
                const uid = data.uid;
                console.log("Login successful! Redirecting... for uid:", uid);
                localStorage.setItem("uid", uid);
                window.location.href = "/reports/dashboard"; // Redirect to dashboard
            } else {
                throw new Error(data.error || 'Login failed');
            }
        })
        .catch(error => {
            console.error("Login error:", error);
            displayError(errorDiv, error.message);
        });
}


export function register() {
    console.log("Register function called");

    const username = document.getElementById('registerUsername').value;
    const firstName = document.getElementById('registerFirstName').value;
    const lastName = document.getElementById('registerLastName').value;
    const phoneNumber = document.getElementById('registerPhoneNumber').value;
    const email = document.getElementById('registerEmail').value;
    const password1 = document.querySelector('input[name="registerPassword1"]').value;
    const password2 = document.querySelector('input[name="registerPassword2"]').value;
    const errorDiv = document.getElementById('registerError');
    clearError(errorDiv);
    if (!username || !firstName || !lastName || !email || !password1 || !password2) {
        displayError(errorDiv, 'All fields are required.');
        return;
    }

    if (password1 !== password2) {
        displayError(errorDiv, 'Passwords do not match.');
        return;
    }

    console.log("Sending registration data to backend...");

    fetch('/accounts/signup/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({ username, firstName, lastName, phoneNumber, email, password: password1 })
    })
        .then(async response => {
            const data = await response.json();
            if (response.ok) {
                console.log("Registration successful! UID:", data.uid);
                window.location.href = data.redirect_url; // Redirect to dashboard or login
            } else {
                throw new Error(data.error || 'Registration failed');
            }
        })
        .catch(error => {
            console.error("Registration error:", error);
            displayError(errorDiv, error.message);
        });
}

// Logout function
export function logOut() {
    return fetch('/accounts/logout/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        credentials: 'include'
    })
        .then(async response => {
            const data = await response.json(); // Parse the JSON response
            if (response.ok) {
                console.log("Logout successful! Redirecting to:", data.redirect_url);
                window.location.href = data.redirect_url; // Use the URL from the response
            } else {
                throw new Error(data.error || 'Logout failed');
            }
        })
        .catch(error => {
            console.error("Logout error:", error);
            alert('Failed to logout. Please try again.');
            throw error; // Re-throw the error so it can be caught by signOut.js
        });
}