<!-- Header with Typing Animation -->
<p align="center">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=22&pause=1000&color=00CFFF&center=true&vCenter=true&width=500&lines=Welcome+to+Neural+Budget+AI;An+AI-powered+Finance+Manager!;Track+Expenses+Effortlessly;Optimize+Your+Budget+With+AI" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Status-Active-success?style=flat-square">
  <img src="https://img.shields.io/github/languages/count/Anmolkumaarsiing/NeuralBudget" />
  <img src="https://img.shields.io/github/repo-size/Anmolkumaarsiing/NeuralBudget" />
  <img src="https://img.shields.io/github/contributors/Anmolkumaarsiing/NeuralBudget" />
</p>

---

## 🚀 **Neural Budget AI**
**Neural Budget AI** is an intelligent financial management application designed to simplify your personal finances. Built with a powerful backend powered by Django and a dynamic JavaScript frontend, it leverages AI to provide smart expense tracking, budgeting, and insightful analytics. The application uses Firebase for secure user authentication and Firestore for scalable, real-time data storage.

This project addresses the challenges of modern financial management by integrating **Generative Artificial Intelligence (GenAI)**, **Optical Character Recognition (OCR)**, and **predictive analytics** to simplify expense tracking and budgeting. It aims to bridge the gap between financial awareness and effective money management by reducing manual data entry, improving prediction accuracy, and providing users with tailored recommendations.

---

## 🏆 **Key Features**

### **User Management & Authentication**
*   **Secure Login & Registration:** Users can create an account and log in securely using their email and password, authenticated via Firebase.
*   **User-Specific Data:** Every user has their own dedicated data space in Firestore, ensuring privacy and personalization.
*   **Personalized Profiles:** Users can view and update their profile information, including their name, profile picture, and other personal details.
*   **Password Reset:** A secure password reset functionality is available, allowing users to reset their password via a link sent to their email.

### **Financial Tracking & Management**
*   **Smart Expense Categorization:** Upload a receipt or a screenshot of a transaction, and the AI-powered OCR (PaddleOCR) and LLM (Google Generative AI) will automatically extract details like amount, merchant, and date, categorize the expense, and record it seamlessly.
*   **Manual Transactions:** Users can manually add income and expenses via intuitive forms, selecting from predefined or custom categories.
*   **Budgeting & Savings Goals:** Set monthly budgets for categories (e.g., food, travel) with real-time tracking and alerts for overspending; track progress toward savings goals with visual indicators.
*   **Transaction History:** View a detailed, searchable history of all transactions with filters by date, category, or amount.

### **AI-Powered Insights & Analytics**
*   **Spending Analysis:** Interactive dashboards with charts and graphs (Matplotlib/Seaborn) breaking down spending habits by category, time, and trends.
*   **Predictive Analytics:** Machine learning models (Scikit-learn) forecast future expenses, detect patterns, and provide actionable insights to optimize spending.
*   **Investment Guide:** Personalized recommendations and tips for investments based on spending patterns and financial goals.
*   **AI-Powered Chatbot:** An interactive, real-time chatbot using Google Generative AI to answer queries (e.g., "What's my food spending this month?") and offer tailored financial advice.

### **Developer & Testing Tools**
*   **Data Generation:** Built-in tools to generate realistic historical or test data for transactions and budgets, aiding development and testing.
*   **Reports & Visualizations:** Comprehensive reporting module for exporting insights and generating custom visualizations.
*   **Modular Architecture:** Separate apps for accounts, budgets, transactions, insights, and more, with shared utilities for Firebase integration and auth middleware for secure sessions.

---

## 🔬 **Research**
This project is based on the research paper **"NeuralBudget: An AI-Powered Personal Finance Management System"**. The paper highlights the need for intelligent and automated financial management systems to address the complexities of modern financial transactions.

### **Objectives**
*   Develop an AI-driven platform to automate expense categorization and reduce manual effort.
*   Implement OCR for seamless data extraction from receipts and invoices.
*   Design an interactive and engaging user interface.
*   Integrate a secure and scalable backend using Django.
*   Provide real-time budget tracking and alerts.
*   Generate smart insights and predictions using machine learning.

### **Key Findings**
*   NeuralBudget reduces manual data entry by up to **80%**.
*   It improves prediction accuracy by **15%** compared to static budgeting applications.
*   The system provides a holistic solution by combining automation, prediction, and user engagement.

---

## 🌟 **Tech Stack**

*   **Backend:** Django, Django REST Framework
*   **Frontend:** HTML, CSS, JavaScript
*   **Database:** PostgreSQL, SQLite, Firebase Firestore
*   **AI/ML:**
    *   **OCR:** PaddleOCR
    *   **Predictive Analytics:** Scikit-learn, NumPy, Pandas
    *   **Generative AI:** Google Generative AI
*   **Visualization:** Matplotlib, Seaborn

---

## 🛠️ **Running the Project Locally**

### **Prerequisites**
*   Python 3.8+
*   Pip
*   Virtualenv (recommended)

