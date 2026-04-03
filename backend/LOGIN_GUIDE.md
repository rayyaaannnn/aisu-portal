# AISU Login & Authentication Guide

## Quick Start

### Credentials

**Default Admin Account** (auto-seeded):
```
Email:    admin@aisu4india.in
Password: Admin@AISU2024
Role:     national (full access)
```

## API Endpoints

### 1. **Register** — Create New Account
```http
POST /api/auth/register
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com",
  "mobile": "9876543210",
  "password": "SecurePass123!",
  "state": "Bihar"
}
```

**Response (201):**
```json
{
  "success": true,
  "message": "Account created successfully!",
  "data": {
    "access_token": "eyJhbGc...",
    "refresh_token": "eyJhbGc...",
    "user": {
      "id": "uuid-string",
      "name": "John Doe",
      "email": "john@example.com",
      "role": "user"
    }
  }
}
```

---

### 2. **Login** — Get Tokens
```http
POST /api/auth/login
Content-Type: application/json

{
  "identifier": "admin@aisu4india.in",
  "password": "Admin@AISU2024"
}
```

**Identifier can be:**
- Email: `admin@aisu4india.in`
- Mobile: `9876543210`
- Member ID: `AISUBR260001`

**Response (200):**
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "access_token": "eyJhbGc...",
    "refresh_token": "eyJhbGc...",
    "user": {
      "id": "uuid-string",
      "name": "National Admin",
      "email": "admin@aisu4india.in",
      "role": "national",
      "state": "ALL"
    }
  }
}
```

---

### 3. **Get Profile** — Current User
```http
GET /api/auth/me
Authorization: Bearer {access_token}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "_id": "uuid-string",
    "name": "National Admin",
    "email": "admin@aisu4india.in",
    "mobile": "0000000000",
    "role": "national",
    "state": "ALL",
    "status": "active",
    "created_at": "2026-03-28T10:30:00Z",
    "updated_at": "2026-03-28T10:30:00Z",
    "primary_membership": {
      "member_id": "AISUBR260001",
      "status": "approved",
      "approved_at": "2026-03-28T10:30:00Z",
      "expiry_date": "28-03-2029"
    }
  }
}
```

---

### 4. **Refresh Token** — Get New Access Token
```http
POST /api/auth/refresh
Authorization: Bearer {refresh_token}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGc..."
  }
}
```

---

### 5. **Change Password** — Update Password
```http
POST /api/auth/change-password
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "old_password": "Admin@AISU2024",
  "new_password": "NewSecure@Pass2024"
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Password changed successfully"
}
```

---

### 6. **Forgot Password — Request OTP**
```http
POST /api/auth/forgot-password/request
Content-Type: application/json

{
  "identifier": "admin@aisu4india.in"
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "If this account exists, a reset code has been sent.",
  "data": {
    "masked_email": "ad***...in"
  }
}
```

---

### 7. **Forgot Password — Reset with OTP**
```http
POST /api/auth/forgot-password/reset
Content-Type: application/json

{
  "identifier": "admin@aisu4india.in",
  "otp": "123456",
  "new_password": "NewSecurePass@2024"
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Password reset successfully. Please login."
}
```

---

## Using Login in Python

### **Method 1: Direct API Calls**
```python
import requests

# Login
response = requests.post(
    'http://localhost:5000/api/auth/login',
    json={
        'identifier': 'admin@aisu4india.in',
        'password': 'Admin@AISU2024'
    }
)
result = response.json()['data']
access_token = result['access_token']

# Get profile
headers = {'Authorization': f'Bearer {access_token}'}
profile = requests.get(
    'http://localhost:5000/api/auth/me',
    headers=headers
).json()['data']

print(f"User: {profile['name']}")
```

### **Method 2: Using login_util.py**
```python
from login_util import login, verify_token

# Login
result = login('admin@aisu4india.in', 'Admin@AISU2024')
if result['success']:
    access_token = result['access_token']
    user = result['user']
    print(f"Logged in as: {user['name']}")
    
    # Get profile
    profile = verify_token(access_token)
    print(f"Email: {profile['email']}")
else:
    print(f"Login failed: {result['message']}")
