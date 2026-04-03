# routes/members.py — Primary Membership (full spec)
from flask import Blueprint, request, current_app, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from utils import ok, err, save_upload, validate_required, require_role
from datetime import datetime
import db, os

members_bp = Blueprint('members', __name__)

REQUIRED = ['fullname', 'parent_name', 'dob', 'age', 'gender',
            'address', 'pin', 'institution', 'state', 'district',
            'city', 'mobile', 'email', 'govtid_type', 'govtid_number',
            'heard_about', 'contribution', 'mode_of_submission']

# ── SUBMIT ────────────────────────────────────────────────────
@members_bp.route('/apply', methods=['POST'])
def apply():
    data   = request.form.to_dict()
    files  = request.files
    missing = validate_required(data, REQUIRED)
    if missing:
        return err(f'Missing: {", ".join(missing)}')
    mobile = data['mobile'].strip()
    if not mobile.isdigit() or len(mobile) != 10:
        return err('Mobile must be 10 digits')
    email = data['email'].strip().lower()
    if db.find_one('primary_members', 'email', email):
        return err('Application with this email already exists')
    if db.find_one('primary_members', 'mobile', mobile):
        return err('Application with this mobile already exists')

    govtid_file  = save_upload(files.get('govtid_file'),  'govtid')
    payment_file = save_upload(files.get('payment_proof'), 'payment')
    photo_file   = save_upload(files.get('photo'),         'photo')
    sign_file    = save_upload(files.get('sign'),          'sign')

    # Generate member ID (will be confirmed on approval)
    member_id = db.gen_member_id(data['state'])

    doc = db.insert('primary_members', {
        'member_id'          : member_id,
        'fullname'           : data['fullname'].upper(),
        'parent_name'        : data.get('parent_name',''),
        'dob'                : data.get('dob',''),
        'age'                : data.get('age',''),
        'gender'             : data.get('gender',''),
        'address'            : data.get('address',''),
        'pin'                : data.get('pin',''),
        'institution'        : data.get('institution',''),
        'state'              : data.get('state',''),
        'district'           : data.get('district',''),
        'city'               : data.get('city',''),
        'mobile'             : mobile,
        'email'              : email,
        'govtid_type'        : data.get('govtid_type',''),
        'govtid_number'      : data.get('govtid_number',''),
        'govtid_file'        : govtid_file,
        'payment_proof'      : payment_file,
        'photo'              : photo_file,
        'sign'               : sign_file,
        'heard_about'        : data.get('heard_about',''),
        'contribution'       : data.get('contribution',''),
        'justify_answers'    : data.get('justify_answers','{}'),
        'mode_of_submission' : data.get('mode_of_submission',''),
        'designation'        : '',
        'role_status'        : 'pending',   # Active/Promoted/Demoted/Transferred/Resigned/Terminated
        'approved_by'        : '',
        'approved_at'        : '',
        'expiry_date'        : '',
        'reports'            : [],
    })
    try:
        from email_service import send_primary_application_received
        send_primary_application_received(doc)
    except Exception as e:
        print(f'Email error: {e}')
    return ok({'application_ref': doc['_id'], 'member_id': member_id},
              'Application submitted! Your AISU Member ID will be emailed after approval.', 201)

# ── LIST ──────────────────────────────────────────────────────
@members_bp.route('/', methods=['GET'])
@require_role('national','vp','secretary','state','district')
def list_members():
    claims   = get_jwt()
    all_m    = db.find_all('primary_members')
    role     = claims.get('role')
    if role == 'state':
        all_m = [m for m in all_m if m.get('state') == claims.get('state')]
    elif role == 'district':
        all_m = [m for m in all_m if m.get('district') == claims.get('district')]
    status = request.args.get('status')
    state  = request.args.get('state')
    if status: all_m = [m for m in all_m if m.get('status') == status]
    if state:  all_m = [m for m in all_m if m.get('state') == state]
    for m in all_m:
        m.pop('govtid_number', None); m.pop('sign', None); m.pop('justify_answers', None)
    return ok(all_m, f'{len(all_m)} records')

