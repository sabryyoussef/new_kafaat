# Portal Endpoints Documentation

Complete reference for all student portal routes across the Kafaat training platform.

---

## Table of Contents

1. [Public Routes (No Login Required)](#public-routes)
2. [Student Enrollment Portal](#student-enrollment-portal)
3. [Student Dashboard & Courses](#student-dashboard--courses)
4. [Document Management](#document-management)
5. [Course Enrollment Requests](#course-enrollment-requests)
6. [Certificates](#certificates)
7. [Authentication](#authentication)

---

## Public Routes

### Course Catalog
Browse available courses without logging in.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/grants/courses/catalog` | GET | Public course catalog page |
| `/grants/courses/<int:course_id>` | GET | Public course detail page |

**Example**:
```
http://localhost:10020/grants/courses/catalog
http://localhost:10020/grants/courses/123
```

---

## Student Enrollment Portal

### Registration (No Login Required)
New students can register for training programs.

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/student/register` | GET | Public | Display registration form |
| `/student/register` | GET | Public | Pre-select course: `?course_id=123` |
| `/student/register/submit` | POST | Public | Submit registration form |
| `/student/register/success` | GET | Public | Registration success page |

**Registration Form Fields**:
- Student Name (English) *required*
- Student Name (Arabic) *required*
- Email *required*
- Phone *required*
- Birth Date *required*
- Gender *required*
- Nationality *required*
- English Level *required*
- Native Language
- Has Previous Certificate (checkbox)
- Certificate Type
- Requested Courses
- Documents (file upload)

**Example**:
```
# Registration form
http://localhost:10020/student/register

# Pre-select a course
http://localhost:10020/student/register?course_id=5

# Success page
http://localhost:10020/student/register/success?reg=REG-00001
```

---

### View Registration Status (Login Required)
Track your registration application status.

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/my/registration` | GET | User | View your registration status |
| `/my/registration/<int:reg_id>` | GET | User | View specific registration |
| `/my/registration/<int:reg_id>/upload` | POST | User | Upload additional documents |

**Registration States**:
- `draft` - New Registration
- `submitted` - Submitted
- `eligibility_review` - Under Eligibility Review
- `document_review` - Under Document Review
- `approved` - Approved
- `rejected` - Rejected
- `enrolled` - Enrolled (Student Record Created)

**Example**:
```
http://localhost:10020/my/registration
http://localhost:10020/my/registration/5
```

---

## Student Dashboard & Courses

### Dashboard
Main dashboard for enrolled students.

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/my/student` | GET | User | Student dashboard (overview) |
| `/my/enrollments` | GET | User | Detailed enrollment tracking |

**Dashboard Includes**:
- Student information
- Enrolled courses
- Progress percentage
- Certificates
- Pending enrollment requests
- Available courses (top 3)

**Example**:
```
http://localhost:10020/my/student
http://localhost:10020/my/enrollments
```

---

### Course Management
View and manage enrolled courses.

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/my/courses` | GET | User | List of enrolled courses |
| `/my/courses/<int:session_id>` | GET | User | Course session detail page |

**Course Session Details Include**:
- Course name and description
- Progress tracking
- Assignments
- Grades
- Session status

**Example**:
```
http://localhost:10020/my/courses
http://localhost:10020/my/courses/42
```

---

## Document Management

### Student Document Portal
Manage document requests and uploads.

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/my/documents` | GET | User | List all document requests |
| `/my/documents/new` | GET | User | Show new document request form |
| `/my/documents/new` | POST | User | Create new document request |
| `/my/documents/<int:request_id>` | GET | User | View document request detail |

**Document Request Types**:
- `upload` - Student uploads a document
- `request` - Student requests a document from academy

**Document Types**:
- National ID / Iqama
- Passport
- Birth Certificate
- Educational Certificate
- Training Certificate
- Transcript
- Other

**Document Request States**:
- `draft` - Draft
- `submitted` - Submitted
- `under_review` - Under Review
- `completed` - Completed
- `rejected` - Rejected

**Example**:
```
http://localhost:10020/my/documents
http://localhost:10020/my/documents/new
http://localhost:10020/my/documents/15
```

**Document Upload**:
```html
<!-- Form for uploading document -->
<form action="/my/documents/new" method="post" enctype="multipart/form-data">
    <input type="hidden" name="csrf_token" value="..."/>
    <select name="request_type">
        <option value="upload">Upload Document</option>
        <option value="request">Request Document</option>
    </select>
    <select name="document_type">
        <option value="national_id">National ID</option>
        <option value="certificate">Certificate</option>
        <!-- ... -->
    </select>
    <textarea name="description"></textarea>
    <input type="file" name="file"/>
    <button type="submit">Submit</button>
</form>
```

---

## Course Enrollment Requests

### Browse & Request Enrollment
Students can browse available courses and request enrollment.

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/my/available-courses` | GET | User | Browse courses available for enrollment |
| `/my/courses/request/<int:course_id>` | GET | User | Enrollment request form |
| `/my/courses/request/submit` | POST | User | Submit enrollment request |
| `/my/enrollment-requests` | GET | User | View all your enrollment requests |

**Enrollment Request Flow**:
1. Student browses available courses (`/my/available-courses`)
2. Clicks "Request Enrollment" on a course
3. Fills out request form (`/my/courses/request/123`)
4. Submits request (creates pending request)
5. Admin reviews and approves/rejects
6. Upon approval, student is enrolled in course

**Enrollment Request States**:
- `draft` - Draft
- `pending` - Pending Admin Review
- `approved` - Approved (Student Enrolled)
- `rejected` - Rejected

**Example**:
```
http://localhost:10020/my/available-courses
http://localhost:10020/my/courses/request/8
http://localhost:10020/my/enrollment-requests
```

**Enrollment Request Form**:
```html
<form action="/my/courses/request/submit" method="post">
    <input type="hidden" name="course_id" value="8"/>
    <textarea name="notes" placeholder="Why do you want to enroll?"></textarea>
    <button type="submit">Submit Request</button>
</form>
```

---

## Certificates

### View & Download Certificates
Access your earned certificates.

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/my/certificates` | GET | User | List of all certificates |
| `/my/certificates/<int:cert_id>/download` | GET | User | Download certificate PDF |

**Certificate Information Includes**:
- Certificate name
- Issue date
- Course name
- Certificate number
- Download link

**Example**:
```
http://localhost:10020/my/certificates
http://localhost:10020/my/certificates/7/download
```

---

## Authentication

### Login & Access
Portal user authentication.

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/grants/login` | GET | Public | Student login (redirects to Odoo login) |
| `/web/login` | GET | Public | Standard Odoo login page |
| `/web/login?redirect=/my/student` | GET | Public | Login with redirect to student dashboard |

**Login Flow**:
1. User visits `/grants/login` or `/web/login`
2. Enters email and password
3. Redirected to `/my/student` (student dashboard)

**Example**:
```
http://localhost:10020/grants/login
http://localhost:10020/web/login?redirect=/my/student
```

---

## Complete Route Summary

### By Module

#### **grants_training_suite_v19** (11 routes)
```
GET  /my/student                              # Dashboard
GET  /my/courses                              # List courses
GET  /my/courses/<int:session_id>            # Course detail
GET  /my/certificates                         # List certificates
GET  /my/certificates/<int:cert_id>/download # Download cert
GET  /my/enrollments                          # Enrollment tracking
GET  /my/available-courses                    # Browse available courses
GET  /my/courses/request/<int:course_id>     # Request enrollment form
POST /my/courses/request/submit              # Submit enrollment request
GET  /my/enrollment-requests                  # View enrollment requests
GET  /grants/login                            # Login redirect
GET  /grants/courses/catalog                  # Public course catalog
GET  /grants/courses/<int:course_id>         # Public course detail
```

#### **student_enrollment_portal** (6 routes)
```
GET  /student/register                        # Registration form
POST /student/register/submit                 # Submit registration
GET  /student/register/success                # Success page
GET  /my/registration                         # View registration status
GET  /my/registration/<int:reg_id>           # Specific registration
POST /my/registration/<int:reg_id>/upload    # Upload documents
```

#### **student_documents_portal** (3 routes)
```
GET  /my/documents                            # List document requests
GET  /my/documents/new                        # New document form
POST /my/documents/new                        # Create document request
GET  /my/documents/<int:request_id>          # Document detail
```

---

## User Journey Examples

### Example 1: New Student Registration
```
1. Visit: http://localhost:10020/student/register
2. Fill registration form
3. Upload documents (ID, certificates)
4. Submit → Redirects to success page
5. Wait for admin approval
6. Receive email with login credentials
7. Login at: http://localhost:10020/grants/login
8. Redirected to: http://localhost:10020/my/student
```

### Example 2: Enrolled Student Requests New Course
```
1. Login: http://localhost:10020/grants/login
2. Dashboard: http://localhost:10020/my/student
3. Browse courses: http://localhost:10020/my/available-courses
4. Click "Request Enrollment" on a course
5. Fill request form: http://localhost:10020/my/courses/request/5
6. Submit request
7. Track status: http://localhost:10020/my/enrollment-requests
8. Upon approval → Course appears in: http://localhost:10020/my/courses
```

### Example 3: Student Uploads Document
```
1. Login: http://localhost:10020/grants/login
2. Documents page: http://localhost:10020/my/documents
3. New request: http://localhost:10020/my/documents/new
4. Select "Upload Document"
5. Choose document type (e.g., "Certificate")
6. Upload file and submit
7. View status: http://localhost:10020/my/documents/12
```

### Example 4: Public User Browses Courses
```
1. Visit: http://localhost:10020/grants/courses/catalog
2. Click on a course
3. View details: http://localhost:10020/grants/courses/8
4. Click "Enroll Now" → Redirects to: http://localhost:10020/student/register?course_id=8
5. Registration form opens with course pre-selected
```

---

## API Testing with cURL

### Register New Student
```bash
curl -X POST http://localhost:10020/student/register/submit \
  -F "student_name_english=John Doe" \
  -F "student_name_arabic=جون دو" \
  -F "email=john@example.com" \
  -F "phone=+1234567890" \
  -F "birth_date=1995-05-15" \
  -F "gender=male" \
  -F "nationality=USA" \
  -F "english_level=advanced" \
  -F "native_language=English" \
  -F "requested_courses=Python Programming, Web Development"
```

### Create Document Request (requires session cookie)
```bash
curl -X POST http://localhost:10020/my/documents/new \
  -H "Cookie: session_id=YOUR_SESSION_ID" \
  -F "request_type=upload" \
  -F "document_type=certificate" \
  -F "description=My Python Certificate" \
  -F "file=@/path/to/certificate.pdf"
```

### Submit Enrollment Request (requires session cookie)
```bash
curl -X POST http://localhost:10020/my/courses/request/submit \
  -H "Cookie: session_id=YOUR_SESSION_ID" \
  -F "course_id=5" \
  -F "notes=I want to improve my programming skills"
```

---

## Response Formats

All routes return HTML templates rendered by Odoo's QWeb engine.

**Success Responses**: Rendered HTML page  
**Error Responses**: Error template with message  
**Redirects**: HTTP 302 with Location header

---

## Security & Access Control

### Public Routes
- No authentication required
- Accessible to anyone
- Examples: `/student/register`, `/grants/courses/catalog`

### User Routes (`auth='user'`)
- Requires portal user login
- Access to student-specific data
- Security checks verify data ownership
- Examples: `/my/student`, `/my/courses`, `/my/documents`

### Security Checks
- Portal users can only view their own data
- Email-based record matching
- Student ID verification
- Document request ownership validation

---

## Error Handling

### Common Errors

| Error | Route | Description |
|-------|-------|-------------|
| 403 Forbidden | Any `/my/*` route | Accessing another user's data |
| 404 Not Found | `/grants/courses/<id>` | Course doesn't exist |
| Validation Error | `/student/register/submit` | Missing required fields |
| No Student | `/my/student` | Portal user not linked to student record |

### Error Templates
- `website.403` - Forbidden access
- `website.404` - Not found
- `grants_training_suite_v19.portal_no_student` - No student record
- Custom error messages in registration/document forms

---

## Development & Testing

### Local Development URLs
```
Base URL: http://localhost:10020
Student Dashboard: http://localhost:10020/my/student
Registration: http://localhost:10020/student/register
Course Catalog: http://localhost:10020/grants/courses/catalog
Documents: http://localhost:10020/my/documents
```

### Production URLs
```
Base URL: https://your-domain.com
Update all examples with your production domain
```

---

## Notes

1. **Session Management**: Odoo handles sessions via cookies
2. **CSRF Protection**: Forms should include CSRF tokens (disabled in some routes with `csrf=False`)
3. **File Uploads**: Use `enctype="multipart/form-data"` for forms with file uploads
4. **Email Notifications**: Automatic emails sent at key stages (registration, approval, etc.)
5. **Multi-language**: Templates support RTL for Arabic content

---

## Version Information

- **Odoo Version**: 19.0
- **Platform**: Kafaat Training Management System
- **Last Updated**: 2025-11-24

---

## Support

For issues or questions:
- **Email**: support@edafa.sa
- **Website**: https://www.edafa.sa
- **GitHub**: Check repository for latest updates

---

## Module Controllers

### Class Names (After Fixes)
- `GrantsStudentPortal` - grants_training_suite_v19
- `StudentEnrollmentPortal` - student_enrollment_portal
- `StudentDocumentsPortal` - student_documents_portal

All classes properly inherit from `CustomerPortal` without conflicts.

---

**End of Documentation**

