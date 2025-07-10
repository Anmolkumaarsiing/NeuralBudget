import { logOut } from './auth.js';

document.addEventListener("DOMContentLoaded", function () {
    // console.log("signOut.js loaded and DOMContentLoaded fired.");
    const signOutLink = document.getElementById('signOutLink'); // Use an ID instead of onclick


    if (signOutLink) {
        signOutLink.addEventListener('click', function (event) {
            event.preventDefault(); // Prevent default link behavior

            // Confirmation dialog
            const confirmLogout = confirm("Are you sure you want to log out?");
            if (confirmLogout) {
                logOut()
                    .then(() => {
                        console.log("Logged out successfully!");
                        window.location.href = "/login/"; // Redirect to login page
                    })
                    .catch(error => {
                        console.error("Logout error:", error);
                        alert("Failed to log out. Please try again.");
                    });
            }
        });
    }
});