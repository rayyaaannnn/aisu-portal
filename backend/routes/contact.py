# routes/contact.py — Contact Form
from flask import Blueprint, request
from utils import ok, err, validate_required
import db

contact_bp = Blueprint('contact', __name__)

@contact_bp.route('/send', methods=['POST'])
def send():
    data = request.get_json(silent=True) or request.form.to_dict()
    missing = validate_required(data, ['name', 'email', 'subject', 'message'])
    if missing:
        return err(f'Missing: {", ".join(missing)}')
    doc = db.insert('contacts', {
        'name'   : data['name'],
        'email'  : data['email'].strip().lower(),
        'mobile' : data.get('mobile', ''),
        'subject': data['subject'],
        'message': data['message'],
        'state'  : data.get('state', ''),
        'status' : 'unread',
    })
    return ok({'ref': doc['_id']}, 'Message received! We will get back to you within 48 hours.', 201)

@contact_bp.route('/', methods=['GET'])
def list_contacts():
    from utils import require_role
    from flask_jwt_extended import verify_jwt_in_request, get_jwt
    try:
        verify_jwt_in_request()
        claims = get_jwt()
        if claims.get('role') not in ('national', 'vp', 'secretary'):
            return err('Access denied', 403)
    except Exception:
        return err('Authentication required', 401)
    return ok(db.find_all('contacts'))

@contact_bp.route('/<_id>/read', methods=['POST'])
def mark_read(_id):
    db.update_one('contacts', _id, {'status': 'read'})
    return ok(msg='Marked as read')

# ── STATE OFFICIALS (public directory) ────────────────────────
@contact_bp.route('/state-officials', methods=['GET'])
def state_officials():
    """Public endpoint returning approved primary members with official emails."""
    officials = db.find_many('primary_members', filters={'status': 'approved'})
    result = []
    for o in officials:
        if o.get('email'):  # Only show members with emails
            result.append({
                'name'        : o.get('fullname', ''),
                'designation' : o.get('designation', 'Primary Member'),
                'level'       : o.get('level', 'state'),
                'state'       : o.get('state', ''),
                'district'    : o.get('district', ''),
                'official_email_1': o.get('official_email_1', o.get('email', '')),
                'official_email_2': o.get('official_email_2', ''),
                'mobile'      : o.get('mobile', ''),
            })
    return ok(result, f'{len(result)} officials')


# ── UPDATE OFFICIAL EMAILS (admin) ────────────────────────────
@contact_bp.route('/set-official-emails/<member_id>', methods=['POST'])
def set_official_emails(member_id):
    from utils import require_role
    from flask_jwt_extended import verify_jwt_in_request, get_jwt
    try:
        verify_jwt_in_request()
        claims = get_jwt()
        if claims.get('role') not in ('national', 'vp', 'secretary'):
            return err('Access denied', 403)
    except Exception:
        return err('Authentication required', 401)
    data = request.get_json(silent=True) or {}
    m = db.find_one('primary_members', '_id', member_id) or db.find_one('primary_members', 'member_id', member_id)
    if not m:
        return err('Member not found', 404)
    db.update_one('primary_members', m['_id'], {
        'official_email_1': data.get('email_1', '').strip().lower(),
        'official_email_2': data.get('email_2', '').strip().lower(),
    })
    return ok(msg='Official emails updated')
