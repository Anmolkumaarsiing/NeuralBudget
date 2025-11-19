# Neural Budget AI - Comprehensive Documentation

## Introduction

**Neural Budget AI** is an AI-powered personal finance management system designed to simplify expense tracking, budgeting, and financial insights. It integrates Django backend with Firebase for authentication and data storage, leveraging AI for OCR-based expense extraction, predictive analytics, and a generative AI chatbot. The project is based on the research paper *"NeuralBudget: An AI-Powered Personal Finance Management System"*, aiming to reduce manual data entry by 80% and improve prediction accuracy by 15%.

### Key Objectives
- Automate expense categorization using OCR and LLMs.
- Provide real-time budget tracking and alerts.
- Offer visual spending analysis and predictive insights.
- Ensure secure, user-specific data handling via Firebase Firestore.
- Deliver an interactive UI with a chatbot for financial queries.

### Project Status
- **Active Development**
- **Repository Size**: ~ (from badges in README)
- **Languages**: Primarily Python (Django), JavaScript, HTML/CSS.
- **Contributors**: Thura Kyaw (Backend), Hansakunvar Rathod (ML Engineer), Anmol Kumar Singh (Full Stack), Harsh (Frontend).

### Contact
- Email: 2203031050045@paruluniversity.ac.in
- LinkedIn/GitHub: Links to team members in README.

## Tech Stack

### Backend
- **Framework**: Django, Django REST Framework
- **Database**: PostgreSQL/SQLite (local), Firebase Firestore (primary, real-time)
- **Authentication**: Firebase Auth
- **Configuration**: `.env` for secrets (e.g., `FIREBASE_API_KEY`), `firebase_key.json` in `apps/`

### Frontend
- **Technologies**: HTML, CSS, JavaScript
- **Static Assets**: Served from `apps/<app>/static/<app>/` (CSS, JS, images)
- **Templates**: Django templates in `apps/<app>/templates/<app>/`

### AI/ML Components
- **OCR & Categorization**: Google Gemini 1.5 Flash for receipt/transaction image processing and categorization
- **Predictive Analytics**: Scikit-learn, NumPy, Pandas for forecasting expenses
- **Generative AI**: Google Generative AI for chatbot and categorization
- **Visualization**: Matplotlib, Seaborn for charts/graphs
- **Directories**:
  - `AI/categorization/`: OCR scripts (e.g., `run_ocr.py`, `structured_output.py`)
  - `AI/Chatbot/`: `chatbot.py` for AI queries
  - `AI/spending_analysis/`: `analysis.py` for insights
  - `ML testings/`: Notebooks and tests (e.g., `Monthly_expense_visuals.ipynb`, OCR tests)

### Utilities
- **Scripts**: In `scripts/` for data generation (e.g., `generate_meaningful_data.py`, `add_default_categories.py`)
- **Requirements**: `requirement.txt` (pip install), plus ML-specific in `ML testings/text_recognition/requirement.txt`

## Project Architecture

The project follows a modular Django structure with separate apps for concerns. Core app handles base templates and middleware. Data is primarily stored in Firestore (user-specific collections), with Django for routing/views. No heavy Django models observed (likely minimal, as Firestore is primary).

### Directory Structure Overview
```
NeuralBudget/
├── AI/                          # AI/ML scripts and tests
│   ├── categorization/          # OCR for expenses
│   ├── Chatbot/                 # Generative AI chatbot
│   └── spending_analysis/       # Analytics scripts
├── apps/                        # Django apps
│   ├── accounts/                # User auth and profiles
│   ├── budgets/                 # Budget setting and tracking
│   ├── common_utils/            # Shared utilities (auth, Firebase)
│   ├── core/                    # Base views, templates, middleware
│   ├── datagen/                 # Data generation tools
│   ├── insights/                # Spending analysis and predictions
│   ├── ml_features/             # ML services (e.g., chatbot)
│   ├── reports/                 # Dashboards and visualizations
│   └── transactions/            # Transaction management
├── media/                       # User uploads (e.g., receipts)
├── ML testings/                 # ML experiments and notebooks
├── neural_budget/               # Django project settings
│   ├── settings.py              # Config (includes Firebase, apps)
│   ├── urls.py                  # Root URL routing
│   └── wsgi.py/asgi.py          # Deployment
├── scripts/                     # Utility scripts
├── .gitignore                   # Excludes secrets (firebase_key.json, .env)
├── manage.py                    # Django management
├── README.md                    # Project overview
└── requirement.txt              # Dependencies
```

