# routes/icell.py — Innovation Cell (ICell)
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from utils import ok, err, save_upload, validate_required, require_role
import db

icell_bp = Blueprint('icell', __name__)

REQUIRED = ['title','problem_statement','proposed_solution',
            'implementation_plan','expected_impact','required_funds']

VALID_STATUSES = ['submitted','under_review','modification_requested','approved','rejected']

# ── SUBMIT (Logged-in user) ────────────────────────────────────
@icell_bp.route('/submit', methods=['POST'])
@jwt_required()
def submit():
    data  = request.form.to_dict()
    files = request.files
    uid   = get_jwt_identity()
    user  = db.find_one('users', '_id', uid)
    missing = validate_required(data, REQUIRED)
    if missing: return err(f'Missing: {", ".join(missing)}')
    doc_file = save_upload(files.get('supporting_doc'), 'govtid')
    proposal_id = db.gen_innovation_id()
    doc = db.insert('innovations', {
        'proposal_id'         : proposal_id,
        'user_id'             : uid,
        'applicant_name'      : user.get('name') if user else data.get('name',''),
        'applicant_email'     : user.get('email') if user else data.get('email',''),
        'title'               : data['title'],
        'problem_statement'   : data['problem_statement'],
        'proposed_solution'   : data['proposed_solution'],
        'implementation_plan' : data['implementation_plan'],
        'expected_impact'     : data['expected_impact'],
        'required_funds'      : data['required_funds'],
        'supporting_doc'      : doc_file,
        'status'              : 'submitted',
        'icell_notes'         : '',
        'investor_status'     : '',
        'fund_disbursed'      : False,
    })
    return ok({'proposal_id': proposal_id},
              f'Innovation proposal submitted! Reference: {proposal_id}', 201)

# ── LIST (ICell/Admin) ─────────────────────────────────────────
@icell_bp.route('/', methods=['GET'])
@require_role('national','vp','secretary','icell','it_cell')
def list_proposals():
    proposals = db.find_all('innovations')
    status = request.args.get('status')
    if status: proposals = [p for p in proposals if p.get('status') == status]
    return ok(proposals)

# ── GET MINE (User) ────────────────────────────────────────────
@icell_bp.route('/my-proposals', methods=['GET'])
@jwt_required()
def my_proposals():
    uid  = get_jwt_identity()
    mine = db.find_all('innovations')
    mine = [p for p in mine if p.get('user_id') == uid]
    # Add reference_id alias for dashboard display
    for p in mine:
        if 'reference_id' not in p:
            p['reference_id'] = p.get('proposal_id', p.get('_id','')[:8].upper())
    return ok(mine)

# ── GET ONE ────────────────────────────────────────────────────
@icell_bp.route('/<_id>', methods=['GET'])
@jwt_required()
def get_proposal(_id):
    uid    = get_jwt_identity()
    claims = get_jwt()
    p = db.find_one('innovations', '_id', _id) or db.find_one('innovations', 'proposal_id', _id)
    if not p: return err('Not found', 404)
    if p.get('user_id') != uid and claims.get('role') not in ('national','vp','secretary','icell'):
        return err('Access denied', 403)
    return ok(p)

# ── UPDATE STATUS (ICell Admin) ────────────────────────────────
@icell_bp.route('/<_id>/status', methods=['POST'])
@require_role('national','vp','secretary','icell')
def update_status(_id):
    data = request.get_json(silent=True) or {}
    new_status = data.get('status')
    if new_status not in VALID_STATUSES:
        return err(f'Status must be one of: {", ".join(VALID_STATUSES)}')
    p = db.find_one('innovations', '_id', _id)
    if not p: return err('Not found', 404)
    db.update_one('innovations', _id, {
        'status'     : new_status,
        'icell_notes': data.get('notes', p.get('icell_notes','')),
    })
    return ok(msg=f'Proposal status updated to {new_status}')

# ── INVESTOR UPDATE (Funds disbursed) ─────────────────────────
@icell_bp.route('/<_id>/fund-update', methods=['POST'])
@require_role('national','vp','icell')
def fund_update(_id):
    data = request.get_json(silent=True) or {}
    p = db.find_one('innovations', '_id', _id)
    if not p: return err('Not found', 404)
    db.update_one('innovations', _id, {
        'investor_status'  : data.get('investor_status', ''),
        'fund_disbursed'   : data.get('fund_disbursed', False),
        'fund_amount'      : data.get('fund_amount', ''),
        'fund_account'     : data.get('fund_account', ''),
        'fund_transfer_date': data.get('fund_transfer_date', ''),
    })
    return ok(msg='Funding details updated')

