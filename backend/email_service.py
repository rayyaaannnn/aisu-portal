# =============================================================
#  email_service.py — AISU Email Automation
#  Uses Gmail SMTP. Set credentials in config.env or env vars.
# =============================================================
import smtplib, os, threading
from email.mime.multipart import MIMEMultipart
from email.mime.text      import MIMEText
from email.mime.base      import MIMEBase
from email                import encoders
from datetime             import datetime

# ── Config (override with env vars in production) ─────────────
SMTP_HOST  = os.environ.get('SMTP_HOST',  'smtp.gmail.com')
SMTP_PORT  = int(os.environ.get('SMTP_PORT', 587))
SMTP_USER  = os.environ.get('SMTP_USER',  'aisu4india@gmail.com')
SMTP_PASS  = os.environ.get('SMTP_PASS',  '')          # Set App Password here
FROM_NAME  = 'All India Students Union (AISU)'
FROM_ADDR  = f'{FROM_NAME} <{SMTP_USER}>'

# ── National Officers (always CC'd on key events) ─────────────
NATIONAL_EMAILS = {
    'president'       : 'president.aisu@gmail.com',
    'vice_president'  : 'vicepresident.aisu@gmail.com',
    'gen_secretary'   : 'secretary.aisu@gmail.com',
    'joint_secretary' : 'jointsec.aisu@gmail.com',
    'treasurer'       : 'treasurer.aisu@gmail.com',
    'it_cell'         : 'itcell.aisu@gmail.com',
    'admin'           : 'aisu4india@gmail.com',
}

# ─────────────────────────────────────────────────────────────

def _send(to_list, subject, html_body, cc_list=None, attachments=None):
    """Send email in a background thread so it never blocks a request."""
    if not SMTP_PASS:
        print(f'[EMAIL] SMTP_PASS not configured. Would send to: {to_list} | Subject: {subject}')
        return
    def _worker():
        try:
            msg = MIMEMultipart('alternative')
            msg['From']    = FROM_ADDR
            msg['To']      = ', '.join(to_list) if isinstance(to_list, list) else to_list
            msg['Subject'] = subject
            if cc_list:
                msg['Cc']  = ', '.join(cc_list) if isinstance(cc_list, list) else cc_list
            msg.attach(MIMEText(html_body, 'html'))
            if attachments:
                for fname, fdata in attachments:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(fdata)
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', f'attachment; filename="{fname}"')
                    msg.attach(part)
            all_recipients = list(to_list if isinstance(to_list, list) else [to_list])
            if cc_list:
                all_recipients += list(cc_list if isinstance(cc_list, list) else [cc_list])
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
                server.ehlo()
                server.starttls()
                server.login(SMTP_USER, SMTP_PASS)
                server.sendmail(SMTP_USER, all_recipients, msg.as_string())
            print(f'[EMAIL] Sent: {subject} → {all_recipients}')
        except Exception as e:
            print(f'[EMAIL] FAILED: {e}')
    threading.Thread(target=_worker, daemon=True).start()

# ── Templates ─────────────────────────────────────────────────

def _base_template(title, content):
    return f"""
    <!DOCTYPE html><html><body style="margin:0;padding:0;background:#f4f4f4;font-family:Arial,sans-serif;">
    <table width="100%" cellpadding="0" cellspacing="0"><tr><td align="center" style="padding:30px 10px;">
    <table width="600" style="background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,0.08);">
      <tr><td style="background:linear-gradient(135deg,#0d1b2a,#1a2f45);padding:30px;text-align:center;">
        <h1 style="color:#ff6f0f;margin:0;font-size:24px;letter-spacing:2px;">AISU4India</h1>
        <p style="color:rgba(255,255,255,0.7);margin:4px 0 0;font-size:13px;">All India Students Union</p>
      </td></tr>
      <tr><td style="padding:32px 36px;">
        <h2 style="color:#1a2f45;margin:0 0 20px;font-size:20px;">{title}</h2>
        {content}
      </td></tr>
      <tr><td style="background:#f8f9fa;padding:20px 36px;border-top:1px solid #e9ecef;text-align:center;">
        <p style="color:#6c757d;font-size:12px;margin:0;">
          &copy; {datetime.now().year} All India Students Union (AISU) &mdash; 
          Dubwaliya Yadavchapra, Chanpatia, West Champaran, Bihar &ndash; 845450<br>
          <a href="https://aisu4india.in" style="color:#ff6f0f;">aisu4india.in</a> | 
          aisu4india@gmail.com | +91 80748 53717
        </p>
      </td></tr>
    </table></td></tr></table></body></html>"""