### Database and Data Flow
- **Firestore Structure**: User-specific docs/collections for profiles, transactions, budgets.
- **Local DB**: SQLite/PostgreSQL for migrations (minimal use).
- **Data Entry**: Manual (forms) or AI (OCR upload → extract → categorize → store).
- **Sessions**: User ID in session for personalization.

## App-by-App Breakdown

### 1. accounts/
Handles user authentication, profiles, and security.

- **Key Files**:
  - `models.py`: Likely empty or minimal (Firestore handles users).
  - `forms.py`: Forms for login, signup, profile updates, password reset.
  - `views.py`: Login/register/logout, profile view/update, password reset (email-based).
  - `services.py`: Firebase integration for auth and profile ops.
  - `urls.py`: Routes like `/login/`, `/profile/`, `/reset-password/`.
  - `static/accounts/`: CSS (login.css, profile.css, reset.css), JS (auth.js, profile.js, signOut.js), images (login.png, signup.png).
  - `templates/accounts/`: login.html, profile.html, reset forms.

- **Functionality**:
  - Secure Firebase login/signup.
  - Profile management (name, picture).
  - Password reset via email link.
  - Usage: Users access via `/accounts/login/`; session sets `user_id`.

### 2. budgets/
Manages monthly budgets, categories, and alerts.

- **Key Files**:
  - `models.py`: Budget models (categories, limits; possibly Firestore-mapped).
  - `views.py`: Set/view budgets, smart categorization.
  - `services.py`: Budget calculations, alerts.
  - `urls.py`: Routes for budget setting.
  - `static/budgets/`: CSS (savings_goals.css), JS (smart_categorization.js? inferred).
  - `templates/budgets/`: set_budget.html, smart_categorization.html, Smart_saver.html.

- **Functionality**:
  - Set category budgets (e.g., food, travel).
  - Smart categorization for new expenses.
  - Warnings for overspending.
  - Usage: Upload receipt → AI categorizes → checks against budget.

### 3. common_utils/
Shared utilities for auth and Firebase.

- **Key Files**:
  - `auth_utils.py`: Helper for user names/emails.
  - `firebase_service.py`: Firestore ops (get_user_profile, etc.).
  - `firebase_config.py`: Firebase initialization.
  - `views_utils.py`: Common view helpers.

- **Functionality**:
  - Centralized Firebase access.
  - Auth checks and profile fetching.
  - Usage: Imported across apps, e.g., `get_user_profile(user_id)` returns dict with name, email.

### 4. core/
Base application structure, middleware, and global templates.

- **Key Files**:
  - `models.py`: Likely empty.
  - `views.py`: Index, chatbot views.
  - `urls.py`: Root routes (e.g., `/`, `/chatbot/`).
  - `auth_middleware.py`: Session-based auth checks.
  - `context_processors.py`: 
    ```
    # apps/core/context_processors.py
    from apps.common_utils.auth_utils import get_user_full_name
    from apps.common_utils.firebase_service import get_user_profile

    def user_full_name(request):
        full_name = None
        user_id = request.session.get('user_id')
        if user_id:
            user_profile = get_user_profile(user_id)
            if user_profile:
                full_name = get_user_full_name(user_profile)
        return {'full_name': full_name}
    ```
    - **Usage**: Added to `settings.py` TEMPLATES['OPTIONS']['context_processors']. Provides `{{ full_name }}` in all templates. Fetches user profile from Firestore via session `user_id`, extracts full name. Ensures personalized UI (e.g., "Welcome, [Full Name]") without repeated queries. Handles unauthenticated users gracefully (full_name=None).
  - `static/core/`: Favicon, CSS/JS/images/videos.
  - `templates/core/`: base.html (extends for all pages), _sidebar.html, _topbar.html, index.html, chatbot.html, output.png (likely OCR result).

