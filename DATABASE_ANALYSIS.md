# AISU Backend Database Layer Complete Analysis

## 1. DB.PY FUNCTIONS (Core Module)

### Basic CRUD Operations

| Function | Parameters | Purpose | Return |
|----------|-----------|---------|--------|
| `insert()` | `collection, doc` | Add new doc; auto-generates `_id`, `created_at`, `status='pending'` | Document with added metadata |
| `find_all()` | `collection` | Retrieve all documents from collection | List of documents |
| `find_one()` | `collection, field, value` | Find single doc by field equality | Document or None |
| `find_many()` | `collection, field=None, value=None, filters=None` | Find multiple docs; supports AND filter dict | List of documents |
| `update_one()` | `collection, _id, updates` | Update doc by _id; auto-adds `updated_at` | Updated document or None |
| `delete_one()` | `collection, _id` | Delete doc by _id | Boolean (success) |
| `count()` | `collection, filters=None` | Count docs (optionally filtered) | Integer count |

### ID Generation Functions

| Function | Format | Example | Used By |
|----------|--------|---------|---------|
| `gen_member_id(state_name)` | `AISU[StateCode][YY][4-digit]` | `AISUBR260014` | members.py (primary members) |
| `gen_student_id(state_name)` | `AISUSM[StateCode][YYYY][6-digit]` | `AISUSMBR20260001` | students.py |
| `gen_affiliation_id()` | `FIYAOA[YYYY][4-digit]` | `FIYAOA20260015` | affiliation.py |
| `gen_complaint_id()` | `AISUCMP[YY][5-digit]` | `AISUCMP2600001` | complaint.py |
| `gen_cert_id(prog_code)` | `AISUCERT[ProgCode][YYYY][6-digit]` | `AISUCERTCOMP2026000145` | certs.py, internship.py |
| `gen_innovation_id()` | `AISUIC[YYYY][4-digit]` | `AISUIC20260025` | icell.py |
| `gen_competition_id()` | `AISUCOMP[YYYY][4-digit]` | `AISUCOMP20260001` | competition.py |

### Expiry/Date Helper Functions

| Function | Purpose | Return |
|----------|---------|--------|
| `days_until_expiry(approved_at_iso, validity_years)` | Calculate days remaining before expiry (uses relativedelta) | Integer or None |
| `is_expired(approved_at_iso, validity_years)` | Check if membership/cert has expired | Boolean |
| `get_expiry_date(approved_at_iso, validity_years)` | Get formatted expiry date | String (DD-MM-YYYY) or 'N/A' |

### Utility Functions

| Function | Purpose |
|----------|---------|
| `_state_code(state_name)` | Map state name to 2-letter code (e.g., 'Andhra Pradesh' → 'AP') |
| `_lock(name)` | Thread-safe lock manager for collection access |
| `_load(c)` | Load JSON collection from disk |
| `_save(c, data)` | Save JSON collection to disk |
| `_path(c)` | Get file path for collection.json |
| `load_collection(collection)` | Alias for find_all() |
| `save_collection(collection, data)` | Direct collection save (bypass normal operations) |
| `make_id()` | Generate random UUID |
| `gen_cert_number(prog_code)` | Alias for gen_cert_id() |

---

## 2. COLLECTIONS & SCHEMAS

### users
**Purpose:** Portal login & role management  
**Fields:**
```python
{
    '_id': uuid,                      # Unique user ID
    'name': str,                      # Full name
    'email': str (unique),            # Unique identifier
    'mobile': str,                    # Phone (10 digits)
    'password': hash,                 # Bcrypt hash
    'role': str,                      # national|vp|secretary|state|district|member|user
    'state': str,                     # State abbreviation
    'designation': str,               # Optional job title
    'member_id': str,                 # Link to primary_members.member_id
    'status': str,                    # active|inactive
    'roles': list,                    # Multi-role list (planned)
    'reset_otp': str,                 # Forgot password OTP
    'reset_otp_expiry': datetime,     # OTP expires in 15 min
    'created_at': datetime,
    'updated_at': datetime
}
```
**Key Constraints:** Email must be unique. Used in auth flow.

