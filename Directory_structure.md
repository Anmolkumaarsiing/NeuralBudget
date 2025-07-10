Our current directory organization, while functional, presents challenges for long-term management, especially with the evolving data storage strategy. Key motivations for this proposal include:

- **Single Source of Truth (MongoDB):** To consolidate all application data into a unified MongoDB database, eliminating the need for separate relational database models and Firestore interactions. This simplifies data management, reduces potential inconsistencies, and streamlines development.
- **Improved Modularity:** Breaking down the application into distinct, self-contained Django apps, each responsible for a specific domain.
- **Clear Separation of Concerns:** Ensuring that models (now MongoEngine Documents), views, templates, static files, and business logic are logically grouped and easily discoverable.
- **Enhanced Maintainability & Scalability:** A well-defined structure facilitates easier onboarding for new developers, simplifies debugging, and supports future feature expansion without introducing complexity.
- **Adherence to Best Practices:** Adopting a structure that aligns with common Django project layouts and modern software engineering principles.

#### ** Proposed Directory Structure**

```
D:/NeuralBudget/
├── .git/                    # Git version control
├── .github/                 # Optional: For CI/CD workflows (e.g., GitHub Actions)
├── .vscode/                 # VS Code specific settings
├── docs/                    # Project documentation, design notes, API docs, etc.
├── scripts/                 # Utility scripts (e.g., data import, custom management commands)
├── requirement.txt          # Python dependencies (will include mongoengine)
├── manage.py                # Django's command-line utility
├── README.md                # Project overview
├── neural_budget/           # Main Django project settings (your project root)
│   ├── __init__.py
│   ├── asgi.py              # ASGI config for async applications
│   ├── settings.py          # Project settings (MongoDB connection config)
│   ├── urls.py              # Project-level URL routing
│   └── wsgi.py              # WSGI config for traditional deployments
├── apps/                    # Directory to hold all Django applications
│   ├── core/                # Core app for common utilities, base templates, shared components
│   │   ├── __init__.py
│   │   ├── admin.py         # Django admin configurations
│   │   ├── apps.py          # App configuration
│   │   ├── models.py        # MongoEngine Documents for core entities (if any)
│   │   ├── urls.py          # App-specific URL routing
│   │   ├── views.py         # Core views
│   │   ├── static/          # Static files (CSS, JS, images) specific to this app
│   │   └── templates/       # HTML templates specific to this app
│   ├── accounts/            # User authentication, registration, profile management
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py        # MongoEngine Documents for User/Account profiles
│   │   ├── urls.py
│   │   ├── views.py
│   │   ├── forms.py         # Forms for authentication, user profiles
│   │   ├── static/
│   │   └── templates/
│   ├── transactions/        # Handles income, expenses, categories
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py        # MongoEngine Documents for Transaction, Category
│   │   ├── urls.py
│   │   ├── views.py
│   │   ├── services.py      # Business logic for transactions (e.g., add, update, delete)
│   │   ├── static/
│   │   └── templates/
│   ├── budgets/             # Handles budget creation, tracking
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py        # MongoEngine Documents for Budget
│   │   ├── urls.py
│   │   ├── views.py
│   │   ├── services.py      # Business logic for budgets
│   │   ├── static/
│   │   └── templates/
│   ├── reports/             # For dashboard, visualizations, aggregated data
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py        # (Optional: MongoEngine Documents for cached reports or complex report definitions)
│   │   ├── urls.py
│   │   ├── views.py
│   │   ├── services.py      # Logic for generating reports/aggregations
│   │   ├── static/
│   │   └── templates/
│   ├── ml_features/         # Machine Learning integration
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── models.py        # (If ML models need database storage in MongoDB)
│   │   ├── services.py      # ML prediction/training logic
│   │   ├── urls.py
│   │   └── views.py
│   └── common_utils/        # General utilities not tied to a specific app
│       ├── __init__.py
│       ├── views_utils.py   # Generic view-related utilities
│       └── auth_utils.py    # Authentication-related utilities (if not specific to 'accounts' app)
```

#### **Explanation of Key Changes and Benefits**

- **`apps/` Directory:** All Django applications will now reside under an `apps/` directory. This provides a clear separation between project-level configuration and application-specific code, making the project root cleaner. `INSTALLED_APPS` in `settings.py` will be updated accordingly (e.g., `'apps.accounts'`, `'apps.transactions'`).
- **MongoDB as Single Source of Truth:**
  - The `models.py` files within each app will now define **MongoEngine Documents** instead of Django ORM models. This ensures all persistent data is stored in MongoDB.
  - The `neural_budget/settings.py` file will contain the necessary `mongoengine.connect` configuration.
  - All existing Firestore integration code will be removed, and any data previously stored in Firestore will be migrated to MongoDB.
- **Modular Applications:**
  - **`core`**: For very fundamental, cross-cutting concerns or base templates.
  - **`accounts`**: Dedicated to user authentication, registration, and profile management.
  - **`transactions`**: Manages income, expenses, and categories, with `Transaction` and `Category` MongoEngine Documents.
  - **`budgets`**: Manages budget creation and tracking, with `Budget` MongoEngine Documents.
  - **`reports`**: Focuses on generating dashboard data, visualizations, and complex reports, leveraging MongoDB for data aggregation.
  - **`ml_features`**: A dedicated app for machine learning components, with the flexibility to store ML-related data in MongoDB.
  - **`common_utils`**: A designated place for truly generic utility functions that are not specific to any single application.
- **`services.py`:** The introduction of `services.py` files within apps promotes a clean separation of business logic from views and MongoEngine Documents. For example, `transactions/services.py` will encapsulate functions like `create_transaction` or `get_monthly_expenses`, making the codebase more organized and testable.
- **Clearer Data Ownership:** Each app will clearly "own" its set of MongoEngine Documents. This simplifies data management and understanding, as data structures and their related logic are contained within their specific app.
- **`docs/` and `scripts/`:** Dedicated directories for project documentation and utility scripts, further decluttering the root directory.

This transition will require:

- **Configuration Update:** Modifying `settings.py` for MongoDB connection.
- **Model Redefinition:** Rewriting existing Django ORM models (if any) and Firestore data structures as MongoEngine Documents.
- **Code Refactoring:** Updating all views, services, and other logic to interact with MongoEngine Documents instead of Django ORM or Firestore APIs.
- **Data Migration:** A one-time process to transfer existing data from any current storage solutions (relational database, Firestore) into MongoDB.
