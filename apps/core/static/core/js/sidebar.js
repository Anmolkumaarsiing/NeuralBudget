// Simple Dropdown Functionality
document.addEventListener('DOMContentLoaded', function () {
    const dropdownButtons = document.querySelectorAll('.drop-btn');

    dropdownButtons.forEach(function (button) {
        button.addEventListener('click', function (e) {
            e.preventDefault();

            const dropdownContent = button.nextElementSibling;
            const dropdownIcon = button.querySelector('.dropdown-icon');
            const isOpen = dropdownContent.classList.contains('show');

            // Close all dropdowns
            dropdownButtons.forEach(function (btn) {
                const content = btn.nextElementSibling;
                const icon = btn.querySelector('.dropdown-icon');

                btn.classList.remove('active');
                content.classList.remove('show');
                icon.classList.remove('rotate');
            });

            // Open clicked dropdown if it was closed
            if (!isOpen) {
                button.classList.add('active');
                dropdownContent.classList.add('show');
                dropdownIcon.classList.add('rotate');
            }
        });
    });

    // Close dropdowns when clicking outside sidebar
    document.addEventListener('click', function (e) {
        if (!e.target.closest('.sidebar')) {
            dropdownButtons.forEach(function (btn) {
                const content = btn.nextElementSibling;
                const icon = btn.querySelector('.dropdown-icon');

                btn.classList.remove('active');
                content.classList.remove('show');
                icon.classList.remove('rotate');
            });
        }
    });

    // Logout confirmation
    c// Handle logout confirmation (Fetch API version)
    document.addEventListener('DOMContentLoaded', function () {
        const signOutLink = document.getElementById('signOutLink');
        if (signOutLink) {
            signOutLink.addEventListener('click', function (e) {
                e.preventDefault();

                if (confirm('Are you sure you want to logout?')) {
                    // Get CSRF token
                    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;

                    // Make POST request to logout
                    fetch('/accounts/logout/', {
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': csrfToken,
                            'Content-Type': 'application/x-www-form-urlencoded',
                        },
                        credentials: 'same-origin'
                    })
                        .then(response => {
                            if (response.ok) {
                                // Redirect to login page or home
                                window.location.href = '/accounts/login/';
                            }
                        })
                        .catch(error => {
                            console.error('Logout error:', error);
                            // Fallback - redirect anyway
                            window.location.href = '/accounts/login/';
                        });
                }
            });
        }
    });

});