### primary_members
**Purpose:** Full membership applications (individuals, 3-year validity)  
**Fields:**
```python
{
    '_id': uuid,
    'member_id': str (unique),        # AISUBR260014 format
    'fullname': str (uppercase),
    'parent_name': str,
    'dob': str (YYYY-MM-DD),
    'age': int,
    'gender': str,                    # M|F|Other
    'address': str,
    'pin': str,
    'institution': str,               # School/College/Org
    'state': str,
    'district': str,
    'city': str,
    'mobile': str (unique),           # 10 digits
    'email': str (unique),            # Links to users table
    'govtid_type': str,               # Aadhaar|PAN|Passport
    'govtid_number': str,             # Sensitive - redacted in list views
    'govtid_file': str,               # Upload filename
    'payment_proof': str,             # Upload filename
    'photo': str,                     # Upload filename
    'sign': str,                      # Upload filename
    'heard_about': str,               # Source of awareness
    'contribution': str,              # What will you contribute?
    'justify_answers': str (JSON),    # Detailed answers
    'mode_of_submission': str,        # Online|Offline|Hybrid
    'designation': str,               # Approved designation
    'level': str,                     # state|district|block|school
    'role_status': str,               # active|promoted|demoted|transferred|additional_responsibility|resigned|terminated
    'status': str,                    # pending|approved|rejected|inactive|expired
    'approval_by': str (user_id),     # Admin who approved
    'approved_at': datetime,          # Approval timestamp
    'expiry_date': str (DD-MM-YYYY),
    'reports': list,                  # [{file, uploaded_at, note}]
    'official_email_1': str,          # Contact email display
    'official_email_2': str,          # Alternative contact
    'created_at': datetime,
    'updated_at': datetime
}
```
**Key Constraints:** One active membership per email/mobile. Links to users portal.

### student_members
**Purpose:** Student membership applications (1-year validity, lower fee)  
**Fields:**
```python
{
    '_id': uuid,
    'student_id': str (unique),       # AISUSMBR20260001 format
    'fullname': str (uppercase),
    'parent_name': str,
    'dob': str,
    'age': int,
    'gender': str,
    'address': str,
    'pin': str,
    'institution': str,               # College name
    'state': str,
    'district': str,
    'city': str,
    'mobile': str,
    'email': str (unique),
    'heard_about': str,
    'payment_proof': str,             # Upload filename
    'mode_of_submission': str,
    'status': str,                    # pending|approved|rejected
    'approved_by': str (user_id),
    'approved_at': datetime,
    'created_at': datetime,
    'updated_at': datetime
}
```
**Key Feature:** Used in competition fee-gate logic (`membership_status()` endpoint).

### complaints
**Purpose:** Tiered complaint portal with anonymous option  
**Fields:**
```python
{
    '_id': uuid,
    'complaint_id': str (unique),     # AISUCMP2600001 format
    'user_id': str,                   # Filing user
    'name': str,
    'mobile': str,
    'email': str,
    'state': str,
    'district': str,
    'institution': str,
    'category': str,                  # Fee & Scholarship|Ragging|Harassment|Academic Issue|etc
    'description': str,               # Issue details
    'proof_file': str,                # Upload filename
    'is_anonymous': bool,             # Can hide identity
    'status': str,                    # open|in_progress|resolved|disposed
    'assigned_to': str,               # Staff member
    'resolution': str,                # Final resolution text
    'is_confidential': bool,          # Always true
    'action_log': list,               # [{level, action, updater, timestamp, document}]
    'created_at': datetime,
    'updated_at': datetime
}
```
**Key Feature:** Multi-level access control (national sees all; state sees only state complaints with ID redacted).

### certificates
**Purpose:** Digital certificates (participation, completion, internship)  
**Fields:**
```python
{
    '_id': uuid,
    'cert_number': str (unique),      # AISUCERTCOMP2026000145 format
    'participant_name': str,
    'participant_email': str,         # Key lookup field
    'program': str,                   # Program/competition name
    'prog_code': str,                 # COMP|ESSAY|INTERN|etc
    'cert_type': str,                 # Participation|Completion|Merit
    'template_id': str,               # Reference to cert_templates._id
    'filename': str,                  # Generated PDF/DOCX path
    'replacements': dict,             # {{Placeholder}}: value mapping
    'status': str,                    # issued|revoked|reissued
    'issued_at': datetime,
    'issued_by': str (user_id),
    'revoked_at': datetime,
    'revoke_reason': str,
    'reissued_from': str,             # If this is a reissue, link to original
    'reissued_to': str,               # If reissued, link to new cert
    'source': str,                    # internship|competition|manual
    'source_id': str,                 # Reference to source record
    'created_at': datetime,
    'updated_at': datetime
}
```
**Key Feature:** Public verification via LookupVerification endpoint (by cert_number, mobile, email).