# ── Email Functions ───────────────────────────────────────────

def send_primary_application_received(member):
    """Send to applicant + national officers when primary form submitted."""
    name = member.get('fullname', 'Applicant')
    ref  = member.get('_id', '')[:8].upper()
    content = f"""
    <p style="color:#495057;">Dear <strong>{name}</strong>,</p>
    <p>Thank you for applying for <strong>Primary Membership</strong> with the All India Students Union (AISU).</p>
    <div style="background:#fff8f0;border-left:4px solid #ff6f0f;padding:16px;border-radius:4px;margin:20px 0;">
      <strong>Application Reference:</strong> {ref}<br>
      <strong>Submitted On:</strong> {datetime.now().strftime('%d %B %Y, %I:%M %p')}<br>
      <strong>Status:</strong> Pending Review
    </div>
    <p>Your application will be reviewed by the National Officers. Upon approval, your unique AISU Member ID and login credentials will be sent to this email address.</p>
    <p style="color:#6c757d;font-size:13px;">Please do not reply to this email. For queries, contact us at aisu4india@gmail.com</p>"""
    # Send to applicant
    _send([member['email']], 'Primary Membership Application Received — AISU', _base_template('Application Received', content))
    # Notify national team
    cc_body = f"""
    <p>A new <strong>Primary Membership</strong> application has been received.</p>
    <table style="border-collapse:collapse;width:100%;">
      <tr><td style="padding:8px;border:1px solid #dee2e6;background:#f8f9fa;"><strong>Name</strong></td><td style="padding:8px;border:1px solid #dee2e6;">{name}</td></tr>
      <tr><td style="padding:8px;border:1px solid #dee2e6;background:#f8f9fa;"><strong>Email</strong></td><td style="padding:8px;border:1px solid #dee2e6;">{member.get('email')}</td></tr>
      <tr><td style="padding:8px;border:1px solid #dee2e6;background:#f8f9fa;"><strong>Mobile</strong></td><td style="padding:8px;border:1px solid #dee2e6;">{member.get('mobile')}</td></tr>
      <tr><td style="padding:8px;border:1px solid #dee2e6;background:#f8f9fa;"><strong>State</strong></td><td style="padding:8px;border:1px solid #dee2e6;">{member.get('state')}</td></tr>
      <tr><td style="padding:8px;border:1px solid #dee2e6;background:#f8f9fa;"><strong>Institution</strong></td><td style="padding:8px;border:1px solid #dee2e6;">{member.get('institution')}</td></tr>
      <tr><td style="padding:8px;border:1px solid #dee2e6;background:#f8f9fa;"><strong>Ref</strong></td><td style="padding:8px;border:1px solid #dee2e6;">{ref}</td></tr>
    </table>
    <p style="margin-top:20px;">Please log in to the Admin Portal to review and approve/reject this application.</p>"""
    national_list = [NATIONAL_EMAILS['president'], NATIONAL_EMAILS['vice_president'], NATIONAL_EMAILS['gen_secretary']]
    _send(national_list, f'New Primary Membership Application — {name}', _base_template('New Application Received', cc_body))

