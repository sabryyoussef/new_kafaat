# Student Portal API Endpoints

This document describes all available endpoints in the Student Portal controller.

## Base URL
- **Development**: `http://localhost:10019`
- **Production**: `https://your-domain.com`

---

## Public Endpoints (No Authentication Required)

### 1. Student Registration Page
**GET** `/grants/register`

Displays the student registration form.

**Response:**
- Renders: `grants_training_suite_v19.portal_student_registration`
- Returns: HTML registration form with active course integrations

**Query Parameters:** None

**Example:**
```
GET http://localhost:10019/grants/register
```

---

### 2. Student Registration Submit
**POST** `/grants/register/submit`

Handles student registration form submission.

**Request Body (Form Data):**
- `name_english` (required): Full name in English
- `name_arabic` (required): Full name in Arabic
- `email` (required): Email address (must be unique)
- `phone` (required): Phone number
- `birth_date` (required): Birth date (YYYY-MM-DD format)
- `gender` (required): Gender (male/female)
- `nationality` (required): Nationality
- `english_level` (required): English proficiency level
- `native_language` (optional): Native language (default: 'Arabic')
- `has_certificate` (optional): 'yes' if has certificate
- `certificate_type` (optional): Type of certificate
- `preferred_course` (optional): Course integration ID

**Response:**
- **Success**: Renders `grants_training_suite_v19.portal_registration_success`
- **Error**: Renders `grants_training_suite_v19.portal_registration_error` with error message

**Creates:**
- Student record (`gr.student`)
- Portal user account (`res.users` with `base.group_portal`)
- Sends welcome email (if template exists)

**Example:**
```
POST http://localhost:10019/grants/register/submit
Content-Type: application/x-www-form-urlencoded

name_english=John Doe&name_arabic=جون دو&email=john@example.com&phone=+1234567890&birth_date=1990-01-01&gender=male&nationality=US&english_level=intermediate
```

---

### 3. Student Login
**GET** `/grants/login`

Redirects to Odoo's login page with redirect parameter.

**Query Parameters:**
- `redirect` (optional): URL to redirect after login (default: `/my/student`)

**Response:**
- Redirects to: `/web/login?redirect=/my/student`

**Example:**
```
GET http://localhost:10019/grants/login?redirect=/my/student
```

---

### 4. Course Catalog (Public)
**GET** `/grants/courses/catalog`

Displays public course catalog with all active course integrations.

**Response:**
- Renders: `grants_training_suite_v19.portal_course_catalog`
- Returns: HTML page with list of active course integrations

**Example:**
```
GET http://localhost:10019/grants/courses/catalog
```

---

### 5. Public Course Detail
**GET** `/grants/courses/<course_id>`

Displays detailed information about a specific course integration.

**URL Parameters:**
- `course_id` (required): Course integration ID (integer)

**Response:**
- **Success**: Renders `grants_training_suite_v19.portal_course_detail_public`
- **Not Found**: Renders `website.404`

**Example:**
```
GET http://localhost:10019/grants/courses/1
```

---

## Authenticated Endpoints (Require Login)

All authenticated endpoints require:
- Valid portal user session
- Student record with matching email

---

### 6. Student Dashboard
**GET** `/my/student`

Displays the student's personal dashboard.

**Authentication:** Required (Portal User)

**Response:**
- **Success**: Renders `grants_training_suite_v19.portal_student_dashboard`
- **No Student Found**: Renders `grants_training_suite_v19.portal_no_student`

**Data Returned:**
- `student`: Student record object
- `courses`: List of course sessions (`student.course_session_ids`)
- `progress`: Progress percentage (`student.progress_percentage`)
- `certificates`: List of certificates (`student.certificate_ids`)

**Example:**
```
GET http://localhost:10019/my/student
Cookie: session_id=...
```

---

### 7. My Courses
**GET** `/my/courses`

Lists all enrolled course sessions for the logged-in student.

**Authentication:** Required (Portal User)

**Response:**
- **Success**: Renders `grants_training_suite_v19.portal_my_courses`
- **No Student Found**: Renders `grants_training_suite_v19.portal_no_student`

**Data Returned:**
- `student`: Student record object
- `sessions`: List of course sessions (`student.course_session_ids`)

**Example:**
```
GET http://localhost:10019/my/courses
Cookie: session_id=...
```

---

