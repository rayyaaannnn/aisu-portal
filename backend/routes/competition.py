# routes/competition.py — Competition Portal
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from utils import ok, err, save_upload, validate_required, require_role
from datetime import datetime
import db, threading

competition_bp = Blueprint('competition', __name__)

# ── CREATE COMPETITION (Admin) ─────────────────────────────────
@competition_bp.route('/', methods=['POST'])
@require_role('national','vp','secretary','it_cell')
def create_competition():
    data = request.get_json(silent=True) or {}
    missing = validate_required(data, ['title','category','comp_type','last_date'])
    if missing: return err(f'Missing: {", ".join(missing)}')
    comp_id = db.gen_competition_id()
    doc = db.insert('competitions', {
        'comp_id'    : comp_id,
        'title'      : data['title'],
        'description': data.get('description',''),
        'category'   : data['category'],
        'comp_type'  : data['comp_type'],  # document_upload / group_quiz / exam_quiz
        'last_date'  : data['last_date'],
        'event_date' : data.get('event_date',''),
        'group_size' : data.get('group_size', 1),
        'time_limit' : data.get('time_limit', 0),   # minutes for exam-mode
        'questions'  : data.get('questions', []),    # for quiz types
        'status'     : 'open',
        'created_by' : get_jwt_identity(),
    })
    # Broadcast email to all student members + past participants
    def _broadcast():
        try:
            from email_service import send_new_competition_notification
            students = [s['email'] for s in db.find_all('student_members') if s.get('status')=='approved']
            past_reg = list({r['email'] for r in db.find_all('competition_registrations')})
            all_r = list(set(students + past_reg))
            if all_r:
                send_new_competition_notification(doc, all_r)
        except Exception as e:
            print(f'Broadcast email error: {e}')
    threading.Thread(target=_broadcast, daemon=True).start()
    return ok({'comp_id': comp_id}, 'Competition created', 201)

# ── LIST ───────────────────────────────────────────────────────
@competition_bp.route('/', methods=['GET'])
def list_competitions():
    comps = db.find_all('competitions')
    status = request.args.get('status', 'open')
    if status != 'all':
        comps = [c for c in comps if c.get('status') == status]
    for c in comps: c.pop('questions', None)   # don't leak quiz questions
    return ok(comps)

# ── GET DETAILS ────────────────────────────────────────────────
@competition_bp.route('/<comp_id>', methods=['GET'])
def get_competition(comp_id):
    c = db.find_one('competitions', 'comp_id', comp_id)
    if not c: return err('Not found', 404)
    c_out = dict(c)
    c_out.pop('questions', None)   # hide questions from public
    return ok(c_out)

# ── REGISTER ───────────────────────────────────────────────────
@competition_bp.route('/<comp_id>/register', methods=['POST'])
@jwt_required()
def register(comp_id):
    c = db.find_one('competitions', 'comp_id', comp_id)
    if not c: return err('Competition not found', 404)
    if c.get('status') != 'open': return err('Registration is closed')
    uid  = get_jwt_identity()
    user = db.find_one('users', '_id', uid)
    if not user: return err('User not found', 401)
    # Duplicate registration check
    existing = [r for r in db.find_all('competition_registrations')
                if r.get('comp_id') == comp_id and r.get('user_id') == uid]
    if existing: return err('Already registered for this competition')
    data = request.get_json(silent=True) or {}
    # Check student membership for fee gate
    email = user.get('email', '')
    student = db.find_one('student_members', 'email', email)
    has_active_membership = False
    fee_required = True
    if student and student.get('status') == 'approved':
        approved_at = student.get('approved_at', '')
        if approved_at and not db.is_expired(approved_at, 1):
            has_active_membership = True
            fee_required = False

    doc = db.insert('competition_registrations', {
        'comp_id'              : comp_id,
        'competition_title'    : c.get('title'),
        'comp_id_ref'          : comp_id,
        'user_id'              : uid,
        'name'                 : user.get('name'),
        'email'                : email,
        'mobile'               : user.get('mobile', ''),
        'institution'          : data.get('institution', user.get('institution','')),
        'state'                : data.get('state', user.get('state','')),
        'group_members'        : data.get('group_members', []),
        'has_active_membership': has_active_membership,
        'fee_required'         : fee_required,
        'fee_paid'             : data.get('fee_paid', False),
        'submission_type'      : c.get('comp_type', 'general'),
        'status'               : 'registered',
    })
    msg = 'Registered successfully. You have free access as an active student member.' if not fee_required           else 'Registered. Please note a per-competition fee applies as your student membership is inactive or expired.'
    return ok({'reg_id': doc['_id'], 'fee_required': fee_required}, msg, 201)

# ── SUBMIT ENTRY (Document Upload) ────────────────────────────
@competition_bp.route('/<comp_id>/submit', methods=['POST'])
@jwt_required()
def submit_entry(comp_id):
    uid  = get_jwt_identity()
    reg  = next((r for r in db.find_all('competition_registrations')
                 if r.get('comp_id')==comp_id and r.get('user_id')==uid), None)
    if not reg: return err('You are not registered for this competition', 403)
    f = request.files.get('submission')
    if not f: return err('No file uploaded')
    fname = save_upload(f, 'govtid')
    if not fname: return err('Invalid file type')
    db.update_one('competition_registrations', reg['_id'], {
        'submission_file': fname,
        'submitted_at'   : datetime.utcnow().isoformat()+'Z',
        'submission_note': request.form.get('note',''),
    })
    return ok(msg='Submission received. Forwarded to selection committee.')