def send_primary_approved(member, default_password):
    content = f"""
    <p>Dear <strong>{member.get('fullname')}</strong>,</p>
    <p>Congratulations! Your <strong>Primary Membership</strong> application has been <span style="color:#28a745;font-weight:bold;">APPROVED</span>.</p>
    <div style="background:#f0fff4;border:2px solid #28a745;border-radius:8px;padding:24px;margin:20px 0;text-align:center;">
      <p style="font-size:13px;color:#6c757d;margin:0 0 8px;">Your AISU Member ID</p>
      <p style="font-size:28px;font-weight:bold;color:#ff6f0f;letter-spacing:3px;margin:0;">{member.get('member_id')}</p>
    </div>
    <p><strong>Login Credentials:</strong></p>
    <table style="border-collapse:collapse;width:100%;margin:16px 0;">
      <tr><td style="padding:8px 12px;background:#f8f9fa;border:1px solid #dee2e6;"><strong>Login URL</strong></td><td style="padding:8px 12px;border:1px solid #dee2e6;"><a href="https://aisu4india.in/login.html">aisu4india.in/login.html</a></td></tr>
      <tr><td style="padding:8px 12px;background:#f8f9fa;border:1px solid #dee2e6;"><strong>Email</strong></td><td style="padding:8px 12px;border:1px solid #dee2e6;">{member.get('email')}</td></tr>
      <tr><td style="padding:8px 12px;background:#f8f9fa;border:1px solid #dee2e6;"><strong>Password</strong></td><td style="padding:8px 12px;border:1px solid #dee2e6;">{default_password}</td></tr>
      <tr><td style="padding:8px 12px;background:#f8f9fa;border:1px solid #dee2e6;"><strong>Designation</strong></td><td style="padding:8px 12px;border:1px solid #dee2e6;">{member.get('designation', 'Primary Member')}</td></tr>
    </table>
    <p style="color:#dc3545;font-size:13px;"><strong>Important:</strong> Please change your password after first login. Your membership is valid for 3 years.</p>"""
    _send([member['email']], 'Primary Membership Approved — Welcome to AISU!', _base_template('Membership Approved', content))

def send_student_application_received(student):
    name = student.get('fullname', 'Student')
    ref  = student.get('_id', '')[:8].upper()
    content = f"""
    <p>Dear <strong>{name}</strong>,</p>
    <p>Thank you for applying for <strong>Student Membership</strong> with AISU.</p>
    <div style="background:#fff8f0;border-left:4px solid #ff6f0f;padding:16px;border-radius:4px;margin:20px 0;">
      <strong>Reference:</strong> {ref}<br>
      <strong>Status:</strong> Under Review
    </div>
    <p>Upon approval, your unique Student ID and login credentials will be emailed to you.</p>"""
    _send([student['email']], 'Student Membership Application Received — AISU', _base_template('Application Received', content))
    # Notify national team + state president
    national_list = [NATIONAL_EMAILS['president'], NATIONAL_EMAILS['vice_president'],
                     NATIONAL_EMAILS['gen_secretary'], NATIONAL_EMAILS['joint_secretary']]
    notify_body = f"<p>New student membership application from <strong>{name}</strong> ({student.get('email')}) — State: {student.get('state')} — Institution: {student.get('institution')}.</p><p>Ref: {ref}</p>"
    _send(national_list, f'New Student Membership — {name}', _base_template('New Student Application', notify_body))

def send_student_approved(student, default_password):
    content = f"""
    <p>Dear <strong>{student.get('fullname')}</strong>,</p>
    <p>Your <strong>Student Membership</strong> has been <span style="color:#28a745;font-weight:bold;">APPROVED</span>!</p>
    <div style="background:#f0fff4;border:2px solid #28a745;border-radius:8px;padding:24px;margin:20px 0;text-align:center;">
      <p style="font-size:13px;color:#6c757d;margin:0 0 8px;">Your AISU Student ID</p>
      <p style="font-size:26px;font-weight:bold;color:#ff6f0f;letter-spacing:2px;margin:0;">{student.get('student_id')}</p>
    </div>
    <p>Login: <a href="https://aisu4india.in/login.html">aisu4india.in/login.html</a> &mdash; Email: {student.get('email')} &mdash; Password: {default_password}</p>
    <p>You have <strong>free access to all competitions for 1 year</strong> from today.</p>"""
    _send([student['email']], 'Student Membership Approved — AISU', _base_template('Welcome to AISU!', content))

