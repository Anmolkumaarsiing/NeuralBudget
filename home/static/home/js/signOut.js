import { signOut } from './auth.js';
document.addEventListener("DOMContentLoaded", function () {
    const signOutLink = document.querySelector('a[id="LogOut"]');
    console.log(signOutLink)
    if (signOutLink) {
        signOutLink.addEventListener('click', function (event) {
            event.preventDefault();  // Prevent default link behavior
            signOut();
        });
    }
});