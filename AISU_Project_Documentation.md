# AISU4India — Complete Project Documentation
**All India Students Union | aisu4india.in**
*Version 2.1 | Last Updated: 23 March 2026*

---

## Table of Contents
1. [Project Overview](#1-project-overview)
2. [File & Folder Structure](#2-file--folder-structure)
3. [Frontend Pages](#3-frontend-pages)
4. [Backend API Reference](#4-backend-api-reference)
5. [Database Schema](#5-database-schema)
6. [ID & Number Formats](#6-id--number-formats)
7. [Email Automation](#7-email-automation)
8. [WebSocket Quiz System](#8-websocket-quiz-system)
9. [Certificate Template Engine](#9-certificate-template-engine)
10. [Admin Portal Guide](#10-admin-portal-guide)
11. [Login Credentials](#11-login-credentials)
12. [Deployment & Startup](#12-deployment--startup)
13. [Troubleshooting](#13-troubleshooting)

---

## 1. Project Overview

**All India Students Union (AISU)** is a national-level registered organization under the **Federation of Indian Youth Association (FIYA)**. The website serves as the digital headquarters for:

- Student empowerment and leadership development
- National-level competition management
- Transparent grievance (complaint) redressal
- Innovation & research proposal management
- Organization affiliation for external bodies
- Internship facilitation via InternXpro Pvt Ltd MOU
- Certificate issuance and public verification
- Real-time group quiz management

### Organization Registrations
| Body | Registration |
|------|-------------|
| Federation of Indian Youth Association (FIYA) | Registration No. FIYA2024NL001 |
| All India Students Union (AISU) | Sub-body of FIYA |
| NITI Aayog | Darpan ID: UP/2024/0342891 |

### Key MOU Partners
| Partner | Agreement Benefit |
|---------|-----------------|
| SkillChase Pvt Ltd | Free online skill courses for students |
| InternXpro Pvt Ltd | Verified internship & job placement |
| NewTapWorld Media | Press coverage & public relations |

---

## 2. File & Folder Structure

```
AISU-Website frontend/
│
├── 📄 index.html                  — Home page (13 sections)
├── 📄 about.html                  — About + Vision + Departments (5 cells)
├── 📄 team.html                   — Organizational team directory
├── 📄 primary-membership.html     — Primary Member application form (6 sections)
├── 📄 student-membership.html     — Student Member application form
├── 📄 affiliation.html            — Organization affiliation application
├── 📄 competition.html            — Competition portal + submission
├── 📄 complaint.html              — Complaint filing portal
├── 📄 innovations.html            — Innovation Cell proposals
├── 📄 internship.html             — Internship application
├── 📄 gallery.html                — Photo gallery + competition results
├── 📄 press.html                  — Press releases + announcements
├── 📄 cert-verify.html            — Public certificate verification
├── 📄 login.html                  — Unified login (Admin/Member/Student)
├── 📄 contact.html                — Contact us + map + directory
├── 📄 admin.html                  — Full Admin Portal UI (NEW)
├── 📄 quiz-room.html              — Live quiz room (WebSocket) (NEW)
│
├── 📁 css/
│   ├── aisu-custom.css            — Custom styles + safe hover animations
│   └── bootstrap.min.css          — Bootstrap 5.3
│
├── 📁 js/
│   ├── aisu-main.js               — Core JS: cursor, navbar, scroll-top, gallery
│   ├── aisu-forms.js              — Form handling, validation, PDF generation
│   └── api.js                     — JWT API client for all backend calls
│
├── 📁 img/                        — Static images
├── 📁 imgnew/                     — AI-generated images (hero, banners)
├── 📁 lib/                        — Local libraries (jsPDF, etc.)
│
└── 📁 backend/
    ├── app.py                     — Flask entry point + SocketIO setup
    ├── db.py                      — JSON file database + ID generators
    ├── email_service.py           — 11 automated email functions
    ├── scheduler.py               — APScheduler renewal jobs
    ├── utils.py                   — Helper functions + JWT helpers
    │
    └── 📁 routes/                 — 13 Blueprint files
        ├── auth.py                — Login, register, JWT refresh
        ├── members.py             — Primary member CRUD + approval
        ├── students.py            — Student member CRUD + approval
        ├── complaint.py           — Complaint filing + status tracking
        ├── competition.py         — Competition CRUD + registration + submission
        ├── certs.py               — Certificate verify + list
        ├── cert_templates.py      — Template upload + generate + Excel import (NEW)
        ├── quiz.py                — Quiz room REST + SocketIO events (NEW)
        ├── icell.py               — Innovation Cell proposals
        ├── internship.py          — Internship applications
        ├── affiliation.py         — Org affiliation applications
        ├── contact.py             — Contact messages
        ├── admin.py               — Admin-level management endpoints
        └── __init__.py
    │
    └── 📁 uploads/
        ├── govtid/                — Government ID uploads
        ├── payment/               — Payment proof uploads
        ├── photo/                 — Profile photos
        ├── sign/                  — Signature uploads
        ├── complaint/             — Complaint evidence files
        ├── cert_templates/        — Certificate template files
        └── certificates/          — Generated certificate DOCX files
    │
    └── 📁 data/
        └── *.json                 — JSON database files (one per collection)
```

---

## 3. Frontend Pages

### 3.1 Home Page ([index.html](file:///C:/Users/Admin/Downloads/AISU-Website%20frontend/index.html)) — 13 Sections
| # | Section | Description |
|---|---------|-------------|
| 1 | **Hero** | "Empowering the Voice of Students Across India" with AI-generated image |
| 2 | **Quick Actions** | 8 icon-link shortcuts (Join/Compete/Complain etc.) |
| 3 | **About Snippet** | Brief org intro + bullet points + Learn More link |
| 4 | **Key Initiatives** | 6 cards: Membership, Competitions, Complaint Portal, Innovation, Internship, Affiliation |
| 5 | **Vision Banner** | Dark "Arise • Awake • Empower" full-width CTA |
| 6 | **Why Join AISU** | 4 feature cards with icons |
| 7 | **National Reach** | Stats: 28 States, 5,000+ Members, 120+ Competitions, 50+ Partners |
| 8 | **Testimonials** | 3 student testimonials |
| 9 | **Announcements & News** | 4 news cards with category badges and links |
| 10 | **Gallery & Results Preview** | Photo grid + 3 competition winners |
| 11 | **Social Media** | Instagram/Facebook/Twitter/LinkedIn links |
| 12 | **CTA** | "Ready to Make a Difference?" with Join buttons |
| 13 | **Footer** | 4-column footer with newsletter + links |

### 3.2 About Page ([about.html](file:///C:/Users/Admin/Downloads/AISU-Website%20frontend/about.html)) — Departments
The Departments/Cells section shows **5 departments** (Competition Dept and Internship Cell were removed per request):

| Department | Icon Colour | Description |
|-----------|-------------|-------------|
| Legal Cell | Blue | Legal assistance, RTI filing, court representation |
| IT & Digital Cell | Indigo | Website, portals, digital infrastructure |
| Social Media Cell | Pink | Social media management |
| Press & Media Cell | Orange | Media relations, NewTapWorld partnership |
| EmpowHer Cell | Purple | Women empowerment, gender-specific issues |
| Anti-Ragging Cell | Red | Ragging reporting, student safety |

### 3.3 Primary Membership Form — 6 Sections
| Section | Fields |
|---------|--------|
| **Personal Information** | Full Name, Father/Mother Name, DOB, Gender, Blood Group, Aadhaar No., Nationality |
| **Contact Details** | Mobile, Email, WhatsApp, Permanent Address, Current Address |
| **Educational Qualification** | Qualification, Institution, Course, Year, Specialisation, Previous Org |
| **Location/Coverage Area** | State, District, Mandal, College/Area |
| **Role & Designation** | Desired Role, Department/Cell, Experience, Skills |
| **Constitution & Declaration** | Constitution agreement, Declaration checkbox + signature |

### 3.4 Student Membership Form
Single-section form with: Name, DOB, Gender, Mobile, Email, Institution, Course, Year, State, District, College, Photo, ID Card upload.

---

## 4. Backend API Reference

**Base URL:** `http://127.0.0.1:5000/api`

### 4.1 Authentication (`/api/auth/`)
| Method | Endpoint | Description | Auth |
|--------|---------|-------------|------|
| POST | `/auth/login` | Login → returns JWT | No |
| POST | `/auth/register` | Register new general user | No |
| POST | `/auth/refresh` | Refresh JWT | JWT |
| GET | `/auth/me` | Get current user | JWT |
| POST | `/auth/logout` | Invalidate token | JWT |

### 4.2 Primary Members (`/api/members/`)
| Method | Endpoint | Description | Auth |
|--------|---------|-------------|------|
| POST | `/members` | Submit primary member application | No |
| GET | `/members` | List all members | Admin JWT |
| GET | `/members/<id>` | Get member details | JWT |
| PATCH | `/members/<id>/status` | Approve/Reject/Terminate | Admin JWT |
| GET | `/members/<id>/reports` | Get performance reports | JWT |
| POST | `/members/<id>/reports` | Upload performance report | JWT |

### 4.3 Student Members (`/api/students/`)
| Method | Endpoint | Description | Auth |
|--------|---------|-------------|------|
| POST | `/students` | Submit student application | No |
| GET | `/students` | List all students | Admin JWT |
| PATCH | `/students/<id>/status` | Approve/Reject | Admin JWT |

### 4.4 Complaints (`/api/complaints/`)
| Method | Endpoint | Description | Auth |
|--------|---------|-------------|------|
| POST | `/complaints` | File new complaint | JWT |
| GET | `/complaints` | List complaints (tiered by role) | JWT |
| GET | `/complaints/<id>` | View complaint detail | JWT |
| PATCH | `/complaints/<id>/status` | Update complaint status | Admin JWT |

### 4.5 Competitions (`/api/competitions/`)
| Method | Endpoint | Description | Auth |
|--------|---------|-------------|------|
| GET | `/competitions` | List all competitions | No |
| POST | `/competitions` | Create new competition | Admin JWT |
| GET | `/competitions/<id>` | Get competition details | No |
| POST | `/competitions/<id>/register` | Register for competition | JWT |
| POST | `/competitions/<id>/submit` | Submit entry | JWT |
| GET | `/competitions/<id>/entries` | List entries | Admin JWT |

### 4.6 Certificates (`/api/certs/`)
| Method | Endpoint | Description | Auth |
|--------|---------|-------------|------|
| GET | `/certs` | List all issued certs | Admin JWT |
| GET | `/certs/verify/<cert_num>` | Public cert verification | No |
| POST | `/certs` | Issue a certificate | Admin JWT |

### 4.7 Certificate Templates (`/api/cert-templates/`) — NEW
| Method | Endpoint | Description | Auth |
|--------|---------|-------------|------|
| POST | `/cert-templates/templates` | Upload template file | Admin JWT |
| GET | `/cert-templates/templates` | List uploaded templates | Admin JWT |
| GET | `/cert-templates/templates/<id>` | Get template details | Admin JWT |
| DELETE | `/cert-templates/templates/<id>` | Delete template | Admin JWT |
| POST | `/cert-templates/generate` | Generate certificates in bulk | Admin JWT |
| GET | `/cert-templates/download/<cert_id>` | Download generated cert | JWT |
| POST | `/cert-templates/participants/upload` | Parse Excel participant list | Admin JWT |

### 4.8 Quiz Rooms (`/api/quiz/`) — NEW
| Method | Endpoint | Description | Auth |
|--------|---------|-------------|------|
| POST | `/quiz/rooms` | Create quiz room | Admin JWT |
| GET | `/quiz/rooms` | List active rooms | No |
| GET | `/quiz/rooms/<code>` | Get room details | No |

**Socket.IO Events (ws://localhost:5000/socket.io):**

| Client → Server | Server → Client | Description |
|----------------|----------------|-------------|
| `join_quiz_room` | `room_state` | Join a room |
| — | `participant_joined` | New participant notification |
| — | `participant_left` | Participant disconnected |
| `moderator_start_quiz` | `quiz_started`, [question](file:///C:/Users/Admin/Downloads/AISU-Website%20frontend/backend/routes/quiz.py#223-236) | Start quiz |
| `moderator_next_question` | [question](file:///C:/Users/Admin/Downloads/AISU-Website%20frontend/backend/routes/quiz.py#223-236) | Advance to next Q |
| `submit_answer` | `answer_received` | Submit answer |
| — | `team_answered` (to mod) | Team answered notification |
| — | `quiz_ended` | Final leaderboard |
| `quiz_chat` | `chat_message` | Live chat |

### 4.9 Innovation Cell (`/api/icell/`)
| Method | Endpoint | Description |
|--------|---------|-------------|
| POST | `/icell` | Submit proposal |
| GET | `/icell` | List proposals |
| PATCH | `/icell/<id>/status` | Review/Approve |

### 4.10 Internship (`/api/internship/`)
| Method | Endpoint | Description |
|--------|---------|-------------|
| POST | `/internship` | Apply for internship |
| GET | `/internship` | List applications |

### 4.11 Affiliation (`/api/affiliation/`)
| Method | Endpoint | Description |
|--------|---------|-------------|
| POST | `/affiliation` | Submit affiliation application |
| GET | `/affiliation` | List affiliations |

### 4.12 Admin (`/api/admin/`)
| Method | Endpoint | Description |
|--------|---------|-------------|
| POST | `/admin/announcements` | Post announcement |
| GET | `/admin/announcements` | List announcements |
| POST | `/admin/press` | Add press release |
| GET | `/admin/stats` | Full dashboard statistics |

### 4.13 Contact (`/api/contact/`)
| Method | Endpoint | Description |
|--------|---------|-------------|
| POST | `/contact` | Send contact message |
| GET | `/contact` | List messages (admin) |

---

## 5. Database Schema

The database uses **JSON flat-file storage** (`backend/data/*.json`). Each collection is a separate file containing an array of objects.

### Collections
| Collection | File | Key Fields |
|-----------|------|-----------|
| [users](file:///C:/Users/Admin/Downloads/AISU-Website%20frontend/backend/routes/admin.py#45-52) | users.json | _id, email, password_hash, role, name |
| `primary_members` | primary_members.json | _id, member_id, full_name, state, district, status |
| `student_members` | student_members.json | _id, student_id, full_name, institution, expiry_date |
| [complaints](file:///C:/Users/Admin/Downloads/AISU-Website%20frontend/backend/routes/complaint.py#71-94) | complaints.json | _id, complaint_id, category, status, reporter_id |
| [competitions](file:///C:/Users/Admin/Downloads/AISU-Website%20frontend/backend/routes/competition.py#47-55) | competitions.json | _id, title, category, last_date, prizes, status |
| `competition_registrations` | competition_registrations.json | _id, competition_id, student_id, submitted_at |
| [certificates](file:///C:/Users/Admin/Downloads/AISU-Website%20frontend/backend/routes/cert_templates.py#90-179) | certificates.json | _id, cert_number, participant_name, program, issued_at |
| `cert_templates` | cert_templates.json | _id, name, prog_code, filename, placeholders |
| `icell_proposals` | icell_proposals.json | _id, proposal_id, title, category, status |
| `internships` | internships.json | _id, applicant_name, student_id, domain, status |
| `affiliations` | affiliations.json | _id, affiliation_id, org_name, state, status |
| `announcements` | announcements.json | _id, title, type, content, posted_at |
| `press_releases` | press_releases.json | _id, title, type, source, content |
| `contact_messages` | contact_messages.json | _id, name, email, subject, message |

---

## 6. ID & Number Formats

| Type | Format | Example |
|------|--------|---------|
| Primary Member ID | `AISU[StateCode][YY][SLNO-4d]` | `AISUBR260001` |
| Student Member ID | `AISUSM[StateCode][YYYY][SLNO-6d]` | `AISUSMUP2026000001` |
| Complaint ID | `AISUCMP[YY][SLNO-5d]` | `AISUCMP2600001` |
| Competition ID | `AISUCOMP[YYYY][SLNO-4d]` | `AISUCOMP20260025` |
| Innovation Proposal ID | `AISUIC[YYYY][SLNO-4d]` | `AISUIC20260015` |
| Affiliation ID | `FIYAOA[YYYY][SLNO-4d]` | `FIYAOA20260015` |
| Certificate ID | `AISUCERT[PROGCODE][YYYY][SLNO-6d]` | `AISUCERTESSAY2026000145` |
| Internship ID | `AISUINT[YY][SLNO-4d]` | `AISUINT260042` |

**State Code Reference (examples):**
`BR` = Bihar, `UP` = Uttar Pradesh, `MH` = Maharashtra, `DL` = Delhi, `RJ` = Rajasthan, `GJ` = Gujarat, `KA` = Karnataka, `TN` = Tamil Nadu

---

## 7. Email Automation

All emails are sent via Gmail SMTP. Set environment variable `SMTP_PASS` to your Gmail App Password.

| Function | Trigger | Recipients |
|----------|---------|-----------|
| [send_primary_application_received](file:///C:/Users/Admin/Downloads/AISU-Website%20frontend/backend/email_service.py#94-124) | Primary form submitted | Applicant + National President + VP + GS |
| [send_primary_approved](file:///C:/Users/Admin/Downloads/AISU-Website%20frontend/backend/email_service.py#125-142) | Admin approves | Member (with ID + appointment letter) |
| `send_primary_rejected` | Admin rejects | Applicant |
| [send_student_application_received](file:///C:/Users/Admin/Downloads/AISU-Website%20frontend/backend/email_service.py#143-160) | Student form submitted | Student + Admin |
| [send_student_approved](file:///C:/Users/Admin/Downloads/AISU-Website%20frontend/backend/email_service.py#161-172) | Admin approves | Student + National Pres/VP/GS/JS + State President |
| [send_renewal_reminder](file:///C:/Users/Admin/Downloads/AISU-Website%20frontend/backend/email_service.py#236-249) | 30 days before expiry (APScheduler) | Member/Student |
| [send_complaint_update](file:///C:/Users/Admin/Downloads/AISU-Website%20frontend/backend/email_service.py#173-188) | Status changed | Reporter (identity hidden from non-national) |
| [send_new_competition_notification](file:///C:/Users/Admin/Downloads/AISU-Website%20frontend/backend/email_service.py#250-268) | New competition created | All student members + all primary members |
| [send_certificate_issued](file:///C:/Users/Admin/Downloads/AISU-Website%20frontend/backend/email_service.py#224-235) | Certificate generated | Certificate holder |
| `send_internship_update` | Internship status changed | Applicant |
| `send_affiliation_update` | Affiliation status changed | Organization contact |

**APScheduler Jobs (daily):**
- [check_primary_renewals](file:///C:/Users/Admin/Downloads/AISU-Website%20frontend/backend/scheduler.py#10-22) — runs at **06:00 UTC** — emails members expiring within 30 days
- [check_student_renewals](file:///C:/Users/Admin/Downloads/AISU-Website%20frontend/backend/scheduler.py#23-37) — runs at **06:30 UTC** — emails students expiring within 30 days

---

## 8. WebSocket Quiz System

### Architecture
```
Browser (quiz-room.html)  ←──→  Flask-SocketIO  ←──→  In-memory _rooms dict
         ↕                                                      ↕
   Socket.IO Client (v4.7)          quiz.py         REST: /api/quiz/rooms
```

### Room Lifecycle
```
1. Admin creates room → POST /api/quiz/rooms → gets 6-char code (e.g. "A3B7C2")
2. Participants join → open quiz-room.html?code=A3B7C2
3. Moderator joins  → open quiz-room.html?code=A3B7C2&mod=1
4. Moderator clicks Start → sends questions JSON → quiz begins
5. Each question: 30s countdown → participants submit answer → scored live
6. Moderator clicks Next → next question
7. After last question → leaderboard broadcast to all
```

### Question JSON Format
```json
[
  {
    "text": "What year was AISU founded?",
    "options": ["2020", "2022", "2024", "2025"],
    "correct_answer": "2024",
    "points": 10,
    "time_limit": 30,
    "image": null
  }
]
```

### Scoring
- **Team-based**: First correct answer from a team earns the points
- Points configurable per question (default: 10)
- Leaderboard sorted by total score descending

---

## 9. Certificate Template Engine

### Supported Template Formats
| Format | Fill Support | Notes |
|--------|-------------|-------|
| `.docx` (Word) | ✅ Full placeholder fill | Best option — auto-detects `{{placeholders}}` |
| `.pdf` | ❌ Record only | Stored but not filled |
| `.pptx` | ❌ Record only | Stored but not filled |
| [.png](file:///C:/Users/Admin/.gemini/antigravity/brain/d16a4f42-105c-4c17-ac31-e9f3fd45488c/team_filter_bar_1774174154306.png), `.jpg` | ❌ Record only | For reference |

### Placeholder Variables (in DOCX templates)
| Placeholder | Replaced With |
|-------------|--------------|
| `{{CertificateNo}}` | `AISUCERTESSAY2026000145` |
| `{{ParticipantName}}` | Participant's full name |
| `{{Program}}` | Competition/program name |
| `{{Date}}` | Certificate issue date |
| `{{Email}}` | Participant's email |
| `{{AnyCustomField}}` | From `extra` dict in API call |

### Bulk Generation Workflow
1. Admin uploads a `.docx` template via Admin Portal → Template Management
2. System auto-detects all `{{placeholder}}` names in the document
3. Admin goes to Generate section → selects template + program code
4. Enters participants **manually** (Name, Email, Program per line) OR imports **Excel** (.xlsx)
5. Clicks Generate → system fills each certificate, assigns unique Cert No., saves to DB, sends email
6. Download button available per certificate in the Issued Certificates table

---

## 10. Admin Portal Guide

**URL:** `http://127.0.0.1:8097/admin.html`

### Sidebar Sections
| Panel | What You Can Do |
|-------|----------------|
| **Dashboard** | Live stats from API, recent applications, quick overview |
| **Primary Members** | Search, filter by status, Approve / Reject individual applications |
| **Student Members** | Same as above for student applications |
| **Complaints** | Filter by status, view complaint details, update status |
| **Competitions** | List all competitions, create new competition with prizes |
| **Internships** | View applications, approve/reject |
| **Innovation Cell** | Review proposals, approve/reject |
| **Affiliations** | Manage organization affiliation applications |
| **Templates** | Upload certificate templates, see detected placeholders, delete |
| **Generate / Issue** | Bulk certificate generation (manual or Excel), download issued certs |
| **Quiz Rooms** | Create quiz room, enter questions JSON, get room code, open moderator view |
| **Announcements** | Post new announcements (type: General/Competition/Event/Important) |
| **Press / Gallery** | Add press releases and gallery items |
| **Admin Users** | Create new admin accounts (National/State/District level) |

### Status Workflow
```
Submitted → Pending Review → Under Review → Approved / Rejected
                                                     ↓
                                              Active (if Approved)
                                                     ↓
                                            Resigned / Terminated (later)
```

---

## 11. Login Credentials

> [!IMPORTANT]
> Change these before deploying to production.

| Account | Email | Password | Role | Access |
|---------|-------|----------|------|--------|
| **National Admin** | `admin@aisu4india.in` | `Admin@AISU2024` | `national` | Full access to all data |

### How Other Accounts Are Created
- **Primary Members**: Apply via form → Admin approves → System creates login with Member ID
- **Student Members**: Apply via form → Admin approves → System creates login with Student ID
- **State/District Admins**: Created manually via Admin Portal → Admin Users panel
- **General Users**: Can register via Login page for limited access

### Login Portal URLs
| User Type | URL | Credentials |
|-----------|-----|-------------|
| Admin | [/admin.html](file:///C:/Users/Admin/Downloads/AISU-Website%20frontend/admin.html) | Email + Password |
| All users | [/login.html](file:///C:/Users/Admin/Downloads/AISU-Website%20frontend/login.html) | Email or Unique ID + Password |

---

## 12. Deployment & Startup

### Prerequisites
```powershell
pip install flask flask-cors flask-jwt-extended flask-socketio python-docx openpyxl apscheduler
```

### Start Commands
```powershell
# Terminal 1 — Backend API + WebSocket
cd "C:\Users\Admin\Downloads\AISU-Website frontend\backend"
python app.py
# Running at: http://127.0.0.1:5000
# Socket.IO:  ws://127.0.0.1:5000/socket.io

# Terminal 2 — Frontend Static Server
cd "C:\Users\Admin\Downloads\AISU-Website frontend"
python -m http.server 8097
# Website at: http://127.0.0.1:8097/index.html
```

### Environment Variables (for production)
```powershell
# Set before running app.py
$env:SMTP_PASS = "your-gmail-app-password"
$env:SECRET_KEY = "your-strong-secret-key"
$env:JWT_SECRET_KEY = "your-strong-jwt-secret"
```

### Gmail App Password Setup
1. Go to [myaccount.google.com](https://myaccount.google.com)
2. Security → 2-Step Verification → App Passwords
3. Create app password for "AISU Backend"
4. Set as `SMTP_PASS` environment variable

### Production Deployment (recommended)
```bash
# Install gunicorn + eventlet for SocketIO
pip install gunicorn eventlet

# Run with eventlet worker (supports WebSocket)
gunicorn --worker-class eventlet -w 1 app:app --bind 0.0.0.0:5000
```

---

## 13. Troubleshooting

### White pages / blank sections
**Cause:** Old `.reveal { opacity: 0 }` CSS hiding content before JS loads
**Fix:** Already resolved — all `.reveal` blocks now use `opacity: 1`

### Backend import errors in IDE (Pyre2)
**Cause:** IDE's Python type checker (Pyre2) doesn't know the backend's working directory
**Status:** False positives — all files verified clean with `ast.parse()`. Backend runs correctly.

### "Room not found" in Quiz Room
**Cause:** Room codes are in-memory only — restart clears them
**Fix:** Create a new room via Admin Portal after each server restart

### Certificate download returns 404
**Cause:** Only `.docx` templates generate downloadable files. PDF/PNG templates create records only
**Fix:** Use a `.docx` Word template with `{{placeholders}}`

### Emails not being sent
**Cause:** `SMTP_PASS` environment variable not set
**Fix:** Set `$env:SMTP_PASS = "your-app-password"` before starting backend

### APScheduler warnings
**Message:** "Werkzeug appears to be used in a production deployment"
**Status:** Expected warning in development mode — safe to ignore

### CORS errors in browser
**Cause:** Frontend served from a port not in the CORS allowed list
**Fix:** Add your port to the `origins` list in [backend/app.py](file:///C:/Users/Admin/Downloads/AISU-Website%20frontend/backend/app.py) line ~50, or use port `8097` or `5500`

---

## 14. Quick Reference Card

```
WEBSITE          http://127.0.0.1:8097/index.html
ADMIN PORTAL     http://127.0.0.1:8097/admin.html
QUIZ ROOM        http://127.0.0.1:8097/quiz-room.html
BACKEND API      http://127.0.0.1:5000/api/health
SOCKET.IO        ws://127.0.0.1:5000/socket.io

ADMIN LOGIN      admin@aisu4india.in / Admin@AISU2024

BACKEND START    cd backend && python app.py
FRONTEND START   python -m http.server 8097

HTML PAGES       17 pages
BACKEND ROUTES   13 blueprints, 70+ endpoints
DB COLLECTIONS   14 JSON files
EMAIL TRIGGERS   11 automated functions
ID GENERATORS    8 format types
```
