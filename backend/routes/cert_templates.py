# routes/cert_templates.py — Certificate template upload & generation
import os, json, uuid, re
from flask import Blueprint, request, send_file
from flask_jwt_extended import jwt_required, get_jwt
from utils import ok, err, require_role
import db
from datetime import datetime

cert_tpl_bp = Blueprint('cert_templates', __name__)

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), '..', 'uploads', 'cert_templates')
CERT_OUT   = os.path.join(os.path.dirname(__file__), '..', 'uploads', 'certificates')
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(CERT_OUT,   exist_ok=True)

ALLOWED_EXT = {'.docx', '.pdf', '.pptx', '.png', '.jpg', '.jpeg'}

# ── Upload a certificate template ────────────────────────────────────────────
@cert_tpl_bp.route('/templates', methods=['POST'])
@jwt_required()
def upload_template():
    claims = get_jwt()
    if claims.get('role') not in ('national', 'admin'):
        return err('Unauthorized', 403)

    name        = request.form.get('name', '').strip()
    prog_code   = request.form.get('prog_code', 'COMP').strip().upper()
    description = request.form.get('description', '')
    file        = request.files.get('template_file')

    if not file or not name:
        return err('Template name and file are required')

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXT:
        return err(f'Unsupported format. Allowed: {", ".join(ALLOWED_EXT)}')

    filename = f"{uuid.uuid4()}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    file.save(filepath)

    tpl = db.insert('cert_templates', {
        'name':        name,
        'prog_code':   prog_code,
        'description': description,
        'filename':    filename,
        'ext':         ext,
        'uploaded_by': claims.get('email'),
        'placeholders': _detect_placeholders(filepath, ext),
    })
    return ok(tpl, 'Template uploaded successfully'), 201


# ── List templates ────────────────────────────────────────────────────────────
@cert_tpl_bp.route('/templates', methods=['GET'])
@jwt_required()
def list_templates():
    templates = db.find_all('cert_templates')
    return ok(templates)


# ── Get single template ───────────────────────────────────────────────────────
@cert_tpl_bp.route('/templates/<tid>', methods=['GET'])
@jwt_required()
def get_template(tid):
    tpl = db.find_one('cert_templates', '_id', tid)
    if not tpl:
        return err('Template not found', 404)
    return ok(tpl)


# ── Delete template ───────────────────────────────────────────────────────────
@cert_tpl_bp.route('/templates/<tid>', methods=['DELETE'])
@jwt_required()
def delete_template(tid):
    claims = get_jwt()
    if claims.get('role') not in ('national', 'admin'):
        return err('Unauthorized', 403)
    tpl = db.find_one('cert_templates', '_id', tid)
    if not tpl:
        return err('Template not found', 404)
    path = os.path.join(UPLOAD_DIR, tpl['filename'])
    if os.path.exists(path):
        os.remove(path)
    db.delete_one('cert_templates', tid)
    return ok(msg='Template deleted')


# ── Generate certificates from a template ────────────────────────────────────
@cert_tpl_bp.route('/generate', methods=['POST'])
@jwt_required()
def generate_certificates():
    """
    Body JSON:
    {
        "template_id": "<_id>",
        "prog_code": "ESSAY",
        "mode": "manual" | "automatic",
        "participants": [
            {"name": "...", "email": "...", "program": "...", "extra": {...}}
        ],
        "competition_id": "..." (optional, for automatic mode)
    }
    """
    claims = get_jwt()
    if claims.get('role') not in ('national', 'admin'):
        return err('Unauthorized', 403)

    data       = request.get_json(silent=True) or {}
    tid        = data.get('template_id')
    prog_code  = data.get('prog_code', 'COMP').upper()
    mode       = data.get('mode', 'manual')
    participants = data.get('participants', [])

    # Automatic mode: pull all registered participants from competition
    if mode == 'automatic' and data.get('competition_id'):
        comp = db.find_one('competitions', '_id', data['competition_id'])
        if not comp:
            return err('Competition not found', 404)
        registrations = db.find_many('competition_registrations', 'competition_id', data['competition_id'])
        participants = [{'name': r.get('name', ''), 'email': r.get('email', ''), 'program': comp.get('title', '')}
                        for r in registrations]

    if not participants:
        return err('No participants provided')

    tpl = db.find_one('cert_templates', '_id', tid) if tid else None

    generated = []
    for p in participants:
        cert_id = db.gen_cert_id(prog_code)
        cert_num = cert_id  # e.g. AISUCERTESSAY2026000145

        # Fill placeholders
        replacements = {
            '{{CertificateNo}}':   cert_num,
            '{{ParticipantName}}': p.get('name', ''),
            '{{Program}}':         p.get('program', ''),
            '{{Date}}':            datetime.utcnow().strftime('%d %B %Y'),
            '{{Email}}':           p.get('email', ''),
        }
        # Add any extra fields
        for k, v in (p.get('extra') or {}).items():
            replacements[f'{{{{{k}}}}}'] = str(v)

        # Generate filled document
        cert_filename = None
        if tpl and tpl.get('ext') == '.docx':
            cert_filename = _fill_docx_template(tpl, replacements, cert_num)
        else:
            # For non-docx templates, store the record with placeholder mapping
            cert_filename = None

        # Save certificate record
        cert_record = db.insert('certificates', {
            'cert_number':       cert_num,
            'participant_name':  p.get('name', ''),
            'participant_email': p.get('email', ''),
            'program':           p.get('program', ''),
            'prog_code':         prog_code,
            'cert_type':         p.get('cert_type', 'Participation'),
            'template_id':       tid,
            'filename':          cert_filename,
            'replacements':      replacements,
            'status':            'issued',
            'issued_at':         datetime.utcnow().isoformat() + 'Z',
        })
        generated.append({'cert_number': cert_num, 'name': p.get('name'), 'id': cert_record['_id']})

        # Send email notification
        try:
            import email_service as es
            es.send_certificate_issued(p.get('email', ''), p.get('name', ''), cert_num, prog_code)
        except Exception:
            pass

    return ok({'generated': len(generated), 'certificates': generated},
              f'{len(generated)} certificates generated successfully')


