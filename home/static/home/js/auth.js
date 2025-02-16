export function getCookie(name) {
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
// console.log("Checking for print calls...");

// Override window.print for debugging
// const originalPrint = window.print;
// window.print = function() {
//     console.trace("Print dialog triggered from:"); // Log the call stack
//     originalPrint.apply(window, arguments);
// };
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
            if (!response.ok) {
                // Parse the error message if the response is JSON
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

function clearError(errorDiv) {
    errorDiv.textContent = '';
    errorDiv.style.display = 'none';
}

function displayError(errorDiv, message) {
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
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