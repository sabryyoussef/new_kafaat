# Module Separation Summary

This document summarizes the modularization work done on the Grants Training system.

## Overview

The Grants Training system has been organized into **separate, focused modules** for better maintainability, scalability, and separation of concerns.

## Module Structure

### 1. **`grants_training_suite_v19`** (Main Module)
**Purpose**: Core training center management system

**Responsibilities**:
- Student management (gr.student)
- Course sessions and enrollments
- Certificates and certification automation
- E-learning integration (course integrations, training programs)
- Progress tracking
- Homework and assignments
- Intake batch management
- Contact pools and CRM integration
- Sales dashboard
- **Student Portal Features**:
  - Student dashboard (`/my/student`)
  - Course browsing and details
  - Certificate viewing and download
  - Course enrollment requests
  - Public course catalog

**Key Routes**:
- `/grants` - Home page
- `/my/student` - Student dashboard
- `/my/courses` - Enrolled courses
- `/my/certificates` - Certificates
- `/my/enrollment-requests` - Course enrollment requests
- `/grants/courses/catalog` - Public course catalog

---

### 2. **`student_enrollment_portal`** (Registration Module)
**Purpose**: New student registration and onboarding

**Responsibilities**:
- **ONLY** handles NEW student registration
- Public registration form
- Multi-step approval workflow (Eligibility → Documents → Approval)
- Document upload during registration
- Automated student record creation
- Portal user creation with credentials
- Email notifications

**Key Routes**:
- `/student/register` - Public registration form
- `/student/register/submit` - Registration submission

**Backend Features**:
- Registration review workflow
- Admin approval interface
- Email templates for registration stages

---

### 3. **`student_documents_portal`** (NEW - Document Management Module)
**Purpose**: Student document management and requests

**Responsibilities**:
- Document upload requests
- Academy document requests
- Document status tracking
- Admin review and processing
- Document download for students
- Email notifications

**Key Routes**:
- `/my/documents` - List all document requests
- `/my/documents/new` - Submit new document request
- `/my/documents/<id>` - View request details

**Backend Features**:
- Document request workflow (Draft → Submitted → In Progress → Completed/Rejected)
- Admin response and notes
- File attachments
- Email templates

---

## Module Dependencies

```
grants_training_suite_v19 (base module)
    ↑
    |-- depends on --> Odoo core modules (portal, website, mail, etc.)
    |
    ├── student_enrollment_portal (depends on grants_training_suite_v19)
    |
    └── student_documents_portal (depends on grants_training_suite_v19)
```

## Workflow: New Student Journey

```
1. VISITOR (not in system)
   ↓
   Browse courses at /grants/courses/catalog
   ↓
   Click "Register & Enroll" → /student/register (student_enrollment_portal)
   ↓
   Fill registration form + select courses + upload documents
   ↓
   Submit → Admin reviews (Eligibility → Documents → Approval)
   ↓
   [APPROVED]
   ↓
2. STUDENT RECORD CREATED + PORTAL USER CREATED
   ↓
   Student receives login credentials via email
   ↓
3. ENROLLED STUDENT
   ↓
   Login → /my/student (grants_training_suite_v19)
   ↓
   Access all student portal features:
   - View enrolled courses
   - Browse available courses
   - Request enrollment in more courses
   - View/download certificates
   - Submit document requests (/my/documents - student_documents_portal)
```

## Benefits of Separation

### ✅ **Modularity**
- Each module has a single, clear responsibility
- Easy to enable/disable features
- Reduced code complexity

### ✅ **Maintainability**
- Changes to registration don't affect document management
- Changes to documents don't affect core training features
- Easier to debug and test

### ✅ **Scalability**
- Can add more specialized modules (e.g., payment portal, exam portal)
- Each module can evolve independently
- Better performance (only load what's needed)

### ✅ **Reusability**
- `student_documents_portal` can be used by other educational modules
- `student_enrollment_portal` can be customized for different programs
- Core module remains stable

## Installation Order

1. Install `grants_training_suite_v19` first (base module)
2. Install `student_enrollment_portal` (for new registrations)
3. Install `student_documents_portal` (for document management)

## Migration Notes

### What Was Moved:

**From `grants_training_suite_v19` to `student_documents_portal`**:
- Model: `gr.document.request.portal`
- Controllers: `/my/documents`, `/my/documents/new`
- Views: `document_request_portal_views.xml`
- Templates: `portal_documents`, `portal_document_request_form`
- Security: Access rights and record rules
- Email templates: Document request notifications

### What Stayed in `grants_training_suite_v19`:

- All course and training management
- Student portal (dashboard, courses, certificates)
- Course enrollment requests (different from registration)
- Public course catalog
- All backend admin features

### What's NEW:

- `student_documents_portal` module (completely new)
- Clean separation between registration and document management
- Improved email templates with better styling

## Testing Checklist

- [ ] New student can register at `/student/register`
- [ ] Admin can review and approve registrations
- [ ] Approved student receives portal credentials
- [ ] Student can login and access dashboard (`/my/student`)
- [ ] Student can view enrolled courses
- [ ] Student can request enrollment in new courses
- [ ] Student can submit document requests (`/my/documents`)
- [ ] Admin can process document requests
- [ ] Student receives email notifications
- [ ] Public visitors can browse course catalog
- [ ] All portal routes work correctly

## Support

For issues or questions about module separation, contact the development team at Edafa.

---

**Version**: 1.0.0  
**Date**: November 24, 2025  
**Author**: Edafa Development Team

