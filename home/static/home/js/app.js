import { login,register } from './auth.js';

const sign_in_btn = document.querySelector("#sign-in-btn");
const sign_up_btn = document.querySelector("#sign-up-btn");
const container = document.querySelector(".container");

sign_up_btn.addEventListener('click', () =>{
    container.classList.add("sign-up-mode");
});

sign_in_btn.addEventListener('click', () =>{
    container.classList.remove("sign-up-mode");
});

document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', (event) => {
            event.preventDefault();
            login();
        });
    }
    const signupForm = document.getElementById('signupForm');

    if (signupForm) {
        signupForm.addEventListener('submit', (event) => {
            event.preventDefault();
            register();
        });
    }
    const signOutLink = document.querySelector('a[id="LogOut"]');
    if (signOutLink) {
        signOutLink.addEventListener('click', function (event) {
            event.preventDefault();  // Prevent default link behavior
            signOut();
        });
    }
});