### competitions
**Purpose:** Competitions/contests with registration & quiz support  
**Fields:**
```python
{
    '_id': uuid,
    'comp_id': str (unique),          # AISUCOMP20260001 format
    'title': str,
    'description': str,
    'category': str,                  # STEM|Essay|Document Upload|Other
    'comp_type': str,                 # document_upload|group_quiz|exam_quiz
    'last_date': str (YYYY-MM-DD),
    'event_date': str,
    'group_size': int,                # Min group members
    'time_limit': int,                # Minutes (for exam mode)
    'questions': list,                # [{id, text, options, correct_answer, points}]
    'instructions': str,              # Quiz instructions
    'status': str,                    # open|completed|closed
    'results': list,                  # [{name, email, institution, rank, category}]
    'created_by': str (user_id),
    'created_at': datetime,
    'updated_at': datetime
}
```
**Key Feature:** Questions with correct_answer removed from client payload (security).

### competition_registrations
**Purpose:** Individual/team registrations for competitions  
**Fields:**
```python
{
    '_id': uuid,
    'comp_id': str,                   # Foreign key to competitions
    'competition_title': str,
    'user_id': str,                   # Registrant
    'name': str,
    'email': str,
    'mobile': str,
    'institution': str,
    'state': str,
    'group_members': list,            # [{name, email, role}]
    'has_active_membership': bool,    # Student membership check
    'fee_required': bool,             # Computed at registration
    'fee_paid': bool,
    'submission_type': str,           # From competition.comp_type
    'status': str,                    # registered|submitted|qualified|disqualified
    'submission_file': str,           # Upload filename
    'submitted_at': datetime,
    'submission_note': str,
    'quiz_started': bool,
    'quiz_start_time': datetime,
    'quiz_submitted': bool,
    'quiz_submit_time': datetime,
    'answers': dict,                  # {question_id: chosen_answer}
    'score': int,
    'score_percent': float,
    'disqualified': bool,
    'disqualification_reason': str,
    'created_at': datetime,
    'updated_at': datetime
}
```
**Key Feature:** Membership-based fee gate (3-month student membership → free; else per-competition fee).

### affiliations
**Purpose:** Organization/institution partnerships  
**Fields:**
```python
{
    '_id': uuid,
    'org_name': str,
    'contact_name': str,
    'email': str (unique),
    'mobile': str,
    'state': str,
    'district': str,
    'address': str,
    'org_type': str,                  # School|College|NGO|Corporate|Other
    'reg_number': str,                # Registration/CIN number
    'website': str,
    'reg_document': str,              # Upload filename
    'status': str,                    # pending|approved|rejected
    'reason': str,                    # Rejection reason
    'created_at': datetime,
    'updated_at': datetime
}
```

### internships
**Purpose:** Internship opportunity applications  
**Fields:**
```python
{
    '_id': uuid,
    'fullname': str,
    'email': str,
    'mobile': str,
    'state': str,
    'institution': str,
    'course': str,
    'year': str,                      # 1st|2nd|3rd|4th Year
    'domain': str,                    # Tech|Business|Social|Other
    'duration': str,                  # Months
    'resume': str,                    # Upload filename
    'partner': str,                   # AISU partner (e.g., SkillChase)
    'status': str,                    # pending|shortlisted|selected|ongoing|completed|rejected
    'selection_status': str,          # Applied|Shortlisted|Selected|Not Selected
    'progress_status': str,           # (blank)|Starting Soon|In Progress|Completed
    'completion_status': str,         # (blank)|Completed
    'rejection_reason': str,
    'progress_log': list,             # [{status, note, updated_by, timestamp}]
    'created_at': datetime,
    'updated_at': datetime
}
```
**Key Feature:** Auto-generates completion certificate when status='completed'.

### innovations
**Purpose:** Innovation/startup idea submissions with investor matching  
**Fields:**
```python
{
    '_id': uuid,
    'proposal_id': str (unique),      # AISUIC20260025 format
    'user_id': str,
    'applicant_name': str,
    'applicant_email': str,
    'title': str,
    'problem_statement': str,
    'proposed_solution': str,
    'implementation_plan': str,
    'expected_impact': str,
    'required_funds': str,            # Budget in INR
    'supporting_doc': str,            # Upload filename
    'status': str,                    # submitted|under_review|modification_requested|approved|rejected
    'icell_notes': str,               # ICell team comments
    'investor_status': str,           # (blank)|forwarded|funded
    'investor_name': str,
    'investor_email': str,            # Forwarded investor email
    'investor_org': str,
    'forwarded_at': datetime,
    'forwarded_by': str,
    'fund_disbursed': bool,
    'disbursed_amount': str,
    'disbursed_at': datetime,
    'bank_ref': str,
    'disbursed_to': str,
    'fund_account': str,               # Bank account details
    'fund_transfer_date': str,
    'created_at': datetime,
    'updated_at': datetime
}
```
**Key Feature:** Multi-stage workflow (submit → review → approve → investor forward → fund).

