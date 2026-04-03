# routes/internship.py — Internship Applications (full spec)
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from utils import ok, err, save_upload, validate_required, require_role
from datetime import datetime
import db

internship_bp = Blueprint('internship', __name__)

REQUIRED = ['fullname', 'email', 'mobile', 'state', 'institution',
            'course', 'year', 'domain', 'duration']

VALID_STATUSES = ['pending', 'shortlisted', 'selected', 'ongoing', 'completed', 'rejected']

@internship_bp.route('/apply', methods=['POST'])
def apply():
    data  = request.form.to_dict()
    files = request.files
    missing = validate_required(data, REQUIRED)
    if missing:
        return err(f'Missing: {", ".join(missing)}')
    existing = db.find_one('internships', 'email', data['email'].strip().lower())
    if existing and existing.get('status') not in ('rejected',):
        return err('An active application with this email already exists')
    resume = save_upload(files.get('resume'), 'govtid')
    doc = db.insert('internships', {
        'fullname'         : data['fullname'],
        'email'            : data['email'].strip().lower(),
        'mobile'           : data['mobile'],
        'state'            : data['state'],
        'institution'      : data['institution'],
        'course'           : data['course'],
        'year'             : data['year'],
        'domain'           : data['domain'],
        'duration'         : data['duration'],
        'resume'           : resume,
        'partner'          : data.get('partner', 'SkillChase'),
        'status'           : 'pending',
        'progress_log'     : [],
        'selection_status' : 'Applied',
        'progress_status'  : '',
        'completion_status': '',
    })
    try:
        import email_service as es
        es.send_generic(doc['email'], doc['fullname'],
            'Internship Application Received — AISU',
            f'Your internship application has been received. '
            f'Reference ID: <b>{doc["_id"][:8].upper()}</b>.<br>'
            f'Track your status by logging into your AISU account.')
    except Exception as e:
        print(f'Email error: {e}')
    return ok({'ref': doc['_id']}, 'Internship application submitted!', 201)


@internship_bp.route('/', methods=['GET'])
@require_role('national', 'vp', 'secretary', 'state')
def list_all():
    claims = get_jwt()
    apps   = db.find_all('internships')
    if claims.get('role') == 'state':
        apps = [a for a in apps if a.get('state') == claims.get('state')]
    status = request.args.get('status')
    if status:
        apps = [a for a in apps if a.get('status') == status]
    return ok(apps)


@internship_bp.route('/my', methods=['GET'])
@jwt_required()
def my_applications():
    uid  = get_jwt_identity()
    user = db.find_one('users', '_id', uid)
    if not user:
        return err('User not found', 404)
    apps = db.find_many('internships', 'email', user.get('email', ''))
    result = [{
        '_id'              : a['_id'],
        'domain'           : a.get('domain'),
        'partner'          : a.get('partner'),
        'duration'         : a.get('duration'),
        'status'           : a.get('status'),
        'selection_status' : a.get('selection_status', 'Applied'),
        'progress_status'  : a.get('progress_status', ''),
        'completion_status': a.get('completion_status', ''),
        'progress_log'     : a.get('progress_log', []),
        'created_at'       : a.get('created_at'),
    } for a in apps]
    return ok(result)


@internship_bp.route('/<_id>/status', methods=['POST'])
@require_role('national', 'vp', 'secretary', 'state')
def update_status(_id):
    claims = get_jwt()
    data   = request.get_json(silent=True) or {}
    new_status = data.get('status', '')
    if new_status not in VALID_STATUSES:
        return err(f'Invalid status. Must be one of: {", ".join(VALID_STATUSES)}')
    app = db.find_one('internships', '_id', _id)
    if not app:
        return err('Not found', 404)
    log_entry = {
        'status'    : new_status,
        'note'      : data.get('note', ''),
        'updated_by': claims.get('name', get_jwt_identity()),
        'timestamp' : datetime.utcnow().isoformat() + 'Z',
    }
    progress_log = app.get('progress_log', [])
    progress_log.append(log_entry)
    STATUS_LABELS = {
        'pending'    : ('Applied', '', ''),
        'shortlisted': ('Shortlisted', '', ''),
        'selected'   : ('Selected', 'Starting Soon', ''),
        'ongoing'    : ('Selected', 'In Progress', ''),
        'completed'  : ('Selected', 'Completed', 'Completed'),
        'rejected'   : ('Not Selected', '', ''),
    }
    sel, prog, comp = STATUS_LABELS.get(new_status, ('Applied', '', ''))
    updates = {
        'status'           : new_status,
        'selection_status' : sel,
        'progress_status'  : prog,
        'completion_status': comp,
        'progress_log'     : progress_log,
    }
    if new_status == 'rejected' and data.get('reason'):
        updates['rejection_reason'] = data['reason']
    db.update_one('internships', _id, updates)
    try:
        import email_service as es
        msg_map = {
            'shortlisted': 'Your internship application has been <b>shortlisted</b>! Our team will contact you soon.',
            'selected'   : 'Congratulations! You have been <b>selected</b> for the internship.',
            'ongoing'    : 'Your internship is now marked as <b>In Progress</b>. Best of luck!',
            'completed'  : 'Your internship is <b>Completed</b>. Your completion certificate will be issued shortly.',
            'rejected'   : f'We regret your internship application was not selected. {data.get("reason", "")}',
        }
        if new_status in msg_map:
            es.send_generic(app['email'], app['fullname'],
                'Internship Application Update — AISU', msg_map[new_status])
    except Exception as e:
        print(f'Email error: {e}')
    # Auto-trigger completion certificate
    if new_status == 'completed':
        try:
            cert_num = db.gen_cert_id('INTERN')
            db.insert('certificates', {
                'cert_number'      : cert_num,
                'participant_name' : app['fullname'],
                'participant_email': app['email'],
                'program'          : f'Internship — {app.get("domain","")} ({app.get("partner","")})',
                'prog_code'        : 'INTERN',
                'cert_type'        : 'Completion',
                'template_id'      : None,
                'filename'         : None,
                'status'           : 'issued',
                'issued_at'        : datetime.utcnow().isoformat() + 'Z',
                'source'           : 'internship',
                'source_id'        : _id,
            })
            import email_service as es
            es.send_certificate_issued(app['email'], app['fullname'], cert_num, 'Internship Completion')
        except Exception as e:
            print(f'Completion cert error: {e}')
    return ok(msg=f'Status updated to {new_status}')


@internship_bp.route('/<_id>/approve', methods=['POST'])
@require_role('national', 'vp', 'secretary')
def approve(_id):
    db.update_one('internships', _id, {
        'status': 'selected', 'selection_status': 'Selected', 'progress_status': 'Starting Soon'
    })
    return ok(msg='Internship application approved')


@internship_bp.route('/<_id>/reject', methods=['POST'])
@require_role('national', 'vp', 'secretary')
def reject(_id):
    data = request.get_json(silent=True) or {}
    db.update_one('internships', _id, {
        'status': 'rejected', 'selection_status': 'Not Selected',
        'rejection_reason': data.get('reason', '')
    })
    return ok(msg='Rejected')
