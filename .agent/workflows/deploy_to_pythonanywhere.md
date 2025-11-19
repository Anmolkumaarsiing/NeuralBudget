---
description: Deploy Django App to PythonAnywhere
---

This workflow guides you through deploying your Django application to PythonAnywhere.

## Prerequisites
1.  A [PythonAnywhere](https://www.pythonanywhere.com/) account.
2.  Your code pushed to a GitHub repository.

## Step 1: Prepare your Code (Local)
1.  **Update `settings.py`**:
    *   Ensure `ALLOWED_HOSTS` can read from environment variables or includes your PythonAnywhere domain (e.g., `['yourusername.pythonanywhere.com']`).
    *   Ensure `STATIC_ROOT` is defined (e.g., `STATIC_ROOT = BASE_DIR / 'staticfiles'`).
    *   Ensure `DEBUG` is set to `False` for production (or controlled by env var).
2.  **Update `requirements.txt`**:
    *   Ensure all dependencies are listed.
    *   Note: `mongoengine` requires a paid PythonAnywhere account to access external databases (like MongoDB Atlas) due to firewall restrictions on free accounts.
3.  **Push changes to GitHub**.

## Step 2: PythonAnywhere Console Setup
1.  Log in to PythonAnywhere and open a **Bash** console.
2.  **Clone your repository**:
    ```bash
    git clone https://github.com/yourusername/your-repo-name.git
    cd your-repo-name
    ```
3.  **Create a Virtual Environment**:
    ```bash
    mkvirtualenv --python=/usr/bin/python3.10 myenv
    # Note: The prompt will change to (myenv)
    ```
4.  **Install Dependencies**:
    ```bash
    pip install -r requirement.txt
    ```
5.  **Set up Environment Variables**:
    *   Create a `.env` file in your project root on PythonAnywhere or set them in the WSGI file later.
    ```bash
    cp .env.example .env  # If you have an example file
    nano .env             # Edit to add your secrets (SECRET_KEY, GEMINI_API_KEY, etc.)
    ```
6.  **Run Migrations**:
    ```bash
    python manage.py migrate
    ```
7.  **Collect Static Files**:
    ```bash
    python manage.py collectstatic
    ```

## Step 3: Web Tab Configuration
1.  Go to the **Web** tab on PythonAnywhere dashboard.
2.  **Add a new web app**:
    *   Click "Add a new web app".
    *   Choose "Manual configuration" (since we are using a virtualenv).
    *   Choose the Python version you used (e.g., 3.10).
3.  **Virtualenv**:
    *   In the "Virtualenv" section, enter the path: `/home/yourusername/.virtualenvs/myenv`
4.  **Code**:
    *   Set "Source code" to: `/home/yourusername/your-repo-name`
    *   Set "Working directory" to: `/home/yourusername/your-repo-name`
5.  **WSGI Configuration File**:
    *   Click the link to edit the WSGI configuration file.
    *   Delete existing content and add:
        ```python
        import os
        import sys

        # path to your project folder
        path = '/home/yourusername/your-repo-name'
        if path not in sys.path:
            sys.path.append(path)

        # Load .env file
        from dotenv import load_dotenv
        project_folder = os.path.expanduser(path)
        load_dotenv(os.path.join(project_folder, '.env'))

        os.environ['DJANGO_SETTINGS_MODULE'] = 'neural_budget.settings'

        from django.core.wsgi import get_wsgi_application
        application = get_wsgi_application()
        ```
    *   *Replace `yourusername` and `your-repo-name` with actual values.*
6.  **Static Files**:
    *   Under "Static files", add a new row:
        *   **URL**: `/static/`
        *   **Directory**: `/home/yourusername/your-repo-name/staticfiles`
7.  **Reload**:
    *   Scroll to the top and click the big green **Reload** button.

## Step 4: Troubleshooting
*   **Check Error Log**: If the site shows an error, check the "Error log" link in the Web tab.
*   **Allowed Hosts**: Make sure your `ALLOWED_HOSTS` in `settings.py` (or `.env`) includes `yourusername.pythonanywhere.com`.