- **Functionality**:
  - Global layout (sidebar/topbar).
  - Auth middleware for protected routes.
  - Chatbot integration.
  - Usage: All pages extend base.html; context_processor auto-injects user name.

### 5. datagen/
Tools for generating test/historical data.

- **Key Files**:
  - `models.py`: Data gen models.
  - `views.py`: UI for generation.
  - `services.py`: Data insertion logic.
  - `templates/datagen/`: data_generator.html, historical_data_generator.html, overview.html, delete_data.html.
  - `static/datagen/`: CSS/JS.

- **Functionality**:
  - Generate random/meaningful transactions for testing.
  - Delete test data.
  - Usage: Access `/datagen/` for UI; scripts like `generate_meaningful_data.py` for CLI.

### 6. insights/
AI-driven financial insights and predictions.

- **Key Files**:
  - `models.py`: Insight models.
  - `views.py`: Render analysis pages.
  - `services.py`: ML computations.
  - `templates/insights/`: spending_insights.html, predictive_analysis.html, investment_guide.html.
  - `static/insights/`: CSS, JS, images.

- **Functionality**:
  - Spending breakdowns (charts).
  - Expense forecasting.
  - Investment tips.
  - Usage: `/insights/spending_insights/`; pulls from Firestore, runs Scikit-learn models.

### 7. ml_features/
ML services, focused on chatbot.

- **Key Files**:
  - `models.py`: ML feature models.
  - `views.py`: ML endpoints.
  - `services/chatbot_service.py`: Chatbot logic using Google GenAI.
  - `urls.py`: Routes.

- **Functionality**:
  - Integrates GenAI for queries (e.g., "What's my spending trend?").
  - Usage: Called from core/chatbot.html; processes user input → AI response.

### 8. reports/
Dashboards and visualizations.

- **Key Files**:
  - `models.py`: Report models.
  - `views.py`: Dashboard rendering.
  - `services.py`: Data aggregation.
  - `templates/reports/`: dashboard.html, visualize.html.
  - `static/reports/`: CSS/JS.

- **Functionality**:
  - Transaction history filters.
  - Charts (Matplotlib/Seaborn rendered).
  - Usage: `/reports/dashboard/`; aggregates Firestore data.

### 9. transactions/
Core expense/income tracking.

- **Key Files**:
  - `schemas.py`: Data schemas (Pydantic? for validation).
  - `views.py`: Add/view transactions.
  - `services.py`: CRUD with Firestore, categorization.
  - `urls.py`: Routes.
  - `static/transactions/`: CSS/JS (transaction_history.js).
  - `templates/transactions/`: add_transaction.html, transaction_history.html.

- **Functionality**:
  - Manual add (form with categories).
  - AI upload (image → OCR → categorize).
  - History search/filter.
  - Usage: `/transactions/add/`; stores in user Firestore collection.

## AI Components in Detail

### OCR for Smart Categorization
- **Location**: `AI/categorization/`
- **Files**:
  - `run_ocr.py`: Processes images (e.g., receipts) using Google Gemini 1.5 Flash.
  - `structured_output.py`: Parses OCR text into structured data (amount, merchant, date).
- **Usage**: In budgets/smart_categorization.html, upload image → run_ocr → LLM categorizes (e.g., "Groceries") → save to transactions.
- **Example Flow**: Image → OCR extracts "Coffee $5" → GenAI classifies as "Dining" → Check budget.

