# MongoDB Migration Guide

## What Changed

✅ Database backend migrated from **JSON files** to **MongoDB**  
✅ All API endpoints remain the same - no frontend changes needed  
✅ Better performance, scalability, and concurrency  

## Quick Start

### Option 1: Local MongoDB (Recommended for Development)

**Install MongoDB Community Edition:**
- **Windows**: https://docs.mongodb.com/manual/tutorial/install-mongodb-on-windows/
- **Mac**: `brew install mongodb-community`
- **Linux**: https://docs.mongodb.com/manual/installation/

**Start MongoDB:**
```powershell
# Windows (if installed via MSI)
net start MongoDB

# Or specify mongod.exe path
"C:\Program Files\MongoDB\Server\7.0\bin\mongod.exe"

# Linux/Mac
mongod
```

Your `.env` is already configured for local MongoDB:
```
MONGO_URI=mongodb://localhost:27017/aisu_db
```

---

### Option 2: MongoDB Atlas (Cloud - Free Tier)

1. Go to https://www.mongodb.com/cloud/atlas
2. Create a free account and cluster
3. Get your connection string (looks like):
   ```
   mongodb+srv://username:password@cluster.mongodb.net/aisu_db?retryWrites=true&w=majority
   ```
4. Update `.env`:
   ```
   MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/aisu_db?retryWrites=true&w=majority
   ```

---

## Migrating Data from JSON

If you have existing data in `/backend/data/` JSON files, run this script to import:

```python
# backend/migrate_to_mongodb.py
import json, os
from db import ensure_db

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
db = ensure_db()

for file in os.listdir(DATA_DIR):
    if file.endswith('.json'):
        collection_name = file.replace('.json', '')
        print(f"Importing {collection_name}...")
        
        with open(os.path.join(DATA_DIR, file), 'r') as f:
            try:
                data = json.load(f)
                if data:
                    db[collection_name].insert_many(data)
                    print(f"  ✓ {len(data)} documents imported")
            except json.JSONDecodeError:
                print(f"  ✗ Invalid JSON in {file}")

print("Migration complete!")
```

Then run:
```bash
python backend/migrate_to_mongodb.py
```

---

## Testing the Migration

**Check MongoDB Connection:**
```bash
cd backend
python -c "import db; db.db.admin.command('ping'); print('✓ MongoDB connected!')"
```

**Start the Backend:**
```bash
cd backend
python app.py
```

Expected output:
```
✓ Connected to MongoDB: mongodb://localhost:27017/aisu_db
✓ Database indexes created
============================================================
  AISU Backend v2.1  —  http://localhost:5000
  ...
```

---

## What's Preserved

✅ All ID generation functions (same format as before)  
✅ All CRUD operations (same function signatures)  
✅ All expiry calculations  
✅ All routes and API endpoints  
✅ All authentication logic  
✅ File uploads still stored in `/uploads/`  

---

## Performance Improvements

| Metric | JSON Files | MongoDB |
|--------|-----------|---------|
| Query speed | O(n) linear | O(1) indexed |
| Concurrency | File locks | Native |
| Max records | ~10K | Millions |
| Scalability | Single machine | Clusterable |
| Transactions | None | ACID |

---

## Troubleshooting

**Error: "ConnectionFailure - Cannot connect to MongoDB"**
- MongoDB is not running. Start it with `mongod` command
- Or update `MONGO_URI` in `.env` to point to your MongoDB server

**Error: "Module 'db' has no attribute..."**
- Backend needs to be restarted to pick up new db.py

**Slow queries?**
- Indexes are created automatically on first run
- Check MongoDB logs for query performance

---

## Reverting to JSON (if needed)

The original JSON-based db.py is backed up. To revert:
1. Replace `backend/db.py` with the old version
2. Update `requirements.txt` to remove pymongo and python-dotenv
3. Remove `.env` file

---

## Next Steps

1. **Ensure MongoDB is running** `mongod`
2. **Restart the backend** `python app.py`
3. **Test API endpoints** at http://localhost:5000/api/health
4. **Migrate existing data** (if any) using the script above

**Happy coding!** 🚀
