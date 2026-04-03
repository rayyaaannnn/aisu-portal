# routes/admin.py — Admin: user management, dashboard stats, state officer creation
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity, verify_jwt_in_request
from utils import ok, err, hash_password, validate_required, require_role
import db

admin_bp = Blueprint('admin', __name__)

# ── DASHBOARD STATS ───────────────────────────────────────────
@admin_bp.route('/stats', methods=['GET'])
@require_role('national', 'vp', 'secretary')
def dashboard_stats():
    members    = db.find_all('primary_members')
    students   = db.find_all('student_members')
    complaints = db.find_all('complaints')
    contacts   = db.find_all('contacts')
    certs      = db.find_all('certificates')
    internships = db.find_all('internships')
    affiliations = db.find_all('affiliations')
    return ok({
        'primary_members': {
            'total'   : len(members),
            'pending' : sum(1 for m in members if m.get('status') == 'pending'),
            'approved': sum(1 for m in members if m.get('status') == 'approved'),
            'rejected': sum(1 for m in members if m.get('status') == 'rejected'),
        },
        'student_members': {
            'total'   : len(students),
            'pending' : sum(1 for s in students if s.get('status') == 'pending'),
            'approved': sum(1 for s in students if s.get('status') == 'approved'),
        },
        'complaints': {
            'total'      : len(complaints),
            'open'       : sum(1 for c in complaints if c.get('status') == 'open'),
            'in_progress': sum(1 for c in complaints if c.get('status') == 'in_progress'),
            'resolved'   : sum(1 for c in complaints if c.get('status') == 'resolved'),
        },
        'contacts'    : len(contacts),
        'certificates': len(certs),
        'internships' : len(internships),
        'affiliations': len(affiliations),
    })

# ── LIST USERS ────────────────────────────────────────────────
@admin_bp.route('/users', methods=['GET'])
@require_role('national')
def list_users():
    users = db.find_all('users')
    for u in users:
        u.pop('password', None)
    return ok(users)

# ── CREATE STATE OFFICER / USER ───────────────────────────────
@admin_bp.route('/users/create', methods=['POST'])
@require_role('national')
def create_user():
    data = request.get_json(silent=True) or {}
    missing = validate_required(data, ['name', 'email', 'password', 'role'])
    if missing:
        return err(f'Missing: {", ".join(missing)}')
    valid_roles = ['national', 'vp', 'secretary', 'treasurer', 'state', 'member']
    if data['role'] not in valid_roles:
        return err(f'Invalid role. Must be one of: {", ".join(valid_roles)}')
    if db.find_one('users', 'email', data['email'].strip().lower()):
        return err('User with this email already exists')
    doc = db.insert('users', {
        'name'    : data['name'],
        'email'   : data['email'].strip().lower(),
        'password': hash_password(data['password']),
        'role'    : data['role'],
        'state'   : data.get('state', ''),
        'designation': data.get('designation', ''),
        'status'  : 'active',
    })
    doc.pop('password', None)
    return ok(doc, 'User created', 201)

# ── UPDATE USER ───────────────────────────────────────────────
@admin_bp.route('/users/<_id>', methods=['PUT'])
@require_role('national')
def update_user(_id):
    data = request.get_json(silent=True) or {}
    updates = {}
    for field in ['name', 'role', 'state', 'designation', 'status']:
        if field in data:
            updates[field] = data[field]
    if 'password' in data and data['password']:
        updates['password'] = hash_password(data['password'])
    if not updates:
        return err('No fields to update')
    updated = db.update_one('users', _id, updates)
    if not updated:
        return err('User not found', 404)
    updated.pop('password', None)
    return ok(updated, 'User updated')

# ── DEACTIVATE USER ───────────────────────────────────────────
@admin_bp.route('/users/<_id>/deactivate', methods=['POST'])
@require_role('national')
def deactivate(_id):
    u = db.find_one('users', '_id', _id)
    if not u:
        return err('User not found', 404)
    db.update_one('users', _id, {'status': 'inactive'})
    return ok(msg='User deactivated')

# ── SEARCH ACROSS COLLECTIONS ─────────────────────────────────
@admin_bp.route('/search', methods=['GET'])
@require_role('national', 'vp', 'secretary')
def search():
    q = request.args.get('q', '').strip().lower()
    if len(q) < 2:
        return err('Search query too short')

    def match(doc, q):
        return any(q in str(v).lower() for v in doc.values())

    results = {
        'primary_members': [m for m in db.find_all('primary_members') if match(m, q)],
        'student_members': [s for s in db.find_all('student_members') if match(s, q)],
        'complaints'     : [c for c in db.find_all('complaints') if match(c, q)],
    }
    return ok(results)


