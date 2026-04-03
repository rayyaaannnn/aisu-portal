// ============================================================
//  js/api.js — AISU Frontend API Client
//  All calls to the Flask backend (http://localhost:5000)
// ============================================================

const API_BASE = 'http://localhost:5000/api';

// ── Token helpers ────────────────────────────────────────────
function getToken()  { return localStorage.getItem('aisu_token'); }
function setToken(t) { localStorage.setItem('aisu_token', t); }
function clearToken(){ localStorage.removeItem('aisu_token'); localStorage.removeItem('aisu_user'); }
function getUser()   { try { return JSON.parse(localStorage.getItem('aisu_user')); } catch { return null; } }
function setUser(u)  { localStorage.setItem('aisu_user', JSON.stringify(u)); }

// ── Generic fetch wrapper ────────────────────────────────────
async function apiCall(method, path, body = null, isForm = false) {
    const headers = {};
    const token   = getToken();
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const options = { method, headers };

    if (body) {
        if (isForm) {
            // FormData — no Content-Type header (browser sets boundary)
            options.body = body;
        } else {
            headers['Content-Type'] = 'application/json';
            options.body = JSON.stringify(body);
        }
    }

    try {
        const res  = await fetch(API_BASE + path, options);
        const json = await res.json();
        if (!res.ok && res.status === 401) {
            // Try refresh
            const refreshed = await refreshToken();
            if (refreshed) return apiCall(method, path, body, isForm);
            clearToken();
            window.location.href = 'login.html';
            return null;
        }
        return json;
    } catch (e) {
        console.error('API Error:', e);
        return { success: false, message: 'Network error. Is the backend running?' };
    }
}

async function refreshToken() {
    const stored = localStorage.getItem('aisu_refresh');
    if (!stored) return false;
    try {
        const res = await fetch(API_BASE + '/auth/refresh', {
            method : 'POST',
            headers: { 'Authorization': `Bearer ${stored}` }
        });
        const json = await res.json();
        if (json.success && json.data?.access_token) {
            setToken(json.data.access_token);
            return true;
        }
    } catch {}
    return false;
}

// ── AUTH ─────────────────────────────────────────────────────
const Auth = {
    async login(email, password) {
        const r = await apiCall('POST', '/auth/login', { email, password });
        if (r?.success) {
            setToken(r.data.access_token);
            localStorage.setItem('aisu_refresh', r.data.refresh_token);
            setUser(r.data.user);
        }
        return r;
    },
    logout() {
        clearToken();
        localStorage.removeItem('aisu_refresh');
        window.location.href = 'login.html';
    },
    async me() { return apiCall('GET', '/auth/me'); },
    async changePassword(old_password, new_password) {
        return apiCall('POST', '/auth/change-password', { old_password, new_password });
    },
    isLoggedIn() { return !!getToken(); },
    getUser,
};

// ── PRIMARY MEMBERSHIP ────────────────────────────────────────
const PrimaryMembers = {
    async apply(formData) {
        return apiCall('POST', '/members/apply', formData, true);
    },
    async list(status, state) {
        let q = [];
        if (status) q.push(`status=${status}`);
        if (state)  q.push(`state=${state}`);
        return apiCall('GET', `/members/${q.length ? '?' + q.join('&') : ''}`);
    },
    async get(id)          { return apiCall('GET', `/members/${id}`); },
    async approve(id, designation) { return apiCall('POST', `/members/${id}/approve`, { designation }); },
    async reject(id, reason)       { return apiCall('POST', `/members/${id}/reject`,  { reason }); },
    async stats()          { return apiCall('GET', '/members/stats/summary'); },
};

// ── STUDENT MEMBERSHIP ────────────────────────────────────────
const StudentMembers = {
    async apply(formData) { return apiCall('POST', '/students/apply', formData, true); },
    async list(status)    {
        const q = status ? `?status=${status}` : '';
        return apiCall('GET', `/students/${q}`);
    },
    async approve(id)     { return apiCall('POST', `/students/${id}/approve`); },
    async reject(id, reason) { return apiCall('POST', `/students/${id}/reject`, { reason }); },
    async stats()         { return apiCall('GET', '/students/stats/summary'); },
};

