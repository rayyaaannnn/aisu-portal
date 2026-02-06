# TODO: Project Reorganization - Separate Backend and Frontend

## Completed - Folder Structure
- [x] 1. Create `backend/` folder for Django project
- [x] 2. Move backend files to backend/:
  - aisu_portal/
  - accounts/
  - manage.py
  - db.sqlite3
  - requirements.txt
  - README.md
- [x] 3. Keep frontend/ as is (React/Vite)

## New Project Structure
```
aisu-portal/
├── backend/          # Django REST API + Templates
│   ├── aisu_portal/  # Django settings, urls, wsgi
│   ├── accounts/     # Django app (models, views, templates)
│   ├── manage.py
│   ├── db.sqlite3
│   └── requirements.txt
└── frontend/         # React/Vite SPA
    ├── src/          # React components
    ├── public/
    ├── package.json
    └── vite.config.js
```

## Running the Project

### Backend (Terminal 1):
```bash
cd backend
python manage.py runserver 8000
```

### Frontend (Terminal 2):
```bash
cd frontend
npm run dev
```

## Next Steps - Building Inside Pages
- Design dashboard views for each role
- Connect React components to Django REST API
- Implement role-based access control