### contacts
**Purpose:** Website contact form submissions  
**Fields:**
```python
{
    '_id': uuid,
    'name': str,
    'email': str,
    'mobile': str,
    'subject': str,
    'message': str,
    'state': str,
    'status': str,                    # unread|read
    'created_at': datetime,
    'updated_at': datetime
}
```

### certificates (cert_templates)
**Purpose:** Reusable certificate templates with placeholders  
**Fields:**
```python
{
    '_id': uuid,
    'name': str,                      # Template display name
    'prog_code': str,                 # COMP|ESSAY|INTERN|etc
    'description': str,
    'filename': str,                  # File on disk
    'ext': str,                       # .docx|.pdf|.pptx|.png|.jpg
    'uploaded_by': str (email),
    'placeholders': list,             # {{CertificateNo}}, {{ParticipantName}}, etc
    'created_at': datetime,
    'updated_at': datetime
}
```

### gallery
**Purpose:** Photo/media gallery for events & publications  
**Fields:**
```python
{
    '_id': uuid,
    'title': str,
    'category': str,                  # event|results|publications
    'description': str,
    'image': str,                     # Upload filename or URL
    'event_date': str,
    'uploaded_by': str (user_id),
    'created_at': datetime,
    'updated_at': datetime
}
```

### announcements
**Purpose:** Admin announcements (dashboard display)  
**Fields:**
```python
{
    '_id': uuid,
    'title': str,
    'type': str,                      # General|Urgent|Update
    'content': str,
    'link': str,                      # External link
    'posted_at': datetime,
    'posted_by': str (user_id)
}
```

### press_releases
**Purpose:** Press releases & media coverage  
**Fields:**
```python
{
    '_id': uuid,
    'title': str,
    'type': str,                      # Press Release|News|Media Coverage
    'source': str,                    # Publication source
    'content': str,
    'event_date': str,
    'location': str,
    'posted_at': datetime
}
```

---

## 3. ROUTE → DB FUNCTION MAPPING

### auth.py
| Route | Method | DB Functions | Purpose |
|-------|--------|--------------|---------|
| `/register` | POST | `find_one('users', 'email')`<br>`find_one('users', 'mobile')`<br>`update_one('users')`<br>`insert('users')` | Register new user or merge with existing |
| `/login` | POST | `find_one('users', 'email')`<br>`find_one('users', 'mobile')`<br>`find_one('primary_members', 'member_id')`<br>`find_one('student_members', 'member_id')` | Authenticate via email/mobile/member ID |
| `/forgot-password/request` | POST | `find_one('users', 'email')`<br>`find_one('users', 'mobile')`<br>`update_one('users')` | Generate & store OTP |
| `/forgot-password/reset` | POST | `find_one('users', 'email')`<br>`find_one('users', 'mobile')` | Verify OTP & reset password |
| `/refresh` | POST | *(JWT only)* | Token refresh (no DB) |
| `/change-password` | POST | `find_one('users', '_id')` | Update password |
| `/me` | GET | `find_one('users', '_id')`<br>`find_one('primary_members', 'email')`<br>`find_one('student_members', 'email')`<br>`get_expiry_date()` | Get user profile with membership info |

### members.py (Primary Membership)
| Route | Method | DB Functions | Purpose |
|-------|--------|--------------|---------|
| `/apply` | POST | `find_one('primary_members', 'email')`<br>`find_one('primary_members', 'mobile')`<br>`gen_member_id()`<br>`insert('primary_members')` | Submit primary membership application |
| `/` | GET | `find_all('primary_members')`<br>*(filtered by role/state)* | List all applications (role-based filtering) |
| `/directory` | GET | `find_all('primary_members')` | Public directory of active members |
| `/<_id>` | GET | `find_one('primary_members', 'member_id')`<br>`find_one('primary_members', '_id')`<br>`days_until_expiry()`<br>`get_expiry_date()` | Get member details with expiry |
| `/<_id>/approve` | POST | `find_one('primary_members', '_id')`<br>`update_one('primary_members')`<br>`find_one('users', 'email')`<br>`insert('users')` | Approve application & create portal login |
| `/<_id>/reject` | POST | `update_one('primary_members')` | Reject application |
| `/<_id>/role-status` | POST | `update_one('primary_members')`<br>`find_one('users', 'email')`<br>`update_one('users')` | Update role (promote/resign/transfer/etc) |
| `/<_id>/upload-report` | POST | `find_one('primary_members')`<br>`update_one('primary_members')` | Upload performance report |
| `/<_id>/renew` | POST | `find_one('primary_members', '_id')`<br>`update_one('primary_members')`<br>`find_one('users', 'email')`<br>`update_one('users')` | Renew 3-year membership |
| `/stats/summary` | GET | `find_all('primary_members')` | Dashboard stats (total, pending, approved) |