// ── COMPLAINTS ────────────────────────────────────────────────
const Complaints = {
    async submit(formData)    { return apiCall('POST', '/complaints/submit', formData, true); },
    async track(complaint_id) { return apiCall('GET', `/complaints/track/${complaint_id}`); },
    async list(status)        {
        const q = status ? `?status=${status}` : '';
        return apiCall('GET', `/complaints/${q}`);
    },
    async update(id, updates) { return apiCall('POST', `/complaints/${id}/update`, updates); },
};

// ── CONTACT ───────────────────────────────────────────────────
const Contact = {
    async send(data) { return apiCall('POST', '/contact/send', data); },
    async list()     { return apiCall('GET', '/contact/'); },
};

// ── CERTIFICATES ──────────────────────────────────────────────
const Certs = {
    async verify(cert_id) { return apiCall('GET', `/certs/verify/${cert_id}`); },
    async issue(data)     { return apiCall('POST', '/certs/issue', data); },
    async list()          { return apiCall('GET', '/certs/'); },
    async revoke(id)      { return apiCall('POST', `/certs/${id}/revoke`); },
};

// ── INTERNSHIP ────────────────────────────────────────────────
const Internship = {
    async apply(formData) { return apiCall('POST', '/internship/apply', formData, true); },
    async list()          { return apiCall('GET', '/internship/'); },
    async approve(id)     { return apiCall('POST', `/internship/${id}/approve`); },
    async reject(id, reason) { return apiCall('POST', `/internship/${id}/reject`, { reason }); },
};

// ── AFFILIATION ───────────────────────────────────────────────
const Affiliation = {
    async apply(formData) { return apiCall('POST', '/affiliation/apply', formData, true); },
    async list()          { return apiCall('GET', '/affiliation/'); },
    async approve(id)     { return apiCall('POST', `/affiliation/${id}/approve`); },
    async reject(id, reason) { return apiCall('POST', `/affiliation/${id}/reject`, { reason }); },
};

// ── ADMIN ─────────────────────────────────────────────────────
const Admin = {
    async stats()                   { return apiCall('GET', '/admin/stats'); },
    async listUsers()               { return apiCall('GET', '/admin/users'); },
    async createUser(data)          { return apiCall('POST', '/admin/users/create', data); },
    async updateUser(id, data)      { return apiCall('PUT', `/admin/users/${id}`, data); },
    async deactivateUser(id)        { return apiCall('POST', `/admin/users/${id}/deactivate`); },
    async search(q)                 { return apiCall('GET', `/admin/search?q=${encodeURIComponent(q)}`); },
};

// ── Helper: build FormData from a <form> element ──────────────
function formToData(formEl) {
    return new FormData(formEl);
}

// ── Helper: show API response as toast/alert ──────────────────
function showApiResult(result, successEl, errorEl, successMsg = null) {
    if (!result) return;
    if (result.success) {
        if (successEl) {
            successEl.textContent = successMsg || result.message;
            successEl.style.display = 'block';
        }
        if (errorEl) errorEl.style.display = 'none';
    } else {
        if (errorEl) {
            errorEl.textContent = result.message || 'An error occurred';
            errorEl.style.display = 'block';
        }
        if (successEl) successEl.style.display = 'none';
    }
}

// Export to window for use in HTML pages
window.Auth           = Auth;
window.PrimaryMembers = PrimaryMembers;
window.StudentMembers = StudentMembers;
window.Complaints     = Complaints;
window.Contact        = Contact;
window.Certs          = Certs;
window.Internship     = Internship;
window.Affiliation    = Affiliation;
window.Admin          = Admin;
window.formToData     = formToData;
window.showApiResult  = showApiResult;
