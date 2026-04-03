#!/usr/bin/env python3
# =============================================================
#  migrate_to_mongodb.py — Import JSON data to MongoDB
# =============================================================
import json, os, sys
from db import ensure_db

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

def migrate():
    try:
        db = ensure_db()
        print("✓ Connected to MongoDB\n")
    except Exception as e:
        print(f"✗ Failed to connect to MongoDB: {e}")
        sys.exit(1)

    if not os.path.exists(DATA_DIR):
        print(f"✗ Data directory not found: {DATA_DIR}")
        return

    migrated_count = 0
    total_documents = 0

    for file in sorted(os.listdir(DATA_DIR)):
        if not file.endswith('.json'):
            continue

        collection_name = file.replace('.json', '')
        file_path = os.path.join(DATA_DIR, file)

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if not data:
                print(f"  ⊘ {collection_name}: Empty")
                continue

            # Clear existing data
            db[collection_name].drop()

            # Insert data
            if isinstance(data, list):
                result = db[collection_name].insert_many(data)
                count = len(result.inserted_ids)
            elif isinstance(data, dict):
                db[collection_name].insert_one(data)
                count = 1
            else:
                print(f"  ✗ {collection_name}: Unexpected data format")
                continue

            print(f"  ✓ {collection_name}: {count} documents")
            migrated_count += 1
            total_documents += count

        except json.JSONDecodeError:
            print(f"  ✗ {collection_name}: Invalid JSON")
        except Exception as e:
            print(f"  ✗ {collection_name}: {e}")

    print(f"\n✓ Migration complete!")
    print(f"  Collections: {migrated_count}")
    print(f"  Documents: {total_documents}")

if __name__ == '__main__':
    migrate()
