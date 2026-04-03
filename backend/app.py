# =============================================================
#  AISU Backend — app.py  (Flask entry point)
#  Run: python app.py
# =============================================================
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
from datetime import timedelta
import os, logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

from routes.auth            import auth_bp
from routes.members         import members_bp
from routes.students        import students_bp
from routes.complaint       import complaint_bp
from routes.contact         import contact_bp
from routes.internship      import internship_bp
from routes.affiliation     import affiliation_bp
from routes.certs           import certs_bp
from routes.admin           import admin_bp
from routes.competition     import competition_bp
from routes.icell           import icell_bp
from routes.quiz            import quiz_bp, register_socket_events
from routes.cert_templates  import cert_tpl_bp

app = Flask(__name__)

# ── Config ────────────────────────────────────────────────────
BASE = os.path.dirname(__file__)
app.config.update(
    SECRET_KEY                = os.environ.get('SECRET_KEY',     'aisu-secret-2024-CHANGE-ME'),
    JWT_SECRET_KEY            = os.environ.get('JWT_SECRET_KEY', 'aisu-jwt-2024-CHANGE-ME'),
    JWT_ACCESS_TOKEN_EXPIRES  = timedelta(hours=12),
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30),
    MAX_CONTENT_LENGTH        = 16 * 1024 * 1024,
    UPLOAD_FOLDER             = os.path.join(BASE, 'uploads'),
    DATA_FOLDER               = os.path.join(BASE, 'data'),
    SMTP_USER                 = os.environ.get('SMTP_USER', 'aisu4india@gmail.com'),
    SMTP_PASS                 = os.environ.get('SMTP_PASS', ''),
)

# ── Ensure dirs ───────────────────────────────────────────────
for d in ['uploads/govtid', 'uploads/payment', 'uploads/photo',
          'uploads/sign', 'uploads/complaint',
          'uploads/cert_templates', 'uploads/certificates', 'uploads/gallery', 'uploads/publications', 'data']:
    os.makedirs(os.path.join(BASE, d), exist_ok=True)

# ── Extensions ───────────────────────────────────────────────
CORS(app,
     resources={r'/api/*': {'origins': '*'}},
     allow_headers=['Content-Type', 'Authorization', 'X-Requested-With'],
     methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
     supports_credentials=False)

# Handle OPTIONS preflight for all routes
@app.before_request
def handle_options():
    from flask import request, make_response
    if request.method == 'OPTIONS':
        resp = make_response()
        resp.headers['Access-Control-Allow-Origin'] = '*'
        resp.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
        resp.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
        resp.headers['Access-Control-Max-Age'] = '3600'
        return resp, 200

jwt = JWTManager(app)

socketio = SocketIO(app,
    cors_allowed_origins='*',
    async_mode='threading',
    logger=False,
    engineio_logger=False
)

# Register Socket.IO events for quiz rooms
register_socket_events(socketio)

# ── Blueprints ───────────────────────────────────────────────
app.register_blueprint(auth_bp,           url_prefix='/api/auth')
app.register_blueprint(members_bp,        url_prefix='/api/members')
app.register_blueprint(students_bp,       url_prefix='/api/students')
app.register_blueprint(complaint_bp,      url_prefix='/api/complaints')
app.register_blueprint(contact_bp,        url_prefix='/api/contact')
app.register_blueprint(internship_bp,     url_prefix='/api/internship')
app.register_blueprint(affiliation_bp,    url_prefix='/api/affiliation')
app.register_blueprint(certs_bp,          url_prefix='/api/certs')
app.register_blueprint(admin_bp,          url_prefix='/api/admin')
app.register_blueprint(competition_bp,    url_prefix='/api/competitions')
app.register_blueprint(icell_bp,          url_prefix='/api/icell')
app.register_blueprint(quiz_bp,           url_prefix='/api/quiz')
app.register_blueprint(cert_tpl_bp,       url_prefix='/api/cert-templates')

# ── Health & Root ─────────────────────────────────────────────
@app.route('/')
def index():
    return {'status': 'AISU Backend Running', 'version': '2.1.0',
            'docs': '/api/health', 'ws': 'Socket.IO enabled on /socket.io'}

@app.route('/api/health')
def health():
    import db
    return {
        'status'  : 'ok',
        'service' : 'AISU API v2.1',
        'socketio': True,
        'collections': {
            'primary_members': db.count('primary_members'),
            'student_members': db.count('student_members'),
            'complaints'     : db.count('complaints'),
            'competitions'   : db.count('competitions'),
            'certificates'   : db.count('certificates'),
            'cert_templates' : db.count('cert_templates'),
        }
    }


# ── Serve uploaded files ──────────────────────────────────────
from flask import send_from_directory

@app.route('/uploads/<path:filename>')
def serve_upload(filename):
    return send_from_directory(os.path.join(BASE, 'uploads'), filename)

# ── Error handlers ────────────────────────────────────────────
@app.errorhandler(404)
def not_found(e):
    return {'success': False, 'message': 'Endpoint not found'}, 404

@app.errorhandler(413)
def too_large(e):
    return {'success': False, 'message': 'File too large (max 16MB)'}, 413

@app.errorhandler(500)
def server_error(e):
    return {'success': False, 'message': 'Internal server error'}, 500

# ── Start scheduler ───────────────────────────────────────────
from scheduler import init_scheduler
try:
    init_scheduler()
except Exception as e:
    print(f'Scheduler init failed: {e}')

if __name__ == '__main__':
    print('\n' + '='*60)
    print('  AISU Backend v2.1  —  http://localhost:5000')
    print('  Socket.IO (Quiz)  —  ws://localhost:5000/socket.io')
    print('  Admin  :  admin@aisu4india.in / Admin@AISU2024')
    print('='*60 + '\n')
    socketio.run(app, debug=True, port=5000, host='0.0.0.0',
                 allow_unsafe_werkzeug=True)