### students.py (Student Membership)
| Route | Method | DB Functions | Purpose |
|-------|--------|--------------|---------|
| `/apply` | POST | `find_one('student_members', 'email')`<br>`gen_student_id()`<br>`insert('student_members')` | Submit student membership application |
| `/` | GET | `find_all('student_members')`<br>*(filtered by state)* | List student applications |
| `/<_id>/approve` | POST | `find_one('student_members', '_id')`<br>`update_one('student_members')` | Approve student membership |
| `/<_id>/reject` | POST | `update_one('student_members')` | Reject student membership |
| `/stats/summary` | GET | `find_all('student_members')` | Dashboard stats |
| `/membership-status/<email>` | GET | `find_one('student_members', 'email')`<br>`is_expired()` | Check membership status for fee gate |

### competitors.py (Competition)
| Route | Method | DB Functions | Purpose |
|-------|--------|--------------|---------|
| `/` | POST | `gen_competition_id()`<br>`insert('competitions')`<br>*(broadcasts to all students)* | Create new competition |
| `/` | GET | `find_all('competitions')`<br>*(filtered by status)* | List competitions |
| `/<comp_id>` | GET | `find_one('competitions', 'comp_id')` | Get competition details |
| `/<comp_id>/register` | POST | `find_one('competitions', 'comp_id')`<br>`find_one('users', '_id')`<br>`find_all('competition_registrations')`<br>`find_one('student_members', 'email')`<br>`is_expired()`<br>`insert('competition_registrations')` | Register participant (with fee check) |
| `/<comp_id>/submit` | POST | `find_all('competition_registrations')`<br>`update_one('competition_registrations')` | Submit entry (document upload) |
| `/<comp_id>/start-quiz` | POST | `find_all('competition_registrations')`<br>`find_one('competitions', 'comp_id')`<br>`update_one('competition_registrations')` | Start quiz session |
| `/<comp_id>/submit-quiz` | POST | `find_all('competition_registrations')`<br>`find_one('competitions', 'comp_id')`<br>`update_one('competition_registrations')` | Submit quiz answers & calculate score |
| `/reg/<reg_id>/disqualify` | POST | `find_one('competition_registrations', '_id')`<br>`update_one('competition_registrations')` | Disqualify participant |
| `/<comp_id>/results` | POST | `find_one('competitions', 'comp_id')`<br>`update_one('competitions')` | Publish results |
| `/<comp_id>/results` | GET | `find_one('competitions', 'comp_id')` | Get published results |
| `/my-registrations` | GET | `find_all('competition_registrations')`<br>*(filtered by user_id)* | My competitions |

### complaint.py
| Route | Method | DB Functions | Purpose |
|-------|--------|--------------|---------|
| `/submit` | POST | `find_one('users', '_id')`<br>`gen_complaint_id()`<br>`insert('complaints')` | File complaint (must be logged in) |
| `/track/<complaint_id>` | GET | `find_one('complaints', 'complaint_id')` | Public complaint tracking (no identity shown) |
| `/` | GET | `find_all('complaints')`<br>*(filtered by role/state/district)* | List complaints (tiered access) |
| `/<_id>/update` | POST | `find_one('complaints', '_id')`<br>`update_one('complaints')` | Add action to complaint |
| `/<_id>/dispose` | POST | `find_one('complaints', '_id')`<br>`update_one('complaints')` | Mark complaint disposed |

### certs.py
| Route | Method | DB Functions | Purpose |
|-------|--------|--------------|---------|
| `/verify/<cert_num>` | GET | `find_one('certificates', 'cert_number')` | Verify cert by number (public) |
| `/verify` | GET | `find_all('certificates')`<br>`find_one('users', 'mobile')`<br>`find_one('primary_members', 'mobile')`<br>`find_one('student_members', 'mobile')` | Verify by mobile/email/cert (public) |
| `/` | GET | `find_all('certificates')`<br>*(search & filter by prog_code)* | List/search certs |
| `/issue` | POST | `gen_cert_id()`<br>`insert('certificates')` | Issue cert manually (admin) |
| `/<_id>/revoke` | POST | `find_one('certificates', '_id')`<br>`update_one('certificates')` | Revoke cert |
| `/<_id>/reissue` | POST | `find_one('certificates', '_id')`<br>`gen_cert_id()`<br>`insert('certificates')`<br>`update_one('certificates')` | Reissue (marks old as reissued) |
| `/all` | GET | `find_all('certificates')`<br>*(filtered by status)* | Admin: all certs |
| `/my` | GET | `find_one('users', '_id')`<br>`find_all('certificates')`<br>*(filtered by email)* | My certificates |