def send_complaint_update(complaint, action_taken, updater_name):
    if complaint.get('is_anonymous'):
        return
    content = f"""
    <p>Dear Complainant,</p>
    <p>An update has been recorded for your complaint:</p>
    <div style="background:#f8f9fa;border-left:4px solid #ff6f0f;padding:16px;border-radius:4px;margin:20px 0;">
      <strong>Complaint ID:</strong> {complaint.get('complaint_id')}<br>
      <strong>Category:</strong> {complaint.get('category')}<br>
      <strong>New Status:</strong> {complaint.get('status', '').title()}<br>
      <strong>Action Taken By:</strong> {updater_name}<br>
      <strong>Details:</strong> {action_taken}
    </div>
    <p>To track your complaint, visit the <a href="https://aisu4india.in/complaint.html">Complaint Portal</a> and enter your Complaint ID.</p>"""
    _send([complaint['email']], f'Complaint Update — {complaint.get("complaint_id")}', _base_template('Complaint Status Update', content))

def send_complaint_disposed(complaint):
    if complaint.get('is_anonymous'):
        return
    content = f"""
    <p>Dear Complainant,</p>
    <p>Your complaint has been <span style="color:#28a745;font-weight:bold;">DISPOSED / RESOLVED</span>.</p>
    <div style="background:#f0fff4;border:1px solid #28a745;padding:16px;border-radius:4px;margin:20px 0;">
      <strong>Complaint ID:</strong> {complaint.get('complaint_id')}<br>
      <strong>Resolution:</strong> {complaint.get('resolution', 'Matter resolved.')}<br>
      <strong>Category:</strong> {complaint.get('category')}
    </div>
    <p>Thank you for bringing this matter to AISU's attention. Your complaint record has been archived for documentation.</p>"""
    _send([complaint['email']], f'Complaint Resolved — {complaint.get("complaint_id")}', _base_template('Complaint Disposed', content))

def send_affiliation_received(affiliation):
    content = f"""
    <p>Dear <strong>{affiliation.get('contact_name')}</strong>,</p>
    <p>We have received your affiliation application for <strong>{affiliation.get('org_name')}</strong>.</p>
    <div style="background:#fff8f0;border-left:4px solid #ff6f0f;padding:16px;border-radius:4px;margin:20px 0;">
      <strong>Reference Number:</strong> {affiliation.get('affiliation_id', affiliation.get('_id', '')[:8].upper())}<br>
      <strong>Status:</strong> Under Review by National Team
    </div>
    <p>Upon approval, an official confirmation will be sent to this email address.</p>"""
    _send([affiliation['email']], 'Affiliation Application Received — AISU/FIYA', _base_template('Application Received', content))

def send_affiliation_approved(affiliation):
    content = f"""
    <p>Dear <strong>{affiliation.get('contact_name')}</strong>,</p>
    <p>Congratulations! The affiliation request for <strong>{affiliation.get('org_name')}</strong> has been <span style="color:#28a745;font-weight:bold;">APPROVED</span>.</p>
    <div style="background:#f0fff4;border:2px solid #28a745;border-radius:8px;padding:24px;margin:20px 0;text-align:center;">
      <p style="font-size:13px;color:#6c757d;margin:0 0 8px;">Your Affiliation Registration Number</p>
      <p style="font-size:24px;font-weight:bold;color:#ff6f0f;letter-spacing:2px;margin:0;">{affiliation.get('affiliation_id')}</p>
    </div>"""
    _send([affiliation['email']], 'Organization Affiliation Approved — FIYA/AISU', _base_template('Affiliation Approved', content))

