# Course Enrollment Request System - Implementation Summary

## Overview

A complete course enrollment request system has been implemented that allows students to browse available courses and submit enrollment requests that require admin approval before enrollment.

## Features Implemented

### 1. Backend Management

#### Model: `course.enrollment.request`
- **Location**: `custom_addons/grants_training_suite_v19/models/course_enrollment_request.py`
- **Fields**:
  - `name`: Auto-generated sequence (ENR00001, ENR00002, etc.)
  - `student_id`: Link to gr.student
  - `course_integration_id`: Link to course
  - `state`: draft/pending/approved/rejected
  - `notes`: Student's motivation for enrollment
  - `admin_notes`: Internal admin notes
  - `rejection_reason`: Shown to student if rejected
  - `approved_by`, `approved_date`: Approval tracking
  - `session_id`: Link to created course session

#### Workflow States
1. **Draft**: Initial state when created
2. **Pending**: After student submits request
3. **Approved**: Admin approves, course session auto-created
4. **Rejected**: Admin rejects with reason

#### Backend Views
- **Form View**: Full workflow with statusbar, approval/rejection buttons
- **List View**: Overview of all requests with color-coded status
- **Kanban View**: Visual board grouped by status
- **Search View**: Filters by status, group by student/course/date

#### Menu Structure
```
Grants Training
└── Student Management
    └── Enrollment Requests
        ├── All Requests
        ├── Pending Requests
        └── Approved Requests
```

### 2. Security & Access Control

#### Access Rights (`ir.model.access.csv`)
- **Public**: Read only
- **Portal Users**: Create and read own requests
- **Internal Users**: Read all
- **Agents**: Full access (CRUD)
- **Managers**: Full access (CRUD)

#### Record Rules (`portal_security_rules.xml`)
- Portal users can only see their own enrollment requests
- Managers and Agents can see all requests
- Security domain: `[('student_id.email', '=', user.email)]` for portal

### 3. Portal Features

#### Available Routes

##### `/my/available-courses` (Authenticated)
- Shows all active courses
- Excludes courses student is already enrolled in
- Displays "Request Enrollment" button or "Request Pending" badge
- Filters out courses with pending/approved requests

##### `/my/courses/request/<course_id>` (Authenticated)
- Enrollment request form
- Validates:
  - Student not already enrolled
  - No existing pending request
  - Course is active
- Allows student to add motivation notes

##### `/my/courses/request/submit` (POST)
- Handles form submission
- Creates enrollment request
- Auto-submits to pending state
- Sends notification email to admins
- Shows success/error page

##### `/my/enrollment-requests` (Authenticated)
- Lists all student's enrollment requests
- Color-coded status badges
- Shows rejection reason (if rejected)
- Link to view session (if approved)
- Bootstrap popovers for additional info

##### Updated `/my/student` (Dashboard)
- Shows pending enrollment requests count with badge
- Displays top 3 recommended courses
- Alert banner for pending requests
- Quick action buttons for browsing and requests

#### Public Course Catalog Updates

##### `/grants/courses/catalog`
- Added "Request Enrollment" button to each course card
- Requires login to access enrollment request

##### `/grants/courses/<course_id>`
- Prominent "Request Enrollment" button
- Updated call-to-action sidebar
- Links to new student registration

### 4. Email Notifications

#### Three Email Templates Created

##### 1. Request Submitted (Admin Notification)
- **ID**: `email_template_enrollment_request_submitted`
- **Sent to**: All managers and agents
- **Trigger**: When student submits request
- **Contains**: Student info, course, request notes, link to review

##### 2. Request Approved (Student Notification)
- **ID**: `email_template_enrollment_request_approved`
- **Sent to**: Student email
- **Trigger**: When admin approves request
- **Contains**: Approval confirmation, session details, portal link

##### 3. Request Rejected (Student Notification)
- **ID**: `email_template_enrollment_request_rejected`
- **Sent to**: Student email
- **Trigger**: When admin rejects request
- **Contains**: Rejection reason, alternative options, browse courses link

### 5. Auto-Session Creation

When an enrollment request is approved:
1. Creates `gr.course.session` record
2. Sets session date to next Monday at 9:00 AM
3. Links session to student and course
4. Sets state to 'scheduled'
5. Stores reference in enrollment request
6. Sends approval email with session details

## User Workflows

### Student Workflow

1. **Browse Courses**
   - Visit `/grants/courses/catalog` (public) or `/my/available-courses` (authenticated)
   - View course details

2. **Request Enrollment**
   - Click "Request Enrollment" button
   - Fill out motivation notes (optional)
   - Submit request

3. **Track Request**
   - View status in `/my/enrollment-requests`
   - Check dashboard for pending count
   - Receive email notifications

4. **Access Course** (After Approval)
   - Receive approval email
   - View session in `/my/courses`
   - Start learning

### Admin Workflow

