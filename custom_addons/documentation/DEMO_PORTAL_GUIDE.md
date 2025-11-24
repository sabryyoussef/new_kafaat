# Demo Portal Guide

Public access demo portal for Kafaat Student Portal - No login required!

---

## 🎯 Overview

The demo portal provides **public access** to all student portal features without requiring authentication. Perfect for:
- Client demonstrations
- Screenshots and documentation
- Training sessions
- Quick testing
- Public previews

---

## 🚀 Quick Start

### 1. Activate Demo Portal

**Via Odoo UI** (Recommended):
```
1. Login to Odoo backend
2. Go to Apps menu
3. Search "Grants Training Suite"
4. Click "Upgrade"
5. Wait for completion
6. Visit http://localhost:10020/demo
```

**Via Command Line**:
```bash
docker exec -it <container-name> odoo-bin \
    -c /etc/odoo/odoo.conf -d kafaat \
    -u grants_training_suite_v19 --stop-after-init
```

### 2. Access Demo Portal

Main demo index:
```
http://localhost:10020/demo
```

---

## 📋 Demo Routes

All routes are **publicly accessible** (no login required):

### Main Demo Index
```
GET /demo
```
Beautiful landing page with cards linking to all demo features.

### Student Dashboard
```
GET /demo/student
```
View student overview, enrolled courses, progress, certificates.

### My Courses
```
GET /demo/courses
GET /demo/courses/<int:session_id>
```
Browse enrolled courses and view course details.

### Certificates
```
GET /demo/certificates
```
View earned certificates and achievements.

### Available Courses
```
GET /demo/available-courses
```
Browse courses available for enrollment.

### Enrollment Requests
```
GET /demo/enrollment-requests
```
Track course enrollment requests and their status.

### Documents
```
GET /demo/documents
```
View document requests and uploads.

### Registration Status
```
GET /demo/registration
```
Check student registration application status.

---

## 🎨 Features

### Beautiful Landing Page

The `/demo` route displays:
- Hero section with project branding
- 9 feature cards with icons and descriptions
- Quick access buttons
- Info sections explaining demo vs production
- Production route reference
- Responsive Bootstrap 5 design

### Automatic Demo Data

- Automatically finds demo student data
- Falls back to first available student if no demo data
- Graceful error handling when no data exists
- Shows helpful messages with instructions

### Visual Indicators

All demo pages include:
- `is_demo: True` flag in context
- Warning banners (can be added to templates)
- Clear indication of demo mode

---

## 🔒 Security

### Safe Implementation

✅ **Read-Only Access**
- Uses `.sudo()` for data access
- No write operations allowed
- Form submissions disabled in demo mode

✅ **Isolated from Production**
- Separate `/demo/` route namespace
- Original `/my/` routes unchanged
- No impact on authentication system

✅ **Production Safety**
- Easy to disable in production
- Clear separation from secure routes
- No security bypass of original routes

---

## 📊 Comparison: Demo vs Production

| Feature | Demo Routes (`/demo/`) | Production Routes (`/my/`) |
|---------|----------------------|---------------------------|
| **Authentication** | Public (no login) | Requires portal login |
| **Data Access** | Uses demo student | User-specific data |
| **Write Access** | Read-only | Full CRUD operations |
| **Security** | .sudo() access | User permissions |
| **Use Case** | Demos, testing | Real student usage |

---

## 🛠 Technical Details

### Controller Class

**File**: `controllers/public_demo_portal.py`

```python
class PublicDemoPortal(http.Controller):
    """Public Demo Portal - No authentication required"""
    
    @http.route(['/demo/student'], type='http', auth='public', website=True)
    def demo_student_dashboard(self, **kw):
        student = self._get_demo_student()
        # ... render dashboard
```

### Key Methods

**`_get_demo_student()`**
- Searches for student with 'demo' in name
- Falls back to first available student
- Returns False if no students exist

**Route Handlers**
- All use `auth='public'`
- All use `.sudo()` for data access
- All set `is_demo: True` in context
- All handle missing data gracefully

### Templates Used

Demo routes reuse existing portal templates:
- `grants_training_suite_v19.portal_student_dashboard`
- `grants_training_suite_v19.portal_my_courses`
- `grants_training_suite_v19.portal_my_certificates`
- `student_documents_portal.portal_documents`
- `student_enrollment_portal.portal_my_registration`

New template:
- `grants_training_suite_v19.demo_portal_index`
- `grants_training_suite_v19.demo_no_data`

---

## 📦 Deployment

### Development Environment

**Keep Demo Routes Enabled**:
- Perfect for testing and development
- Easy access to all features
- No need to create test users

### Production Environment

**Option 1: Keep Demo Routes**
- Useful for client demos
- Safe read-only access
- Clear demo indicators

**Option 2: Disable Demo Routes**

Comment out in `controllers/__init__.py`:
```python
# from . import public_demo_portal  # Disabled in production
```

**Option 3: Add Access Restrictions**

Add to `ir.rule.xml`:
```xml
<record id="demo_portal_access_rule" model="ir.rule">
    <field name="name">Restrict Demo Portal</field>
    <!-- Add domain restrictions -->
</record>
```

