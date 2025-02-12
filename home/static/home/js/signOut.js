import { logOut } from './auth.js';
document.addEventListener("DOMContentLoaded", function () {
    const signOutLink = document.querySelector('a[onclick="signOut()"]');
    console.log(signOutLink)
    if (signOutLink) {
        signOutLink.addEventListener('click', function (event) {
            event.preventDefault();  // Prevent default link behavior
            logOut();
        });
    }
});