# ── QUIZ: START SESSION (Exam-Mode) ───────────────────────────
@competition_bp.route('/<comp_id>/start-quiz', methods=['POST'])
@jwt_required()
def start_quiz(comp_id):
    uid  = get_jwt_identity()
    reg  = next((r for r in db.find_all('competition_registrations')
                 if r.get('comp_id')==comp_id and r.get('user_id')==uid), None)
    if not reg: return err('Not registered', 403)
    if reg.get('quiz_started'): return err('Quiz already started')
    if reg.get('disqualified'): return err('You have been disqualified')
    c = db.find_one('competitions', 'comp_id', comp_id)
    if not c or c.get('comp_type') not in ('exam_quiz','group_quiz'):
        return err('Not a quiz competition')
    db.update_one('competition_registrations', reg['_id'], {
        'quiz_started'  : True,
        'quiz_start_time': datetime.utcnow().isoformat()+'Z',
    })
    # Return questions (shuffle order)
    import random
    questions = list(c.get('questions', []))
    random.shuffle(questions)
    # Remove correct_answer from client payload
    safe_q = [{k:v for k,v in q.items() if k != 'correct_answer'} for q in questions]
    return ok({
        'questions'  : safe_q,
        'time_limit' : c.get('time_limit', 30),
        'total'      : len(safe_q),
        'instructions': c.get('instructions',''),
    })

# ── QUIZ: SUBMIT ANSWERS ───────────────────────────────────────
@competition_bp.route('/<comp_id>/submit-quiz', methods=['POST'])
@jwt_required()
def submit_quiz(comp_id):
    uid  = get_jwt_identity()
    reg  = next((r for r in db.find_all('competition_registrations')
                 if r.get('comp_id')==comp_id and r.get('user_id')==uid), None)
    if not reg: return err('Not registered', 403)
    if reg.get('disqualified'): return err('Disqualified')
    if reg.get('quiz_submitted'): return err('Already submitted')
    data    = request.get_json(silent=True) or {}
    answers = data.get('answers', {})   # {question_id: chosen_option}
    c       = db.find_one('competitions', 'comp_id', comp_id)
    # Score
    score = 0
    total = len(c.get('questions', []))
    for q in c.get('questions', []):
        if answers.get(q.get('id')) == q.get('correct_answer'):
            score += 1
    db.update_one('competition_registrations', reg['_id'], {
        'quiz_submitted' : True,
        'quiz_submit_time': datetime.utcnow().isoformat()+'Z',
        'answers'        : answers,
        'score'          : score,
        'score_percent'  : round(score/total*100, 1) if total else 0,
    })
    return ok({'score': score, 'total': total}, 'Quiz submitted')

# ── DISQUALIFY ─────────────────────────────────────────────────
@competition_bp.route('/reg/<reg_id>/disqualify', methods=['POST'])
@require_role('national','vp','secretary','it_cell')
def disqualify(reg_id):
    data = request.get_json(silent=True) or {}
    reg  = db.find_one('competition_registrations', '_id', reg_id)
    if not reg: return err('Not found', 404)
    db.update_one('competition_registrations', reg_id, {
        'disqualified'        : True,
        'disqualification_reason': data.get('reason', 'Rule violation'),
    })
    try:
        from email_service import _send, _base_template
        body = f"<p>You have been disqualified from <strong>{reg.get('comp_title')}</strong>.</p><p>Reason: {data.get('reason','Rule violation')}</p>"
        _send([reg['email']], f'Disqualified: {reg.get("comp_title")}', _base_template('Disqualification Notice', body))
    except Exception as e:
        print(f'Email error: {e}')
    return ok(msg='Disqualified')

# ── RESULTS (Admin: post results) ─────────────────────────────
@competition_bp.route('/<comp_id>/results', methods=['POST'])
@require_role('national','vp','secretary')
def post_results(comp_id):
    data = request.get_json(silent=True) or {}
    c = db.find_one('competitions', 'comp_id', comp_id)
    if not c: return err('Not found', 404)
    db.update_one('competitions', c['_id'], {
        'status' : 'completed',
        'results': data.get('results', []),  # [{name,email,institution,rank,category}]
    })
    return ok(msg='Results published')

# ── GET RESULTS (Public) ───────────────────────────────────────
@competition_bp.route('/<comp_id>/results', methods=['GET'])
def get_results(comp_id):
    c = db.find_one('competitions', 'comp_id', comp_id)
    if not c: return err('Not found', 404)
    if c.get('status') != 'completed': return err('Results not yet published')
    return ok({'comp_id': comp_id, 'title': c.get('title'), 'results': c.get('results', [])})

# ── MY REGISTRATIONS ──────────────────────────────────────────
@competition_bp.route('/my-registrations', methods=['GET'])
@jwt_required()
def my_registrations():
    uid  = get_jwt_identity()
    regs = [r for r in db.find_all('competition_registrations') if r.get('user_id') == uid]
    return ok(regs)
