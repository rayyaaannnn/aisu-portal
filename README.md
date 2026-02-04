# AISU Portal

A role-based web platform built using **Django** to monitor and manage members of **AISU** during the observation period.
This project is designed as an **IT task** to demonstrate basic web development, authentication, and role management.

---

## Objective

The purpose of this project is to:

* Provide **proof of work** during the observation period
* Create a **centralized platform** to manage AISU members
* Assign and control access based on **user roles**

This task is mandatory for IT team candidates to proceed further in the selection process.

---

## User Roles

The platform supports the following roles:

1. **Super Admin**

   * Full control over the system
   * Manages all users and roles
   * Access to Django Admin Panel

2. **IT Team**

   * Manages technical operations
   * Can monitor users and data

3. **State Team**

   * Manages state-level members

4. **District Team**

   * Manages district-level members

Each role is redirected to its own dashboard after login.

---

## Features (Current)

* Django project setup
* User authentication (login/logout)
* Role-based access control
* Django Admin Panel enabled
* GitHub version control

---

## Tech Stack

* **Backend:** Django (Python)
* **Frontend:** Django Templates (HTML, CSS)
* **Database:** SQLite (default)
* **Version Control:** Git & GitHub

---

## How to Run the Project Locally

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/aisu-portal.git
cd aisu_portal
```

### 2. Install dependencies

```bash
pip install django
```

### 3. Apply migrations

```bash
python manage.py migrate
```

### 4. Create superuser

```bash
python manage.py createsuperuser
```

### 5. Run the server

```bash
python manage.py runserver
```

### 6. Open in browser

```
http://127.0.0.1:8000/
```

Admin Panel:

```
http://127.0.0.1:8000/admin/
```

---

## Project Status

🚧 **Under active development**
Planned next steps:

* Custom dashboards for each role
* Member management system
* Role assignment via admin panel
* UI improvements

---

## Note

This project is developed as part of the **AISU IT Team observation task** and serves as a demonstration of basic web development and role-based system design.

---
