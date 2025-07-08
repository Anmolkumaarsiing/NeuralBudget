import { clearError, displayError, getCookie } from './help.js';

const csrftoken = getCookie('csrftoken');

// Use a flag to ensure setInterval is only set up once
let tokenRefreshIntervalId = null;

/**
 * Handles Firebase authentication state changes and sets up token refreshing.
 */
document.addEventListener("DOMContentLoaded", () => {
    if (typeof firebase !== 'undefined' && firebase.apps.length > 0) {
        firebase.auth().onAuthStateChanged(function(user) {
            if (user) {
                // User is signed in.
                console.log("Firebase user detected");

                // If interval is not already running, set it up
                if (tokenRefreshIntervalId === null) {
                    // Refresh token every 50 minutes (Firebase tokens expire in 60 minutes)
                    const refreshInterval = 50 * 60 * 1000; 

                    tokenRefreshIntervalId = setInterval(async () => {
                        try {
                            const idToken = await user.getIdToken(true); // Force refresh
                            console.log("Firebase ID token refreshed. Sending to backend...");
                            
                            const response = await fetch('/refresh_token/', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json',
                                    'X-CSRFToken': csrftoken
                                },
                                body: JSON.stringify({ idToken: idToken })
                            });

                            if (!response.ok) {
                                const errorData = await response.json();
                                console.error("Failed to refresh token on backend:", errorData.error);
                            } else {
                                console.log("Token successfully refreshed on backend.");
                            }
                        } catch (error) {
                            console.error("Error refreshing Firebase ID token:", error);
                        }
                    }, refreshInterval);
                }
            } else {
                // User is signed out.
                console.log("No Firebase user detected.");
                // Clear any existing refresh interval if user logs out
                if (tokenRefreshIntervalId !== null) {
                    clearInterval(tokenRefreshIntervalId);
                    tokenRefreshIntervalId = null;
                }
            }
        });
    } else {
        console.warn("Firebase not initialized or not available. Token refresh will not be set up.");
    }
});

export function login(email, password) {
    console.log("Login function called");
    const errorDiv = document.getElementById('loginError');
    clearError(errorDiv);

    console.log("Attempting login with:", { email, password });

    fetch('/login/', {
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
                window.location.href = "/dashboard/"; // Redirect to dashboard
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
    const email = document.getElementById('registerEmail').value;
    const password1 = document.querySelector('input[name="registerPassword1"]').value;
    const password2 = document.querySelector('input[name="registerPassword2"]').value;
    const errorDiv = document.getElementById('registerError');
    clearError(errorDiv);
    if (!username || !email || !password1 || !password2) {
        displayError(errorDiv, 'All fields are required.');
        return;
    }

    if (password1 !== password2) {
        displayError(errorDiv, 'Passwords do not match.');
        return;
    }

    console.log("Sending registration data to backend...");

    fetch('/signup/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({ username, email, password: password1 })
    })
        .then(response => response.json())
        .then(data => {
            if (data.message === 'Registration successful') {
                console.log("User created in Firebase! UID:", data.uid);
                window.location.href = "/dashboard/";
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
    fetch('/logout/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
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
        .catch(error => {
            console.error("Logout error:", error);
            alert('Failed to logout. Please try again.');
        });
}