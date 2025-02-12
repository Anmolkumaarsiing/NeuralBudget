import { createUserWithEmailAndPassword } from "https://www.gstatic.com/firebasejs/9.22.1/firebase-auth.js";

// Helper function to get CSRF token
function getCSRFToken() {
    const csrfCookie = document.cookie
        .split(';')
        .find(cookie => cookie.trim().startsWith('csrftoken='));
    return csrfCookie ? csrfCookie.split('=')[1] : null;
}


export function login() {
    console.log("Login function called");

    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    const errorDiv = document.getElementById('loginError');

    // Clear errors
    if (errorDiv) {
        errorDiv.style.display = 'none';
        errorDiv.innerText = '';
    }

    // Send email/password to backend
    fetch('/login/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            email: email,
            password: password
        })
    })
        .then(async response => {
            const text = await response.text();
            if (!response.ok) throw new Error(text || 'Login failed');
            return JSON.parse(text);
        })
        .then(data => {
            if (data.message === 'Login successful') {
                console.log("Login successful! Redirecting...");
                window.location.href = "/dashboard/";  // Redirect to dashboard
            } else {
                throw new Error(data.error || 'Login failed');
            }
        })
        .catch((error) => {
            console.error("Login error:", error);
            if (errorDiv) {
                errorDiv.style.display = 'block';
                errorDiv.innerText = error.message;
            } else {
                alert(error.message);
            }
        });
}

export function register(event) {
    console.log("Register function called"); // Debug line

    const username = document.getElementById('registerUsername').value;
    const email = document.getElementById('registerEmail').value;
    const password1 = document.getElementById('registerPassword1').value;
    const password2 = document.getElementById('registerPassword2').value;
    const errorDiv = document.getElementById('registerError');

    // Clear any existing error messages
    if (errorDiv) {
        errorDiv.style.display = 'none';
        errorDiv.innerText = '';
    }

    console.log("Form data:", { username, email, password1, password2 }); // Debug line

    // Validate input
    if (!username || !email || !password1 || !password2) {
        console.log("Validation error: All fields are required"); // Debug line
        if (errorDiv) {
            errorDiv.style.display = 'block';
            errorDiv.innerText = 'All fields are required.';
        }
        return;
    }

    if (password1 !== password2) {
        console.log("Validation error: Passwords do not match"); // Debug line
        if (errorDiv) {
            errorDiv.style.display = 'block';
            errorDiv.innerText = 'Passwords do not match.';
        }
        return;
    }

    console.log("Attempting Firebase registration with email:", email); // Debug line

    // Create user in Firebase
    createUserWithEmailAndPassword(auth, email, password1)
        .then((userCredential) => {
            console.log("Firebase registration successful:", userCredential); // Debug line
            return userCredential.user.getIdToken();
        })
        .then((idToken) => {
            console.log("Got ID token:", idToken); // Debug line
            const csrfToken = getCSRFToken();
            console.log("CSRF token:", csrfToken); // Debug line

            // Send registration data to the backend
            return fetch('/home/register/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                    'Authorization': `Bearer ${idToken}`
                },
                body: JSON.stringify({
                    username: username,
                    email: email,
                    idToken: idToken
                })
            });
        })
        .then(response => {
            console.log("Backend response status:", response.status); // Debug line
            if (!response.ok) {
                return response.json().then(data => {
                    console.log("Backend error response:", data); // Debug line
                    throw new Error(data.error || 'Registration failed');
                });
            }
            return response.json();
        })
        .then(data => {
            console.log("Backend response data:", data); // Debug line
            if (data.message === 'Registration successful') {
                console.log("Redirecting to dashboard..."); // Debug line
                window.location.href = "/dashboard/";
            } else {
                throw new Error(data.error || 'Registration failed');
            }
        })
        .catch((error) => {
            console.error("Registration error:", error); // Debug line
            if (errorDiv) {
                errorDiv.style.display = 'block';
                errorDiv.innerText = error.message;
            }
        });
}

export function logOut() {
    fetch('/logout/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        credentials: 'include'
    })
    .then(response => {
        if (response.ok) {
            window.location.href = '/login/';
    } else {
        throw new Error('Logout failed');
    }
})
    .catch((error) => {
        console.error("Logout error:", error);
        alert('Failed to logout. Please try again.');
    })
}
