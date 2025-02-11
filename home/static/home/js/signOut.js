import { signOut } from './auth.js';
document.addEventListener("DOMContentLoaded", function () {
    const signOutLink = document.querySelector('a[onclick*="signOut"]');
    if (signOutLink) {
        signOutLink.addEventListener('click', function (event) {
            event.preventDefault();  // Prevent default link behavior
            signOut();
        });
    }
});