### affiliation.py
| Route | Method | DB Functions | Purpose |
|-------|--------|--------------|---------|
| `/apply` | POST | `find_one('affiliations', 'email')`<br>`insert('affiliations')` | Apply for org affiliation |
| `/` | GET | `find_all('affiliations')` | List affiliations (admin) |
| `/<_id>/approve` | POST | `update_one('affiliations')` | Approve affiliation |
| `/<_id>/reject` | POST | `update_one('affiliations')` | Reject affiliation |

### internship.py
| Route | Method | DB Functions | Purpose |
|-------|--------|--------------|---------|
| `/apply` | POST | `find_one('internships', 'email')`<br>`insert('internships')` | Submit internship application |
| `/` | GET | `find_all('internships')`<br>*(filtered by state/status)* | List internships |
| `/my` | GET | `find_one('users', '_id')`<br>`find_many('internships', 'email')` | My internship applications |
| `/<_id>/status` | POST | `find_one('internships', '_id')`<br>`update_one('internships')`<br>`gen_cert_id()` (if completed)<br>`insert('certificates')` | Update status (auto-cert on complete) |
| `/<_id>/approve` | POST | `update_one('internships')` | Approve (same as shortlist→select) |
| `/<_id>/reject` | POST | `update_one('internships')` | Reject internship |

### icell.py (Innovation Cell)
| Route | Method | DB Functions | Purpose |
|-------|--------|--------------|---------|
| `/submit` | POST | `find_one('users', '_id')`<br>`gen_innovation_id()`<br>`insert('innovations')` | Submit innovation proposal |
| `/` | GET | `find_all('innovations')`<br>*(filtered by status)* | List proposals (ICell/admin) |
| `/my-proposals` | GET | `find_all('innovations')`<br>*(filtered by user_id)* | My proposals |
| `/<_id>` | GET | `find_one('innovations', '_id')`<br>`find_one('innovations', 'proposal_id')` | Get proposal details |
| `/<_id>/status` | POST | `find_one('innovations', '_id')`<br>`update_one('innovations')` | Update review status |
| `/<_id>/fund-update` | POST | `find_one('innovations', '_id')`<br>`update_one('innovations')` | Update funding details |
| `/<_id>/forward-investor` | POST | `find_one('innovations', '_id')`<br>`update_one('innovations')` | Forward proposal to investor |
| `/<_id>/fund-disbursement` | POST | `find_one('innovations', '_id')`<br>`update_one('innovations')` | Record fund disbursement |

### contact.py
| Route | Method | DB Functions | Purpose |
|-------|--------|--------------|---------|
| `/send` | POST | `insert('contacts')` | Submit contact form (public) |
| `/` | GET | `find_all('contacts')` | List contacts (admin) |
| `/<_id>/read` | POST | `update_one('contacts')` | Mark contact as read |
| `/state-officials` | GET | `find_many('primary_members', filters={'status': 'approved'})` | Public directory of state officials |
| `/set-official-emails/<member_id>` | POST | `find_one('primary_members')`<br>`update_one('primary_members')` | Set contact emails (admin) |

### admin.py
| Route | Method | DB Functions | Purpose |
|-------|--------|--------------|---------|
| `/stats` | GET | `find_all('primary_members')`<br>`find_all('student_members')`<br>`find_all('complaints')`<br>`find_all('contacts')`<br>`find_all('certificates')`<br>`find_all('internships')`<br>`find_all('affiliations')` | Dashboard statistics |
| `/users` | GET | `find_all('users')` | List all portal users (national admin) |
| `/users/create` | POST | `find_one('users', 'email')`<br>`insert('users')` | Create user (national admin) |
| `/users/<_id>` | PUT | `update_one('users')` | Update user |
| `/users/<_id>/deactivate` | POST | `find_one('users', '_id')`<br>`update_one('users')` | Deactivate user |
| `/search` | GET | `find_all('primary_members')`<br>`find_all('student_members')`<br>`find_all('complaints')` | Cross-collection search |
| `/announcements` | GET | `load_collection('announcements')` | Get announcements |
| `/announcements` | POST | `load_collection('announcements')`<br>`save_collection('announcements')` | Post announcement |
| `/announcements/<ann_id>` | DELETE | `load_collection('announcements')`<br>`save_collection('announcements')` | Delete announcement |
| `/press` | GET | `load_collection('press_releases')` | Get press releases |
| `/press` | POST | `load_collection('press_releases')`<br>`save_collection('press_releases')` | Post press release |
| `/renewals/primary` | GET | `load_collection('primary_members')` | Get expiring memberships |
| `/renewals/<member_id>/process` | POST | `load_collection('primary_members')`<br>`save_collection('primary_members')` | Process membership renewal |
| `/gallery` | GET | `find_all('gallery')`<br>*(filtered by category)* | Get gallery items |
| `/gallery` | POST | `insert('gallery')` | Add gallery item |
| `/gallery/<item_id>` | DELETE | `delete_one('gallery')` | Delete gallery item |