```

---

## Testing

### **Run Full Test Suite**
```bash
cd backend
python test_login.py
```

This tests all authentication endpoints:
- ✓ User registration
- ✓ Login (email, mobile, member_id)
- ✓ Get profile (/me)
- ✓ Token refresh
- ✓ Password change
- ✓ Forgot password flow
- ✓ Invalid login rejection

### **Quick Manual Test**
```bash
cd backend
python -c "from login_util import login; result = login('admin@aisu4india.in', 'Admin@AISU2024'); print('✓ Login successful!' if result['success'] else '✗ Failed')"
```

---

## Frontend Implementation

### **HTML Form → Login**
```html
<form id="loginForm">
  <input type="text" id="identifier" placeholder="Email, mobile, or member ID" required>
  <input type="password" id="password" placeholder="Password" required>
  <button type="submit">Login</button>
</form>

<script>
document.getElementById('loginForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const response = await fetch('/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      identifier: document.getElementById('identifier').value,
      password: document.getElementById('password').value
    })
  });
  
  const data = await response.json();
  if (data.success) {
    // Store tokens
    localStorage.setItem('access_token', data.data.access_token);
    localStorage.setItem('refresh_token', data.data.refresh_token);
    
    // Redirect to dashboard
    window.location.href = '/dashboard.html';
  } else {
    alert(data.message);
  }
});
</script>
```

### **Protected Route Example**
```html
<script>
// Get token from storage
const token = localStorage.getItem('access_token');

// Fetch protected endpoint
fetch('/api/auth/me', {
  headers: { 'Authorization': `Bearer ${token}` }
})
.then(r => r.json())
.then(data => {
  if (data.success) {
    document.getElementById('userName').textContent = data.data.name;
  } else {
    // Token expired or invalid - redirect to login
    window.location.href = '/login.html';
  }
});
</script>
```

---

## Token Management

### **Token Expiry**
- **Access Token**: 12 hours
- **Refresh Token**: 30 days

### **Auto-Refresh Pattern**
```python
import time
from login_util import login, refresh_access_token

# Initial login
result = login('admin@aisu4india.in', 'Admin@AISU2024')
access_token = result['access_token']
refresh_token = result['refresh_token']

# Later... when token might be expired
def get_valid_token():
    global access_token, refresh_token
    
    # Try to use current token
    try:
        # If API call fails with 401, refresh
        new_token = refresh_access_token(refresh_token)
        if new_token:
            access_token = new_token
    except:
        pass
    
    return access_token
```

---

## Error Handling

### **Common Errors**

| Error | Cause | Fix |
|-------|-------|-----|
| `Invalid credentials` | Wrong email/password | Check username and password |
| `Account is not active` | Admin deactivated account | Contact national admin |
| `Missing fields: identifier and password` | Incomplete request body | Send both identifier and password |
| `Cannot connect to backend` | Backend not running | Start with `python backend/app.py` |
| `Unauthorized (401)` | Invalid or expired token | Login again or refresh token |
| `Forbidden (403)` | Insufficient permissions | Different role required |

---

## Security Notes

✅ **Passwords are hashed** with bcrypt (not stored in plain text)  
✅ **JWT tokens are signed** with SECRET_KEY  
✅ **Access tokens are short-lived** (12 hours)  
✅ **OTP valid for 15 minutes** (forgot password)  
✅ **No session files** stored (stateless auth)  

⚠️ **Important**: Never share access tokens  
⚠️ **Keep refresh tokens secure** (like passwords)  
⚠️ **Use HTTPS in production**  

---

## Example Workflows

### **User Registration → Login → Access Protected Route**
```python
from login_util import login, register, verify_token

# 1. Register
reg = register(
    'Jane Doe', 
    'jane@example.com',
    '9876543210',
    'SecurePass123!',
    'Bihar'
)
access_token = reg['access_token']

# 2. Get profile immediately after registration
profile = verify_token(access_token)
print(f"Registered as: {profile['name']}")

# 3. Use the token to access protected routes
import requests
headers = {'Authorization': f'Bearer {access_token}'}
members = requests.get('http://localhost:5000/api/members', headers=headers).json()
```

### **Login → Check Membership Status → Renew if Expired**
```python
from login_util import login, verify_token

result = login('user@example.com', 'password123')
if result['success']:
    profile = verify_token(result['access_token'])
    
    # Check if primary membership is expiring
    if 'primary_membership' in profile:
        mem = profile['primary_membership']
        print(f"Membership: {mem['status']}")
        print(f"Expires: {mem['expiry_date']}")
        
        if mem['status'] == 'expired':
            print("Please renew your membership!")
```

---

**For more details, see:**
- [routes/auth.py](routes/auth.py) — Full implementation
- [login_util.py](login_util.py) — Python helper functions
- [test_login.py](test_login.py) — Test suite with examples
