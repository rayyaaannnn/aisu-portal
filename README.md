# AISU Website — Complete System (v2 Final)

**All India Students Union (AISU)** — Full-stack web portal matching the WSS specification.

---

## Quick Start

### 1. Install Python dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure email (optional but recommended)
Set environment variables before running:
```bash
export SMTP_USER="aisu4india@gmail.com"
export SMTP_PASS="your-gmail-app-password"
export JWT_SECRET_KEY="your-secret-key-change-this"
export SECRET_KEY="your-flask-secret-change-this"
```

### 3. Start the backend
```bash
cd backend
python app.py
```
Backend runs at: `http://localhost:5000`

### 4. Open the frontend
Open any `.html` file in the root folder directly in your browser, or serve it:
```bash
cd ..   # back to root
python -m http.server 8080
```
Frontend at: `http://localhost:8080`

---

## Default Admin Login
- **URL**: `http://localhost:8080/login.html`
- **Email**: `admin@aisu4india.in`
- **Password**: `Admin@AISU2024`

---

## Pages

| Page | URL | Description |
|------|-----|-------------|
| Home | `index.html` | Landing page with announcements |
| Login | `login.html` | Login with email / mobile / member ID |
| **Dashboard** | `dashboard.html` | **NEW** — User dashboard (certs, membership, internships) |
| Admin Portal | `admin.html` | Full admin with 17 panels |
| Primary Membership | `primary-membership.html` | Apply for primary membership |
| Student Membership | `student-membership.html` | Apply for student membership |
| Competition | `competition.html` | Browse & register for competitions |
| Complaint | `complaint.html` | File & track complaints |
| Certificate Verify | `cert-verify.html` | Verify by cert no / mobile / email |
| Internship | `internship.html` | Apply for internship |
| Innovation Cell | `innovations.html` | Submit innovation proposals |
| Affiliation | `affiliation.html` | Organization affiliation |
| Gallery | `gallery.html` | Gallery, results & publications |
| Press | `press.html` | Press releases & announcements |
| Our Team | `team.html` | Dynamic team directory with filters |
| About | `about.html` | About AISU |
| Contact | `contact.html` | Contact + state officials directory |

---

## Backend API Routes

| Prefix | Module | Key Features |
|--------|--------|--------------|
| `/api/auth` | auth.py | Login (email/mobile/memberID), OTP forgot password, JWT refresh |
| `/api/members` | members.py | Primary membership CRUD, approve/reject, role-status, renewal |
| `/api/students` | students.py | Student membership, membership status check |
| `/api/complaints` | complaint.py | Tiered-access complaints, action log, document upload |
| `/api/competitions` | competition.py | Create, register (fee-gated), submit, quiz, results |
| `/api/certs` | certs.py | Issue, verify (cert/mobile/email), revoke, reissue, my-certs |
| `/api/cert-templates` | cert_templates.py | Upload templates, generate bulk certs, Excel import |
| `/api/internship` | internship.py | Apply, status tracking, completion cert auto-trigger |
| `/api/icell` | icell.py | Submit proposal, approve, forward to investor, fund disbursement |
| `/api/affiliation` | affiliation.py | Organization affiliation |
| `/api/quiz` | quiz.py | WebSocket quiz rooms |
| `/api/admin` | admin.py | Stats, press, announcements, gallery, results, publications, users |
| `/api/contact` | contact.py | Contact form, state officials directory |

---

## What's New in This Version (vs original V2)

### Backend
- ✅ **Login** accepts email, mobile number, or unique member ID
- ✅ **Forgot password** with 6-digit OTP via email
- ✅ **Duplicate registration** merges roles instead of creating new account
- ✅ **Internship** full status tracking (Applied → Shortlisted → Selected → In Progress → Completed)
- ✅ **Internship completion** auto-triggers certificate issuance
- ✅ **Certificate verification** by mobile number or email (returns all certs)
- ✅ **Certificate records** admin panel — view all, search, reissue, revoke
- ✅ **Gallery management** — admin can upload event photos by category
- ✅ **Competition results** — admin publishes winners with photos
- ✅ **Publications** — admin publishes essays/artwork from competitions
- ✅ **ICell investor forwarding** — forward approved proposals to investors by email
- ✅ **ICell fund disbursement** — record and notify innovator when funds arrive
- ✅ **Appointment order email** sent to national team on member approval
- ✅ **State officials directory** endpoint for Contact Us page
- ✅ **Competition fee gate** — active student members get free access; lapsed/no membership pay per-competition
- ✅ **File uploads** now accept docx/xlsx/pptx/mp4 in addition to images/PDF
- ✅ **Uploaded files** served statically at `/uploads/`

### Frontend
- ✅ **dashboard.html** — Complete user dashboard with 8 panels:
  - Overview with membership status + stat cards
  - My Profile
  - Membership Status (primary + student with expiry)
  - My Certificates
  - Performance Reports (upload)
  - My Competitions
  - My Internships with progress tracker
  - Innovation Cell proposals
  - Complaint tracker
- ✅ **login.html** — Regular users now redirected to dashboard (not index)
- ✅ **admin.html** — 5 new panels: Gallery, Competition Results, Publications, Cert Records, Internship Status
- ✅ **gallery.html** — Loads live data from backend (gallery items, results, publications)
- ✅ **team.html** — Dynamic member directory with state/level filters
- ✅ **contact.html** — Loads state officials with official emails dynamically

---

## Requirements (requirements.txt)
```
flask
flask-cors
flask-jwt-extended
flask-socketio
bcrypt
python-dateutil
APScheduler
openpyxl
python-docx
```