### cert_templates.py
| Route | Method | DB Functions | Purpose |
|-------|--------|--------------|---------|
| `/templates` | POST | `insert('cert_templates')` | Upload certificate template |
| `/templates` | GET | `find_all('cert_templates')` | List templates |
| `/templates/<tid>` | GET | `find_one('cert_templates', '_id')` | Get template details |
| `/templates/<tid>` | DELETE | `delete_one('cert_templates')` | Delete template |
| `/generate` | POST | `find_one('competitions', '_id')`<br>`find_many('competition_registrations')`<br>`find_one('cert_templates', '_id')`<br>`gen_cert_id()`<br>`insert('certificates')` | Bulk issue certificates |
| `/download/<cert_id>` | GET | `find_one('certificates', '_id')` | Download generated cert file |

### quiz.py (WebSocket via SocketIO)
| Socket Event | DB Functions | Purpose |
|--------------|--------------|---------|
| `join_quiz_room` | *(in-memory)* | Join quiz room (NO DB - ephemeral) |
| `moderator_start_quiz` | *(in-memory)* | Start quiz |
| `moderator_next_question` | *(in-memory)* | Advance to next Q |
| `submit_answer` | *(in-memory)* | Submit answer & score |
| `quiz_chat` | *(in-memory)* | Chat broadcast |
| `disconnect` | *(in-memory)* | Cleanup |

---

## 4. SPECIAL USE CASES & RELATIONSHIPS

### Data Relationships (Foreign Keys - Conceptual)

| Parent | Child | Field | Purpose |
|--------|-------|-------|---------|
| `users` | `primary_members` | `email` | Link user portal to membership |
| `users` | `student_members` | `email` | Link user portal to student membership |
| `users` | `competition_registrations` | `user_id` | Registrant user |
| `users` | `complaints` | `user_id` | Complaint filer |
| `users` | `innovations` | `user_id` | Proposal submitter |
| `competitions` | `competition_registrations` | `comp_id` | Registered in competition |
| `primary_members` | `certificates` | `email` (via participant_email) | Issued to member |
| `internships` | `certificates` | `email` (via source_id) | Auto-issued on completion |
| `cert_templates` | `certificates` | `template_id` | Used in generation |

### Multi-Stage Workflows

**1. Primary Membership Lifecycle:**
```
apply() → pending
  ↓
approve() → approved + role_status=active + user created
  ↓
role-status(promoted/transferred) → promoted/transferred
  ↓
renew() → reset approved_at (3 years)
  ↓
role-status(resigned) → inactive
```

**2. Complaint Escalation:**
```
submit() → open
  ↓
update() + action_log entry → in_progress
  ↓
update() + action_log entry → resolved
  ↓
dispose() → disposed
```

**3. Innovation to Investor:**
```
submit() → submitted
  ↓
update_status(approved) → approved
  ↓
forward_to_investor() → investor_status=forwarded
  ↓
record_fund_disbursement() → fund_disbursed=True
```

**4. Internship to Certificate:**
```
apply() → pending
  ↓
update_status(selected/ongoing) → status=selected/ongoing
  ↓
update_status(completed)
  ↓ (automatic)
gen_cert_id('INTERN') + insert('certificates')
  ↓
send_certificate_issued(email, cert_num)
```

### Computed Fields (Not Stored)

| Collection | Field | Computation |
|-----------|-------|-------------|
| `primary_members` | `days_to_expiry` | `days_until_expiry(approved_at, 3)` |
| `student_members` | expiry_date | `get_expiry_date(approved_at, 1)` |
| `competition_registrations` | `fee_required` | Check if student membership active & not expired |
| `complaints` | visible_fields | Depends on role (national sees all; state redacts identity) |
| `users` | membership info | Joined from primary_members & student_members on email |

### Thread Safety & Locking

All collection reads/writes use `_lock(collection_name)` to prevent race conditions:
```python
with _lock(collection):
    data = _load(collection)
    # ... modify data ...
    _save(collection, data)
```

### Transactions & Atomic Operations

