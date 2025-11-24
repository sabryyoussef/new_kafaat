# Kafaat Training Management System

**Version**: 19.0  
**Platform**: Odoo 19 Enterprise  
**Author**: Edafa  
**Website**: https://www.edafa.sa

A comprehensive training management platform for educational institutions, featuring student enrollment, course management, document processing, and certificate issuance.

---

## 📋 Table of Contents

- [Features](#features)
- [Modules](#modules)
- [Installation](#installation)
- [Portal Routes](#portal-routes)
- [Documentation](#documentation)
- [Development](#development)
- [Support](#support)

---

## ✨ Features

### 🎓 Student Management
- Public student registration portal
- Multi-step enrollment approval workflow
- Student dashboard with course tracking
- Progress monitoring and analytics
- Certificate management

### 📚 Course Management
- Course catalog (public & authenticated)
- Course enrollment requests
- Session tracking and attendance
- Progress tracking per course
- Certificate generation upon completion

### 📄 Document Management
- Admin-initiated document requests
- Student-initiated document uploads
- Document verification workflow
- Registration document tracking
- Secure file storage

### 🎯 Enrollment Processing
- Online registration forms
- Eligibility assessment
- Document verification
- Automated student record creation
- Portal user provisioning

### 📊 Batch Processing
- Bulk student intake via Excel/CSV
- Automated eligibility assessment
- Configurable criteria management
- Result export functionality
- Standalone operation (no dependencies)

---

## 📦 Modules

### Core Modules

#### 1. **grants_training_suite_v19** (Base Module)
Main training management system with student, course, and certificate management.

**Features**:
- Student records management
- Course integration and sessions
- Certificate issuance
- Student portal and dashboard
- Course enrollment requests
- Public course catalog

**Dependencies**: `base`, `mail`, `portal`, `website`

---

#### 2. **student_enrollment_portal**
Complete student enrollment workflow with multi-step review process.

**Features**:
- Public registration form
- Document upload during registration
- Multi-step approval workflow:
  - Eligibility Review
  - Document Verification
  - Final Approval
- Automated portal user creation
- Email notifications at each stage

**Dependencies**: `grants_training_suite_v19`, `portal`, `website`, `mail`

**Key Routes**:
- `/student/register` - Registration form
- `/my/registration` - Track registration status

---

#### 3. **student_documents_portal**
Unified document management for all student-related documents.

**Features**:
- Student-initiated document uploads
- Admin-initiated document requests
- Registration document tracking
- Document review workflow
- Integration with registration process

**Dependencies**: `grants_training_suite_v19`, `student_enrollment_portal`, `portal`, `website`

**Key Routes**:
- `/my/documents` - Document management
- `/my/documents/new` - Upload/request documents

---

### Utility Modules

#### 4. **batch_intake_processor**
Standalone module for batch processing of student applications.

**Features**:
- Excel/CSV file import
- Configurable eligibility criteria
- Automated assessment
- Detailed reporting
- Result export (Excel/CSV)
- No dependencies on other custom modules

**Dependencies**: `base`, `mail`, `hr`

**Use Case**: Process large batches of applications from external sources.

---

## 🚀 Installation

### Prerequisites
- Docker & Docker Compose
- Git
- PostgreSQL 17
- Odoo 19 Enterprise

### Quick Start

1. **Clone Repository**
```bash
git clone https://github.com/sabryyoussef/new_kafaat.git kafaat-main
cd kafaat-main
```

2. **Start Services**
```bash
docker-compose up -d
```

3. **Access Odoo**
```
URL: http://localhost:10020
Database: kafaat
Master Password: admin
```

4. **Install Modules**
- Login to Odoo
- Go to Apps
- Update Apps List
- Install modules in order:
  1. `grants_training_suite_v19`
  2. `student_enrollment_portal`
  3. `student_documents_portal`
  4. `batch_intake_processor` (optional)

### Configuration

**Port Configuration** (docker-compose.yml):
```yaml
services:
  web:
    ports:
      - "10020:8069"  # Change 10020 to your preferred port
```

**Database Connection**:
```yaml
environment:
  - HOST=db
  - USER=odoo
  - PASSWORD=odoo
```

---

## 🌐 Portal Routes

### Quick Access

| Portal | URL | Auth |
|--------|-----|------|
| Course Catalog | `/grants/courses/catalog` | Public |
| Student Registration | `/student/register` | Public |
| Student Login | `/grants/login` | Public |
| Student Dashboard | `/my/student` | User |
| My Courses | `/my/courses` | User |
| My Documents | `/my/documents` | User |
| My Certificates | `/my/certificates` | User |

### Complete Route Reference

See **[PORTAL_ENDPOINTS.md](custom_addons/documentation/PORTAL_ENDPOINTS.md)** for:
- All 20+ portal routes
- Detailed parameter descriptions
- cURL examples
- User journey workflows
- Security notes

See **[QUICK_REFERENCE.md](custom_addons/documentation/QUICK_REFERENCE.md)** for:
- One-page lookup table
- Quick links
- Common workflows
- State transitions

---

## 📚 Documentation

### Main Documentation Files

| File | Description |
|------|-------------|
| **[PORTAL_ENDPOINTS.md](custom_addons/documentation/PORTAL_ENDPOINTS.md)** | Complete portal routes reference |
| **[QUICK_REFERENCE.md](custom_addons/documentation/QUICK_REFERENCE.md)** | Quick lookup guide |
| **[DOCUMENTATION_INDEX.md](custom_addons/documentation/DOCUMENTATION_INDEX.md)** | Documentation guide |
| **[DOCUMENT_CONSOLIDATION_SUMMARY.md](custom_addons/documentation/DOCUMENT_CONSOLIDATION_SUMMARY.md)** | Module architecture |

### Module-Specific Documentation

| Module | README Location |
|--------|----------------|
| student_enrollment_portal | `custom_addons/student_enrollment_portal/README.md` |
| student_documents_portal | `custom_addons/student_documents_portal/README.md` |

---

## 🎯 User Workflows

### New Student Registration
```
1. Visit /student/register
2. Fill registration form
3. Upload required documents
4. Submit application
5. Wait for admin approval (3-step process)
6. Receive email with login credentials
7. Login at /grants/login
8. Access dashboard at /my/student
```

### Enrolled Student Requests Course
```
1. Login at /grants/login
2. Browse available courses at /my/available-courses
3. Click "Request Enrollment"
4. Submit request with notes
5. Admin reviews and approves
6. Course appears in /my/courses
7. Track progress and earn certificate
```

### Student Uploads Document
```
1. Login and go to /my/documents
2. Click "New Document Request"
3. Select "Upload Document"
4. Choose document type
5. Upload file
6. Submit for review
7. Track status in /my/documents
```

---

## 🛠 Development

### Project Structure
```
kafaat-main/
├── custom_addons/
│   ├── documentation/                   # 📚 All documentation
│   │   ├── PORTAL_ENDPOINTS.md         # Route reference
│   │   ├── QUICK_REFERENCE.md          # Quick lookup
│   │   ├── DOCUMENTATION_INDEX.md      # Doc guide
│   │   └── DOCUMENT_CONSOLIDATION_SUMMARY.md  # Architecture
│   ├── grants_training_suite_v19/      # Base module
│   ├── student_enrollment_portal/      # Registration
│   ├── student_documents_portal/       # Documents
│   └── batch_intake_processor/         # Batch processing
├── odoo_enterprise19/                   # Odoo enterprise
├── docker-compose.yml                   # Docker config
└── README.md                            # This file
```

### Module Dependencies

```
grants_training_suite_v19 (base)
    ↓
student_enrollment_portal
    ↓
student_documents_portal

batch_intake_processor (standalone)
```

### Controller Classes

To avoid conflicts, each module uses unique controller class names:

| Module | Controller Class |
|--------|-----------------|
| grants_training_suite_v19 | `GrantsStudentPortal` |
| student_enrollment_portal | `StudentEnrollmentPortal` |
| student_documents_portal | `StudentDocumentsPortal` |

### Adding Custom Routes

1. Create controller in `controllers/` directory
2. Inherit from `CustomerPortal` or `http.Controller`
3. Use `@http.route()` decorator
4. Import in `controllers/__init__.py`
5. Restart Odoo

**Example**:
```python
from odoo import http
from odoo.addons.portal.controllers.portal import CustomerPortal

class MyPortal(CustomerPortal):
    @http.route(['/my/custom'], type='http', auth='user', website=True)
    def my_custom_page(self, **kw):
        return request.render('my_module.my_template', {})
```

### Development URLs

**Local Development**:
```
Base: http://localhost:10020
Backend: http://localhost:10020/web
Portal: http://localhost:10020/my
```

**Database Management**:
```
URL: http://localhost:10020/web/database/manager
Master Password: admin
```

---

## 🔐 Security

### Access Control

| Group | Description | Access Level |
|-------|-------------|--------------|
| Portal User | Students | Portal routes only |
| Agent | Training staff | Read/Write students, courses |
| Manager | Administrators | Full access |

### Security Features

- Email-based record matching
- Portal user isolation (students see only their data)
- Document ownership verification
- CSRF protection on forms
- Secure file uploads
- Audit trail via chatter

---

## 🧪 Testing

### Demo Data

All modules include demo data:
- Sample students
- Sample courses
- Sample registrations
- Sample documents
- Sample enrollment requests

**Enable demo data**: Install modules with demo data enabled.

### Manual Testing Checklist

**Registration Flow**:
- [ ] Public registration form works
- [ ] Document upload functional
- [ ] Email notifications sent
- [ ] Portal user created
- [ ] Student can login

**Course Enrollment**:
- [ ] Browse available courses
- [ ] Submit enrollment request
- [ ] Track request status
- [ ] Course appears after approval

**Document Management**:
- [ ] Upload new document
- [ ] View document list
- [ ] Download uploaded documents
- [ ] Track document status

---

## 📊 Database Models

### Core Models

| Model | Description | Module |
|-------|-------------|--------|
| `gr.student` | Student records | grants_training_suite_v19 |
| `gr.course.integration` | Course catalog | grants_training_suite_v19 |
| `gr.course.session` | Student enrollments | grants_training_suite_v19 |
| `gr.certificate` | Certificates | grants_training_suite_v19 |
| `student.registration` | Registration applications | student_enrollment_portal |
| `course.enrollment.request` | Course requests | grants_training_suite_v19 |
| `gr.document.request.portal` | Student documents | student_documents_portal |
| `gr.registration.document` | Registration docs | student_documents_portal |
| `batch.intake` | Batch processing | batch_intake_processor |

---

## 🚧 Troubleshooting

### Common Issues

**1. Port Conflict**
```bash
# Change port in docker-compose.yml
ports:
  - "10021:8069"  # Use different port
```

**2. Module Not Found**
```bash
# Restart Odoo and update apps list
docker-compose restart web
# Then: Apps > Update Apps List
```

**3. Database Connection Error**
```bash
# Check PostgreSQL is running
docker-compose ps
# Check logs
docker-compose logs db
```

**4. Student Cannot Login**
```bash
# Verify portal user created
# Check: Settings > Users > Portal Users
# Verify email matches student email
```

**5. Routes Not Working**
```bash
# Restart Odoo
docker-compose restart web
# Clear browser cache
# Check controller class names are unique
```

---

## 🔄 Updates & Maintenance

### Update Modules
```bash
# Pull latest changes
git pull origin master

# Restart services
docker-compose restart web

# Update modules in Odoo
# Apps > Installed > Module > Upgrade
```

### Backup Database
```bash
# Via web interface
http://localhost:10020/web/database/manager

# Or via command line
docker exec -t kafaat-db pg_dump -U odoo kafaat > backup.sql
```

### Restore Database
```bash
docker exec -i kafaat-db psql -U odoo -d kafaat < backup.sql
```

---

## 📞 Support

### Contact Information

- **Company**: Edafa
- **Website**: https://www.edafa.sa
- **Email**: support@edafa.sa

### Resources

- **Odoo Documentation**: https://www.odoo.com/documentation/19.0/
- **GitHub Repository**: https://github.com/sabryyoussef/new_kafaat
- **Issue Tracker**: Use GitHub Issues

### Getting Help

1. Check documentation files first
2. Review error logs: `docker-compose logs web`
3. Search GitHub issues
4. Contact support team

---

## 📄 License

**License**: OEEL-1 (Odoo Enterprise Edition License)

This project uses Odoo Enterprise Edition which requires a valid license.

---

## 👥 Contributing

### Development Guidelines

1. Fork the repository
2. Create feature branch
3. Follow Odoo coding standards
4. Test thoroughly
5. Submit pull request

### Coding Standards

- Follow Odoo guidelines
- Use meaningful variable names
- Add docstrings to methods
- Include security rules
- Test with demo data

---

## 🎉 Acknowledgments

- Built on Odoo 19 Enterprise
- Developed by Edafa team
- Special thanks to all contributors

---

## 📈 Roadmap

### Planned Features

- [ ] Mobile app integration
- [ ] Advanced analytics dashboard
- [ ] Automated certificate generation
- [ ] Payment gateway integration
- [ ] WhatsApp notifications
- [ ] Multi-language support (full Arabic)

---

## 📝 Changelog

### Version 19.0.1.0.0 (2025-11-24)

**Added**:
- Student enrollment portal with multi-step approval
- Unified document management system
- Course enrollment request workflow
- Batch intake processor
- Comprehensive portal routes
- Demo data for all modules

**Fixed**:
- Portal controller class name conflicts
- Document management consolidation
- Menu structure and navigation

**Documentation**:
- Complete portal endpoints reference
- Quick reference guide
- Module architecture documentation

---

## 🌟 Features Highlights

### For Students
✅ Easy online registration  
✅ Track application status  
✅ Browse and request courses  
✅ Manage documents  
✅ View certificates  
✅ Track progress  

### For Administrators
✅ Multi-step approval workflow  
✅ Document verification  
✅ Batch processing  
✅ Automated notifications  
✅ Comprehensive reporting  
✅ Audit trails  

### For Institutions
✅ Scalable architecture  
✅ Modular design  
✅ Secure portal  
✅ Integration ready  
✅ Customizable workflows  
✅ Full audit trail  

---

**Version**: 19.0.1.0.0  
**Last Updated**: 2025-11-24  
**Status**: Production Ready ✅

---

**Made with ❤️ by Edafa**
