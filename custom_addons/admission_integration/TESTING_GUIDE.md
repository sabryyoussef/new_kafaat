# Admission Integration Module - Testing Guide

## 📋 Overview

This guide helps you test the `admission_integration` module. The module integrates three sources into OpenEduCat Admission:
- **Student Registration Portal** (`student_enrollment_portal`)
- **Batch Intake** (`batch_intake`)
- **Contact Pool Manager** (`contact_pool_manager`)

All students from these sources appear in the unified **OpenEduCat Admission** tree view.

---

## ✅ Prerequisites

- Module `admission_integration` is installed
- User has **Back Office Admin** or **Faculty** role
- At least one **Admission Register** exists (Admissions → Admission Registers)

---

## 🧪 Test Scenario 1: Student Registration Portal → Admission

### Step 1: Create Registration via Portal

**Portal URL:** `http://localhost:8019/student/register`

1. Open the portal URL in your browser
2. Fill the registration form:
   - **Student Name (English):** `Test Student Portal`
   - **Student Name (Arabic):** `طالب اختبار`
   - **Email:** `test.portal@example.com` (use unique email)
   - **Phone:** `+966501234567`
   - **Birth Date:** `2000-01-15`
   - **Gender:** `Male`
   - **Nationality:** `Saudi Arabia`
   - **English Level:** `Intermediate`
3. Click **"Submit Registration"**
4. ✅ Note your Registration Number (e.g., `REG00001`)

---

### Step 2: Approve Registration (Backend)

**Menu Path:** `Student Registrations` → `New Registrations`

1. Log in as admin/back office user
2. Go to: **Student Registrations** → **New Registrations**
3. Find and open your registration (`REG00001`)
4. Approve through workflow:
   - Click **"Start Review"** (Draft → Submitted)
   - Click **"Approve Eligibility"** (Submitted → Eligibility Review)
   - Click **"Approve Documents"** (Eligibility Review → Document Review)
   - Click **"Final Approve"** (Document Review → Approved)
5. ✅ Verify state is **"Approved"**

---

### Step 3: Create Admission from Registration

**Menu Path:** `Student Registrations` → `New Registrations` → [Open Registration]

1. In the approved registration form, look for **"Create Admission"** button in header
2. Click **"Create Admission"**
3. ✅ **Expected:** Admission record opens in new window
4. ✅ **Expected:** Admission Number generated (e.g., `ADM00001`)
5. ✅ **Expected:** Registration form shows "Admission Information" section with link

---

### Step 4: Verify in Admission Tree View

**Menu Path:** `Admissions` → `Admissions`

1. Navigate to: **Admissions** → **Admissions**
2. Find your admission:
   - Search by name: `Test Student Portal`
   - Or by application number
3. ✅ **Check:**
   - Application Number is populated
   - Name: `Test Student Portal`
   - **Source Type:** `Student Registration Portal` ✅
   - State: `Submitted`

---

### Step 5: Verify Admission Details

**Menu Path:** `Admissions` → `Admissions` → [Open Admission]

1. Open the admission record
2. Scroll to **"Source Information"** section
3. ✅ **Verify:**
   - Source Type: `Student Registration Portal`
   - Source Registration: Link to your registration
   - Is Imported: `Yes`
4. Click **"View Source"** button in header
5. ✅ **Expected:** Opens original registration in new window

---

### Step 6: Test Duplicate Prevention

**Menu Path:** `Student Registrations` → `New Registrations` → [Open Registration]

1. Go back to your registration
2. Try clicking **"Create Admission"** again
3. ✅ **Expected:** Error: "Admission record already exists for this registration"

---

## 🧪 Test Scenario 2: Batch Intake → Admission

### Step 1: Create Batch Intake

**Menu Path:** `Batch Intake` → `Batch Intakes`

1. Navigate to: **Batch Intake** → **Batch Intakes**
2. Click **"Create"**
3. Fill form:
   - **Name:** `Test Batch Intake`
   - **Course:** Select an OpenEduCat course
   - **Batch:** (Optional) Select a batch
4. Click **"Save"**

---

### Step 2: Upload Student File

**Menu Path:** `Batch Intake` → `Batch Intakes` → [Open Batch]

1. Open your batch intake
2. Click **"Download Template"** to get CSV template
3. Create a CSV file with test data:
   ```csv
   Name,Email,Phone,Birth Date,Gender
   Test Student Batch1,test.batch1@example.com,+966501111111,2000-02-15,Male
   Test Student Batch2,test.batch2@example.com,+966502222222,2000-03-20,Female
   ```
