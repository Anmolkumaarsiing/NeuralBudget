import { initializeApp } from "https://www.gstatic.com/firebasejs/9.22.1/firebase-app.js";
import { getAuth, signInWithEmailAndPassword, createUserWithEmailAndPassword } from "https://www.gstatic.com/firebasejs/9.22.1/firebase-auth.js";
import firebaseConfig from "./firebase-config.js";

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

export function login() {
    var email = document.getElementById('email').value;
    var password = document.getElementById('password').value;

    signInWithEmailAndPassword(auth, email, password)
        .then((userCredential) => {
            console.log("Firebase authentication successful");
            return userCredential.user.getIdToken();
        })
        .then((idToken) => {
            console.log("Got ID token, sending to backend");
            return fetch('/auth/login/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${idToken}`
                },
                body: JSON.stringify({ email: email })
            });
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.error || 'Login failed');
                });
            }
            return response.json();
        })
        .then(data => {
            console.log("Backend response:", data);
            if (data.message === 'Login successful') {
                console.log("Redirecting to dashboard...");
                window.location.replace("/auth/dashboard/");
            } else {
                throw new Error(data.error || 'Login failed');
            }
        })
        .catch((error) => {
            console.error("Login error:", error);
            document.getElementById('error-message').innerText = error.message;
        });
}

export function register() {
    var email = document.getElementById('email').value;
    var password = document.getElementById('password').value;

    createUserWithEmailAndPassword(auth, email, password)
        .then((userCredential) => {
            console.log("Registration successful: ", userCredential);
            return userCredential.user.getIdToken();
        })
        .then((idToken) => {
            return fetch('/auth/register/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${idToken}`
                },
                body: JSON.stringify({ email: email })
            });
        })
        .then(response => response.json())
        .then(data => {
            console.log(data);
            if (data.message === 'Registration successful') {
                window.location.href = "/auth/dashboard/";
            } else {
                throw new Error(data.error || 'Registration failed');
            }
        })
        .catch((error) => {
            document.getElementById('error-message').innerText = error.message;
        });
}

window.login = login;
window.register = register;

