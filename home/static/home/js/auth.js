// Helper function to get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken'); // Get the CSRF token

// Helper function to display errors
function displayError(errorDiv, message) {
    if (errorDiv) {
        errorDiv.style.display = 'block';
        errorDiv.innerText = message;
    } else {
        alert(message);
    }
}

// Helper function to clear errors
function clearError(errorDiv) {
    if (errorDiv) {
        errorDiv.style.display = 'none';
        errorDiv.innerText = '';
    }
}

// Login function
export function login(email, password) {
    console.log("Login function called");
    const errorDiv = document.getElementById('loginError');
    clearError(errorDiv);
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
        if (!response.ok) throw new Error(text || 'Login failed');
        return JSON.parse(text);
    })
    .then(data => {
        if (data.message === 'Login successful') {
            console.log("Login successful! Redirecting...");
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

// Register function
export function register() {
    console.log("Register function called");

    const username = document.getElementById('registerUsername').value;
    const email = document.getElementById('registerEmail').value;
    const password1 = document.getElementById('registerPassword1').value;
    const password2 = document.getElementById('registerPassword2').value;
    const errorDiv = document.getElementById('registerError');

    clearError(errorDiv);

    // Validate input
    if (!username || !email || !password1 || !password2) {
        displayError(errorDiv, 'All fields are required.');
        return;
    }

    if (password1 !== password2) {
        displayError(errorDiv, 'Passwords do not match.');
        return;
    }

    console.log("Attempting Firebase registration with email:", email);

    // Create user in Firebase
    createUserWithEmailAndPassword(auth, email, password1)
        .then((userCredential) => {
            console.log("Firebase registration successful:", userCredential);
            return userCredential.user.getIdToken();
        })
        .then((idToken) => {
            // Send registration data to the backend
            return fetch('/home/register/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken,
                    'Authorization': `Bearer ${idToken}`
                },
                body: JSON.stringify({ username, email, idToken })
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
            if (data.message === 'Registration successful') {
                console.log("Redirecting to dashboard...");
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