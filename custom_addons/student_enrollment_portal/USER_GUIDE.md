# Student Enrollment Portal - User Guide

## Table of Contents
1. [Overview](#overview)
2. [User Roles](#user-roles)
3. [Complete Use Case Scenario](#complete-use-case-scenario)
4. [Student Guide](#student-guide)
5. [Administrator Guide](#administrator-guide)
6. [Workflow States](#workflow-states)
7. [Troubleshooting](#troubleshooting)

---

## Overview

The Student Enrollment Portal is a comprehensive system that manages the entire student registration lifecycle from initial application through course enrollment. It provides a seamless experience for both students (via public portal) and administrators (via backend management).

### Key Features
- ✅ Public registration form accessible to anyone
- ✅ Multi-step review process with quality gates
- ✅ Document upload and verification
- ✅ Automated student record creation
- ✅ Portal user account generation
- ✅ Email notifications at each stage
- ✅ Full audit trail via chatter

---

## User Roles

### 1. **Public Users (Students)**
- Can access the registration form without login
- Can submit registration applications
- Can upload supporting documents
- Can track their registration status (after approval)

### 2. **Portal Users (Approved Students)**
- Can log in to the student portal
- Can view their registration status
- Can upload additional documents
- Can access enrolled courses (after enrollment)

### 3. **Agents (Staff)**
- Can view all registrations
- Can review and approve/reject applications
- Can add review notes
- Can create student records
- Can enroll students in courses

### 4. **Managers (Administrators)**
- Full access to all features
- Can manage all registrations
- Can configure system settings
- Can generate reports

---

## Complete Use Case Scenario

### **Scenario: Sarah's Journey to Enrollment**

#### **Background**
Sarah is a 25-year-old professional from Riyadh who wants to improve her English skills for career advancement. She heard about the academy through a friend and wants to enroll in an English language course.

---

### **Phase 1: Discovery & Registration**

#### **Step 1: Sarah Discovers the Academy**
- Sarah visits the academy's website
- She clicks on "Register Now" or navigates to `/student/register`
- She sees a professional, user-friendly registration form

#### **Step 2: Sarah Fills the Registration Form**

**Personal Information:**
- Full Name (English): Sarah Ahmed
- Full Name (Arabic): سارة أحمد
- Birth Date: 1998-05-15
- Gender: Female
- Nationality: Saudi Arabia
- Native Language: Arabic

**Contact Information:**
- Email: sarah.ahmed@email.com
- Phone: +966501234567

**Educational Background:**
- English Level: Intermediate
- Has Previous Certificate: Yes
- Certificate Type: TOEFL ITP Score 450

**Course Request:**
- "I would like to enroll in Business English courses to improve my professional communication skills. I am particularly interested in courses that focus on presentations and email writing."

**Documents Uploaded:**
- National ID (front and back)
- TOEFL certificate
- University degree

#### **Step 3: Submission**
- Sarah checks the terms and conditions
- Clicks "Submit Registration"
- Sees success page with registration number: **REG00001**
- Receives confirmation email: "Thank you for registering! Your application is being reviewed."

**Sarah's Experience:**
> "The registration process was so smooth! I filled everything out in about 10 minutes, and I got an immediate confirmation. Now I just need to wait for their response."

---

### **Phase 2: Administrative Review**

#### **Step 4: Agent Receives Notification**

**Agent: Fatima (Admissions Officer)**
- Receives email notification: "New student registration submitted"
- Logs into Odoo backend
- Navigates to: **Student Registrations → New Registrations**
- Sees Sarah's application (REG00001) in the list

#### **Step 5: Eligibility Review**

**Fatima's Actions:**
1. Opens Sarah's registration record
2. Reviews the information:
   - Age: 25 ✓ (meets minimum age)
   - English Level: Intermediate ✓
   - Has TOEFL certificate ✓
   - Clear course goals ✓

3. Clicks **"Start Review"** button
4. Status changes to: **Eligibility Review**

5. Adds eligibility notes:
   ```
   Eligibility Assessment:
   - Applicant meets age requirements (25 years old)
   - Has intermediate English level with TOEFL 450
   - Clear learning objectives for Business English
   - Previous education: University degree holder
   - Recommendation: APPROVED for Business English track
   ```

6. Clicks **"Approve Eligibility"** button
7. Status changes to: **Document Review**

**Fatima's Thought Process:**
> "Sarah looks like a great candidate. She has clear goals, previous English certification, and her TOEFL score shows she's ready for intermediate-level courses. Let me verify her documents now."

#### **Step 6: Document Verification**

**Fatima's Actions:**
1. Reviews uploaded documents:
   - National ID: Clear, valid, matches name ✓
   - TOEFL Certificate: Authentic, score 450 ✓
   - University Degree: Verified ✓

2. Adds document notes:
   ```
   Document Verification:
   - National ID verified (ID: 1234567890)
   - TOEFL ITP certificate verified (Score: 450, Date: 2023-08-15)
   - University degree verified (Bachelor's in Business Administration)
   - All documents are clear and authentic
   - Status: APPROVED
   ```

3. Clicks **"Approve Documents"** button
4. Status changes to: **Approved**

---

### **Phase 3: Student Record Creation**

#### **Step 7: Creating Sarah's Student Profile**

**Fatima's Actions:**
1. Clicks **"Finalize & Create Student"** button
2. System automatically:
   - Creates student record in database (Student ID: STU00001)
   - Creates portal user account (login: sarah.ahmed@email.com)
   - Sends password reset email to Sarah
   - Sends approval email with next steps

**Approval Email to Sarah:**
```
Subject: Congratulations! Your Registration is Approved - REG00001

Dear Sarah Ahmed,

We are pleased to inform you that your registration has been approved! 
Welcome to our academy.

Registration Number: REG00001
Student ID: STU00001
Approval Date: November 24, 2025

Your Portal Access:
- Login Email: sarah.ahmed@email.com
- You will receive a separate email to set your password

What's Next?
1. Check your email for password setup instructions
2. Log in to your student portal
3. View your course enrollments
4. Access course materials

We look forward to seeing you in class!

Best regards,
Academy Admissions Team
```

**Sarah's Reaction:**
> "Wow! I got approved in just 2 days! And they've already set up my student account. This is so professional!"

---

### **Phase 4: Portal Access Setup**

#### **Step 8: Sarah Sets Up Her Portal Account**

**Sarah's Actions:**
1. Receives password reset email
2. Clicks the link to set her password
3. Creates a secure password
4. Logs into the student portal at `/my`

**Sarah's Portal Dashboard:**
- My Registration: Shows REG00001 - Status: Approved ✓
- My Enrollments: (Empty - waiting for course assignment)
- My Certificates: (Empty - will appear after course completion)
- My Documents: Can upload additional documents if needed

---

### **Phase 5: Course Enrollment**

#### **Step 9: Fatima Enrolls Sarah in Courses**

**Fatima's Actions:**
1. Opens Sarah's registration record (REG00001)
2. Clicks **"Enroll in Courses"** button
3. Enrollment wizard opens
4. Selects courses for Sarah:
   - Business English Level 1 (8 weeks)
   - Professional Email Writing (4 weeks)
   - Presentation Skills (4 weeks)
5. Sets start date: December 1, 2025
6. Confirms enrollment

**System Actions:**
- Creates course session records
- Links Sarah (STU00001) to selected courses
- Sends enrollment confirmation email
- Updates registration status to: **Enrolled**

**Enrollment Confirmation Email to Sarah:**
```
Subject: Course Enrollment Confirmation - STU00001

Dear Sarah Ahmed,

You have been successfully enrolled in your courses!

Student ID: STU00001
Enrollment Date: November 24, 2025

Your Enrolled Courses:
1. Business English Level 1
   - Duration: 8 weeks
   - Start Date: December 1, 2025
   - Schedule: Sunday & Tuesday, 6:00 PM - 8:00 PM

2. Professional Email Writing
   - Duration: 4 weeks
   - Start Date: December 1, 2025
   - Schedule: Wednesday, 6:00 PM - 8:00 PM

3. Presentation Skills
   - Duration: 4 weeks
   - Start Date: December 8, 2025
   - Schedule: Thursday, 6:00 PM - 8:00 PM

Next Steps:
1. Log in to your student portal
2. Review your course schedule
3. Download course materials
4. Attend your first class on December 1st

Access Portal: http://academy.com/my

We look forward to seeing you in class!

Best regards,
Academy Team
```

---

### **Phase 6: Student Portal Experience**

#### **Step 10: Sarah Uses the Student Portal**

**Sarah's Portal Features:**

**1. My Enrollments**
- Lists all enrolled courses
- Shows progress for each course
- Displays upcoming classes
- Shows attendance records

**2. My Certificates**
- Will display certificates after course completion
- Download option for each certificate
- Request duplicate certificates

**3. My Documents**
- View uploaded documents
- Upload additional documents if requested
- Track document verification status

**4. My Registration**
- View original registration details
- See approval history
- Contact support if needed

**Sarah's Experience:**
> "I love the portal! I can see all my courses, track my progress, and even download my certificates when I complete the courses. Everything is in one place!"

---

### **Phase 7: Course Completion**

#### **Step 11: Sarah Completes Her First Course**

**After 8 Weeks:**
- Sarah completes "Business English Level 1"
- Passes final exam with 85%
- System automatically generates certificate
- Certificate appears in "My Certificates" section
- Sarah downloads her certificate as PDF

**Certificate Details:**
- Certificate Number: CERT00001
- Student: Sarah Ahmed (STU00001)
- Course: Business English Level 1
- Completion Date: January 26, 2026
- Grade: 85% (Excellent)
- Issued by: Academy Director

---

## Student Guide

### How to Register

1. **Visit the Registration Page**
   - Go to: `http://your-academy.com/student/register`
   - No login required

2. **Fill Personal Information**
   - Enter your full name in English and Arabic
   - Provide birth date, gender, nationality
   - Specify your native language

3. **Provide Contact Details**
   - Enter a valid email address (you'll use this to log in later)
   - Provide a phone number for contact

4. **Educational Background**
   - Select your English level honestly
   - Indicate if you have previous certificates
   - Specify certificate type if applicable

5. **Course Request**
   - Describe which courses you want to take
   - Explain your learning goals
   - Be specific about your interests

6. **Upload Documents**
   - National ID or passport
   - Previous certificates (if any)
   - Any other supporting documents
   - Accepted formats: PDF, JPG, PNG

7. **Submit**
   - Review all information
   - Check terms and conditions
   - Click "Submit Registration"
   - Save your registration number!

### How to Check Your Status

**Before Approval:**
- You'll receive email updates at each stage
- Check your email regularly

**After Approval:**
1. Log in to the student portal: `/my`
2. Click "My Registration"
3. View your current status and review notes

### How to Upload Additional Documents

1. Log in to student portal
2. Go to "My Registration"
3. Scroll to "Upload Additional Documents"
4. Select files
5. Click "Upload Documents"
6. Admin will be notified automatically

---

## Administrator Guide

### How to Review Registrations

#### **Eligibility Review Process**

1. **Access New Registrations**
   - Navigate to: **Student Registrations → New Registrations**
   - Filter by "Submitted" status

2. **Open Registration Record**
   - Click on a registration to open
   - Review all submitted information

3. **Start Review**
   - Click **"Start Review"** button
   - Status changes to "Eligibility Review"
   - You become the assigned reviewer

4. **Assess Eligibility**
   Check the following:
   - Age requirements met?
   - English level appropriate for requested courses?
   - Previous education/certificates valid?
   - Clear learning objectives?
   - Complete information provided?

5. **Add Review Notes**
   - Click in "Eligibility Notes" field
   - Document your assessment
   - Include specific reasons for decision
   - Be thorough for audit purposes

6. **Make Decision**
   - **To Approve:** Click **"Approve Eligibility"**
     - Moves to Document Review stage
   - **To Reject:** Click **"Reject"**
     - Add rejection reason
     - Student receives rejection email

#### **Document Review Process**

1. **Access Document Review Queue**
   - Navigate to: **Student Registrations → Document Review**

2. **Verify Documents**
   - Click on "Documents" tab
   - Review each uploaded file
   - Check for:
     - Authenticity
     - Clarity/readability
     - Validity dates
     - Name matches
     - Required documents present

3. **Add Document Notes**
   - Document verification results
   - Note any issues or concerns
   - List verified documents

4. **Make Decision**
   - **To Approve:** Click **"Approve Documents"**
     - Moves to Approved status
   - **To Reject:** Click **"Reject"**
     - Specify which documents are problematic
     - Student receives rejection email

#### **Finalization Process**

1. **Access Approved Registrations**
   - Navigate to: **Student Registrations → Approved**

2. **Create Student Record**
   - Click **"Finalize & Create Student"** button
   - System automatically:
     - Creates student record (gr.student)
     - Generates student ID
     - Creates portal user account
     - Sends approval email with login credentials

3. **Verify Creation**
   - Check "Student Record" field is populated
   - Verify student ID is assigned
   - Confirm approval email was sent

#### **Enrollment Process**

1. **Enroll in Courses**
   - Click **"Enroll in Courses"** button
   - Enrollment wizard opens

2. **Select Courses**
   - Choose appropriate courses based on:
     - Student's English level
     - Requested courses
     - Available schedules
     - Prerequisites met

3. **Set Schedule**
   - Assign start date
   - Select class times
   - Confirm instructor

4. **Confirm Enrollment**
   - Review selections
   - Click "Confirm"
   - Student receives enrollment confirmation email

### How to Handle Rejections

**Best Practices:**

1. **Be Specific**
   - Clearly state the reason for rejection
   - Reference specific requirements not met
   - Provide actionable feedback

2. **Be Professional**
   - Use polite, respectful language
   - Avoid personal judgments
   - Focus on objective criteria

3. **Offer Alternatives**
   - Suggest prerequisite courses if applicable
   - Recommend reapplication timeline
   - Provide contact for questions

**Example Rejection Reasons:**

**Eligibility Rejection:**
```
Thank you for your interest in our programs. After careful review, 
we are unable to approve your registration at this time due to the 
following reasons:

- English level assessment indicates beginner level, while requested 
  courses require intermediate proficiency
- We recommend completing our Foundation English course first
- You may reapply after completing the prerequisite course

Please contact admissions@academy.com for more information about 
our Foundation English program.
```

**Document Rejection:**
```
We have reviewed your submitted documents and require additional 
verification:

- National ID image is unclear - please upload a clearer scan
- Previous certificate needs official translation to English
- Missing: Proof of previous education

Please upload the required documents through your portal, and we 
will review your application again.
```

### Using Different Views

#### **Kanban View**
- **Best for:** Visual workflow management
- **How to use:**
  - Drag and drop cards between columns
  - Quick status overview
  - Group by state (default)
  - Color-coded by status

#### **List View**
- **Best for:** Detailed information review
- **How to use:**
  - Sort by any column
  - Filter by multiple criteria
  - Export to Excel
  - Bulk operations

#### **Form View**
- **Best for:** Detailed review and editing
- **Features:**
  - Complete information display
  - Workflow buttons in header
  - Chatter for communication
  - Document attachments
  - Full audit trail

### Reporting and Analytics

**Available Reports:**
1. **Registration Volume**
   - Track applications over time
   - Identify peak periods
   - Plan resource allocation

2. **Approval Rates**
   - Monitor approval/rejection ratios
   - Identify common rejection reasons
   - Improve processes

3. **Processing Time**
   - Track time in each stage
   - Identify bottlenecks
   - Optimize workflow

4. **Source Analysis**
   - Track where students hear about academy
   - Measure marketing effectiveness
   - Allocate marketing budget

---

## Workflow States

### State Diagram

```
┌─────────┐
│  DRAFT  │ (Student starts form but doesn't submit)
└────┬────┘
     │ Student clicks "Submit"
     ▼
┌──────────┐
│SUBMITTED │ (Waiting for admin review)
└────┬─────┘
     │ Admin clicks "Start Review"
     ▼
┌────────────────────┐
│ELIGIBILITY_REVIEW  │ (Admin reviewing qualifications)
└─────────┬──────────┘
          │
    ┌─────┴─────┐
    │           │
    ▼           ▼
┌─────────┐  ┌─────────────────┐
│REJECTED │  │DOCUMENT_REVIEW  │ (Admin verifying documents)
└─────────┘  └────────┬─────────┘
                      │
                ┌─────┴─────┐
                │           │
                ▼           ▼
          ┌─────────┐  ┌──────────┐
          │REJECTED │  │ APPROVED │ (Ready for finalization)
          └─────────┘  └────┬─────┘
                            │ Admin clicks "Finalize"
                            ▼
                       ┌──────────┐
                       │ ENROLLED │ (Student in courses)
                       └──────────┘
```

### State Descriptions

| State | Description | Who Can Act | Available Actions |
|-------|-------------|-------------|-------------------|
| **Draft** | Registration started but not submitted | Student | Submit |
| **Submitted** | Waiting for admin review | Admin | Start Review |
| **Eligibility Review** | Admin checking qualifications | Admin | Approve Eligibility, Reject |
| **Document Review** | Admin verifying documents | Admin | Approve Documents, Reject |
| **Approved** | Registration approved, ready for finalization | Admin | Finalize & Create Student |
| **Rejected** | Registration rejected | - | - (Final state) |
| **Enrolled** | Student enrolled in courses | Admin | View Enrollments |

---

## Troubleshooting

### Common Issues and Solutions

#### **Issue 1: Student Can't Access Registration Form**

**Symptoms:**
- 404 error when accessing `/student/register`
- Page doesn't load

**Solutions:**
1. Verify module is installed and upgraded
2. Check Odoo server is running
3. Clear browser cache
4. Try incognito/private browsing mode
5. Check URL is correct: `http://your-domain/student/register`

#### **Issue 2: Registration Submission Fails**

**Symptoms:**
- Error message after clicking Submit
- Form doesn't submit

**Solutions:**
1. Check all required fields are filled (marked with *)
2. Verify email format is valid
3. Ensure file uploads are not too large (max 10MB per file)
4. Check file formats are supported (PDF, JPG, PNG)
5. Try different browser

#### **Issue 3: Student Doesn't Receive Emails**

**Symptoms:**
- No confirmation email after submission
- No approval email after finalization

**Solutions:**
1. Check spam/junk folder
2. Verify email address is correct in registration
3. Check Odoo email configuration (Settings → Technical → Email → Outgoing Mail Servers)
4. Test email server connection
5. Check email templates are active

#### **Issue 4: Portal Login Doesn't Work**

**Symptoms:**
- Can't log in to student portal
- "Invalid username or password" error

**Solutions:**
1. Verify registration is approved and finalized
2. Check password reset email was received
3. Use "Forgot Password" link
4. Verify email address is correct
5. Contact admin to reset password manually

#### **Issue 5: Documents Won't Upload**

**Symptoms:**
- Upload button doesn't work
- Files don't appear after upload

**Solutions:**
1. Check file size (max 10MB)
2. Verify file format (PDF, JPG, PNG only)
3. Try different file
4. Check browser console for errors
5. Try different browser
6. Check internet connection

#### **Issue 6: Admin Can't See Registrations**

**Symptoms:**
- Registration list is empty
- Can't access registration menu

**Solutions:**
1. Verify user has correct access rights (Manager or Agent group)
2. Check filters - remove all filters to see all records
3. Refresh browser
4. Check module is installed
5. Verify database connection

#### **Issue 7: Kanban View Shows Error**

**Symptoms:**
- Error when switching to kanban view
- "Missing 'card' template" error

**Solutions:**
1. Upgrade module to latest version
2. Clear browser cache
3. Restart Odoo server
4. Check XML view definition is correct

---

## Best Practices

### For Students

1. **Be Honest**
   - Provide accurate information
   - Don't exaggerate English level
   - Upload authentic documents only

2. **Be Complete**
   - Fill all required fields
   - Upload all requested documents
   - Provide clear, readable scans

3. **Be Specific**
   - Clearly state your learning goals
   - Specify which courses interest you
   - Explain your background

4. **Be Responsive**
   - Check email regularly
   - Respond to requests for additional info
   - Upload documents promptly

5. **Keep Records**
   - Save your registration number
   - Keep copies of uploaded documents
   - Save confirmation emails

### For Administrators

1. **Be Timely**
   - Review registrations within 2-3 business days
   - Don't let applications sit too long
   - Set up email notifications

2. **Be Thorough**
   - Review all information carefully
   - Verify all documents
   - Document your decisions

3. **Be Consistent**
   - Apply same criteria to all applicants
   - Follow established policies
   - Document exceptions

4. **Be Communicative**
   - Provide clear feedback
   - Explain rejection reasons
   - Offer alternatives when possible

5. **Be Organized**
   - Use filters and views effectively
   - Keep notes up to date
   - Follow up on pending items

---

## Support

### For Students
- **Email:** admissions@academy.com
- **Phone:** +966 11 234 5678
- **Portal:** Contact support button in portal
- **Hours:** Sunday-Thursday, 9 AM - 5 PM

### For Administrators
- **Technical Support:** it@academy.com
- **Training:** Request training sessions
- **Documentation:** This guide + README.md

---

## Appendix

### Email Templates

All email templates can be customized in:
**Settings → Technical → Email → Templates**

Available templates:
1. `email_template_registration_confirmation`
2. `email_template_registration_rejected`
3. `email_template_registration_approved`
4. `email_template_enrollment_confirmation`

### Security Groups

- `base.group_portal` - Portal users (students)
- `grants_training_suite_v19.group_agent` - Staff
- `grants_training_suite_v19.group_manager` - Administrators

### Useful URLs

- Registration Form: `/student/register`
- Registration Success: `/student/register/success`
- Student Portal: `/my`
- My Registration: `/my/registration`

---

**Version:** 1.0  
**Last Updated:** November 24, 2025  
**Module:** student_enrollment_portal v19.0.1.0.0

