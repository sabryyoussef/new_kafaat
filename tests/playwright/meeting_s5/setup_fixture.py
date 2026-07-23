#!/usr/bin/env python3
"""Prepare sabry-test fixture for S5 Playwright (batch + session + portal students).

Option A: creates a controlled active op.session for UAT — not production auto-create.
"""
import xmlrpc.client
from datetime import date, datetime, timedelta, timezone

URL = 'http://127.0.0.1:8069'
DB = 'sabry-test'
PWD = 'admin'
uid = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common').authenticate(DB, 'admin', PWD, {})
m = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object', allow_none=True)


def kw(model, method, args=None, kwargs=None):
    return m.execute_kw(DB, uid, PWD, model, method, args or [], kwargs or {})


course_ids = kw('op.course', 'search', [[]], {'limit': 1})
if not course_ids:
    raise SystemExit('No op.course found')
course_id = course_ids[0]

batch_ids = kw('op.batch', 'search', [[['code', '=', 'S5PW1']]], {'limit': 1})
if batch_ids:
    batch_id = batch_ids[0]
else:
    batch_id = kw('op.batch', 'create', [{
        'name': 'S5 PW Batch',
        'code': 'S5PW1',
        'course_id': course_id,
        'start_date': str(date.today()),
        'end_date': str(date.today() + timedelta(days=120)),
    }])

kw('op.batch', 'action_generate_qr', [[batch_id]])
batch = kw('op.batch', 'read', [[batch_id]], {
    'fields': ['attendance_qr_token', 'attendance_qr_url', 'name'],
})[0]
token = batch['attendance_qr_token']


def get_xmlid(module, name):
    data = kw(
        'ir.model.data', 'search_read',
        [[['module', '=', module], ['name', '=', name]]],
        {'fields': ['res_id'], 'limit': 1},
    )
    return data[0]['res_id']


portal_gid = get_xmlid('base', 'group_portal')
country_id = get_xmlid('base', 'sa')
program_ids = kw('op.program', 'search', [[]], {'limit': 1})

subject_ids = kw('op.subject', 'search', [[]], {'limit': 1})
if not subject_ids:
    subject_ids = [kw('op.subject', 'create', [{
        'name': 'S5 PW Subject',
        'code': 'S5PWSUB',
        'type': 'theory',
        'subject_type': 'compulsory',
    }])]
faculty_ids = kw('op.faculty', 'search', [[]], {'limit': 1})
if not faculty_ids:
    f_partner = kw('res.partner', 'create', [{'name': 'S5 PW Faculty'}])
    faculty_ids = [kw('op.faculty', 'create', [{
        'partner_id': f_partner,
        'first_name': 'S5',
        'last_name': 'Faculty',
        'birth_date': '1980-01-01',
        'gender': 'male',
    }])]

now = datetime.now(timezone.utc).replace(tzinfo=None)
start = now - timedelta(minutes=5)
end = now + timedelta(minutes=90)
old_sessions = kw('op.session', 'search', [[
    ['batch_id', '=', batch_id],
    ['state', '!=', 'cancel'],
]])
if old_sessions:
    kw('op.session', 'write', [old_sessions, {'state': 'cancel'}])

session_id = kw('op.session', 'create', [{
    'batch_id': batch_id,
    'course_id': course_id,
    'subject_id': subject_ids[0],
    'faculty_id': faculty_ids[0],
    'start_datetime': start.strftime('%Y-%m-%d %H:%M:%S'),
    'end_datetime': end.strftime('%Y-%m-%d %H:%M:%S'),
    'state': 'confirm',
}])


def ensure_portal_student(login, id_number, enroll=False):
    users = kw('res.users', 'search', [[['login', '=', login]]], {'limit': 1})
    partners = kw('res.partner', 'search', [[['email', '=', login]]], {'limit': 1})
    if partners:
        partner_id = partners[0]
    else:
        partner_id = kw('res.partner', 'create', [{
            'name': login,
            'email': login,
        }])
    if users:
        user_id = users[0]
        kw('res.users', 'write', [[user_id], {'password': 'S5Portal!23'}])
    else:
        user_id = kw('res.users', 'create', [{
            'name': login.split('@')[0],
            'login': login,
            'email': login,
            'partner_id': partner_id,
            'password': 'S5Portal!23',
            'group_ids': [(6, 0, [portal_gid])],
        }])

    students = kw('op.student', 'search', [[['email', '=', login]]], {'limit': 1})
    vals = {
        'name': login.split('@')[0],
        'name_english': login.split('@')[0],
        'name_arabic': 'متدرب S5',
        'first_name': 'S5',
        'last_name': login.split('@')[0],
        'partner_id': partner_id,
        'email': login,
        'phone': '0501234567',
        'street': 'Street',
        'city': 'Riyadh',
        'country_id': country_id,
        'birth_date': '2000-01-01',
        'gender': 'm',
        'id_number': id_number,
        'user_id': user_id,
    }
    if program_ids:
        vals['specialization_id'] = program_ids[0]
    if students:
        student_id = students[0]
        kw('op.student', 'write', [[student_id], vals])
    else:
        student_id = kw('op.student', 'create', [vals])

    if enroll:
        existing = kw('op.student.course', 'search', [[
            ['student_id', '=', student_id],
            ['batch_id', '=', batch_id],
        ]], {'limit': 1})
        if not existing:
            kw('op.student.course', 'create', [{
                'student_id': student_id,
                'course_id': course_id,
                'batch_id': batch_id,
                'state': 'running',
                'roll_number': id_number[-4:],
            }])
    return student_id, user_id


sid, uid_s = ensure_portal_student('s5.pw.student@test.local', '358PW00001', enroll=True)
oid, uid_o = ensure_portal_student('s5.pw.other@test.local', '358PW00002', enroll=False)

env_path = '/opt/new_kafaat/tests/playwright/meeting_s5/.s5_env'
with open(env_path, 'w') as f:
    f.write(f'S5_BATCH_ID={batch_id}\n')
    f.write(f'S5_TOKEN={token}\n')
    f.write(f'S5_SESSION_ID={session_id}\n')
    f.write('S5_PORTAL_LOGIN=s5.pw.student@test.local\n')
    f.write('S5_PORTAL_PASSWORD=S5Portal!23\n')
    f.write('S5_OTHER_LOGIN=s5.pw.other@test.local\n')
    f.write('S5_OTHER_PASSWORD=S5Portal!23\n')

print('batch_id', batch_id)
print('session_id', session_id)
print('token', token)
print('url', batch['attendance_qr_url'])
print('student', sid, 'other', oid)
print('wrote', env_path)
print('NOTE: Option A UAT session created for sabry-test only — do not auto-create on TR_K19')