---

## 🧪 Testing

### Manual Testing

1. **Visit demo index**:
   ```
   http://localhost:10020/demo
   ```
   ✓ Should show landing page with cards

2. **Test each feature card**:
   - Click each card
   - Verify page loads
   - Check data displays correctly

3. **Verify no login required**:
   - Open in incognito/private window
   - Should work without authentication

4. **Check error handling**:
   - Test with no demo data
   - Verify graceful error messages

### Automated Testing (cURL)

```bash
# Demo index
curl -s -o /dev/null -w "%{http_code}" http://localhost:10020/demo

# Student dashboard
curl -s -o /dev/null -w "%{http_code}" http://localhost:10020/demo/student

# Courses
curl -s -o /dev/null -w "%{http_code}" http://localhost:10020/demo/courses

# All should return 200 OK
```

---

## ⚠️ Important Notes

### Demo Data Required

For best experience:
1. Install modules with demo data enabled
2. Or create sample students manually
3. Demo portal works with any student data

### Read-Only Environment

- No form submissions work
- No data modifications allowed
- All POST routes return to demo pages
- Perfect for safe demonstrations

### Production Warning

**DO NOT** use demo routes for:
- Real student access
- Production workflows
- Authenticated operations
- Data modifications

---

## 🎯 Use Cases

### 1. Client Demonstrations

**Scenario**: Show portal features to potential clients

**Benefits**:
- No user creation needed
- Clean demo environment
- Professional presentation
- Quick feature showcase

### 2. Screenshot Generation

**Scenario**: Create documentation screenshots

**Benefits**:
- Consistent demo data
- No login required
- Easy to reproduce
- Professional appearance

### 3. Training Sessions

**Scenario**: Train staff on portal features

**Benefits**:
- No test accounts needed
- Safe environment
- Easy access for trainees
- No risk of data corruption

### 4. Development Testing

**Scenario**: Quick testing during development

**Benefits**:
- Fast access to features
- No authentication setup
- Easy to test changes
- Rapid iteration

---

## 📝 Customization

### Adding New Demo Routes

1. **Add route handler** in `public_demo_portal.py`:
```python
@http.route(['/demo/new-feature'], type='http', auth='public', website=True)
def demo_new_feature(self, **kw):
    student = self._get_demo_student()
    return request.render('module.template', {
        'student': student,
        'is_demo': True,
    })
```

2. **Add card** to demo index in `demo_portal_templates.xml`:
```xml
<div class="col-md-4 mb-4">
    <div class="card h-100">
        <div class="card-body">
            <h5 class="card-title">New Feature</h5>
            <p class="card-text">Description...</p>
            <a href="/demo/new-feature" class="btn btn-primary">
                View Feature
            </a>
        </div>
    </div>
</div>
```

### Customizing Demo Data Selection

Modify `_get_demo_student()` in `public_demo_portal.py`:

```python
def _get_demo_student(self):
    # Search by specific criteria
    student = request.env['gr.student'].sudo().search([
        ('name', '=', 'John Demo'),
        ('email', 'like', 'demo@')
    ], limit=1)
    
    return student
```

---

## 🔗 Related Documentation

- **[PORTAL_ENDPOINTS.md](PORTAL_ENDPOINTS.md)** - Complete route reference
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Quick lookup guide
- **[README.md](../../README.md)** - Main project documentation

---

## 💡 Tips & Tricks

### Tip 1: Create Dedicated Demo Student

```python
# In demo data XML
<record id="demo_student_john" model="gr.student">
    <field name="name">John Demo</field>
    <field name="email">demo@example.com</field>
    <!-- Add enrolled courses, certificates, etc. -->
</record>
```

### Tip 2: Add Demo Banner to Templates

```xml
<t t-if="is_demo">
    <div class="alert alert-warning">
        <i class="fa fa-exclamation-triangle"/> 
        Demo Mode - You are viewing sample data
    </div>
</t>
```

### Tip 3: Use Demo for Screenshots

1. Visit `/demo` in clean browser
2. Take screenshots
3. Data stays consistent
4. Professional appearance

---

## 🐛 Troubleshooting

### Issue: 404 Not Found on /demo routes

**Solution**: Upgrade the module
```
Apps → Grants Training Suite → Upgrade
```

### Issue: No demo data message

**Solution**: Install with demo data or create sample students
```sql
INSERT INTO gr_student (name, email) 
VALUES ('Demo Student', 'demo@example.com');
```

### Issue: Templates not rendering correctly

**Solution**: Check template inheritance and is_demo flag
```python
values = {
    'is_demo': True,  # Add this flag
    'student': student,
}
```

---

## 📞 Support

- **GitHub**: https://github.com/sabryyoussef/new_kafaat
- **Email**: support@edafa.sa
- **Documentation**: custom_addons/documentation/

---

**Version**: 1.0.0  
**Last Updated**: 2025-11-24  
**Status**: Production Ready ✅

---

**Made with ❤️ for easy demonstrations**