# ─── Announcements ────────────────────────────────────────────────────────────
@admin_bp.route('/announcements', methods=['GET'])
def get_announcements():
    from db import load_collection
    anns = load_collection('announcements')
    return jsonify(anns), 200

@admin_bp.route('/announcements', methods=['POST'])
@jwt_required()
def post_announcement():
    from db import load_collection, save_collection, make_id
    claims = get_jwt()
    if claims.get('role') not in ['national','state','district']:
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.get_json() or {}
    anns = load_collection('announcements')
    ann = {
        '_id': make_id(),
        'title': data.get('title',''),
        'type': data.get('type','General'),
        'content': data.get('content',''),
        'link': data.get('link',''),
        'posted_at': __import__('datetime').datetime.utcnow().isoformat(),
        'posted_by': get_jwt_identity()
    }
    anns.insert(0, ann)
    save_collection('announcements', anns)
    return jsonify(ann), 201

@admin_bp.route('/announcements/<ann_id>', methods=['DELETE'])
@jwt_required()
def delete_announcement(ann_id):
    from db import load_collection, save_collection
    anns = load_collection('announcements')
    anns = [a for a in anns if a.get('_id') != ann_id]
    save_collection('announcements', anns)
    return jsonify({'msg': 'deleted'}), 200

# ─── Press / Gallery ──────────────────────────────────────────────────────────
@admin_bp.route('/press', methods=['GET'])
def get_press():
    from db import load_collection
    return jsonify(load_collection('press_releases')), 200

@admin_bp.route('/press', methods=['POST'])
@jwt_required()
def post_press():
    from db import load_collection, save_collection, make_id
    data = request.get_json() or {}
    items = load_collection('press_releases')
    item = {
        '_id': make_id(),
        'title': data.get('title',''),
        'type': data.get('type','Press Release'),
        'source': data.get('source',''),
        'content': data.get('content',''),
        'event_date': data.get('event_date',''),
        'location': data.get('location',''),
        'posted_at': __import__('datetime').datetime.utcnow().isoformat()
    }
    items.insert(0, item)
    save_collection('press_releases', items)
    return jsonify(item), 201

# ─── Renewal Management ───────────────────────────────────────────────────────
@admin_bp.route('/renewals/primary', methods=['GET'])
@jwt_required()
def get_primary_renewals():
    from db import load_collection
    import datetime
    members = load_collection('primary_members')
    now = datetime.datetime.utcnow()
    expiring = []
    for m in members:
        if m.get('status') == 'active' and m.get('expiry_date'):
            try:
                exp = datetime.datetime.fromisoformat(m['expiry_date'])
                days = (exp - now).days
                if days <= 90:
                    expiring.append({**m, 'days_to_expiry': days})
            except: pass
    return jsonify(expiring), 200

@admin_bp.route('/renewals/<member_id>/process', methods=['POST'])
@jwt_required()
def process_renewal(member_id):
    from db import load_collection, save_collection
    import datetime
    data = request.get_json() or {}
    mtype = data.get('type','primary')
    coll = 'primary_members' if mtype == 'primary' else 'student_members'
    members = load_collection(coll)
    for m in members:
        if m.get('_id') == member_id or m.get('member_id') == member_id:
            m['status'] = 'active'
            m['renewed_at'] = datetime.datetime.utcnow().isoformat()
            from datetime import timedelta
            years = 3 if mtype == 'primary' else 1
            m['expiry_date'] = (datetime.datetime.utcnow() + timedelta(days=365*years)).isoformat()
            save_collection(coll, members)
            return jsonify({'msg': 'Renewal processed', 'record': m}), 200
    return jsonify({'error': 'Member not found'}), 404

# ─── Appointment Orders ───────────────────────────────────────────────────────
@admin_bp.route('/appointment/<member_id>', methods=['POST'])
@jwt_required()
def issue_appointment(member_id):
    from db import load_collection, save_collection
    import datetime
    data = request.get_json() or {}
    members = load_collection('primary_members')
    for m in members:
        if m.get('_id') == member_id or m.get('member_id') == member_id:
            m['designation'] = data.get('designation', m.get('designation',''))
            m['department']  = data.get('department', m.get('department',''))
            m['appointment_date'] = datetime.datetime.utcnow().isoformat()
            m['appointment_order'] = data.get('order_text','')
            save_collection('primary_members', members)
            # Send email
            try:
                from email_service import send_primary_approved
                send_primary_approved(m)
            except: pass
            return jsonify({'msg': 'Appointment order issued', 'record': m}), 200
    return jsonify({'error': 'Member not found'}), 404