def send_certificate_issued(email, name, cert_id, program_or_type, event=None):
    content = f"""
    <p>Dear <strong>{name}</strong>,</p>
    <p>Your certificate has been issued for <strong>{program_or_type}</strong>.</p>
    <div style="background:#f0fff4;border:2px solid #28a745;border-radius:8px;padding:24px;margin:20px 0;text-align:center;">
      <p style="font-size:13px;color:#6c757d;margin:0 0 8px;">Certificate Number</p>
      <p style="font-size:20px;font-weight:bold;color:#ff6f0f;letter-spacing:2px;margin:0;">{cert_id}</p>
    </div>
    <p>To download your certificate, log in to your account at <a href="https://aisu4india.in/login.html">aisu4india.in</a> and visit <strong>My Certificates</strong>.</p>
    <p>To verify this certificate, visit <a href="https://aisu4india.in/cert-verify.html">our verification page</a> and enter the certificate number above.</p>"""
    _send([email], f'Certificate Issued — {cert_type}', _base_template('Your Certificate is Ready', content))

def send_renewal_reminder(member, days_left, member_type='primary'):
    validity = '3 years' if member_type == 'primary' else '1 year'
    content = f"""
    <p>Dear <strong>{member.get('fullname') or member.get('name', 'Member')}</strong>,</p>
    <p>Your AISU {member_type.title()} Membership expires in <strong>{days_left} days</strong>.</p>
    <div style="background:#fff3cd;border-left:4px solid #ffc107;padding:16px;border-radius:4px;margin:20px 0;">
      <strong>Member ID:</strong> {member.get('member_id') or member.get('student_id', '')}<br>
      <strong>Membership Type:</strong> {member_type.title()}<br>
      <strong>Validity Period:</strong> {validity}<br>
      <strong>Action Required:</strong> Renew before expiry to avoid service interruption
    </div>
    <p>Please log in to your account to initiate the renewal process.</p>"""
    _send([member['email']], f'AISU Membership Renewal Due in {days_left} Days', _base_template('Renewal Reminder', content))

def send_new_competition_notification(competition, recipients):
    """Broadcast email to all student members + past participants."""
    content = f"""
    <p>A new competition has been launched on the AISU Competition Portal!</p>
    <div style="background:#fff8f0;border-left:4px solid #ff6f0f;padding:20px;border-radius:4px;margin:20px 0;">
      <h3 style="margin:0 0 12px;color:#1a2f45;">{competition.get('title')}</h3>
      <strong>Category:</strong> {competition.get('category')}<br>
      <strong>Last Date:</strong> {competition.get('last_date', 'TBA')}<br>
      <strong>Type:</strong> {competition.get('comp_type', 'General')}
    </div>
    <p>{competition.get('description', '')}</p>
    <p style="text-align:center;margin:24px 0;">
      <a href="https://aisu4india.in/competition.html" 
         style="background:#ff6f0f;color:#fff;padding:12px 28px;border-radius:6px;text-decoration:none;font-weight:bold;">
         Register Now
      </a>
    </p>"""
    _send(recipients, f'New Competition: {competition.get("title")} — AISU', _base_template('New Competition Launched!', content))

def send_generic(email, name, subject, html_content):
    """General-purpose email sender for any custom notification."""
    content = f"""
    <p>Dear <strong>{name}</strong>,</p>
    {html_content}
    <p style="color:#6c757d;font-size:12px;margin-top:24px;">
    If you have questions, contact us at aisu4india@gmail.com or +91 80748 53717.
    </p>"""
    _send([email], subject, _base_template(subject, content))

def send_competition_broadcast(competition, recipients):
    """Broadcast to student members + all past participants."""
    send_new_competition_notification(competition, recipients)