### Chatbot
- **Location**: `AI/Chatbot/chatbot.py`, `apps/ml_features/services/chatbot_service.py`
- **Functionality**: Google GenAI for natural language queries (e.g., "How much did I spend on food?").
- **Usage**: `/core/chatbot/`; JS in chatbot.html sends messages → service processes → displays response. Integrates with Firestore for user data.

### Predictive Analytics
- **Location**: `AI/spending_analysis/analysis.py`, `apps/insights/services.py`
- **Functionality**: Uses historical transactions → Scikit-learn models (e.g., regression) for forecasts.
- **Usage**: In predictive_analysis.html; computes trends, alerts (e.g., "Food expenses may exceed $200 next month").

### Visualizations
- **Notebooks**: `AI/Monthly_expense_visuals.ipynb` for prototyping.
- **Integration**: Rendered in reports/insights via Matplotlib/Seaborn → static images or JS charts.

## Setup and Running Locally

### Prerequisites
- Python 3.8+
- Git, Pip, Virtualenv
- Firebase project (for Auth/Firestore)
- Google GenAI API key

### Step-by-Step Setup
1. **Clone Repo**:
   ```
   git clone https://github.com/Anmolkumaarsiing/NeuralBudget.git
   cd NeuralBudget
   ```

2. **Virtual Environment**:
   ```
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```
   pip install -r requirement.txt
   # For ML: pip install scikit-learn google-generativeai matplotlib seaborn
   ```

4. **Firebase Setup**:
   - Download service account key as `firebase_key.json` → place in `apps/`.
   - Create `.env` in root:
     ```
     FIREBASE_API_KEY=your_api_key
     # Other keys (GenAI, etc.)
     ```
   - Add to `.gitignore`: `firebase_key.json`, `.env`.

5. **Migrations** (if using local DB):
   ```
   python manage.py migrate
   ```

6. **Run Server**:
   ```
   python manage.py runserver
   ```
   - Access: http://127.0.0.1:8000/

7. **Data Generation** (Optional):
   - Run scripts: `python scripts/generate_meaningful_data.py`
   - Or use `/datagen/` UI.

### Usage Examples
- **Register/Login**: `/accounts/login/` → Firebase auth.
- **Add Transaction**: `/transactions/add/` → Manual or upload image (OCR auto-fills).
- **Set Budget**: `/budgets/set_budget/` → Select category, amount.
- **View Insights**: `/insights/spending_insights/` → Charts from Firestore.
- **Chatbot**: `/core/chatbot/` → Ask "Budget status?" → AI responds using user data.
- **Context Processor Example**: In any template, `{{ full_name }}` shows user's name (fetched via session → Firestore). E.g., in base.html topbar: "Hi, {{ full_name }}!" – Processes on each request if user_id in session.

### Testing and Development
- **Scripts**: `scripts/add_default_categories.py` (pre-populate categories), `scripts/delete_user_transactions.py` (cleanup).
- **Data Gen**: `/datagen/historical_data_generator.html` for bulk inserts.
- **ML Testing**: Run notebooks in `AI/` or `ML testings/`.
- **Edge Cases**: Handle no user (full_name=None), invalid images (OCR fallback to manual), Firestore errors (middleware catches).

## Deployment Considerations
- **Hosting**: Heroku/Vercel for Django; Firebase for backend services.
- **Security**: Secrets in env; Firebase rules for user isolation.
- **Scalability**: Firestore auto-scales; Cache predictions.
- **Monitoring**: Add logging in views/services.

## Research and Outcomes
- **Findings**: 80% reduction in manual entry via OCR/LLM; 15% better predictions.
- **Outcomes**: Holistic tool for tracking, budgeting, insights; extensible for more AI features.

## Troubleshooting
- **Firebase Errors**: Check `firebase_key.json` path and `.env`.
- **OCR Fails**: Ensure Google GenAI API key is set; test with `AI/categorization/run_ocr.py`.
- **No Models**: Project leans on Firestore; add Django models if needed for local caching.
- **Templates Missing**: Extend `core/base.html` in all apps.

This documentation covers all aspects based on project structure and files. For code-level details, inspect individual .py files.
