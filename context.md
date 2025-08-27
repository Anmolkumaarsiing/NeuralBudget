
### Context Processor Implementation for Full Name in Top Bar

To avoid code duplication and ensure consistency, a Django Context Processor can be used to make the user's full name automatically available in all templates, especially for the top bar.

**Steps to Implement:**

1.  **Create `apps/core/context_processors.py`:**
    ```python
    # apps/core/context_processors.py
    from apps.common_utils.auth_utils import get_user_id, get_user_full_name
    from apps.common_utils.firebase_service import get_user_profile

    def user_full_name(request):
        full_name = None
        if request.session.get('user_id'):
            user_id = request.session.get('user_id')
            user_profile = get_user_profile(user_id)
            if user_profile:
                full_name = get_user_full_name(user_profile)
        return {'full_name': full_name}
    ```

2.  **Register the context processor in `neural_budget/settings.py`:**
    Locate the `TEMPLATES` setting and add the path to your new context processor under `OPTIONS['context_processors']`.

    ```python
    # neural_budget/settings.py
    TEMPLATES = [
        {
            # ... other settings ...
            "OPTIONS": {
                "context_processors": [
                    # ... existing context processors ...
                    'apps.core.context_processors.user_full_name', # Add this line
                ],
            },
        },
    ]
    ```

**How it works:**

*   The `user_full_name` function will be called automatically by Django for every request that renders a template.
*   Inside this function, it checks if a `user_id` exists in the session (meaning a user is logged in).
*   If a user is logged in, it fetches their profile from Firestore and constructs their full name.
*   The dictionary `{'full_name': full_name}` is returned, and Django merges this into the context of *all* templates.
*   Therefore, `{{ full_name }}` can be used directly in `_topbar.html` (or any other template) without needing to be explicitly passed from each view.
