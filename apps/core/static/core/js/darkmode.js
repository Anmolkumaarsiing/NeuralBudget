// darkmode.js
// Initialize the dark mode state based on localStorage
window.addEventListener("load", function() {
    const darkMode = localStorage.getItem("darkMode");
    const darkModeToggle = document.getElementById("darkModeToggle");
    
    if(darkMode === "true"){
        document.body.classList.add("dark-mode");
        darkModeToggle.checked = true;
    } else {
        document.body.classList.remove("dark-mode");
        darkModeToggle.checked = false;
    }
});
document.getElementById("darkModeToggle").addEventListener("change", function () {
    let darkMode = localStorage.getItem("darkMode");
    
    if(darkMode === "true"){
        document.body.classList.remove("dark-mode");
        localStorage.setItem("darkMode", "false");
    } else {
        document.body.classList.add("dark-mode");
        localStorage.setItem("darkMode", "true");
    }
});