### **Setup Instructions**
1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Anmolkumaarsiing/NeuralBudget.git
    cd NeuralBudget
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirement.txt
    ```

4.  **Firebase Configuration:**
    *   Place your Firebase service account key file named `firebase_key.json` inside the `apps` directory.
    *   Create a `.env` file in the root directory and add your `FIREBASE_API_KEY` and other sensitive information.
    *   Make sure to add `firebase_key.json` and `.env` to your `.gitignore` file to avoid committing them.

5.  **Run the database migrations:**
    ```bash
    python manage.py migrate
    ```

6.  **Run the development server:**
    ```bash
    python manage.py runserver
    ```

7.  **Access the application:**
    Open your browser and navigate to `http://127.0.0.1:8000/`.

---

## 🎯 **Outcomes**

The primary outcome of this project is a fully functional, AI-powered personal finance management application that allows users to:

*   Effortlessly track their income and expenses.
*   Gain a clear understanding of their financial health through visualizations.
*   Set and manage budgets to achieve their financial goals.
*   Leverage AI to automate the process of expense categorization.

The project serves as a practical example of integrating a powerful backend framework like Django with modern frontend technologies and AI services to create a real-world application.

---

## 👨‍💻 **Our Super Cool Team**
> Meet the talented developers behind **Neural Budget AI**!

<table align="center">
  <tr>
    <td align="center">
      <img src="https://media.licdn.com/dms/image/v2/D4D03AQH3vXlFbqUqWA/profile-displayphoto-shrink_800_800/profile-displayphoto-shrink_800_800/0/1688562310995?e=1744243200&v=beta&t=oJiUZJcw6zDy8uojrKHh9veZeVSTDaoChbI_KDHRCwY" width="100px" alt="Thura Kyaw"/>
      <br><b>Thura Kyaw</b><br>Backend Developer<br>
      <a href="https://www.linkedin.com/in/thurakyaw/"><img src="https://img.shields.io/badge/-LinkedIn-blue?style=flat-square&logo=linkedin"></a>
      <a href="https://github.com/codes71"><img src="https://img.shields.io/badge/-GitHub-black?style=flat-square&logo=github"></a>
    </td>
    <td align="center">
      <img src="https://media.licdn.com/dms/image/v2/D4D03AQHOnM4yGqWUtA/profile-displayphoto-shrink_800_800/profile-displayphoto-shrink_800_800/0/1732121458518?e=1744243200&v=beta&t=CtHZ2_BWUv68mQFqStRAa-D2shThf-Fw0InjzyTSlJE" width="100px" alt="Hansakunvar Rathod"/>
      <br><b>Hansakunvar Rathod</b><br>ML Engineer<br>
      <a href="https://www.linkedin.com/in/hansha-rathod-34883a251/"><img src="https://img.shields.io/badge/-LinkedIn-blue?style=flat-square&logo=linkedin"></a>
      <a href="https://github.com/Hansha111"><img src="https://img.shields.io/badge/-GitHub-black?style=flat-square&logo=github"></a>
    </td>
    <td align="center">
      <img src="https://media.licdn.com/dms/image/v2/D4D03AQGGzv0ND6MTkg/profile-displayphoto-shrink_800_800/profile-displayphoto-shrink_800_800/0/1711904070755?e=1744243200&v=beta&t=5rCWH1j3LQW4ZF3hJWFKoREiqDc5T_-XOUznH8rAv-s" width="100px" alt="Anmol Kumar Singh"/>
      <br><b>Anmol Kumar Singh</b><br>Full Stack Developer<br>
      <a href="https://www.linkedin.com/in/anmolkumaarsiingh/"><img src="https://img.shields.io/badge/-LinkedIn-blue?style=flat-square&logo=linkedin"></a>
      <a href="https://github.com/Anmolkumaarsiing"><img src="https://img.shields.io/badge/-GitHub-black?style=flat-square&logo=github"></a>
    </td>
    <td align="center">
      <img src="https://media.licdn.com/dms/image/v2/D5603AQHROsUyQePjKw/profile-displayphoto-shrink_800_800/profile-displayphoto-shrink_800_800/0/1700139200145?e=1744243200&v=beta&t=1Bm59_kLVIKGrofqysE795zJqrJj30UyJAm2GQvgOgc" width="100px" alt="Harsh"/>
      <br><b>Harsh</b><br>Frontend Developer<br>
      <a href="https://www.linkedin.com/in/harsh-choudhary-08b00b266/"><img src="https://img.shields.io/badge/-LinkedIn-blue?style=flat-square&logo=linkedin"></a>
      <a href="https://github.com/Harshchoudhary07"><img src="https://img.shields.io/badge/-GitHub-black?style=flat-square&logo=github"></a>
    </td>
  </tr>
</table>


## 📩 **Contact Us**
📧 Reach out to us via Email or Social Media!  
<p align="center">
  <a href="mailto:2203031050045@paruluniversity.ac.in"><img src="https://img.shields.io/badge/Email-Send-blue?style=flat-square&logo=gmail"></a>
  <a href="https://www.linkedin.com/in/anmolkumaarsiingh"><img src="https://img.shields.io/badge/LinkedIn-Connect-blue?style=flat-square&logo=linkedin"></a>
  <a href="[https://github.com/your-repo](https://github.com/Anmolkumaarsiing"><img src="https://img.shields.io/badge/GitHub-Follow-black?style=flat-square&logo=github"></a>
</p>