# ── INVESTOR FORWARDING ────────────────────────────────────────
@icell_bp.route('/<_id>/forward-investor', methods=['POST'])
@require_role('national', 'vp', 'icell')
def forward_to_investor(_id):
    from datetime import datetime
    claims = get_jwt()
    data   = request.get_json(silent=True) or {}
    p = db.find_one('innovations', '_id', _id)
    if not p:
        return err('Proposal not found', 404)
    if p.get('status') not in ('approved',):
        return err('Only approved proposals can be forwarded to investors')

    investor_name  = data.get('investor_name', '').strip()
    investor_email = data.get('investor_email', '').strip()
    investor_org   = data.get('investor_org', '').strip()
    message_note   = data.get('message', '')

    if not investor_email:
        return err('investor_email is required')

    updates = {
        'investor_status'    : 'forwarded',
        'investor_name'      : investor_name,
        'investor_email'     : investor_email,
        'investor_org'       : investor_org,
        'forwarded_at'       : datetime.utcnow().isoformat() + 'Z',
        'forwarded_by'       : claims.get('name', get_jwt_identity()),
    }
    db.update_one('innovations', _id, updates)

    # Email the investor
    try:
        import email_service as es
        investor_body = f"""
        <p>Dear {investor_name or 'Investor'},</p>
        <p>All India Students Union (AISU) would like to bring an innovation proposal to your attention on behalf of a promising student innovator.</p>
        <table style="border-collapse:collapse;width:100%;margin:16px 0;">
          <tr><td style="padding:8px;background:#f8f9fa;border:1px solid #dee2e6;"><strong>Proposal</strong></td><td style="padding:8px;border:1px solid #dee2e6;">{p.get('title')}</td></tr>
          <tr><td style="padding:8px;background:#f8f9fa;border:1px solid #dee2e6;"><strong>Innovator</strong></td><td style="padding:8px;border:1px solid #dee2e6;">{p.get('applicant_name')}</td></tr>
          <tr><td style="padding:8px;background:#f8f9fa;border:1px solid #dee2e6;"><strong>Problem Statement</strong></td><td style="padding:8px;border:1px solid #dee2e6;">{p.get('problem_statement','')[:300]}…</td></tr>
          <tr><td style="padding:8px;background:#f8f9fa;border:1px solid #dee2e6;"><strong>Proposed Solution</strong></td><td style="padding:8px;border:1px solid #dee2e6;">{p.get('proposed_solution','')[:300]}…</td></tr>
          <tr><td style="padding:8px;background:#f8f9fa;border:1px solid #dee2e6;"><strong>Required Funds</strong></td><td style="padding:8px;border:1px solid #dee2e6;">₹{p.get('required_funds','TBD')}</td></tr>
        </table>
        {f'<p><em>Note from AISU: {message_note}</em></p>' if message_note else ''}
        <p>To express interest or for a detailed discussion, please reply to this email or contact us at aisu4india@gmail.com</p>
        """
        es.send_generic(investor_email, investor_name or 'Investor',
                        f'Innovation Proposal — {p.get("title")} | AISU ICell',
                        investor_body)
    except Exception as e:
        print(f'Investor email error: {e}')

    # Notify applicant
    try:
        import email_service as es
        es.send_generic(p.get('applicant_email', ''), p.get('applicant_name', ''),
                        'Your Innovation Proposal Has Been Forwarded to an Investor — AISU ICell',
                        f'Great news! Your proposal <strong>"{p.get("title")}"</strong> has been forwarded to a potential investor '
                        f'({investor_org or investor_email}) by the AISU Innovation Cell on your behalf.<br><br>'
                        f'The investor will be in touch if they wish to proceed. AISU ICell will assist in any negotiations and fund transfer.')
    except Exception as e:
        print(f'Applicant notification error: {e}')

    return ok(msg=f'Proposal forwarded to investor: {investor_email}')


# ── FUND DISBURSEMENT RECORDING ────────────────────────────────
@icell_bp.route('/<_id>/fund-disbursement', methods=['POST'])
@require_role('national', 'vp', 'icell')
def record_fund_disbursement(_id):
    from datetime import datetime
    data = request.get_json(silent=True) or {}
    p = db.find_one('innovations', '_id', _id)
    if not p:
        return err('Proposal not found', 404)

    amount        = data.get('amount', '')
    bank_ref      = data.get('bank_ref', '')
    disbursed_to  = data.get('disbursed_to', p.get('applicant_name', ''))
    disbursed_at  = datetime.utcnow().isoformat() + 'Z'

    db.update_one('innovations', _id, {
        'fund_disbursed'     : True,
        'disbursed_amount'   : amount,
        'disbursed_at'       : disbursed_at,
        'bank_ref'           : bank_ref,
        'disbursed_to'       : disbursed_to,
        'investor_status'    : 'funded',
    })

    # Notify innovator
    try:
        import email_service as es
        es.send_generic(
            p.get('applicant_email', ''), p.get('applicant_name', ''),
            'Fund Disbursement Notification — AISU ICell',
            f'We are pleased to inform you that funds for your innovation proposal <strong>"{p.get("title")}"</strong> have been disbursed.<br><br>'
            f'<strong>Amount:</strong> ₹{amount}<br>'
            f'<strong>Bank Reference:</strong> {bank_ref or "N/A"}<br>'
            f'<strong>Date:</strong> {disbursed_at[:10]}<br><br>'
            f'Congratulations from the AISU Innovation Cell team!'
        )
    except Exception as e:
        print(f'Fund disbursement email error: {e}')

    return ok(msg='Fund disbursement recorded and innovator notified')
