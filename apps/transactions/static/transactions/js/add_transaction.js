import { getCookie } from '/static/core/js/help.js';

document.addEventListener("DOMContentLoaded", function () {
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

        if (typeof checkBudget === 'function') {
            checkBudget(finalCategory, amount);
        } else {
            console.error("checkBudget function not defined.");
        }

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
            const response = await fetch("/transactions/add_transaction/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie('csrftoken')  // Include CSRF token from cookie
                },
                body: JSON.stringify({ transaction, id })
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

    // Handle add category button click
    document.getElementById("add-category-btn").addEventListener("click", async () => {
        const newCategoryName = document.getElementById("other-category").value.trim();
        if (newCategoryName) {
            try {
                const response = await fetch("/transactions/add_category/", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": getCookie('csrftoken'),
                    },
                    body: JSON.stringify({ category_name: newCategoryName }),
                });
                const data = await response.json();
                if (response.ok) {
                    alert("Category added successfully!");
                    // Optionally, refresh categories in the dropdown
                    location.reload(); // Simple reload to refresh categories
                } else {
                    throw new Error(data.error || "Failed to add category");
                }
            } catch (error) {
                console.error("Error adding category:", error);
                alert(error.message);
            }
        } else {
            alert("Please enter a category name.");
        }
    });

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

document.addEventListener("DOMContentLoaded", function () {
    const ocrForm = document.getElementById('ocrForm');
    if (ocrForm) {
        ocrForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(ocrForm);
            const receiptFile = formData.get('image');

            if (!receiptFile || receiptFile.size === 0) {
                alert('Please select an image to upload.');
                return;
            }

            try {
                const response = await fetch('/ml_features/categorize_expense/', {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                    },
                    body: formData,
                });

                const data = await response.json();

                if (response.ok) {
                    alert('Transaction extracted and added successfully!');
                    window.location.href = "/transactions/transaction_history/";
                } else {
                    throw new Error(data.error || 'Failed to process image.');
                }
            } catch (error) {
                console.error('Error processing image:', error);
                alert(error.message);
            }
        });
    }
});