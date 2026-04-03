# routes/quiz.py  — Group Quiz Rooms (WebSocket via Flask-SocketIO)
# Handles: room creation, joining, real-time Q&A, scoring, moderator control
from flask import Blueprint, request
from flask_socketio import SocketIO, join_room, leave_room, emit, rooms
from flask_jwt_extended import decode_token
from utils import ok, err, require_role
import db, uuid
from datetime import datetime

quiz_bp = Blueprint('quiz', __name__)

# In-memory quiz rooms (reset on server restart — intentional for live sessions)
_rooms = {}  # room_code -> room_data

# ── REST: Create a quiz room ──────────────────────────────────────────────────
@quiz_bp.route('/rooms', methods=['POST'])
def create_room():
    from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
    from functools import wraps
    data = request.get_json(silent=True) or {}
    comp_id   = data.get('competition_id')
    room_name = data.get('room_name', 'Quiz Room')
    max_teams = int(data.get('max_teams', 8))
    time_limit = int(data.get('time_limit_minutes', 30))

    code = str(uuid.uuid4())[:6].upper()
    _rooms[code] = {
        'code':         code,
        'competition_id': comp_id,
        'room_name':    room_name,
        'max_teams':    max_teams,
        'time_limit_minutes': time_limit,
        'status':       'waiting',     # waiting | active | ended
        'participants': {},            # socket_id -> {name, team, score}
        'teams':        {},            # team_name -> {members: [], score}
        'questions':    [],
        'current_q':    -1,
        'answers':      {},            # q_index -> {team: answer}
        'chat':         [],
        'created_at':   datetime.utcnow().isoformat() + 'Z',
        'moderator_sid': None,
    }
    return ok({'room_code': code, 'room': _rooms[code]}, 'Quiz room created')


# ── REST: List open rooms ─────────────────────────────────────────────────────
@quiz_bp.route('/rooms', methods=['GET'])
def list_rooms():
    public = [{
        'code':       c,
        'room_name':  r['room_name'],
        'status':     r['status'],
        'participants': len(r['participants']),
        'max_teams':  r['max_teams'],
    } for c, r in _rooms.items()]
    return ok(public)


# ── REST: Get room details ────────────────────────────────────────────────────
@quiz_bp.route('/rooms/<code>', methods=['GET'])
def get_room(code):
    if code not in _rooms:
        return err('Room not found', 404)
    return ok(_rooms[code])


# ─────────────────────────────────────────────────────────────────────────────
#  SOCKET.IO EVENT HANDLERS
#  Registered in app.py via register_socket_events(socketio)
# ─────────────────────────────────────────────────────────────────────────────