# ── PUBLIC DIRECTORY (active members only) ─────────────────────
@members_bp.route('/directory', methods=['GET'])
def directory():
    """Public endpoint — only approved/active members visible."""
    all_m = db.find_all('primary_members')
    active = [m for m in all_m if m.get('status') == 'approved'
              and m.get('role_status') not in ('resigned','terminated','expired')]
    level = request.args.get('level')
    state = request.args.get('state')
    if level: active = [m for m in active if m.get('level') == level]
    if state: active = [m for m in active if m.get('state') == state]
    result = [{
        'name'       : m.get('fullname'),
        'designation': m.get('designation'),
        'state'      : m.get('state'),
        'district'   : m.get('district'),
        'institution': m.get('institution'),
        'email'      : m.get('email'),
        'photo'      : m.get('photo'),
        'level'      : m.get('level'),
    } for m in active]
    return ok(result)

# ── GET ONE ───────────────────────────────────────────────────
@members_bp.route('/<_id>', methods=['GET'])
@jwt_required()
def get_member(_id):
    claims = get_jwt()
    m = db.find_one('primary_members', 'member_id', _id) or db.find_one('primary_members', '_id', _id)
    if not m: return err('Not found', 404)
    if claims.get('role') == 'state' and claims.get('state') != m.get('state'):
        return err('Access denied', 403)
    m.pop('govtid_number', None)
    # Add expiry info
    if m.get('approved_at'):
        m['days_to_expiry'] = db.days_until_expiry(m['approved_at'], 3)
        m['expiry_date']    = db.get_expiry_date(m['approved_at'], 3)
    return ok(m)

# ── APPROVE ───────────────────────────────────────────────────
@members_bp.route('/<_id>/approve', methods=['POST'])
@require_role('national','vp','secretary')
def approve(_id):
    data = request.get_json(silent=True) or {}
    m    = db.find_one('primary_members', '_id', _id)
    if not m: return err('Not found', 404)
    now  = datetime.utcnow().isoformat() + 'Z'
    db.update_one('primary_members', _id, {
        'status'     : 'approved',
        'role_status': 'active',
        'designation': data.get('designation', 'Primary Member'),
        'level'      : data.get('level', 'state'),
        'approved_by': get_jwt_identity(),
        'approved_at': now,
        'expiry_date': db.get_expiry_date(now, 3),
    })
    # Create portal login
    from utils import hash_password
    default_pw = m['mobile'][-4:] + '@AISU'
    if not db.find_one('users', 'email', m['email']):
        db.insert('users', {
            'name'      : m['fullname'],
            'email'     : m['email'],
            'password'  : hash_password(default_pw),
            'role'      : 'member',
            'state'     : m['state'],
            'member_id' : m['member_id'],
            'status'    : 'active',
        })
    try:
        from email_service import send_primary_approved, send_generic
        m2 = db.find_one('primary_members', '_id', _id)
        send_primary_approved(m2, default_pw)
        # Send appointment order to national team
        designation = data.get('designation', 'Primary Member')
        level       = data.get('level', 'state')
        appt_body   = (
            f"A new member has been approved and an appointment order has been issued.<br><br>"
            f"<strong>Name:</strong> {m2.get('fullname')}<br>"
            f"<strong>Member ID:</strong> {m2.get('member_id')}<br>"
            f"<strong>Designation:</strong> {designation}<br>"
            f"<strong>Level:</strong> {level}<br>"
            f"<strong>State:</strong> {m2.get('state')}<br>"
            f"<strong>Email:</strong> {m2.get('email')}<br>"
            f"<strong>Approved At:</strong> {now[:10]}"
        )
        from email_service import NATIONAL_EMAILS
        from email_service import _send, _base_template
        national_list = [NATIONAL_EMAILS['president'], NATIONAL_EMAILS['vice_president'], NATIONAL_EMAILS['gen_secretary']]
        _send(national_list, f'Appointment Order Issued — {m2.get("fullname")}',
              _base_template('New Appointment Order', appt_body))
    except Exception as e:
        print(f'Email error: {e}')
    return ok({'member_id': m['member_id']}, 'Member approved')

