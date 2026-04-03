# routes/certs.py — Certificate issuance, verification, revoke, reissue
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from utils import ok, err, require_role
from datetime import datetime
import db

certs_bp = Blueprint('certs', __name__)

# ── VERIFY (public — by cert number, mobile, or email) ────────
@certs_bp.route('/verify/<cert_num>', methods=['GET'])
def verify_by_number(cert_num):
    c = db.find_one('certificates', 'cert_number', cert_num.upper())
    if not c:
        return err('Certificate not found. Please check the number and try again.', 404)
    if c.get('status') == 'revoked':
        return ok({
            'cert_number'     : c['cert_number'],
            'status'          : 'revoked',
            'revoked_at'      : c.get('revoked_at'),
            'revoke_reason'   : c.get('revoke_reason', ''),
        }, 'This certificate has been revoked.')
    return ok(_safe_cert(c), 'Certificate is valid.')


@certs_bp.route('/verify', methods=['GET'])
def verify_by_identifier():
    """Verify by mobile or email — returns all certs for that person."""
    identifier = request.args.get('q', '').strip()
    id_type    = request.args.get('type', '').strip()   # 'mobile' | 'email' | 'cert'

    if not identifier:
        return err('Query parameter q is required')

    if id_type == 'cert' or (not id_type and identifier.upper().startswith('AISUCERT')):
        c = db.find_one('certificates', 'cert_number', identifier.upper())
        if not c:
            return err('Certificate not found', 404)
        return ok([_safe_cert(c)], f'1 certificate found')

    all_certs = db.find_all('certificates')

    if id_type == 'mobile' or (not id_type and identifier.isdigit()):
        digits = ''.join(c for c in identifier if c.isdigit())
        # Look up user by mobile
        user = db.find_one('users', 'mobile', digits)
        if not user:
            # Also check member records
            mem = None
            for col in ('primary_members', 'student_members', 'competition_registrations'):
                mem = db.find_one(col, 'mobile', digits)
                if mem:
                    break
        email_to_match = None
        if user:
            email_to_match = user.get('email', '')
        elif mem:
            email_to_match = mem.get('email', '')
        if not email_to_match:
            return ok([], 'No certificates found for this mobile number.')
        certs = [_safe_cert(c) for c in all_certs
                 if c.get('participant_email', '').lower() == email_to_match.lower()
                 and c.get('status') != 'revoked']
        return ok(certs, f'{len(certs)} certificate(s) found')

    if id_type == 'email' or '@' in identifier:
        email = identifier.lower()
        certs = [_safe_cert(c) for c in all_certs
                 if c.get('participant_email', '').lower() == email
                 and c.get('status') != 'revoked']
        return ok(certs, f'{len(certs)} certificate(s) found')

    return err('Could not determine identifier type. Use type=cert, type=mobile, or type=email')


def _safe_cert(c):
    return {
        'cert_number'     : c.get('cert_number'),
        'participant_name': c.get('participant_name'),
        'program'         : c.get('program'),
        'cert_type'       : c.get('cert_type', 'Participation'),
        'prog_code'       : c.get('prog_code'),
        'issued_at'       : c.get('issued_at'),
        'status'          : c.get('status', 'issued'),
    }


# ── LIST / SEARCH (admin) ─────────────────────────────────────
@certs_bp.route('/', methods=['GET'])
def list_or_search_certs():
    q = request.args.get('q', '').strip()
    all_certs = db.find_all('certificates')
    if q:
        ql = q.lower()
        all_certs = [c for c in all_certs if
                     ql in c.get('cert_number', '').lower() or
                     ql in c.get('participant_name', '').lower() or
                     ql in c.get('participant_email', '').lower() or
                     ql in c.get('program', '').lower()]
    prog = request.args.get('prog_code')
    if prog:
        all_certs = [c for c in all_certs if c.get('prog_code') == prog.upper()]
    return ok(all_certs, f'{len(all_certs)} certificates')


