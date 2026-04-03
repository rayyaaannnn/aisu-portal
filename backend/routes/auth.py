# routes/auth.py — Login, registration, token refresh, password change
from flask import Blueprint, request
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, get_jwt
)
from utils import ok, err, hash_password, check_password, validate_required, require_role
import db

auth_bp = Blueprint('auth', __name__)

# ── REGISTER (Public — user self-signup) ──────────────────────
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json(silent=True) or {}
    missing = validate_required(data, ['name', 'email', 'mobile', 'password'])
    if missing:
        return err(f'Missing fields: {", ".join(missing)}')

    email  = data['email'].strip().lower()
    mobile = ''.join(c for c in data['mobile'] if c.isdigit())
    name   = data['name'].strip()
    pwd    = data['password']

    if len(mobile) < 10:
        return err('Mobile number must be at least 10 digits')
    if len(pwd) < 6:
        return err('Password must be at least 6 characters')

    # If account already exists with this email or mobile, ADD roles rather than duplicate
    existing = db.find_one('users', 'email', email)
    if not existing:
        existing = db.find_one('users', 'mobile', mobile)

    if existing:
        # Merge: add any new roles/activities to existing account, update name/state if blank
        updates = {}
        if not existing.get('name') and name:
            updates['name'] = name
        if not existing.get('state') and data.get('state'):
            updates['state'] = data.get('state', '')
        if updates:
            db.update_one('users', existing['_id'], updates)
        identity = existing['_id']
        claims   = {'role': existing['role'], 'name': existing.get('name', name),
                    'email': existing['email'], 'state': existing.get('state', '')}
        access   = create_access_token(identity=identity, additional_claims=claims)
        refresh  = create_refresh_token(identity=identity, additional_claims=claims)
        return ok({
            'access_token' : access,
            'refresh_token': refresh,
            'user': {'id': existing['_id'], 'name': existing.get('name', name),
                     'email': existing['email'], 'role': existing['role']},
            'merged': True
        }, 'Account already exists. Logged in to your existing account.')

    user_doc = db.insert('users', {
        'name'    : name,
        'email'   : email,
        'mobile'  : mobile,
        'state'   : data.get('state', ''),
        'password': hash_password(pwd),
        'role'    : 'user',
        'status'  : 'active',
        'roles'   : ['user'],  # list for future multi-role support
    })

    identity = user_doc['_id']
    claims   = {'role': 'user', 'name': name, 'email': email, 'state': data.get('state', '')}
    access   = create_access_token(identity=identity, additional_claims=claims)
    refresh  = create_refresh_token(identity=identity, additional_claims=claims)
    return ok({
        'access_token' : access,
        'refresh_token': refresh,
        'user': {'id': user_doc['_id'], 'name': name, 'email': email, 'role': 'user'}
    }, 'Account created successfully!', 201)


# ── Seed default admin on first run ──────────────────────────
def seed_admin():
    if not db.find_one('users', 'email', 'admin@aisu4india.in'):
        db.insert('users', {
            'name'    : 'National Admin',
            'email'   : 'admin@aisu4india.in',
            'mobile'  : '0000000000',
            'password': hash_password('Admin@AISU2024'),
            'role'    : 'national',
            'state'   : 'ALL',
            'status'  : 'active',
            'roles'   : ['national'],
        })
        print('✅ Default admin seeded: admin@aisu4india.in / Admin@AISU2024')

try:
    seed_admin()
except Exception:
    pass


# ── LOGIN (email, mobile, or unique member ID) ─────────────────
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}
    missing = validate_required(data, ['identifier', 'password'])
    # Support both old 'email' field and new 'identifier' field
    if missing:
        if data.get('email') and data.get('password'):
            data['identifier'] = data['email']
        else:
            return err('Missing fields: identifier and password required')

    identifier = data['identifier'].strip()
    pwd        = data['password']

    # Try email first
    user = db.find_one('users', 'email', identifier.lower())

    # Try mobile
    if not user:
        digits = ''.join(c for c in identifier if c.isdigit())
        if digits:
            user = db.find_one('users', 'mobile', digits)

    # Try unique member ID (primary or student)
    if not user:
        mem = db.find_one('primary_members', 'member_id', identifier.upper())
        if not mem:
            mem = db.find_one('student_members', 'member_id', identifier.upper())
        if mem:
            user = db.find_one('users', 'email', mem.get('email', ''))

    if not user or not check_password(pwd, user['password']):
        return err('Invalid credentials. Use email, mobile number, or member ID.', 401)
    if user.get('status') != 'active':
        return err('Account is not active. Please contact national admin.', 403)

    identity          = user['_id']
    additional_claims = {
        'role' : user['role'],
        'name' : user['name'],
        'email': user['email'],
        'state': user.get('state', ''),
    }
    access  = create_access_token(identity=identity, additional_claims=additional_claims)
    refresh = create_refresh_token(identity=identity, additional_claims=additional_claims)
    return ok({
        'access_token' : access,
        'refresh_token': refresh,
        'user': {
            'id'   : user['_id'],
            'name' : user['name'],
            'email': user['email'],
            'role' : user['role'],
            'state': user.get('state', ''),
        }
    }, 'Login successful')


