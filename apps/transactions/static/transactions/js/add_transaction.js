import { getCookie } from '/static/core/js/help.js';

document.addEventListener("DOMContentLoaded", function () {
    // Set today's date
    const dateInput = document.getElementById('date');
    if (dateInput) {
        dateInput.valueAsDate = new Date();
    }

    // Form submission
    const manualForm = document.getElementById("manualForm");
    if (manualForm) {
        manualForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const name = document.getElementById("name").value;
            const amount = parseFloat(document.getElementById("amount").value);
            const date = document.getElementById("date").value;
            const status = document.getElementById("status").value;
            const transaction_type = document.getElementById("transaction_type").value;
            const id = localStorage.getItem("uid");

            let transaction = {};

            if (transaction_type === 'income') {
                transaction = {
                    source: name,
                    amount,
                    date,
                    status
                };
            } else {
                const category = document.getElementById("category").value;
                const otherCategory = document.getElementById("other-category").value;
                const finalCategory = category === "Other" ? otherCategory : category;

                if (typeof checkBudget === 'function') {
                    checkBudget(finalCategory, amount);
                } else {
                    console.error("checkBudget function not defined.");
                }

                transaction = {
                    name,
                    category: finalCategory,
                    amount,
                    date,
                    status
                };
            }

            try {
                const response = await fetch("/transactions/add_transaction/", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": getCookie('csrftoken')
                    },
                    body: JSON.stringify({ transaction, id })
                });

                const data = await response.json();
                if (response.ok) {
                    alert("Transaction added successfully!");
                    manualForm.reset();
                    // Reset the form to the default state (expense)
                    setTransactionType('expense');
                } else {
                    throw new Error(data.error || "Failed to add transaction");
                }
            } catch (error) {
                console.error("Error:", error);
                alert(error.message);
            }
        });
    }

    // OCR Form submission
    // OCR Form submission
    // OCR Form submission
    const ocrForm = document.getElementById('ocrForm');
    const previewModal = document.getElementById('ocrPreviewModal');
    const previewForm = document.getElementById('previewForm');
    const cancelPreviewBtn = document.getElementById('cancelPreviewBtn');

    console.log("OCR Elements:", { ocrForm, previewModal, previewForm, cancelPreviewBtn }); // Debug log

    if (ocrForm) {
        ocrForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(ocrForm);
            const receiptFile = formData.get('image');

            if (!receiptFile || receiptFile.size === 0) {
                alert('Please select an image to upload.');
                return;
            }

            // Show loading state (optional but good)
            const submitBtn = ocrForm.querySelector('button[type="submit"]');
            const originalBtnText = submitBtn.textContent;
            submitBtn.textContent = 'Processing...';
            submitBtn.disabled = true;

            try {
                const ocrResponse = await fetch('/ml_features/categorize_expense/', {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                    },
                    body: formData,
                });

                const ocrData = await ocrResponse.json();

                if (!ocrResponse.ok) {
                    throw new Error(ocrData.error || 'Failed to process image.');
                }

                // Populate Preview Modal
                const transaction = ocrData.transaction;
                document.getElementById('preview-name').value = transaction.name || '';
                document.getElementById('preview-amount').value = transaction.amount || 0;
                document.getElementById('preview-date').value = transaction.date || new Date().toISOString().split('T')[0];
                document.getElementById('preview-category').value = transaction.category || 'Other';
                document.getElementById('preview-status').value = transaction.status || 'Pending';

                // Show Modal
                previewModal.style.display = 'block';

            } catch (error) {
                console.error('Error processing image:', error);
                alert(error.message);
            } finally {
                submitBtn.textContent = originalBtnText;
                submitBtn.disabled = false;
            }
        });
    }

    // Handle Preview Confirmation
    if (previewForm) {
        previewForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            console.log("Preview form submitted"); // Debug log

            const transaction = {
                name: document.getElementById('preview-name').value,
                amount: parseFloat(document.getElementById('preview-amount').value),
                date: document.getElementById('preview-date').value,
                category: document.getElementById('preview-category').value,
                status: document.getElementById('preview-status').value
            };

            const userId = localStorage.getItem("uid");

            try {
                const addResponse = await fetch('/transactions/add_transaction/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken'),
                    },
                    body: JSON.stringify({ transaction: transaction, id: userId }),
                });

                const addData = await addResponse.json();

                if (addResponse.ok) {
                    alert('Transaction added successfully!');
                    previewModal.style.display = 'none';
                    window.location.href = "/transactions/transaction_history/";
                } else {
                    throw new Error(addData.error || 'Failed to save transaction.');
                }
            } catch (error) {
                console.error('Error saving transaction:', error);
                alert(error.message);
            }
        });
    } else {
        console.error("Preview form not found!");
    }

    // Handle Cancel
    if (cancelPreviewBtn) {
        cancelPreviewBtn.addEventListener('click', () => {
            console.log("Cancel button clicked"); // Debug log
            previewModal.style.display = 'none';
        });
    } else {
        console.error("Cancel button not found!");
    }

    // Close modal if clicked outside
    window.addEventListener('click', (event) => {
        if (event.target === previewModal) {
            previewModal.style.display = 'none';
        }
    });

    // UI Toggles
    const expenseBtn = document.getElementById('expenseBtn');
    const incomeBtn = document.getElementById('incomeBtn');
    const manualBtn = document.getElementById('manualBtn');
    const ocrBtn = document.getElementById('ocrBtn');
    const categorySelect = document.getElementById("category");

    if (expenseBtn) {
        expenseBtn.addEventListener('click', () => setTransactionType('expense'));
    }
    if (incomeBtn) {
        incomeBtn.addEventListener('click', () => setTransactionType('income'));
    }
    if (manualBtn) {
        manualBtn.addEventListener('click', () => showForm('manual'));
    }
    if (ocrBtn) {
        ocrBtn.addEventListener('click', () => showForm('ocr'));
    }
    if (categorySelect) {
        categorySelect.addEventListener('change', toggleOtherCategory);
    }

    function setTransactionType(type) {
        const categoryLabel = document.getElementById('category_label');
        const categorySelect = document.getElementById('category');
        const otherCategoryContainer = document.getElementById('other-category-container');
        const transactionTypeInput = document.getElementById('transaction_type');
        const submitButton = document.querySelector('#manualForm button[type="submit"]');
        const ocrButton = document.getElementById('ocrBtn');
        const nameLabel = document.getElementById('name_label');
        const statusField = document.getElementById('status');
        const entryToggle = document.getElementById('manualBtn');

        if (type === 'expense') {
            expenseBtn.classList.add('active');
            incomeBtn.classList.remove('active');
            categoryLabel.style.display = 'block';
            categorySelect.style.display = 'block';
            transactionTypeInput.value = 'expense';
            submitButton.textContent = 'Submit Expense';
            ocrButton.style.display = 'inline-block';
            nameLabel.textContent = 'Transaction Name:';
            statusField.disabled = false;
        } else {
            expenseBtn.classList.remove('active');
            incomeBtn.classList.add('active');
            categoryLabel.style.display = 'none';
            entryToggle.classList.remove = 'entry-toggle';
            categorySelect.style.display = 'none';
            otherCategoryContainer.style.display = 'none'; // Also hide the "other" category input
            transactionTypeInput.value = 'income';
            submitButton.textContent = 'Submit Income';
            ocrButton.style.display = 'none';
            nameLabel.textContent = 'Source:';
            statusField.value = 'Completed';
            statusField.disabled = true;
            // Also hide the OCR form if it's visible
            document.getElementById('ocrForm').style.display = 'none';
            document.getElementById('manualForm').style.display = 'block';
            manualBtn.classList.add('active');
            ocrBtn.classList.remove('active');
        }
    }

    function showForm(type) {
        document.getElementById("manualForm").style.display =
            type === "manual" ? "block" : "none";
        document.getElementById("ocrForm").style.display =
            type === "ocr" ? "block" : "none";
        manualBtn.classList.toggle("active", type === "manual");
        ocrBtn.classList.toggle("active", type === "ocr");
    }

    function toggleOtherCategory() {
        const selected = document.getElementById("category").value;
        document.getElementById("other-category-container").style.display =
            selected === "Other" ? "block" : "none";
    }

    // Handle add category button click
    const addCategoryBtn = document.getElementById("add-category-btn");
    if (addCategoryBtn) {
        addCategoryBtn.addEventListener("click", async () => {
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
                        location.reload();
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
    }
});
