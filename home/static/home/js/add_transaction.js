import { getCookie } from './help.js';

// Handle form submission
document.getElementById("addTransactionForm").addEventListener("submit", async (e) => {
    e.preventDefault(); 
    const name = document.getElementById("name").value;
    const category = document.getElementById("category").value;
    const otherCategory = document.getElementById("other-category").value;
    const amount = parseFloat(document.getElementById("amount").value);
    const date = document.getElementById("date").value;
    const status = document.getElementById("status").value;
    const finalCategory = category === "Other" ? otherCategory : category;
    const id = localStorage.getItem("uid");
    
    const transaction = {
        name,
        category: finalCategory,
        amount,
        date,
        status
    };

    console.log(transaction);

    try {
        // Submit transaction to Django
        const response = await fetch("/add_transaction/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie('csrftoken')  // Include CSRF token from cookie
            },
            body: JSON.stringify({transaction, id})
        });

        const data = await response.json();
        if (response.ok) {
            alert("Transaction added successfully!");
            document.getElementById("addTransactionForm").reset(); // Clear the form
        } else {
            throw new Error(data.error || "Failed to add transaction");
        }
    } catch (error) {
        console.error("Error:", error);
        alert(error.message);
    }
});

// Handle "Other" category input visibility
function toggleOtherCategory() {
    const categorySelect = document.getElementById("category");
    const otherCategoryContainer = document.getElementById("other-category-container");
    const otherCategoryInput = document.getElementById("other-category");

    if (categorySelect.value === "Other") {
        otherCategoryContainer.style.display = "block";
        otherCategoryInput.required = true;
    } else {
        otherCategoryContainer.style.display = "none";
        otherCategoryInput.required = false;
    }
}

// Add event listener for category dropdown change
document.getElementById("category").addEventListener("change", toggleOtherCategory);

document.addEventListener("DOMContentLoaded", function () {
    const dropdownButtons = document.querySelectorAll(".drop-btn");
        dropdownButtons.forEach(button => {
            button.addEventListener("click", function () {
                const dropdownContent = this.nextElementSibling;
                const icon = this.querySelector(".dropdown-icon");
    
                dropdownContent.classList.toggle("active");
    
                if (dropdownContent.classList.contains("active")) {
                    dropdownContent.style.display = "block";
                    icon.classList.remove("fa-angle-right");
                    icon.classList.add("fa-angle-down");
                } else {
                    dropdownContent.style.display = "none";
                    icon.classList.remove("fa-angle-down");
                    icon.classList.add("fa-angle-right");
                }
            });
    });
});