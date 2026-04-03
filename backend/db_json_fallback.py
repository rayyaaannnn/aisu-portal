# =============================================================
#  db.py — JSON-file-based data store (Fallback version)
# =============================================================
import os, json, uuid, threading
from datetime import datetime, date

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
_locks = {}
os.makedirs(DATA_DIR, exist_ok=True)

def _lock(name):
    if name not in _locks:
        _locks[name] = threading.Lock()
    return _locks[name]

def _path(c): return os.path.join(DATA_DIR, f'{c}.json')

def _load(c):
    p = _path(c)
    if not os.path.exists(p): return []
    with open(p, 'r', encoding='utf-8') as f:
        try: return json.load(f)
        except: return []

def _save(c, data):
    with open(_path(c), 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ── CRUD ──────────────────────────────────────────────────────

def insert(collection, doc):
    doc = dict(doc)
    doc.setdefault('_id',        str(uuid.uuid4()))
    doc.setdefault('created_at', datetime.utcnow().isoformat() + 'Z')
    doc.setdefault('status',     'pending')
    with _lock(collection):
        data = _load(collection)
        data.append(doc)
        _save(collection, data)
    return doc

def find_all(collection):
    with _lock(collection):
        return list(_load(collection))

def find_one(collection, field, value):
    with _lock(collection):
        for doc in _load(collection):
            if doc.get(field) == value:
                return doc
    return None

def find_many(collection, field=None, value=None, filters=None):
    """filters = dict of {field: value} ANDed together."""
    with _lock(collection):
        data = _load(collection)
    if filters:
        return [d for d in data if all(d.get(k) == v for k, v in filters.items())]
    if field:
        return [d for d in data if d.get(field) == value]
    return data

def update_one(collection, _id, updates):
    with _lock(collection):
        data = _load(collection)
        for doc in data:
            if doc.get('_id') == _id:
                doc.update(updates)
                doc['updated_at'] = datetime.utcnow().isoformat() + 'Z'
                _save(collection, data)
                return doc
    return None

def delete_one(collection, _id):
    with _lock(collection):
        data = _load(collection)
        new  = [d for d in data if d.get('_id') != _id]
        changed = len(new) < len(data)
        if changed: _save(collection, new)
        return changed

def count(collection, filters=None):
    return len(find_many(collection, filters=filters) if filters else find_all(collection))

# ── ID Generators (exact spec format) ────────────────────────

def _state_code(state_name):
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

def gen_member_id(state_name):
    """Format: AISU[StateCode][YY][4-digit-serial]  e.g. AISUBR260014"""
    sc   = _state_code(state_name)
    year = datetime.utcnow().strftime('%y')
    seq  = count('primary_members') + 1
    return f'AISU{sc}{year}{seq:04d}'

def gen_student_id(state_name):
    """Format: AISUSM[StateCode][YYYY][000001]  e.g. AISUSMBR20260001"""
    sc   = _state_code(state_name)
    year = datetime.utcnow().strftime('%Y')
    seq  = count('student_members') + 1
    return f'AISUSM{sc}{year}{seq:06d}'

def gen_affiliation_id():
    """Format: FIYAOA[YYYY][Serial]  e.g. FIYAOA20260015"""
    year = datetime.utcnow().strftime('%Y')
    seq  = count('affiliations') + 1
    return f'FIYAOA{year}{seq:04d}'

def gen_complaint_id():
    """Format: AISUCMP[YY][5-digit]  e.g. AISUCMP2600001"""
    year = datetime.utcnow().strftime('%y')
    seq  = count('complaints') + 1
    return f'AISUCMP{year}{seq:05d}'

def gen_cert_id(prog_code='COMP'):
    """Format: AISUCERT[ProgCode][YYYY][6-digit]  e.g. AISUCERTCOMP2026000145"""
    year = datetime.utcnow().strftime('%Y')
    seq  = count('certificates') + 1
    return f'AISUCERT{prog_code.upper()}{year}{seq:06d}'

def gen_innovation_id():
    """Format: AISUIC[YYYY][4-digit]  e.g. AISUIC20260025"""
    year = datetime.utcnow().strftime('%Y')
    seq  = count('innovations') + 1
    return f'AISUIC{year}{seq:04d}'

def gen_competition_id():
    year = datetime.utcnow().strftime('%Y')
    seq  = count('competitions') + 1
    return f'AISUCOMP{year}{seq:04d}'

# ── Expiry helpers ────────────────────────────────────────────

def days_until_expiry(approved_at_iso, validity_years):
    """Return days remaining before membership expires. Negative = expired."""
    try:
        approved = datetime.fromisoformat(approved_at_iso.replace('Z', ''))
        from dateutil.relativedelta import relativedelta
        expiry = approved + relativedelta(years=validity_years)
        delta  = expiry.date() - date.today()
        return delta.days
    except Exception:
        return None

def is_expired(approved_at_iso, validity_years):
    d = days_until_expiry(approved_at_iso, validity_years)
    return d is not None and d <= 0

def get_expiry_date(approved_at_iso, validity_years):
    try:
        approved = datetime.fromisoformat(approved_at_iso.replace('Z', ''))
        from dateutil.relativedelta import relativedelta
        expiry = approved + relativedelta(years=validity_years)
        return expiry.strftime('%d-%m-%Y')
    except Exception:
        return 'N/A'

# -- Aliases for compatibility -----------------------------------------
def gen_cert_number(prog_code='COMP'):
    return gen_cert_id(prog_code)

def make_id():
    return str(uuid.uuid4())

def load_collection(collection):
    return find_all(collection)

def save_collection(collection, data):
    with _lock(collection):
        _save(collection, data)

# Dummy MongoDB functions for compatibility (not used in JSON mode)
def create_indexes():
    pass

def ensure_db():
    pass