# ── FORGOT PASSWORD (request OTP) ─────────────────────────────
@auth_bp.route('/forgot-password/request', methods=['POST'])
def forgot_password_request():
    data = request.get_json(silent=True) or {}
    identifier = data.get('identifier', '').strip()
    if not identifier:
        return err('Email or mobile required')
    user = db.find_one('users', 'email', identifier.lower())
    if not user:
        digits = ''.join(c for c in identifier if c.isdigit())
        if digits:
            user = db.find_one('users', 'mobile', digits)
    if not user:
        # Return ok anyway to prevent user enumeration
        return ok(msg='If this account exists, a reset code has been sent.')
    import random, string
    from datetime import datetime, timedelta
    otp = ''.join(random.choices(string.digits, k=6))
    expiry = (datetime.utcnow() + timedelta(minutes=15)).isoformat() + 'Z'
    db.update_one('users', user['_id'], {'reset_otp': otp, 'reset_otp_expiry': expiry})
    try:
        import email_service as es
        es.send_generic(user['email'], user['name'],
            'Password Reset Code — AISU',
            f'Your password reset code is: <b style="font-size:1.5em;">{otp}</b><br>'
            f'This code expires in 15 minutes. Do not share it with anyone.')
    except Exception as e:
        print(f'OTP email error: {e}')
    return ok({'masked_email': user['email'][:2] + '***' + user['email'][-8:]},
              'Reset code sent to your registered email.')


# ── FORGOT PASSWORD (verify OTP + set new password) ───────────
@auth_bp.route('/forgot-password/reset', methods=['POST'])
def forgot_password_reset():
    data = request.get_json(silent=True) or {}
    missing = validate_required(data, ['identifier', 'otp', 'new_password'])
    if missing:
        return err(f'Missing: {", ".join(missing)}')
    identifier = data['identifier'].strip()
    user = db.find_one('users', 'email', identifier.lower())
    if not user:
        digits = ''.join(c for c in identifier if c.isdigit())
        user = db.find_one('users', 'mobile', digits) if digits else None
    if not user:
        return err('Account not found', 404)
    from datetime import datetime
    otp        = data['otp'].strip()
    stored_otp = user.get('reset_otp', '')
    expiry_str = user.get('reset_otp_expiry', '')
    if otp != stored_otp:
        return err('Invalid reset code', 400)
    if expiry_str:
        expiry = datetime.fromisoformat(expiry_str.replace('Z', ''))
        if datetime.utcnow() > expiry:
            return err('Reset code has expired. Please request a new one.', 400)
    if len(data['new_password']) < 8:
        return err('Password must be at least 8 characters')
    db.update_one('users', user['_id'], {
        'password': hash_password(data['new_password']),
        'reset_otp': '',
        'reset_otp_expiry': '',
    })
    return ok(msg='Password reset successfully. Please login.')


# ── REFRESH ───────────────────────────────────────────────────
@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    claims   = get_jwt()
    access   = create_access_token(identity=identity, additional_claims={
        'role' : claims.get('role'),
        'name' : claims.get('name'),
        'email': claims.get('email'),
        'state': claims.get('state'),
    })
    return ok({'access_token': access}, 'Token refreshed')


# ── CHANGE PASSWORD ───────────────────────────────────────────
@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    data = request.get_json(silent=True) or {}
    missing = validate_required(data, ['old_password', 'new_password'])
    if missing:
        return err(f'Missing: {", ".join(missing)}')
    uid  = get_jwt_identity()
    user = db.find_one('users', '_id', uid)
    if not user or not check_password(data['old_password'], user['password']):
        return err('Incorrect current password', 401)
    if len(data['new_password']) < 8:
        return err('New password must be at least 8 characters')
    db.update_one('users', uid, {'password': hash_password(data['new_password'])})
    return ok(msg='Password changed successfully')


# ── WHO AM I ─────────────────────────────────────────────────
@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    uid  = get_jwt_identity()
    user = db.find_one('users', '_id', uid)
    if not user:
        return err('User not found', 404)
    user.pop('password', None)
    user.pop('reset_otp', None)
    user.pop('reset_otp_expiry', None)
    # Attach member records if any
    member  = db.find_one('primary_members', 'email', user.get('email', ''))
    student = db.find_one('student_members', 'email', user.get('email', ''))
    if member:
        user['primary_membership'] = {
            'member_id'   : member.get('member_id'),
            'status'      : member.get('status'),
            'approved_at' : member.get('approved_at'),
            'expiry_date' : db.get_expiry_date(member.get('approved_at', ''), 3) if member.get('approved_at') else None,
        }
    if student:
        user['student_membership'] = {
            'member_id'   : student.get('member_id'),
            'status'      : student.get('status'),
            'approved_at' : student.get('approved_at'),
            'expiry_date' : db.get_expiry_date(student.get('approved_at', ''), 1) if student.get('approved_at') else None,
        }
    return ok(user)