**NOT fully supported** - limited to single-collection operations:
- ✅ Approve primary member + insert user (two ops, but designed as atomic flow)
- ✅ Update status + auto-generate certificate (icell/internship flows)
- ❌ No cross-collection rollback on partial failure

### Aggregation Patterns (No Native Aggregation)

| Operation | Method | Example |
|-----------|--------|---------|
| Count by field | Manual loop + dict tally | `_count_by_state(members)` in members.py |
| Filter multiple conditions | `find_many(filters={...})` | Status + state filters |
| Join tables | Manual iteration on email | User + membership lookup in `/me` |
| Search across collections | Loop in `admin/search` | Search primary_members, student_members, complaints |

### Performance Considerations

| Collection | Size Factor | Optimization |
|-----------|------------|--------------|
| `users` | ~100s-1000s | Email/mobile indexed in find_one() for login |
| `primary_members` | ~100s | Status/state filters iterated (linear scan) |
| `competition_registrations` | High (multiplied by comp count) | Stored as list, filtered on each list_competitions |
| `complaints` | Medium | All loaded into memory for tiered filtering |
| `quiz rooms` | Ephemeral | In-memory dict (ephemeral, reset on server restart) |

### Data Uploads (Non-DB Storage)

All file uploads stored in `/backend/uploads/` by category:
```
govtid/        → Govt ID scans, resume, supporting docs
payment/       → Payment proofs
photo/         → Member photos
sign/          → Signatures
complaint/     → Complaint evidence
gallery/       → Gallery images
cert_templates/ → Certificate template files
certificates/   → Generated PDF/DOCX certificates
publications/   → Publications
```

DB stores only **filename** + optional cloud URL, not binary data.

---

## 5. SUMMARY TABLE: Collections & Usage

| Collection | Records | Key ID | Status Field | Contains Uploads | API Endpoints |
|-----------|---------|--------|--------------|------------------|---------------|
| users | 100s-1000s | `_id` (UUID) | `active`/`inactive` | No | /auth, /admin/users |
| primary_members | 100s | `member_id` (AISU format) | `approved`/`pending`/`rejected`/`inactive` | Yes (4 files) | /members/* |
| student_members | 100s-1000s | `student_id` (AISUSM format) | `approved`/`pending`/`rejected` | Yes (1 file) | /students/* |
| competition_registrations | High multiplier | `_id` | `registered`/`submitted`/`qualified`/`disqualified` | Yes (submission) | /competitions/* |
| competitions | 10s-100s | `comp_id` | `open`/`completed` | No | /competitions/* |
| complaints | 100s | `complaint_id` | `open`/`in_progress`/`resolved`/`disposed` | Yes (proof) | /complaints/* |
| certificates | 100s-1000s | `cert_number` | `issued`/`revoked`/`reissued` | Yes (file) | /certs/* |
| affiliations | 10s-100s | Auto UUID | `approved`/`pending`/`rejected` | Yes (1 file) | /affiliation/* |
| internships | 10s-100s | `_id` | `pending`/`shortlisted`/`selected`/`completed` | Yes (resume) | /internship/* |
| innovations | 10s-100s | `proposal_id` | `submitted`/`approved`/`rejected` | Yes (doc) | /icell/* |
| contacts | 100s-1000s | `_id` | `unread`/`read` | No | /contact/* |
| cert_templates | 10s | `_id` | N/A | Yes (.docx/.pdf) | /cert-templates/* |
| gallery | 100s | `_id` | N/A | Yes (image) | /gallery |
| announcements | 10s-100s | `_id` | N/A | No | /announcements |
| press_releases | 10s-100s | `_id` | N/A | No | /press |

---

## 6. KEY INSIGHTS & OBSERVATIONS

### Strengths
✅ **Simple & Transparent** - JSON-based, easy to inspect and backup  
✅ **Thread-Safe** - Uses locks for concurrent access  
✅ **Flexible ID Schemas** - Semantic IDs (AISUBR260014) vs generic UUIDs  
✅ **Tiered Access Control** - Built into route handlers (not DB-enforced)  

### Limitations
❌ **No Transactions** - Single-collection ops only; multi-step workflows can partially fail  
❌ **Linear Scans** - Every `find_many()` loads entire collection into memory  
❌ **No Indexing** - Field lookups are O(n)  
❌ **File I/O Overhead** - Every operation reads/writes entire JSON file  
❌ **Scalability** - Not suitable for >10K collections  

### Recommendations for Production
1. Migrate to MongoDB/PostgreSQL for multi-collection operations & transactions
2. Add indices on frequently queried fields (email, state, status)
3. Implement proper query optimizations instead of linear scans
4. Add data backup & disaster recovery procedures
5. Consider separate storage for large files (S3/Azure Blob)

