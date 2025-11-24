# Student Enrollment Portal

A comprehensive student enrollment system for Odoo 19 that provides a complete workflow from public registration to course enrollment.

## Features

### 🎓 Public Registration Portal
- Beautiful, user-friendly registration form accessible to anyone
- Multi-language support (English and Arabic names)
- Document upload capability (ID, certificates, etc.)
- Course selection and preferences
- Automatic registration number generation (REG00001, REG00002, etc.)

### 🔍 Multi-Step Review Process
1. **Eligibility Review** - Admin reviews student qualifications
2. **Document Review** - Admin verifies uploaded documents
3. **Approval** - Final approval with automatic student record creation
4. **Enrollment** - Admin enrolls approved students in courses

### 📊 Backend Management
- **Kanban View** - Visual workflow management with drag-and-drop
- **Tree View** - List view with color-coded status indicators
- **Form View** - Detailed registration information with chatter
- **Search & Filters** - Filter by status, reviewer, date, etc.
- **Menu Structure** - Organized menus for each review stage

### 👤 Student Portal
- Students can check their registration status
- Upload additional documents during review
- View review notes and feedback
- Progress indicator showing current stage
- Access to contact support

### 🔐 Security
- Portal users can only see their own registrations
- Managers and agents have full access to all registrations
- Record-level security rules
- Email-based access control

### 📧 Email Notifications
- Registration confirmation email
- Rejection notification with reason
- Approval notification with login credentials
- Enrollment confirmation

### 🔗 Integration
- Seamless integration with `grants_training_suite_v19`
- Automatic creation of `gr.student` records
- Portal user creation with password reset
- Links to course enrollment system

## Installation

1. Ensure `grants_training_suite_v19` is installed
2. Copy the `student_enrollment_portal` folder to your Odoo addons directory
3. Update the app list in Odoo
4. Install the "Student Enrollment Portal" module

## Configuration

No additional configuration required. The module works out of the box.

## Usage

### For Students

1. Navigate to `/student/register` on your Odoo website
2. Fill in the registration form with personal and educational information
3. Upload required documents
4. Submit the registration
5. Check status at `/my/registration` (requires login after approval)

### For Administrators

1. Go to **Student Registrations** menu
2. Review new submissions in **New Registrations**
3. Click **Start Review** to begin eligibility review
4. Add eligibility notes and approve or reject
5. Review documents in **Document Review**
6. Approve documents to move to final approval
7. Click **Finalize & Create Student** to:
   - Create student record in `gr.student`
   - Create portal user account
   - Send approval email with login credentials
8. Click **Enroll in Courses** to assign courses

## Workflow States

- **Draft** - New registration (not yet submitted)
- **Submitted** - Student has submitted the form
- **Eligibility Review** - Admin is reviewing eligibility
- **Document Review** - Admin is verifying documents
- **Approved** - Registration approved, student record created
- **Rejected** - Registration rejected at any stage
- **Enrolled** - Student enrolled in courses

## Technical Details

### Models
- `student.registration` - Main registration model with workflow

### Controllers
- `/student/register` - Public registration form
- `/student/register/submit` - Form submission handler
- `/student/register/success` - Success page
- `/my/registration` - Portal status page
- `/my/registration/<id>/upload` - Document upload handler

### Views
- Form view with workflow buttons
- Tree view with color coding
- Kanban view for workflow management
- Search view with filters and grouping
- Portal templates for public access

### Security
- `ir.model.access.csv` - Model access rights
- `security_rules.xml` - Record-level security rules

### Data
- `sequences.xml` - Registration number sequence
- `email_templates.xml` - Email notification templates

## Dependencies

- `grants_training_suite_v19` - Core student and course management
- `portal` - Portal functionality
- `website` - Public website features
- `mail` - Chatter and email notifications

## Support

For issues or questions, please contact the development team.

## License

OEEL-1 (Odoo Enterprise Edition License)

## Author

Edafa - https://www.edafa.sa

## Version

19.0.1.0.0

