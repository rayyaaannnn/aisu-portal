# routes/students.py — Student Membership
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt
from utils import ok, err, save_upload, validate_required, require_role, state_code
import db

students_bp = Blueprint('students', __name__)

REQUIRED = ['fullname', 'parent_name', 'dob', 'age', 'gender',
            'address', 'pin', 'institution', 'state', 'district',
            'city', 'mobile', 'email', 'heard_about', 'mode_of_submission']

# ── SUBMIT (Public) ────────────────────────────────────────────
@students_bp.route('/apply', methods=['POST'])
def apply():
    data  = request.form.to_dict()
    files = request.files
    missing = validate_required(data, REQUIRED)
    if missing:
        return err(f'Missing: {", ".join(missing)}')

    mobile = data['mobile'].strip()
    if not mobile.isdigit() or len(mobile) != 10:
        return err('Mobile must be 10 digits')

    if db.find_one('student_members', 'email', data['email'].strip().lower()):
        return err('An application with this email already exists')

    sc         = state_code(data['state'])
    student_id = db.gen_student_id(sc)
    payment    = save_upload(files.get('payment_proof'), 'payment')

    doc = db.insert('student_members', {
        'student_id'        : student_id,
        'fullname'          : data['fullname'].upper(),
        'parent_name'       : data.get('parent_name', ''),
        'dob'               : data.get('dob', ''),
        'age'               : data.get('age', ''),
        'gender'            : data.get('gender', ''),
        'address'           : data.get('address', ''),
        'pin'               : data.get('pin', ''),
        'institution'       : data.get('institution', ''),
        'state'             : data.get('state', ''),
        'district'          : data.get('district', ''),
        'city'              : data.get('city', ''),
        'mobile'            : mobile,
        'email'             : data['email'].strip().lower(),
        'heard_about'       : data.get('heard_about', ''),
        'payment_proof'     : payment,
        'mode_of_submission': data.get('mode_of_submission', ''),
        'status'            : 'pending',
    })
    return ok({'application_ref': doc['_id']},
              'Student membership application submitted! Your AISU Student ID will be emailed after approval.', 201)

# ── LIST ───────────────────────────────────────────────────────
@students_bp.route('/', methods=['GET'])
@require_role('national', 'vp', 'secretary', 'state')
def list_students():
    claims = get_jwt()
    all_s  = db.find_all('student_members')
    if claims.get('role') == 'state':
        all_s = [s for s in all_s if s.get('state') == claims.get('state')]
    status = request.args.get('status')
    if status:
        all_s = [s for s in all_s if s.get('status') == status]
    return ok(all_s, f'{len(all_s)} records')

# ── APPROVE ────────────────────────────────────────────────────
@students_bp.route('/<_id>/approve', methods=['POST'])
@require_role('national', 'vp', 'secretary')
def approve(_id):
    from flask_jwt_extended import get_jwt_identity
    from datetime import datetime
    s = db.find_one('student_members', '_id', _id)
    if not s:
        return err('Not found', 404)
    db.update_one('student_members', _id, {
        'status'     : 'approved',
        'approved_by': get_jwt_identity(),
        'approved_at': datetime.utcnow().isoformat() + 'Z',
    })
    return ok({'student_id': s['student_id']}, 'Student approved')

# ── REJECT ─────────────────────────────────────────────────────
@students_bp.route('/<_id>/reject', methods=['POST'])
@require_role('national', 'vp', 'secretary')
def reject(_id):
    data = request.get_json(silent=True) or {}
    s = db.find_one('student_members', '_id', _id)
    if not s:
        return err('Not found', 404)
    db.update_one('student_members', _id, {
        'status'          : 'rejected',
        'rejection_reason': data.get('reason', ''),
    })
    return ok(msg='Rejected')

# ── STATS ──────────────────────────────────────────────────────
@students_bp.route('/stats/summary', methods=['GET'])
@require_role('national', 'vp', 'secretary')
def stats():
    all_s = db.find_all('student_members')
    return ok({
        'total'   : len(all_s),
        'pending' : sum(1 for s in all_s if s.get('status') == 'pending'),
        'approved': sum(1 for s in all_s if s.get('status') == 'approved'),
        'rejected': sum(1 for s in all_s if s.get('status') == 'rejected'),
    })


# ── CHECK MEMBERSHIP STATUS (used by competition module) ──────
@students_bp.route('/membership-status/<email>', methods=['GET'])
def membership_status(email):
    """Returns whether a student has active, lapsed, or no membership."""
    student = db.find_one('student_members', 'email', email.strip().lower())
    if not student or student.get('status') != 'approved':
        return ok({'has_membership': False, 'fee_required': True,
                   'message': 'No active student membership. Per-competition fee applies.'})
    approved_at = student.get('approved_at', '')
    if approved_at and db.is_expired(approved_at, 1):
        return ok({'has_membership': True, 'lapsed': True, 'fee_required': True,
                   'student_id': student.get('student_id'),
                   'message': 'Student membership expired. Renew or pay per-competition fee.'})
    return ok({'has_membership': True, 'lapsed': False, 'fee_required': False,
               'student_id': student.get('student_id'),
               'expiry_date': db.get_expiry_date(approved_at, 1),
               'message': 'Active student membership — free access to competitions.'})
