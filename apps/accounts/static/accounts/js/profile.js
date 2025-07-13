import { getCookie } from '/static/core/js/help.js';

document.addEventListener('DOMContentLoaded', function() {
    const csrftoken = getCookie('csrftoken');

    // DOM Elements
    const editToggle = document.getElementById('editToggle');
    const cancelEdit = document.getElementById('cancelEdit');
    const profileForm = document.getElementById('profileForm');
    const formInputs = profileForm.querySelectorAll('input, textarea, select');
    const formActions = document.querySelector('.form-actions');
    const editProfilePic = document.getElementById('editProfilePic');
    const profilePicUpload = document.getElementById('profilePicUpload');
    const profileImage = document.getElementById('profileImage');
    
    // Store initial form values to revert on cancel
    const initialFormValues = {};
    formInputs.forEach(input => {
        initialFormValues[input.id] = input.value;
    });

    // Enable/disable form editing
    function toggleFormEditing(enable) {
        formInputs.forEach(input => {
            input.disabled = !enable;
        });
        
        if (enable) {
            formActions.style.display = 'flex';
            editToggle.style.display = 'none';
        } else {
            formActions.style.display = 'none';
            editToggle.style.display = 'flex';
            // Revert to initial values on cancel
            for (const id in initialFormValues) {
                const input = document.getElementById(id);
                if (input) {
                    input.value = initialFormValues[id];
                }
            }
        }
    }
    
    // Edit button click handler
    editToggle.addEventListener('click', function(e) {
        e.preventDefault();
        toggleFormEditing(true);
    });
    
    // Cancel button click handler
    cancelEdit.addEventListener('click', function(e) {
        e.preventDefault();
        toggleFormEditing(false);
    });
    
    // Form submit handler
    profileForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const updatedProfileData = {
            first_name: document.getElementById('first-name').value,
            last_name: document.getElementById('last-name').value,
            email: document.getElementById('email').value, // Email might be read-only, but included for completeness
            phone_number: document.getElementById('phone').value,
            date_of_birth: document.getElementById('dob').value,
            financial_goals: document.getElementById('goals').value,
            risk_tolerance: parseInt(document.getElementById('risk').value) // Parse to int
        };

        try {
            const response = await fetch('/accounts/update_profile/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify(updatedProfileData)
            });

            const data = await response.json();

            if (response.ok) {
                alert('Profile updated successfully!');
                // Update displayed name/email in header
                document.getElementById('profileName').textContent = `${updatedProfileData.first_name} ${updatedProfileData.last_name}`.trim();
                document.getElementById('profileEmail').textContent = updatedProfileData.email;
                
                // Update initial values for next edit session
                formInputs.forEach(input => {
                    initialFormValues[input.id] = input.value;
                });

                toggleFormEditing(false);
            } else {
                throw new Error(data.error || 'Failed to update profile.');
            }
        } catch (error) {
            console.error('Error updating profile:', error);
            alert(error.message);
        }
    });
    
    // Profile picture upload handler
    editProfilePic.addEventListener('click', function() {
        profilePicUpload.click();
    });
    
    profilePicUpload.addEventListener('change', async function(e) {
        if (e.target.files && e.target.files[0]) {
            const file = e.target.files[0];
            const reader = new FileReader();
            
            reader.onload = function(event) {
                profileImage.src = event.target.result;
            };
            
            reader.readAsDataURL(file);

            // Upload image to backend
            const formData = new FormData();
            formData.append('profile_picture', file);

            try {
                const response = await fetch('/accounts/upload_profile_picture/', {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrftoken
                    },
                    body: formData
                });

                const data = await response.json();

                if (response.ok) {
                    alert('Profile picture uploaded successfully!');
                    // Optionally update the photo_url in the displayed profile data if needed
                } else {
                    throw new Error(data.error || 'Failed to upload profile picture.');
                }
            } catch (error) {
                console.error('Error uploading profile picture:', error);
                alert(error.message);
            }
        }
    });
    
    // Initialize form as disabled
    toggleFormEditing(false);
});