### 8. Course Session Detail
**GET** `/my/courses/<session_id>`

Displays detailed information about a specific course session.

**Authentication:** Required (Portal User)

**URL Parameters:**
- `session_id` (required): Course session ID (integer)

**Response:**
- **Success**: Renders `grants_training_suite_v19.portal_course_detail`
- **No Student Found**: Renders `grants_training_suite_v19.portal_no_student`
- **Access Denied**: Renders `website.403` (if session doesn't belong to student)

**Security:**
- Verifies that `session.student_id` matches the logged-in student
- Returns 403 if student tries to access another student's session

**Data Returned:**
- `student`: Student record object
- `session`: Course session record object

**Example:**
```
GET http://localhost:10019/my/courses/5
Cookie: session_id=...
```

---

### 9. My Certificates
**GET** `/my/certificates`

Lists all certificates earned by the logged-in student.

**Authentication:** Required (Portal User)

**Response:**
- **Success**: Renders `grants_training_suite_v19.portal_my_certificates`
- **No Student Found**: Renders `grants_training_suite_v19.portal_no_student`

**Data Returned:**
- `student`: Student record object
- `certificates`: List of certificates (`student.certificate_ids`)

**Example:**
```
GET http://localhost:10019/my/certificates
Cookie: session_id=...
```

---

## Helper Methods

### `_get_student_for_portal_user()`
Internal method that retrieves the student record for the current portal user.

**Logic:**
1. Checks if user is logged in and not public
2. Searches for student by matching `gr.student.email` with `request.env.user.email`
3. Returns student record or `False`

**Usage:** Used by all authenticated endpoints

---

### `_prepare_home_portal_values(counters)`
Extends portal home values with student-specific counters.

**Parameters:**
- `counters`: Dictionary of counter names

**Returns:**
- Adds `course_count` to values if `'course_count'` is in counters

---

## Error Handling

### Common Error Responses

1. **Template Not Found**
   - Error: Template rendering fails
   - Check: Ensure all templates exist in `portal_templates.xml`

2. **Student Not Found**
   - Error: No student record matches portal user email
   - Solution: Create student record with matching email

3. **Access Denied (403)**
   - Error: Student tries to access another student's course session
   - Response: `website.403` template

4. **Registration Validation Errors**
   - Missing required fields
   - Duplicate email
   - Response: `portal_registration_error` template with error message

---

## Security Considerations

1. **Authentication**
   - Public routes: No authentication required
   - Authenticated routes: Require valid portal user session

2. **Authorization**
   - Students can only view their own data
   - Course session access is verified by `student_id` match
   - Portal security rules enforce data isolation

3. **CSRF Protection**
   - Registration endpoint has `csrf=False` (public endpoint)
   - Other POST endpoints use Odoo's default CSRF protection

4. **Data Access**
   - All queries use `.sudo()` for proper access control
   - Student matching is done by email comparison

---

## Testing

### Manual Testing Checklist

- [ ] Registration form displays correctly
- [ ] Registration creates student and portal user
- [ ] Welcome email is sent (if template exists)
- [ ] Login redirects correctly
- [ ] Course catalog shows active courses
- [ ] Public course detail displays correctly
- [ ] Student dashboard loads with correct data
- [ ] My courses lists student's sessions
- [ ] Course session detail shows correct session
- [ ] Access denied for other student's session
- [ ] My certificates lists student's certificates
- [ ] No student found error displays correctly

### Test Data Requirements

1. **Student Record**
   - Email: `test@example.com`
   - Name: "Test Student"
   - State: `enrolled` or `draft`

2. **Portal User**
   - Login: `test@example.com` (must match student email)
   - Groups: `base.group_portal`
   - Active: `True`

3. **Course Integration**
   - Status: `active`
   - At least one active course for catalog testing

4. **Course Session** (optional)
   - Linked to test student
   - For testing authenticated endpoints

---

## Dependencies

- `odoo.addons.portal.controllers.portal.CustomerPortal`
- `odoo.http` module
- `odoo.exceptions` for error handling

## Related Files

- **Controller**: `controllers/student_portal.py`
- **Templates**: `views/portal/portal_templates.xml`
- **Documentation**: `STUDENT_PORTAL.md`

---

## Version

- **Module**: grants_training_suite_v19
- **Odoo Version**: 19.0
- **Last Updated**: 2025-11-24

