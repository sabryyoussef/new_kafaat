# Quick Reference Guide - Kafaat Portal Routes

Quick lookup table for all portal endpoints.

---

## 🚀 Quick Links (localhost:10020)

### For Visitors (No Login)
| What | URL |
|------|-----|
| 📚 Browse Courses | `/grants/courses/catalog` |
| 📝 Register as Student | `/student/register` |
| 🔐 Login | `/grants/login` |

### For Students (Login Required)
| What | URL |
|------|-----|
| 🏠 Dashboard | `/my/student` |
| 📖 My Courses | `/my/courses` |
| 🎓 Certificates | `/my/certificates` |
| 📄 Documents | `/my/documents` |
| ➕ Request Course | `/my/available-courses` |
| 📋 My Requests | `/my/enrollment-requests` |
| 📝 Registration Status | `/my/registration` |

---

## 📋 All Routes by Category

### 🌐 Public Access (No Login)
```
GET  /grants/courses/catalog              Browse courses
GET  /grants/courses/<id>                 Course details
GET  /student/register                    Registration form
GET  /student/register?course_id=<id>    Register with pre-selected course
POST /student/register/submit             Submit registration
GET  /student/register/success            Success page
GET  /grants/login                        Login page
```

### 👤 Student Dashboard
```
GET  /my/student                          Main dashboard
GET  /my/enrollments                      Enrollment tracking
```

### 📚 Courses
```
GET  /my/courses                          List enrolled courses
GET  /my/courses/<session_id>            Course details
GET  /my/available-courses               Browse available courses
GET  /my/courses/request/<course_id>     Request enrollment
POST /my/courses/request/submit          Submit request
GET  /my/enrollment-requests             Track requests
```

### 📄 Documents
```
GET  /my/documents                        List documents
GET  /my/documents/new                   New document form
POST /my/documents/new                   Submit document
GET  /my/documents/<id>                  Document details
```

### 🎓 Certificates
```
GET  /my/certificates                     List certificates
GET  /my/certificates/<id>/download      Download PDF
```

### 📝 Registration
```
GET  /my/registration                     View status
GET  /my/registration/<id>               Registration details
POST /my/registration/<id>/upload        Upload documents
```

---

## 🔑 Access Levels

| Symbol | Meaning |
|--------|---------|
| 🌐 | Public (no login) |
| 👤 | Portal user (student login) |
| 🔒 | Admin only (backend) |

---

## 🎯 Common Workflows

### New Student Registration
```
1. /student/register              → Fill form
2. /student/register/submit       → Submit
3. /student/register/success      → Confirmation
4. [Wait for approval]
5. /grants/login                  → Login
6. /my/student                    → Dashboard
```

### Request New Course
```
1. /my/available-courses          → Browse
2. /my/courses/request/5          → Request form
3. /my/courses/request/submit     → Submit
4. /my/enrollment-requests        → Track
5. [After approval]
6. /my/courses                    → See course
```

### Upload Document
```
1. /my/documents                  → List
2. /my/documents/new              → Form
3. [Upload file]
4. /my/documents/<id>             → View status
```

---

## 📊 Registration States

| State | Description |
|-------|-------------|
| `draft` | New application |
| `submitted` | Under review |
| `eligibility_review` | Checking eligibility |
| `document_review` | Reviewing documents |
| `approved` | Approved |
| `rejected` | Rejected |
| `enrolled` | Student created |

---

## 📊 Enrollment Request States

| State | Description |
|-------|-------------|
| `draft` | Draft |
| `pending` | Waiting admin approval |
| `approved` | Approved & enrolled |
| `rejected` | Rejected |

---

## 📊 Document States

| State | Description |
|-------|-------------|
| `draft` | Draft |
| `submitted` | Submitted |
| `under_review` | Being reviewed |
| `completed` | Completed |
| `rejected` | Rejected |

---

## 🔧 Development

### Test URLs (Local)
```
http://localhost:10020/my/student
http://localhost:10020/student/register
http://localhost:10020/grants/courses/catalog
```

### Default Port
- **Development**: `10020`
- Update in `docker-compose.yml` if needed

---

## 🎨 Modules

| Module | Routes | Purpose |
|--------|--------|---------|
| `grants_training_suite_v19` | 13 | Main student portal, courses, certificates |
| `student_enrollment_portal` | 6 | Registration workflow |
| `student_documents_portal` | 4 | Document management |

---

## 💡 Tips

1. **Pre-select Course**: Add `?course_id=<id>` to registration URL
2. **Direct Login**: Use `/web/login?redirect=/my/student`
3. **Check Status**: Visit `/my/registration` to track application
4. **Download Certificate**: Click download on `/my/certificates` page
5. **Track Requests**: Visit `/my/enrollment-requests` for pending enrollments

---

## 🔗 Full Documentation

See `PORTAL_ENDPOINTS.md` for complete documentation with:
- Detailed parameter descriptions
- cURL examples
- Security notes
- Error handling
- API testing guide

---

## 📞 Support

- **Email**: support@edafa.sa
- **Website**: https://www.edafa.sa
- **Version**: Odoo 19.0

---

**Last Updated**: 2025-11-24

