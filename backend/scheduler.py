# scheduler.py — Background renewal check jobs
from apscheduler.schedulers.background import BackgroundScheduler
import db
from email_service import send_renewal_reminder
import logging

log = logging.getLogger(__name__)
scheduler = BackgroundScheduler()

def check_primary_renewals():
    """Daily job: send reminders at 30, 7, 1 day before expiry."""
    members = db.find_all('primary_members')
    for m in members:
        if m.get('status') != 'approved': continue
        days = db.days_until_expiry(m.get('approved_at', m.get('created_at', '')), 3)
        if days in (30, 7, 1):
            send_renewal_reminder(m, days, 'primary')
            log.info(f'Renewal reminder sent to primary member {m.get("member_id")} ({days} days)')
        elif days is not None and days <= 0 and m.get('status') != 'expired':
            db.update_one('primary_members', m['_id'], {'status': 'expired'})
            log.info(f'Primary member {m.get("member_id")} marked expired')

def check_student_renewals():
    """Daily job: remind students 30, 7, 1 day before 1-year expiry."""
    students = db.find_all('student_members')
    for s in students:
        if s.get('status') != 'approved': continue
        days = db.days_until_expiry(s.get('approved_at', s.get('created_at', '')), 1)
        if days in (30, 7, 1):
            send_renewal_reminder(s, days, 'student')
            log.info(f'Renewal reminder sent to student {s.get("student_id")} ({days} days)')
        elif days is not None and days <= 0 and s.get('status') != 'expired':
            db.update_one('student_members', s['_id'], {
                'status'          : 'expired',
                'competition_paid': True,   # must pay per-competition now
            })

def init_scheduler():
    scheduler.add_job(check_primary_renewals, 'cron', hour=6, minute=0, id='primary_renewal')
    scheduler.add_job(check_student_renewals, 'cron', hour=6, minute=30, id='student_renewal')
    scheduler.start()
    log.info('Scheduler started: renewal checks at 06:00 and 06:30 UTC daily')
