// apps/core/static/core/js/main.js

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.drop-btn').forEach(button => {
        button.addEventListener('click', () => {
            // Find the dropdown content and icon related to this button
            const dropdownContent = button.nextElementSibling;
            const dropdownIcon = button.querySelector('.dropdown-icon');

            // Toggle the 'show' class to display/hide the dropdown
            if (dropdownContent) {
                dropdownContent.classList.toggle('show');
            }

            // Toggle the 'rotate' class to animate the arrow icon
            if (dropdownIcon) {
                dropdownIcon.classList.toggle('rotate');
            }
        });
    });
});