// Firebase configuration
const firebaseConfig = {
    apiKey: "{{ FIREBASE_API_KEY }}",
    authDomain: "neuralbudgetai.firebaseapp.com", // Replace with your actual auth domain
    projectId: "neuralbudgetai", // Replace with your actual project ID
    storageBucket: "neuralbudgetai.appspot.com", // Replace with your actual storage bucket
    messagingSenderId: "1070300712000", // Replace with your actual messaging sender ID
    appId: "1:1070300712000:web:1234567890abcdef" // Replace with your actual app ID
};

// Initialize Firebase
firebase.initializeApp(firebaseConfig);