def register_socket_events(socketio: SocketIO):

    @socketio.on('join_quiz_room')
    def on_join(data):
        """Participant joins a quiz room."""
        code      = data.get('room_code', '').strip().upper()
        name      = data.get('name', 'Anonymous')
        team_name = data.get('team', 'Solo')
        is_mod    = data.get('is_moderator', False)
        sid       = request.sid

        if code not in _rooms:
            emit('error', {'msg': 'Room not found'})
            return

        room = _rooms[code]
        if room['status'] == 'ended':
            emit('error', {'msg': 'Quiz has ended'})
            return

        join_room(code)
        room['participants'][sid] = {'name': name, 'team': team_name, 'score': 0, 'is_mod': is_mod}
        if is_mod:
            room['moderator_sid'] = sid

        if team_name not in room['teams']:
            room['teams'][team_name] = {'members': [], 'score': 0}
        if name not in room['teams'][team_name]['members']:
            room['teams'][team_name]['members'].append(name)

        emit('room_state', {
            'room_code':    code,
            'room_name':    room['room_name'],
            'participants': list(room['participants'].values()),
            'teams':        room['teams'],
            'status':       room['status'],
            'is_moderator': is_mod,
        }, to=sid)

        socketio.emit('participant_joined', {
            'name': name, 'team': team_name,
            'total': len(room['participants'])
        }, to=code, skip_sid=sid)

    @socketio.on('moderator_start_quiz')
    def on_start(data):
        """Moderator starts the quiz — sends first question."""
        code = data.get('room_code', '').upper()
        sid  = request.sid
        if code not in _rooms:
            return
        room = _rooms[code]
        if room.get('moderator_sid') != sid:
            emit('error', {'msg': 'Only the moderator can start'})
            return

        questions = data.get('questions', [])
        if questions:
            room['questions'] = questions

        room['status'] = 'active'
        room['current_q'] = 0
        socketio.emit('quiz_started', {'status': 'active'}, to=code)
        _send_question(socketio, code, 0)

    @socketio.on('moderator_next_question')
    def on_next(data):
        """Moderator advances to next question."""
        code = data.get('room_code', '').upper()
        sid  = request.sid
        if code not in _rooms:
            return
        room = _rooms[code]
        if room.get('moderator_sid') != sid:
            emit('error', {'msg': 'Only moderator can advance'})
            return
        room['current_q'] += 1
        if room['current_q'] >= len(room['questions']):
            # Quiz over
            room['status'] = 'ended'
            scores = sorted(
                [{'team': t, 'score': v['score']} for t, v in room['teams'].items()],
                key=lambda x: x['score'], reverse=True
            )
            socketio.emit('quiz_ended', {'leaderboard': scores}, to=code)
        else:
            _send_question(socketio, code, room['current_q'])

    @socketio.on('submit_answer')
    def on_answer(data):
        """Participant submits an answer."""
        code    = data.get('room_code', '').upper()
        answer  = data.get('answer')
        sid     = request.sid
        if code not in _rooms:
            return
        room = _rooms[code]
        q_idx = room['current_q']
        if q_idx < 0 or q_idx >= len(room['questions']):
            return
        q = room['questions'][q_idx]
        participant = room['participants'].get(sid, {})
        team = participant.get('team', 'Solo')

        if q_idx not in room['answers']:
            room['answers'][q_idx] = {}

        # First correct answer from a team scores
        already = room['answers'][q_idx].get(team)
        correct = (str(answer).strip().lower() == str(q.get('correct_answer', '')).strip().lower())

        if already is None:
            room['answers'][q_idx][team] = {'answer': answer, 'correct': correct, 'time': datetime.utcnow().isoformat()}
            if correct:
                points = int(q.get('points', 10))
                room['teams'][team]['score'] = room['teams'][team].get('score', 0) + points
                participant['score'] = participant.get('score', 0) + points

        emit('answer_received', {'correct': correct, 'team_score': room['teams'][team]['score']}, to=sid)
        # Tell moderator
        if room.get('moderator_sid'):
            socketio.emit('team_answered', {
                'team': team, 'answer': answer, 'correct': correct
            }, to=room['moderator_sid'])

    @socketio.on('quiz_chat')
    def on_chat(data):
        """Broadcast chat message in quiz room."""
        code = data.get('room_code', '').upper()
        msg  = data.get('message', '')[:300]
        sid  = request.sid
        if code not in _rooms:
            return
        name = _rooms[code]['participants'].get(sid, {}).get('name', 'Anonymous')
        entry = {'name': name, 'message': msg, 'time': datetime.utcnow().isoformat()}
        _rooms[code]['chat'].append(entry)
        socketio.emit('chat_message', entry, to=code)

    @socketio.on('disconnect')
    def on_disconnect():
        sid = request.sid
        for code, room in _rooms.items():
            if sid in room['participants']:
                p = room['participants'].pop(sid)
                leave_room(code)
                socketio.emit('participant_left', {
                    'name': p.get('name'), 'total': len(room['participants'])
                }, to=code)
                break


def _send_question(socketio, code, idx):
    room = _rooms[code]
    q = room['questions'][idx]
    payload = {
        'index':   idx,
        'total':   len(room['questions']),
        'text':    q.get('text', q.get('question', '')),
        'options': q.get('options', []),
        'points':  q.get('points', 10),
        'time_limit': q.get('time_limit', 30),
        'image':   q.get('image', None),
    }
    socketio.emit('question', payload, to=code)
