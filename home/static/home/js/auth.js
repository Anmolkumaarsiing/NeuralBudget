import { initializeApp } from "https://www.gstatic.com/firebasejs/9.22.1/firebase-app.js";
import { getAuth, signInWithEmailAndPassword, createUserWithEmailAndPassword } from "https://www.gstatic.com/firebasejs/9.22.1/firebase-auth.js";



// Helper function to get CSRF token
function getCSRFToken() {
    const csrfCookie = document.cookie
        .split(';')
        .find(cookie => cookie.trim().startsWith('csrftoken='));
    return csrfCookie ? csrfCookie.split('=')[1] : null;
}


export function login(request) {
    console.log("Login function called");

    var email = document.getElementById('loginEmail').value;
    var password = document.getElementById('loginPassword').value;
    const errorDiv = document.getElementById('loginError');

    // Clear any existing error messages
    if (errorDiv) {
        errorDiv.style.display = 'none';
        errorDiv.innerText = '';
    }

    fetch('/login/', {  // Make sure this matches your URL pattern
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
        console.log("Response status:", response.status);

        const text = await response.text();
        console.log("Response text:", text);  // Debug log

        if (!response.ok) {
            try {
                const data = JSON.parse(text);
                throw new Error(data.error || 'Login failed');
            } catch (e) {
                throw new Error('Server returned an invalid response');
            }
        }
        
        try {
            const data = JSON.parse(text);
            return data;
        } catch (e) {
            throw new Error('Invalid JSON response from server');
        }
    })
    .then(data => {
        console.log("Backend response:", data);
        if (data.message === 'Login successful') {
            console.log("Redirecting to dashboard...");
            window.location.replace("/dashboard/");
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
            console.error("Error div not found");
            alert(error.message);  // Fallback error display
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

export function signOut() {
    auth.signOut()
        .then(() => {
            // Clear session on the server
            return fetch('/logout/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                },
                credentials: 'include'
            });
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
        });
}
