#!/usr/bin/env python3
# =============================================================
#  start_backend.py — Easy backend startup with auto-fallback
# =============================================================
import os
import sys
import subprocess

print("\n" + "="*60)
print("  AISU Backend Startup")
print("="*60 + "\n")

# Check if we're in the backend directory
if not os.path.exists('app.py'):
    print("❌ Error: app.py not found. Make sure you're in the backend directory:")
    print("   cd backend/")
    sys.exit(1)

# Check Python version
import sys
if sys.version_info < (3, 8):
    print("❌ Error: Python 3.8+ required")
    sys.exit(1)

print("✓ Backend directory confirmed\n")

# Try to import required packages
try:
    import flask
    print("✓ Flask installed")
except:
    print("❌ Flask not found. Run: pip install -r requirements.txt")
    sys.exit(1)

# Check for MongoDB
print("\n" + "-"*60)
print("  Checking MongoDB Connection...")
print("-"*60 + "\n")

mongo_available = False
try:
    from pymongo import MongoClient
    client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=2000)
    client.admin.command('ping')
    mongo_available = True
    print("✓ MongoDB is running on localhost:27017")
except Exception as e:
    print("⚠️  MongoDB not available:")
    print(f"   {str(e)[:80]}")
    print("\nOptions:")
    print("  1. Start MongoDB with: mongod")
    print("  2. Or use MongoDB Atlas (cloud)")
    print("  3. Or continue with JSON fallback (not recommended)")
    
    response = input("\nContinue without MongoDB? (json fallback) [y/N]: ").strip().lower()
    if response != 'y':
        print("\n❌ Startup cancelled")
        sys.exit(1)
    else:
        print("\n⚠️  Using JSON file storage (not recommended for production)")

# Start Flask app
print("\n" + "="*60)
print("  Starting Flask Application...")
print("="*60 + "\n")

print("✓ Server starting on http://localhost:5000")
print("✓ API endpoint: http://localhost:5000/api/auth/login")
print("✓ Press CTRL+C to stop\n")

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Run Flask app
os.system(f'"{sys.executable}" app.py')
