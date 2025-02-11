import { initializeApp } from "https://www.gstatic.com/firebasejs/9.22.1/firebase-app.js";
import { getAuth, signInWithEmailAndPassword, createUserWithEmailAndPassword } from "https://www.gstatic.com/firebasejs/9.22.1/firebase-auth.js";
import firebaseConfig from "./firebase-config.js";

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

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

    signInWithEmailAndPassword(auth, email, password)
        .then((userCredential) => {
            console.log("Firebase authentication successful");
            return userCredential.user.getIdToken();
        })
        .then((idToken) => {
            console.log("Got ID token:", idToken);

            return fetch('/login/', {  // Make sure this matches your URL pattern
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${idToken}`
                },
                body: JSON.stringify({
                    email: email,
                    idToken: idToken
                })
            });
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
    event.preventDefault();

    var email = document.getElementById('registerEmail').value;
    var password = document.getElementById('registerPassword').value;
    const errorDiv = document.getElementById('registerError');

    createUserWithEmailAndPassword(auth, email, password)
        .then((userCredential) => {
            console.log("Registration successful: ", userCredential);
            return userCredential.user.getIdToken();
        })
        .then((idToken) => {
            const csrfToken = getCSRFToken() || document.querySelector('[name=csrfmiddlewaretoken]').value;

            return fetch('/home/register/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                    'Authorization': `Bearer ${idToken}`
                },
                credentials: 'include',
                body: JSON.stringify({
                    email: email,
                    idToken: idToken
                })
            });
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.error || 'Registration failed');
                });
            }
            return response.json();
        })
        .then(data => {
            console.log(data);
            if (data.message === 'Registration successful') {
                window.location.href = "//dashboard/";
            } else {
                throw new Error(data.error || 'Registration failed');
            }
        })
        .catch((error) => {
            console.error("Registration error:", error);
            if (errorDiv) {
                errorDiv.textContent = error.message;
                errorDiv.style.display = 'block';
            }
        });
}

