# TODO: Clean Backend - API Only Setup

## Step 1: Remove Django Templates
- [ ] 1. Remove `backend/accounts/templates/` folder (no longer needed)

## Step 2: Clean Views
- [ ] 2. Remove template-based views from `backend/accounts/views.py`
  - Keep: `login_view`, `logout_view`, `role_redirect` (for JWT)
  - Remove: All `render()` calls for templates (super_admin_dashboard, it_dashboard, state_dashboard, etc.)

## Step 3: Clean URLs
- [ ] 3. Remove template-based URLs from `backend/accounts/urls.py`
  - Keep: JWT endpoints, API endpoints
  - Remove: Dashboard URLs (handled by React)

## Step 4: Clean Main URLs
- [ ] 4. Remove React catch-all route from `backend/aisu_portal/urls.py`

## Step 5: Verify
- [ ] 5. Test Django API still works: `python manage.py runserver`
- [ ] 6. Test React login still works: `npm run dev`