# ── Download a specific certificate ──────────────────────────────────────────
@cert_tpl_bp.route('/download/<cert_id>', methods=['GET'])
@jwt_required()
def download_certificate(cert_id):
    cert = db.find_one('certificates', '_id', cert_id)
    if not cert:
        return err('Certificate not found', 404)
    if cert.get('filename'):
        path = os.path.join(CERT_OUT, cert['filename'])
        if os.path.exists(path):
            return send_file(path, as_attachment=True)
    return err('Certificate file not yet generated. Contact admin.', 404)


# ── Upload participants via Excel ─────────────────────────────────────────────
@cert_tpl_bp.route('/participants/upload', methods=['POST'])
@jwt_required()
def upload_participants():
    claims = get_jwt()
    if claims.get('role') not in ('national', 'admin'):
        return err('Unauthorized', 403)

    file = request.files.get('excel_file')
    if not file:
        return err('Excel file required')

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ('.xlsx', '.xls', '.csv'):
        return err('Only .xlsx, .xls, .csv files supported')

    try:
        import openpyxl
        wb = openpyxl.load_workbook(file)
        ws = wb.active
        headers = [str(c.value).strip() if c.value else '' for c in next(ws.iter_rows(min_row=1, max_row=1))]
        participants = []
        for row in ws.iter_rows(min_row=2, values_only=True):
            participant = {headers[i]: (str(v).strip() if v else '') for i, v in enumerate(row) if i < len(headers)}
            if any(participant.values()):
                participants.append(participant)
        return ok({'count': len(participants), 'participants': participants, 'headers': headers},
                  f'{len(participants)} participants loaded')
    except Exception as e:
        return err(f'Failed to parse Excel: {str(e)}')


# ─── Private helpers ──────────────────────────────────────────────────────────

def _detect_placeholders(filepath, ext):
    """Detect {{placeholder}} patterns in uploaded template."""
    placeholders = []
    try:
        if ext == '.docx':
            from docx import Document
            doc = Document(filepath)
            text = ' '.join(p.text for p in doc.paragraphs)
            for t in doc.tables:
                for row in t.rows:
                    for cell in row.cells:
                        text += ' ' + cell.text
            placeholders = re.findall(r'\{\{(\w+)\}\}', text)
    except Exception:
        pass
    return list(set(placeholders))


def _fill_docx_template(tpl, replacements, cert_num):
    """Fill placeholders in a .docx template and save output."""
    try:
        from docx import Document
        src = os.path.join(UPLOAD_DIR, tpl['filename'])
        doc = Document(src)

        def replace_in_run(run):
            for ph, val in replacements.items():
                if ph in run.text:
                    run.text = run.text.replace(ph, val)

        for para in doc.paragraphs:
            for run in para.runs:
                replace_in_run(run)
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for para in cell.paragraphs:
                        for run in para.runs:
                            replace_in_run(run)

        out_name = f"{cert_num}.docx"
        out_path = os.path.join(CERT_OUT, out_name)
        doc.save(out_path)
        return out_name
    except Exception as e:
        return None
