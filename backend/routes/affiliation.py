# routes/affiliation.py — Organization Affiliation Applications
from flask import Blueprint, request
from utils import ok, err, save_upload, validate_required, require_role
import db

affiliation_bp = Blueprint('affiliation', __name__)

REQUIRED = ['org_name', 'contact_name', 'email', 'mobile',
            'state', 'district', 'address', 'org_type']

@affiliation_bp.route('/apply', methods=['POST'])
def apply():
    data  = request.form.to_dict()
    files = request.files
    missing = validate_required(data, REQUIRED)
    if missing:
        return err(f'Missing: {", ".join(missing)}')
    if db.find_one('affiliations', 'email', data['email'].strip().lower()):
        return err('Application with this email already exists')
    reg_doc = save_upload(files.get('reg_document'), 'govtid')
    doc = db.insert('affiliations', {
        'org_name'    : data['org_name'],
        'contact_name': data['contact_name'],
        'email'       : data['email'].strip().lower(),
        'mobile'      : data['mobile'],
        'state'       : data['state'],
        'district'    : data['district'],
        'address'     : data['address'],
        'org_type'    : data['org_type'],
        'reg_number'  : data.get('reg_number', ''),
        'website'     : data.get('website', ''),
        'reg_document': reg_doc,
        'status'      : 'pending',
    })
    return ok({'ref': doc['_id']}, 'Affiliation application submitted!', 201)

@affiliation_bp.route('/', methods=['GET'])
@require_role('national', 'vp', 'secretary')
def list_all():
    return ok(db.find_all('affiliations'))

@affiliation_bp.route('/<_id>/approve', methods=['POST'])
@require_role('national', 'vp')
def approve(_id):
    db.update_one('affiliations', _id, {'status': 'approved'})
    return ok(msg='Affiliation approved')

@affiliation_bp.route('/<_id>/reject', methods=['POST'])
@require_role('national', 'vp')
def reject(_id):
    data = request.get_json(silent=True) or {}
    db.update_one('affiliations', _id, {'status': 'rejected', 'reason': data.get('reason', '')})
    return ok(msg='Rejected')