# ─── Gallery Management ───────────────────────────────────────────────────────
from flask import Blueprint, request, jsonify
import db as _db_mod

@admin_bp.route('/gallery', methods=['GET'])
def get_gallery():
    items = _db_mod.find_all('gallery')
    category = request.args.get('category')
    if category:
        items = [i for i in items if i.get('category') == category]
    return jsonify({'success': True, 'data': items})

@admin_bp.route('/gallery', methods=['POST'])
@jwt_required()
def add_gallery_item():
    from utils import save_upload
    from datetime import datetime
    data  = request.form.to_dict()
    files = request.files
    if not data.get('title') or not data.get('category'):
        return jsonify({'success': False, 'message': 'title and category are required'}), 400
    img = save_upload(files.get('image'), 'gallery') if files.get('image') else data.get('image_url', '')
    doc = _db_mod.insert('gallery', {
        'title'      : data['title'],
        'category'   : data['category'],   # event / results / publications
        'description': data.get('description', ''),
        'image'      : img,
        'event_date' : data.get('event_date', ''),
        'uploaded_by': get_jwt_identity(),
        'created_at' : datetime.utcnow().isoformat() + 'Z',
    })
    return jsonify({'success': True, 'data': doc}), 201

@admin_bp.route('/gallery/<item_id>', methods=['DELETE'])
@jwt_required()
def delete_gallery_item(item_id):
    deleted = _db_mod.delete_one('gallery', item_id)
    if not deleted:
        return jsonify({'success': False, 'message': 'Item not found'}), 404
    return jsonify({'success': True, 'message': 'Deleted'})

# ─── Competition Results Management ──────────────────────────────────────────
@admin_bp.route('/competition-results', methods=['GET'])
def get_competition_results():
    results = _db_mod.find_all('competition_results')
    return jsonify({'success': True, 'data': results})

@admin_bp.route('/competition-results', methods=['POST'])
@jwt_required()
def post_competition_result():
    from utils import save_upload
    from datetime import datetime
    data  = request.form.to_dict()
    files = request.files
    if not data.get('competition_name'):
        return jsonify({'success': False, 'message': 'competition_name is required'}), 400
    photo = save_upload(files.get('photo'), 'gallery') if files.get('photo') else data.get('photo_url', '')
    doc = _db_mod.insert('competition_results', {
        'competition_name': data['competition_name'],
        'competition_id'  : data.get('competition_id', ''),
        'position'        : data.get('position', ''),      # Winner / Runner-up / Merit
        'winner_name'     : data.get('winner_name', ''),
        'institution'     : data.get('institution', ''),
        'state'           : data.get('state', ''),
        'photo'           : photo,
        'description'     : data.get('description', ''),
        'created_at'      : datetime.utcnow().isoformat() + 'Z',
    })
    return jsonify({'success': True, 'data': doc}), 201

@admin_bp.route('/competition-results/<res_id>', methods=['DELETE'])
@jwt_required()
def delete_competition_result(res_id):
    _db_mod.delete_one('competition_results', res_id)
    return jsonify({'success': True, 'message': 'Deleted'})

# ─── Publications Management ──────────────────────────────────────────────────
@admin_bp.route('/publications', methods=['GET'])
def get_publications():
    pubs = _db_mod.find_all('publications')
    return jsonify({'success': True, 'data': pubs})

@admin_bp.route('/publications', methods=['POST'])
@jwt_required()
def add_publication():
    from utils import save_upload
    from datetime import datetime
    data  = request.form.to_dict()
    files = request.files
    if not data.get('title') or not data.get('type'):
        return jsonify({'success': False, 'message': 'title and type are required'}), 400
    file_saved = save_upload(files.get('file'), 'publications') if files.get('file') else None
    doc = _db_mod.insert('publications', {
        'title'           : data['title'],
        'type'            : data.get('type', 'essay'),   # essay / artwork / article
        'author'          : data.get('author', ''),
        'institution'     : data.get('institution', ''),
        'competition_name': data.get('competition_name', ''),
        'description'     : data.get('description', ''),
        'file'            : file_saved,
        'image_url'       : data.get('image_url', ''),
        'created_at'      : datetime.utcnow().isoformat() + 'Z',
    })
    return jsonify({'success': True, 'data': doc}), 201

@admin_bp.route('/publications/<pub_id>', methods=['DELETE'])
@jwt_required()
def delete_publication(pub_id):
    _db_mod.delete_one('publications', pub_id)
    return jsonify({'success': True, 'message': 'Deleted'})