4. Click **"Upload File"** and select your CSV
5. Click **"Validate File"**
6. Click **"Process File"**
7. ✅ **Expected:** State changes to "Processed"
8. ✅ **Expected:** Students appear in "OpenEduCat Students" tab

---

### Step 3: Create Admissions from Batch

**Menu Path:** `Batch Intake` → `Batch Intakes` → [Open Batch]

1. In the batch intake form, look for **"Create Admissions"** button in header
2. Click **"Create Admissions"**
3. ✅ **Expected:** Success message: "Created X admission record(s)"
4. ✅ **Expected:** List view of created admissions opens

---

### Step 4: Verify in Admission Tree View

**Menu Path:** `Admissions` → `Admissions`

1. Navigate to: **Admissions** → **Admissions**
2. Click filter: **"From Batch Intake"**
3. ✅ **Expected:** See 2 admissions (one per student)
4. ✅ **Check each admission:**
   - Source Type: `Batch Intake` ✅
   - Course and Batch populated (if set in batch)
   - Student names match: `Test Student Batch1`, `Test Student Batch2`

---

### Step 5: Verify Individual Admission

**Menu Path:** `Admissions` → `Admissions` → [Open Admission]

1. Open one of the batch admissions
2. ✅ **Verify:**
   - Student information matches batch student
   - Course/Batch from batch intake
   - Source Batch Intake: Link to batch intake
3. Click **"View Source"** button
4. ✅ **Expected:** Opens batch intake in new window

---

### Step 6: Test Duplicate Prevention

**Menu Path:** `Batch Intake` → `Batch Intakes` → [Open Batch]

1. Go back to batch intake
2. Try clicking **"Create Admissions"** again
3. ✅ **Expected:** Error: "No new admissions created. All students already have admission records."

---

## 🧪 Test Scenario 3: Contact Pool → Admission

### Step 1: Create Contact Pool

**Menu Path:** `Contact Pool Manager` → `Contact Pools`

1. Navigate to: **Contact Pool Manager** → **Contact Pools**
2. Click **"Create"**
3. Fill form:
   - **Name:** `Test Contact Pool`
4. Click **"Save"**

---

### Step 2: Add Contacts to Pool

**Menu Path:** `Contacts` → `Contacts`

**Option A: Create New Contacts**
1. Navigate to: **Contacts** → **Contacts**
2. Create 2-3 contacts:
   - **Contact 1:**
     - Name: `Test Contact 1`
     - Email: `test.contact1@example.com`
     - Phone: `+966503333333`
     - **Important:** Ensure "Is a Company" is **NOT** checked
   - **Contact 2:**
     - Name: `Test Contact 2`
     - Email: `test.contact2@example.com`
     - Phone: `+966504444444`
     - **Important:** Ensure "Is a Company" is **NOT** checked

**Option B: Assign Existing Contacts**
1. Go to: **Contact Pool Manager** → **Contact Pools** → [Open Pool]
2. Click **"Batch Assign Contacts"**
3. Select your contacts and assign

3. ✅ **Verify:** Contact Count shows 2-3 in pool

---

### Step 3: Create Admissions from Contacts

**Menu Path:** `Contact Pool Manager` → `Contact Pools` → [Open Pool]

1. Open your contact pool
2. Look for **"Create Admissions from Contacts"** button in header
3. Click the button
4. ✅ **Expected:** Success message: "Created X admission record(s)"
5. ✅ **Expected:** List view of created admissions opens

---

### Step 4: Verify in Admission Tree View

**Menu Path:** `Admissions` → `Admissions`

1. Navigate to: **Admissions** → **Admissions**
2. Click filter: **"From Contact Pool"**
3. ✅ **Expected:** See admissions for eligible contacts
4. ✅ **Check each admission:**
   - Source Type: `Contact Pool Manager` ✅
   - State: `Draft` (needs review)
   - Student names match: `Test Contact 1`, `Test Contact 2`

---

### Step 5: Verify Individual Admission

**Menu Path:** `Admissions` → `Admissions` → [Open Admission]

1. Open one of the pool admissions
2. ✅ **Verify:**
   - Contact information populated
   - Source Contact Pool: Link to pool
   - Source Contact: Link to contact/partner
3. Click **"View Source"** button
4. ✅ **Expected:** Opens contact pool in new window

---

