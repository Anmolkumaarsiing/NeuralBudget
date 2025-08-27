import { getCookie } from '/static/core/js/help.js';

document.addEventListener('DOMContentLoaded', () => {
    const setupContainer = document.getElementById('setup-container');
    const resultsContainer = document.getElementById('results-container');
    const detailsForm = document.getElementById('details-form');
    const getLocationBtn = document.getElementById('get-location-btn');
    const generateTipsBtn = document.getElementById('generate-tips-btn');
    const editSalaryBtn = document.getElementById('edit-salary-btn');
    const salaryDisplay = document.getElementById('salary-display');
    const tipsGrid = document.getElementById('tips-grid');
    
    let userLocation = null;
    let userSalary = parseFloat(salaryDisplay.textContent.replace(/,/g, '')) || null;

    // --- Event Listeners ---
    getLocationBtn.addEventListener('click', () => {
        if (!navigator.geolocation) {
            alert("Geolocation is not supported by this browser.");
            return;
        }
        
        // Check for secure context (HTTPS), which is often required
        if (window.isSecureContext === false) {
            alert("Location access is blocked. Please ensure you are on a secure (https) connection.");
            return;
        }

        getLocationBtn.textContent = "Getting Location...";
        getLocationBtn.disabled = true;
        navigator.geolocation.getCurrentPosition(positionSuccess, positionError);
    });

    detailsForm.addEventListener('submit', (e) => {
        e.preventDefault();
        userSalary = document.getElementById('monthly-salary').value;
        if (!userLocation) {
            alert("Please get your location before generating the guide.");
            return;
        }
        fetchAndRenderTips();
    });

    editSalaryBtn.addEventListener('click', () => {
        setupContainer.style.display = 'block';
        resultsContainer.style.display = 'none';
        document.getElementById('monthly-salary').value = userSalary;
    });

    // --- Main Functions ---
    // Replace the existing positionSuccess function with this one

function positionSuccess(pos) {
    const { latitude, longitude } = pos.coords;

    fetch("/insights/api/get-city/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken"),
        },
        body: JSON.stringify({ lat: latitude, lon: longitude }),
    })
    .then(res => res.json())
    .then(data => {
        if (data.error) throw new Error(data.error);
        userLocation = data.city;
        getLocationBtn.innerHTML = `<i class="fas fa-check-circle"></i> Location Found: ${userLocation}`;
        generateTipsBtn.disabled = false;
        getLocationBtn.disabled = false;
    })
    .catch(error => {
        console.error("Error fetching city name:", error);
        userLocation = "Unknown";
        alert("Could not determine your city from location coordinates.");
        generateTipsBtn.disabled = false;
        getLocationBtn.disabled = false;
    });
}


    function positionError(error) {
        let errorMessage = "An unknown error occurred.";
        if (error.code === 1) { // PERMISSION_DENIED
            errorMessage = "You have denied location access. Please enable it in your browser settings and refresh the page.";
        } else if (error.code === 2) { // POSITION_UNAVAILABLE
            errorMessage = "Location information is unavailable.";
        }
        alert(errorMessage);
        getLocationBtn.textContent = "Get My Location";
        getLocationBtn.disabled = false;
    }
    
    async function fetchAndRenderTips() {
        setupContainer.style.display = 'none';
        resultsContainer.style.display = 'block';
        tipsGrid.innerHTML = '<div class="spinner-container"><div class="spinner"></div><p>SAVI is generating your investment guide...</p></div>';

        try {
            const response = await fetch('/insights/api/generate-investment-tips/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: JSON.stringify({ salary: userSalary, location: userLocation }),
            });
            const data = await response.json();
            if (!response.ok) throw new Error(data.error);
            
            renderTips(data.investment_tips);
            salaryDisplay.textContent = parseFloat(userSalary).toFixed(2);

        } catch (error) {
            tipsGrid.innerHTML = `<div class="error-container"><p>${error.message}</p></div>`;
        }
    }

    function renderTips(tips) {
        tipsGrid.innerHTML = '';
        if (!tips || tips.length === 0) {
            tipsGrid.innerHTML = '<p>Could not generate any tips at this time.</p>';
            return;
        }
        tips.forEach(tip => {
            const tipCard = document.createElement('div');
            tipCard.className = 'tip-card';
            tipCard.innerHTML = `
                <div class="tip-icon"><i class="${tip.icon}"></i></div>
                <div class="tip-content">
                    <h4>${tip.title} <span class="risk-badge risk-${tip.risk_level.toLowerCase()}">${tip.risk_level}</span></h4>
                    <p>${tip.description}</p>
                    <p><strong>Next Step:</strong> ${tip.action_step}</p>
                </div>
            `;
            tipsGrid.appendChild(tipCard);
        });
    }

    // If salary is already known on page load, automatically try to get location
    if (userSalary) {
        getLocationBtn.click();
        generateTipsBtn.textContent = "Regenerate My Guide";
    }
});