# utils.py — shared helpers
import os, re, uuid, bcrypt
from functools import wraps
from flask import current_app, request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'pdf', 'webp', 'doc', 'docx', 'xlsx', 'xls', 'pptx', 'mp4', 'mp3'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_upload(file_obj, subfolder):
    """Save an uploaded file safely. Returns stored filename or None."""
    if not file_obj or not allowed_file(file_obj.filename):
        return None
    ext = file_obj.filename.rsplit('.', 1)[1].lower()
    fname = f'{uuid.uuid4().hex}.{ext}'
    dest = os.path.join(current_app.config['UPLOAD_FOLDER'], subfolder, fname)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    file_obj.save(dest)
    return fname

def hash_password(pw):
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()

def check_password(pw, hashed):
    return bcrypt.checkpw(pw.encode(), hashed.encode())

def ok(data=None, msg='success', code=200):
    resp = {'success': True, 'message': msg}
    if data is not None:
        resp['data'] = data
    return jsonify(resp), code

def err(msg='error', code=400, details=None):
    resp = {'success': False, 'message': msg}
    if details:
        resp['details'] = details
    return jsonify(resp), code

def validate_required(data, fields):
    missing = [f for f in fields if not data.get(f)]
    return missing  # empty list = all good

def state_code(state_name):
    codes = {
        'Andhra Pradesh':'AP','Arunachal Pradesh':'AR','Assam':'AS','Bihar':'BR',
        'Chhattisgarh':'CG','Delhi':'DL','Goa':'GA','Gujarat':'GJ','Haryana':'HR',
        'Himachal Pradesh':'HP','Jammu & Kashmir':'JK','Jharkhand':'JH',
        'Karnataka':'KA','Kerala':'KL','Madhya Pradesh':'MP','Maharashtra':'MH',
        'Manipur':'MN','Meghalaya':'ML','Mizoram':'MZ','Nagaland':'NL',
        'Odisha':'OD','Punjab':'PB','Rajasthan':'RJ','Sikkim':'SK',
        'Tamil Nadu':'TN','Telangana':'TS','Tripura':'TR','Uttar Pradesh':'UP',
        'Uttarakhand':'UK','West Bengal':'WB',
    }
    return codes.get(state_name, 'XX')

# ── Role-based JWT decorator ──────────────────────────────────
def require_role(*roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                verify_jwt_in_request()
                claims = get_jwt()
                if claims.get('role') not in roles:
                    return err('Access denied', 403)
            except Exception as e:
                return err('Authentication required', 401)
            return fn(*args, **kwargs)
        return wrapper
    return decorator