1. **Receive Notification**
   - Email notification when new request submitted
   - View in "Pending Requests" menu

2. **Review Request**
   - Open enrollment request form
   - Review student info and motivation
   - Check course availability
   - Add admin notes

3. **Approve or Reject**
   - **Approve**: Click "Approve" button
     - System auto-creates course session
     - Student receives approval email
   - **Reject**: Add rejection reason → Click "Reject"
     - Student receives rejection email with reason

4. **Track History**
   - View all requests in "All Requests"
   - Filter by status
   - Monitor enrollment patterns

## Technical Details

### Database Sequence
- **Code**: `course.enrollment.request`
- **Prefix**: ENR
- **Padding**: 5 digits
- **Example**: ENR00001, ENR00002

### Dependencies
- `grants_training_suite_v19` (base module)
- `portal` (portal functionality)
- `website` (public pages)
- `mail` (chatter and email)

### Files Created/Modified

#### New Files
1. `models/course_enrollment_request.py` - Main model
2. `views/course_enrollment_request_views.xml` - Backend views
3. Portal templates in `views/portal/portal_templates.xml`:
   - `portal_available_courses`
   - `portal_enrollment_request_form`
   - `portal_enrollment_request_success`
   - `portal_enrollment_request_error`
   - `portal_my_enrollment_requests`

#### Modified Files
1. `models/__init__.py` - Added import
2. `data/sequence.xml` - Added sequence
3. `data/email_templates.xml` - Added 3 email templates
4. `security/ir.model.access.csv` - Added access rights
5. `security/portal_security_rules.xml` - Added record rules
6. `controllers/student_portal.py` - Added 5 new routes
7. `views/portal/portal_templates.xml` - Updated dashboard, catalog, detail pages
8. `__manifest__.py` - Added new views file

## Testing Checklist

### Backend Testing
- [ ] Install/upgrade module successfully
- [ ] View enrollment requests menu
- [ ] Create manual enrollment request
- [ ] Submit request (draft → pending)
- [ ] Approve request (creates session)
- [ ] Reject request (with reason)
- [ ] Check email templates render correctly
- [ ] Verify security rules (portal user can't see others' requests)

### Portal Testing
- [ ] Browse available courses at `/my/available-courses`
- [ ] Submit enrollment request
- [ ] View request in `/my/enrollment-requests`
- [ ] Check dashboard shows pending count
- [ ] Verify "Request Enrollment" buttons on catalog
- [ ] Test duplicate request prevention
- [ ] Test already-enrolled prevention
- [ ] Receive approval/rejection emails

### Integration Testing
- [ ] Approved request creates course session
- [ ] Session appears in `/my/courses`
- [ ] Student can access session details
- [ ] Admin notifications sent correctly
- [ ] Email links work properly

## Configuration

### Required Setup
1. Ensure `grants_training_suite_v19` module is installed
2. Create at least one active course integration
3. Have at least one student record
4. Configure email server for notifications
5. Assign users to Manager or Agent groups

### Optional Configuration
- Customize email templates in Settings > Technical > Email Templates
- Adjust session default date logic in `_create_course_session` method
- Modify approval workflow if needed

## Future Enhancements (Potential)

1. **Bulk Actions**: Approve/reject multiple requests at once
2. **Prerequisites**: Check if student meets course prerequisites
3. **Capacity Management**: Limit enrollments per course
4. **Waitlist**: Auto-approve from waitlist when spots open
5. **Payment Integration**: Require payment before approval
6. **Calendar Integration**: Sync session dates with calendar
7. **SMS Notifications**: Send SMS in addition to email
8. **Student Comments**: Allow students to add comments after submission
9. **Approval Workflow**: Multi-level approval (agent → manager)
10. **Analytics Dashboard**: Track enrollment request metrics

## Support & Troubleshooting

### Common Issues

#### Issue: "Request Enrollment" button requires login
**Solution**: This is by design. Students must be logged in to request enrollment.

#### Issue: Can't see enrollment requests in backend
**Solution**: Check user groups. Only Agents and Managers can see all requests.

#### Issue: Session not created after approval
**Solution**: Check logs for errors. Ensure course integration is properly configured.

#### Issue: Email notifications not sent
**Solution**: Verify email server configuration in Settings > Technical > Parameters.

### Debug Mode
Enable developer mode to:
- View technical field names
- Access debug information
- Check email queue
- View server logs

## Repository Status

All changes have been committed and pushed to:
- Repository: `https://github.com/sabryyoussef/new_kafaat`
- Branch: `master`
- Commits:
  - Part 1: Backend model, views, security
  - Part 2: Portal routes, templates, dashboard updates

## Conclusion

The Course Enrollment Request System is now fully implemented and ready for use. Students can browse courses and submit enrollment requests through an intuitive portal interface, while admins can efficiently review and process requests through the backend. The system includes proper security, email notifications, and automatic session creation upon approval.

All planned features have been completed successfully!