# ── REJECT ────────────────────────────────────────────────────
@members_bp.route('/<_id>/reject', methods=['POST'])
@require_role('national','vp','secretary')
def reject(_id):
    data = request.get_json(silent=True) or {}
    m = db.find_one('primary_members', '_id', _id)
    if not m: return err('Not found', 404)
    db.update_one('primary_members', _id, {'status': 'rejected', 'rejection_reason': data.get('reason','')})
    return ok(msg='Rejected')

# ── ROLE STATUS UPDATE (Promote/Resign/Transfer/Terminate) ────
@members_bp.route('/<_id>/role-status', methods=['POST'])
@require_role('national','vp','secretary')
def update_role_status(_id):
    data = request.get_json(silent=True) or {}
    valid = ['active','promoted','demoted','transferred',
             'additional_responsibility','resigned','terminated']
    new_status = data.get('role_status')
    if new_status not in valid:
        return err(f'Invalid status. Must be one of: {", ".join(valid)}')
    updates = {'role_status': new_status}
    if new_status in ('resigned', 'terminated'):
        updates['status'] = 'inactive'
        # Revoke portal login
        user = db.find_one('users', 'email', db.find_one('primary_members','_id',_id)['email'])
        if user: db.update_one('users', user['_id'], {'status': 'inactive'})
    if 'designation' in data: updates['designation'] = data['designation']
    if 'note'        in data: updates['role_note']    = data['note']
    db.update_one('primary_members', _id, updates)
    return ok(msg=f'Role status updated to {new_status}')

# ── PERFORMANCE REPORT UPLOAD ─────────────────────────────────
@members_bp.route('/<_id>/upload-report', methods=['POST'])
@jwt_required()
def upload_report(_id):
    m = db.find_one('primary_members', '_id', _id) or db.find_one('primary_members', 'member_id', _id)
    if not m: return err('Not found', 404)
    uid = get_jwt_identity()
    user = db.find_one('users', '_id', uid)
    if not user or (user.get('member_id') != m.get('member_id') and get_jwt().get('role') not in ('national','vp','secretary')):
        return err('Access denied', 403)
    f = request.files.get('report')
    if not f: return err('No file uploaded')
    fname = save_upload(f, 'govtid')
    if not fname: return err('Invalid file type')
    reports = m.get('reports', [])
    reports.append({'file': fname, 'uploaded_at': datetime.utcnow().isoformat()+'Z', 'note': request.form.get('note','')})
    db.update_one('primary_members', m['_id'], {'reports': reports})
    return ok(msg='Report uploaded')

# ── RENEW ─────────────────────────────────────────────────────
@members_bp.route('/<_id>/renew', methods=['POST'])
@require_role('national','vp','secretary')
def renew(_id):
    m = db.find_one('primary_members', '_id', _id)
    if not m: return err('Not found', 404)
    now = datetime.utcnow().isoformat() + 'Z'
    db.update_one('primary_members', _id, {
        'status'     : 'approved',
        'role_status': 'active',
        'approved_at': now,
        'expiry_date': db.get_expiry_date(now, 3),
    })
    user = db.find_one('users', 'email', m['email'])
    if user: db.update_one('users', user['_id'], {'status': 'active'})
    return ok(msg='Membership renewed for 3 years from today')

# ── STATS ─────────────────────────────────────────────────────
@members_bp.route('/stats/summary', methods=['GET'])
@require_role('national','vp','secretary')
def stats():
    all_m = db.find_all('primary_members')
    return ok({
        'total'   : len(all_m),
        'pending' : sum(1 for m in all_m if m.get('status')=='pending'),
        'approved': sum(1 for m in all_m if m.get('status')=='approved'),
        'rejected': sum(1 for m in all_m if m.get('status')=='rejected'),
        'expired' : sum(1 for m in all_m if m.get('status')=='expired'),
        'by_state': _count_by_state(all_m),
    })

def _count_by_state(members):
    counts = {}
    for m in members:
        s = m.get('state','Unknown')
        counts[s] = counts.get(s, 0) + 1
    return counts