## 🧪 Test Scenario 4: Unified View & Filters

### Step 1: View All Admissions

**Menu Path:** `Admissions` → `Admissions`

1. Navigate to: **Admissions** → **Admissions**
2. Remove all filters (click "Clear" or remove active filters)
3. ✅ **Expected:** See admissions from all three sources:
   - From Student Registration Portal
   - From Batch Intake
   - From Contact Pool
   - Manual entries (if any)

---

### Step 2: Test Source Filters

**Menu Path:** `Admissions` → `Admissions` → [Search Bar]

1. Click filter: **"From Registration Portal"**
   - ✅ **Expected:** Only portal admissions shown

2. Click filter: **"From Batch Intake"**
   - ✅ **Expected:** Only batch admissions shown

3. Click filter: **"From Contact Pool"**
   - ✅ **Expected:** Only pool admissions shown

4. Click filter: **"Imported"**
   - ✅ **Expected:** All three source types shown

5. Click filter: **"Manual Entry"**
   - ✅ **Expected:** Only manually created admissions shown

---

### Step 3: Test Group By

**Menu Path:** `Admissions` → `Admissions` → [Group By]

1. Click **"Group By"** dropdown
2. Select **"Source Type"**
3. ✅ **Expected:** Admissions grouped by:
   - Manual Entry
   - Student Registration Portal
   - Batch Intake
   - Contact Pool Manager

---

## 🧪 Test Scenario 5: Admission Workflow

### Step 1: Test Workflow on Imported Admission

**Menu Path:** `Admissions` → `Admissions` → [Open Admission]

1. Open any imported admission (from any source)
2. Test workflow buttons:
   - Click **"Submit"** (if in Draft)
   - Click **"Confirm"** (if in Submit/Pending)
   - Click **"Admission Confirm"** (if in Confirm)
   - Click **"Enroll"** (if in Admission)
3. ✅ **Expected:** Each state transition works
4. ✅ **Expected:** Source information persists through workflow

---

## ✅ Final Verification Checklist

After completing all scenarios, verify:

- [ ] ✅ Portal registration → Admission created successfully
- [ ] ✅ Batch intake → Multiple admissions created successfully
- [ ] ✅ Contact pool → Multiple admissions created successfully
- [ ] ✅ All admissions appear in unified tree view
- [ ] ✅ Source Type column shows correctly for all
- [ ] ✅ Filters work for each source type
- [ ] ✅ "View Source" button works for all sources
- [ ] ✅ Duplicate prevention works (can't create twice)
- [ ] ✅ Normal admission workflow functions
- [ ] ✅ No errors in Odoo logs

---

## 🐛 Troubleshooting

### Issue: "Create Admission" button not visible

**Solution:**
- Ensure registration is in **"Approved"** state
- Check user has **Back Office Admin** or **Faculty** role
- Verify `source_admission_id` field is empty

**Menu to check:** `Settings` → `Users & Companies` → `Users` → [Your User] → `Access Rights`

---

### Issue: "No default admission register found"

**Solution:**
1. Navigate to: **Admissions** → **Admission Registers**
2. Create a new register:
   - **Name:** `Default Register 2025`
   - **Start Date:** Today's date
   - **End Date:** One year from today
   - **Active:** Checked
3. Save and try again

---

### Issue: Admissions not appearing in tree view

**Solution:**
- Remove all active filters
- Check user has read access to `op.admission` model
- Verify source type is set correctly in admission record

---

### Issue: "View Source" button not working

**Solution:**
- Verify source record still exists (not deleted)
- Check source type is set correctly
- Ensure source reference fields are populated

---

## 📊 Expected Results Summary

| Source | Button Location | Admission State | Source Type |
|--------|----------------|-----------------|-------------|
| Student Registration Portal | Registration form header | `Submitted` | `Student Registration Portal` |
| Batch Intake | Batch intake form header | `Submitted` | `Batch Intake` |
| Contact Pool | Contact pool form header | `Draft` | `Contact Pool Manager` |

---

## 📝 Notes

- **Default Admission Register:** Module creates one automatically if none exists, but it's better to create manually
- **State Management:**
  - Portal/Batch admissions start at `Submitted`
  - Contact Pool admissions start at `Draft` (needs manual review)
- **Course Assignment:**
  - Batch Intake: Course/Batch from batch intake
  - Portal/Pool: May need manual course assignment

---

**Happy Testing! 🎉**

If you encounter any issues, check the Odoo logs or contact support.

