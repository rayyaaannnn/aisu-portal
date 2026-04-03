# routes/complaint.py — Complaint Portal (full tiered-access spec)
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from utils import ok, err, save_upload, validate_required, require_role
from datetime import datetime
import db

complaint_bp = Blueprint('complaint', __name__)

REQUIRED = ['category','description']

CATEGORIES = [
    'Fee & Scholarship','Ragging','Harassment','Academic Issue',
    'Discrimination','Faculty Misconduct','Infrastructure','Other'
]

# ── SUBMIT (Must be logged in — student/general user) ─────────
@complaint_bp.route('/submit', methods=['POST'])
@jwt_required()
def submit():
    uid   = get_jwt_identity()
    user  = db.find_one('users', '_id', uid)
    if not user: return err('Authentication required', 401)
    data  = request.form.to_dict()
    files = request.files
    missing = validate_required(data, REQUIRED)
    if missing: return err(f'Missing: {", ".join(missing)}')
    if data['category'] not in CATEGORIES:
        return err(f'Invalid category. Must be one of: {", ".join(CATEGORIES)}')
    proof_file = save_upload(files.get('proof'), 'complaint')
    cmplt_id   = db.gen_complaint_id()
    doc = db.insert('complaints', {
        'complaint_id'   : cmplt_id,
        'user_id'        : uid,
        'name'           : user.get('name'),
        'mobile'         : user.get('mobile',''),
        'email'          : user.get('email'),
        'state'          : data.get('state', user.get('state','')),
        'district'       : data.get('district',''),
        'institution'    : data.get('institution',''),
        'category'       : data['category'],
        'description'    : data['description'],
        'proof_file'     : proof_file,
        'is_anonymous'   : data.get('is_anonymous','false').lower() == 'true',
        'status'         : 'open',
        'action_log'     : [],    # [{level, action, updater, timestamp, doc}]
        'assigned_to'    : '',
        'resolution'     : '',
        'is_confidential': True,
    })
    return ok({'complaint_id': cmplt_id}, f'Complaint registered. Track using ID: {cmplt_id}', 201)

# ── TRACK BY ID (Public — no identity shown) ──────────────────
@complaint_bp.route('/track/<complaint_id>', methods=['GET'])
def track(complaint_id):
    c = db.find_one('complaints', 'complaint_id', complaint_id)
    if not c: return err('Complaint ID not found', 404)
    return ok({
        'complaint_id': c['complaint_id'],
        'category'    : c['category'],
        'status'      : c['status'],
        'created_at'  : c['created_at'],
        'resolution'  : c.get('resolution',''),
        'updates'     : [
            { 'action': a.get('action'), 'timestamp': a.get('timestamp'), 'level': a.get('level') }
            for a in c.get('action_log', [])
        ],
    })

# ── LIST — tiered access ───────────────────────────────────────
@complaint_bp.route('/', methods=['GET'])
@jwt_required()
def list_complaints():
    claims = get_jwt()
    role   = claims.get('role')
    all_c  = db.find_all('complaints')
    status = request.args.get('status')
    if status: all_c = [c for c in all_c if c.get('status') == status]

    if role in ('national','vp','secretary'):
        # FULL visibility
        result = all_c
    elif role in ('state','district','mandal','institutional'):
        # ID-ONLY: cannot see complainant identity
        sub_level_visible = ['complaint_id','category','status','created_at',
                             'description','proof_file','action_log','resolution',
                             'district','institution']
        result = [{k: c.get(k) for k in sub_level_visible} for c in all_c
                  if c.get('state') == claims.get('state')]
    else:
        return err('Access denied', 403)

    return ok(result, f'{len(result)} complaints')

# ── UPDATE / ADD ACTION ────────────────────────────────────────
@complaint_bp.route('/<_id>/update', methods=['POST'])
@jwt_required()
def update_complaint(_id):
    claims = get_jwt()
    role   = claims.get('role')
    allowed = ('national','vp','secretary','state','district','mandal','institutional')
    if role not in allowed: return err('Access denied', 403)
    data = request.form.to_dict()
    files= request.files
    c    = db.find_one('complaints', '_id', _id)
    if not c: return err('Not found', 404)
    doc_file = save_upload(files.get('support_doc'), 'complaint')
    action_entry = {
        'level'    : role,
        'action'   : data.get('action',''),
        'updater'  : claims.get('name', get_jwt_identity()),
        'timestamp': datetime.utcnow().isoformat()+'Z',
        'document' : doc_file,
    }
    action_log = c.get('action_log', [])
    action_log.append(action_entry)
    updates = {'action_log': action_log}
    if 'status' in data:
        valid_s = ['open','in_progress','resolved','disposed']
        if data['status'] not in valid_s: return err(f'Invalid status: {data["status"]}')
        updates['status'] = data['status']
    if 'resolution' in data: updates['resolution'] = data['resolution']
    if 'assigned_to' in data: updates['assigned_to'] = data['assigned_to']
    db.update_one('complaints', _id, updates)
    # Email complainant
    try:
        from email_service import send_complaint_update, send_complaint_disposed
        c2 = db.find_one('complaints', '_id', _id)
        if data.get('status') == 'disposed':
            send_complaint_disposed(c2)
        else:
            send_complaint_update(c2, data.get('action',''), action_entry['updater'])
    except Exception as e:
        print(f'Email error: {e}')
    return ok(msg='Complaint updated')

# ── DISPOSE ───────────────────────────────────────────────────
@complaint_bp.route('/<_id>/dispose', methods=['POST'])
@require_role('national','vp','secretary')
def dispose(_id):
    data = request.get_json(silent=True) or {}
    c    = db.find_one('complaints', '_id', _id)
    if not c: return err('Not found', 404)
    db.update_one('complaints', _id, {
        'status'    : 'disposed',
        'resolution': data.get('resolution', 'Resolved and disposed.'),
        'disposed_at': datetime.utcnow().isoformat()+'Z',
    })
    try:
        from email_service import send_complaint_disposed
        send_complaint_disposed(db.find_one('complaints', '_id', _id))
    except Exception as e:
        print(f'Email error: {e}')
    return ok(msg='Complaint disposed')
