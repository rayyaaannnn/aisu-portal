# =============================================================
#  db.py — MongoDB with automatic JSON fallback
# =============================================================
import os, uuid as uuid_module, json, threading
from datetime import datetime, date
from pathlib import Path

import logging
logger = logging.getLogger(__name__)

# ── Global State ──────────────────────────────────────────────
USE_MONGODB = False
db = None
json_lock = threading.Lock()
STORAGE_MODE = "JSON"  # Will be set to "MongoDB" if connection succeeds

# ── JSON Storage Backend ──────────────────────────────────────
class JSONCollection:
    """MongoDB-compatible wrapper for JSON file storage."""
    
    def __init__(self, name):
        self.name = name
        self.filepath = os.path.join(os.path.dirname(__file__), 'data', f'{name}.json')
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
    
    def _load(self):
        """Load documents from JSON file."""
        try:
            if os.path.exists(self.filepath):
                with open(self.filepath, 'r') as f:
                    return json.load(f) or []
        except Exception as e:
            logger.warning(f"Error loading {self.name}: {e}")
        return []
    
    def _save(self, data):
        """Save documents to JSON file."""
        try:
            with json_lock:
                with open(self.filepath, 'w') as f:
                    json.dump(data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving {self.name}: {e}")
    
    def insert_one(self, doc):
        """Insert a single document."""
        docs = self._load()
        doc = dict(doc)
        doc['_id'] = str(doc.get('_id', uuid_module.uuid4()))
        docs.append(doc)
        self._save(docs)
        class Result:
            inserted_id = doc['_id']
        return Result()
    
    def insert_many(self, docs):
        """Insert multiple documents."""
        data = self._load()
        for doc in docs:
            doc = dict(doc)
            doc['_id'] = str(doc.get('_id', uuid_module.uuid4()))
            data.append(doc)
        self._save(data)
        return list(docs)
    
    def find(self, query=None):
        """Find documents matching query."""
        if query is None:
            query = {}
        docs = self._load()
        results = []
        for doc in docs:
            match = True
            for key, value in query.items():
                if key not in doc or doc[key] != value:
                    match = False
                    break
            if match:
                results.append(doc)
        return results
    
    def find_one(self, query):
        """Find first document matching query."""
        results = self.find(query)
        return results[0] if results else None
    
    def update_one(self, query, updates):
        """Update first document matching query."""
        docs = self._load()
        updated = False
        matched = 0
        
        update_dict = updates.get('$set', updates)
        
        for i, doc in enumerate(docs):
            match = True
            for key, value in query.items():
                if key not in doc or doc[key] != value:
                    match = False
                    break
            if match:
                matched += 1
                doc.update(update_dict)
                updated = True
                break
        
        if updated:
            self._save(docs)
        
        class Result:
            matched_count = matched
        return Result()
    
    def delete_one(self, query):
        """Delete first document matching query."""
        docs = self._load()
        for i, doc in enumerate(docs):
            match = True
            for key, value in query.items():
                if key not in doc or doc[key] != value:
                    match = False
                    break
            if match:
                docs.pop(i)
                self._save(docs)
                class Result:
                    deleted_count = 1
                return Result()
        class Result:
            deleted_count = 0
        return Result()
    
    def count_documents(self, query=None):
        """Count documents matching query."""
        if query is None:
            query = {}
        return len(self.find(query))
    
    def drop(self):
        """Delete all documents."""
        self._save([])
    
    def create_index(self, field, unique=False, sparse=False):
        """Create index (no-op for JSON)."""
        pass

class JSONDatabase:
    """MongoDB-compatible wrapper for JSON storage."""
    
    def __init__(self):
        self.collections = {}
    
    def __getitem__(self, name):
        if name not in self.collections:
            self.collections[name] = JSONCollection(name)
        return self.collections[name]

# ── MongoDB Connection ────────────────────────────────────────
def get_db():
    """Get MongoDB database connection, fallback to JSON."""
    global USE_MONGODB, STORAGE_MODE
    
    MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/aisu_db')
    
    try:
        from pymongo import MongoClient
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
        client.admin.command('ping')
        db_instance = client.aisu_db
        logger.info(f"✓ Connected to MongoDB")
        USE_MONGODB = True
        STORAGE_MODE = "MongoDB"
        return db_instance
    except Exception as e:
        logger.warning(f"⚠ MongoDB unavailable - using JSON storage")
        USE_MONGODB = False
        STORAGE_MODE = "JSON"
        return JSONDatabase()

# Initialize connection at startup
db = get_db()

def ensure_db():
    """Ensure database connection is active."""
    global db
    if db is None:
        db = get_db()
    return db

# ── Create indexes for performance ────────────────────────────
def create_indexes():
    """Create indexes for common queries."""
    try:
        db_ref = ensure_db()
        db_ref['primary_members'].create_index('email', unique=True, sparse=True)
        db_ref['primary_members'].create_index('member_id', unique=True)
        db_ref['primary_members'].create_index('status')
        db_ref['student_members'].create_index('email', unique=True, sparse=True)
        db_ref['student_members'].create_index('student_id', unique=True)
        db_ref['student_members'].create_index('status')
        db_ref['competitions'].create_index('competition_id', unique=True)
        db_ref['complaints'].create_index('complaint_id', unique=True)
        db_ref['certificates'].create_index('cert_id', unique=True)
        db_ref['users'].create_index('email', unique=True, sparse=True)
        logger.info(f"✓ Indexes created ({STORAGE_MODE} mode)")
    except Exception as e:
        logger.info(f"✓ Indexes ready ({STORAGE_MODE} mode)")

# ── CRUD Operations ───────────────────────────────────────────

def insert(collection, doc):
    """Insert document into collection."""
    doc = dict(doc)
    doc.setdefault('_id', str(uuid_module.uuid4()))
    doc.setdefault('created_at', datetime.utcnow().isoformat() + 'Z')
    doc.setdefault('status', 'active')
    
    db_ref = ensure_db()
    db_ref[collection].insert_one(doc)
    return doc

def find_all(collection):
    """Find all documents in collection."""
    db_ref = ensure_db()
    docs = list(db_ref[collection].find({}))
    return [{**doc, '_id': str(doc.get('_id', ''))} for doc in docs]

def find_one(collection, field, value):
    """Find single document by field."""
    db_ref = ensure_db()
    doc = db_ref[collection].find_one({field: value})
    if doc:
        doc['_id'] = str(doc.get('_id', ''))
    return doc

def find_many(collection, field=None, value=None, filters=None):
    """Find multiple documents with filters."""
    db_ref = ensure_db()
    query = {}
    
    if filters:
        query = filters
    elif field and value is not None:
        query = {field: value}
    
    docs = list(db_ref[collection].find(query))
    return [{**doc, '_id': str(doc.get('_id', ''))} for doc in docs]

def update_one(collection, _id, updates):
    """Update single document by ID."""
    db_ref = ensure_db()
    updates = dict(updates)
    updates['updated_at'] = datetime.utcnow().isoformat() + 'Z'
    
    result = db_ref[collection].update_one(
        {'_id': _id},
        {'$set': updates}
    )
    
    if result.matched_count > 0:
        doc = db_ref[collection].find_one({'_id': _id})
        if doc:
            doc['_id'] = str(doc.get('_id', ''))
        return doc
    return None

def delete_one(collection, _id):
    """Delete single document by ID."""
    db_ref = ensure_db()
    result = db_ref[collection].delete_one({'_id': _id})
    return result.deleted_count > 0

def count(collection, filters=None):
    """Count documents in collection."""
    db_ref = ensure_db()
    if filters:
        return db_ref[collection].count_documents(filters)
    return db_ref[collection].count_documents({})

# ── ID Generators ─────────────────────────────────────────────

def uuid():
    return uuid_module.uuid4()

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

def gen_member_id(state_name='Bihar'):
    year = datetime.utcnow().strftime('%y')
    seq  = count('primary_members') + 1
    sc   = _state_code(state_name)
    return f'AISU{sc}{year}{seq:04d}'

def gen_student_id(state_name='Bihar'):
    year = datetime.utcnow().strftime('%Y')
    seq  = count('student_members') + 1
    sc   = _state_code(state_name)
    return f'AISUSM{sc}{year}{seq:06d}'

def gen_affiliation_id():
    year = datetime.utcnow().strftime('%Y')
    seq  = count('affiliations') + 1
    return f'FIYAOA{year}{seq:04d}'

def gen_complaint_id():
    year = datetime.utcnow().strftime('%y')
    seq  = count('complaints') + 1
    return f'AISUCMP{year}{seq:05d}'

def gen_cert_id(prog_code='COMP'):
    year = datetime.utcnow().strftime('%Y')
    seq  = count('certificates') + 1
    return f'AISUCERT{prog_code.upper()}{year}{seq:06d}'

def gen_innovation_id():
    year = datetime.utcnow().strftime('%Y')
    seq  = count('innovations') + 1
    return f'AISUIC{year}{seq:04d}'

def gen_competition_id():
    year = datetime.utcnow().strftime('%Y')
    seq  = count('competitions') + 1
    return f'AISUCOMP{year}{seq:04d}'

# ── Expiry Helpers ────────────────────────────────────────────

def days_until_expiry(approved_at_iso, validity_years):
    try:
        approved = datetime.fromisoformat(approved_at_iso.replace('Z', ''))
        from dateutil.relativedelta import relativedelta
        expiry = approved + relativedelta(years=validity_years)
        delta  = expiry.date() - date.today()
        return delta.days
    except:
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
    except:
        return 'N/A'

# ── Aliases ────────────────────────────────────────────────────
def gen_cert_number(prog_code='COMP'):
    return gen_cert_id(prog_code)

def make_id():
    return str(uuid_module.uuid4())

def load_collection(collection):
    return find_all(collection)

def save_collection(collection, data):
    db_ref = ensure_db()
    db_ref[collection].drop()
    if data:
        db_ref[collection].insert_many(data)

# Initialize on startup
try:
    create_indexes()
    logger.info(f"Database ready ({STORAGE_MODE} mode)")
except Exception as e:
    logger.warning(f"Database initialization issue: {e}")
