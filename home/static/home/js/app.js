import { login, register, logOut } from './auth.js';

const sign_in_btn = document.querySelector("#sign-in-btn");
const sign_up_btn = document.querySelector("#sign-up-btn");
const container = document.querySelector(".container");

// Toggle between login and sign-up modes
sign_up_btn.addEventListener('click', () => {
    container.classList.add("sign-up-mode");
});

sign_in_btn.addEventListener('click', () => {
    container.classList.remove("sign-up-mode");
});

// Handle form submissions and errors
document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');
    const signupForm = document.getElementById('signupForm');
    const signOutLink = document.querySelector('a[id="LogOut"]');

    // Login Form Submission
    if (loginForm) {
        loginForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const email = document.getElementById('loginEmail').value;
            console.log(email);
            const password = document.getElementById('loginPassword').value;

            try {
                await login(email, password);
                alert("Login successful!");
                // Redirect or update UI after successful login
                window.location.href = "/dashboard"; // Example redirect
            } catch (error) {
                alert(`Login failed: ${error.message}`);
            }
        });
    }

    // Signup Form Submission
    if (signupForm) {
        signupForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const email = signupForm.querySelector('input[name="email"]').value;
            const password = signupForm.querySelector('input[name="password"]').value;
            const confirmPassword = signupForm.querySelector('input[name="confirmPassword"]').value;

            if (password !== confirmPassword) {
                alert("Passwords do not match!");
                return;
            }

            try {
                await register(email, password);
                alert("Registration successful! Please log in.");
                container.classList.remove("sign-up-mode"); // Switch to login mode
            } catch (error) {
                alert(`Registration failed: ${error.message}`);
            }
        });
    }

    // Sign Out Link
    if (signOutLink) {
        signOutLink.addEventListener('click', async (event) => {
            event.preventDefault();
            try {
                await logOut();
                alert("Signed out successfully!");
                window.location.href = "/"; // Redirect to home page
            } catch (error) {
                alert(`Sign out failed: ${error.message}`);
            }
        });
    }
});