# ── ISSUE (manual — admin only) ───────────────────────────────
@certs_bp.route('/issue', methods=['POST'])
@require_role('national', 'vp', 'secretary')
def issue():
    data = request.get_json(silent=True) or {}
    for f in ['participant_name', 'participant_email', 'program', 'prog_code']:
        if not data.get(f):
            return err(f'Missing required field: {f}')
    cert_num = db.gen_cert_id(data['prog_code'].upper())
    cert = db.insert('certificates', {
        'cert_number'      : cert_num,
        'participant_name' : data['participant_name'],
        'participant_email': data['participant_email'].strip().lower(),
        'program'          : data['program'],
        'prog_code'        : data['prog_code'].upper(),
        'cert_type'        : data.get('cert_type', 'Participation'),
        'template_id'      : data.get('template_id'),
        'filename'         : data.get('filename'),
        'status'           : 'issued',
        'issued_at'        : datetime.utcnow().isoformat() + 'Z',
        'issued_by'        : get_jwt_identity(),
    })
    try:
        import email_service as es
        es.send_certificate_issued(
            data['participant_email'], data['participant_name'],
            cert_num, data['program'])
    except Exception as e:
        print(f'Email error: {e}')
    return ok({'cert_number': cert_num, 'id': cert['_id']},
              'Certificate issued successfully', 201)


# ── REVOKE ────────────────────────────────────────────────────
@certs_bp.route('/<_id>/revoke', methods=['POST'])
@require_role('national', 'vp')
def revoke(_id):
    data = request.get_json(silent=True) or {}
    c = db.find_one('certificates', '_id', _id)
    if not c:
        return err('Certificate not found', 404)
    db.update_one('certificates', _id, {
        'status'       : 'revoked',
        'revoked_at'   : datetime.utcnow().isoformat() + 'Z',
        'revoke_reason': data.get('reason', ''),
    })
    return ok(msg='Certificate revoked')


# ── REISSUE ───────────────────────────────────────────────────
@certs_bp.route('/<_id>/reissue', methods=['POST'])
@require_role('national', 'vp', 'secretary')
def reissue(_id):
    c = db.find_one('certificates', '_id', _id)
    if not c:
        return err('Certificate not found', 404)
    new_num = db.gen_cert_id(c.get('prog_code', 'COMP'))
    new_cert = db.insert('certificates', {
        'cert_number'      : new_num,
        'participant_name' : c['participant_name'],
        'participant_email': c['participant_email'],
        'program'          : c['program'],
        'prog_code'        : c.get('prog_code', 'COMP'),
        'cert_type'        : c.get('cert_type', 'Participation'),
        'template_id'      : c.get('template_id'),
        'filename'         : c.get('filename'),
        'status'           : 'issued',
        'issued_at'        : datetime.utcnow().isoformat() + 'Z',
        'reissued_from'    : c['cert_number'],
    })
    db.update_one('certificates', _id, {'status': 'reissued', 'reissued_to': new_num})
    try:
        import email_service as es
        es.send_certificate_issued(c['participant_email'], c['participant_name'],
                                   new_num, c['program'])
    except Exception as e:
        print(f'Email error: {e}')
    return ok({'new_cert_number': new_num, 'id': new_cert['_id']}, 'Certificate reissued')


# ── LIST ALL (admin records panel) ───────────────────────────
@certs_bp.route('/all', methods=['GET'])
@require_role('national', 'vp', 'secretary')
def list_all():
    certs = db.find_all('certificates')
    status = request.args.get('status')
    if status:
        certs = [c for c in certs if c.get('status') == status]
    return ok(certs, f'{len(certs)} certificates')


# ── MY CERTIFICATES (logged-in user) ─────────────────────────
@certs_bp.route('/my', methods=['GET'])
@jwt_required()
def my_certs():
    uid  = get_jwt_identity()
    user = db.find_one('users', '_id', uid)
    if not user:
        return err('User not found', 404)
    email = user.get('email', '')
    certs = [_safe_cert(c) for c in db.find_all('certificates')
             if c.get('participant_email', '').lower() == email.lower()
             and c.get('status') != 'revoked']
    return ok(certs, f'{len(certs)} certificate(s) found')
