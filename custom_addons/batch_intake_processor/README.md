# Batch Intake Processor

A standalone Odoo 19 module for processing student intake applications in bulk via Excel/CSV uploads.

## Features

✅ **File Upload**: Upload student data via Excel (.xlsx, .xls) or CSV files  
✅ **Automatic Parsing**: Intelligent column mapping and data extraction  
✅ **Eligibility Validation**: Configurable criteria with automatic assessment  
✅ **Categorization**: Automatic classification as Eligible/Not Eligible  
✅ **Detailed Reports**: Validation notes with pass/fail reasons  
✅ **Export Results**: Export processed data to Excel/CSV  
✅ **No Dependencies**: Completely standalone - no custom module dependencies

## Installation

1. Copy this module to your Odoo `addons` directory
2. Install Python dependencies:
   ```bash
   pip install openpyxl xlrd
   ```
3. Restart Odoo server
4. Go to Apps > Update Apps List
5. Search for "Batch Intake Processor"
6. Click Install

## Usage Workflow

### 1. Configure Eligibility Criteria

Go to **Batch Intake > Configuration > Eligibility Criteria**

Set your requirements:
- Minimum/Maximum Age
- Required Education Level
- Minimum GPA
- Required English Level
- Required Pass Rate (%)

### 2. Prepare Your Data File

Create an Excel or CSV file with the following columns:

| Name | Email | Phone | Age | Nationality | Education | GPA | English Level |
|------|-------|-------|-----|-------------|-----------|-----|---------------|
| John Smith | john@example.com | +1234567890 | 22 | USA | Bachelor | 3.5 | Advanced |
| Jane Doe | jane@example.com | +1234567891 | 19 | UK | High School | 2.8 | Intermediate |

**Column Names** (case-insensitive, flexible):
- **Name**: name, full name, student name, applicant name
- **Email**: email, e-mail, email address
- **Phone**: phone, mobile, contact, phone number
- **Age**: age
- **Education**: education, education level, qualification
- **GPA**: gpa, grade, marks
- **Nationality**: nationality, country
- **English Level**: english, english level

###3. Upload and Process

**Method 1: Quick Upload**
1. Go to **Batch Intake > Batches**
2. Click **Create**
3. Upload your file
4. Click **Process File**

**Method 2: Upload Wizard**
1. Go to **Batch Intake > Upload Batch**
2. Select your file
3. Set intake date and description
4. Click **Upload and Process** (or **Upload Only** to review first)

### 4. Review Results

After processing, you'll see:
- **Total Applicants**: Number of records processed
- **Eligible**: Applicants who meet criteria
- **Not Eligible**: Applicants who don't meet criteria
- **Eligibility Rate**: Percentage of eligible applicants

Click **View Applicants** to see detailed results with validation notes for each applicant.

### 5. Export Results

1. Open a processed batch
2. Click **Export Results**
3. Choose format (Excel or CSV)
4. Select filter (All, Eligible Only, Not Eligible Only, etc.)
5. Choose whether to include validation notes
6. Click **Export**
7. Download the generated file

## Eligibility Validation Logic

The system checks each criterion and calculates an overall score:

```
Eligibility Score = (Passed Checks / Total Checks) × 100%
```

Example validation output:
```
✓✓✓ ELIGIBLE - Score: 100.0% (Required: 75.0%)
✓ Age (22) meets minimum requirement (18)
✓ Age (22) within maximum limit (35)
✓ Education level (Bachelor) meets requirement
✓ GPA (3.5) meets minimum (2.5)
✓ English level (Advanced) meets requirement
```

## Sample Files

### Excel Sample
Download template: [sample_intake.xlsx](static/sample_intake.xlsx)

### CSV Sample
```csv
Name,Email,Phone,Age,Nationality,Education,GPA,English Level
John Smith,john@example.com,+1234567890,22,USA,Bachelor,3.5,Advanced
Jane Doe,jane@example.com,+1234567891,19,UK,High School,2.8,Intermediate
Ahmed Ali,ahmed@example.com,+966501234567,25,Saudi Arabia,Bachelor,3.2,Advanced
```

## Configuration

### Eligibility Criteria Fields

- **Minimum Age**: Applicants must be at least this age
- **Maximum Age**: Applicants must not exceed this age (0 = no limit)
- **Required Education Level**: String match (e.g., "High School", "Bachelor")
- **Minimum GPA**: Minimum grade/GPA on a 0-100 scale
- **Required English Level**: String match (e.g., "Intermediate", "Advanced")
- **Required Pass Rate**: Percentage of criteria that must be met (e.g., 75% means 3 out of 4 checks must pass)

## Security

Two user groups are provided:

1. **Batch Intake User**: Can upload, process, and export batches
2. **Batch Intake Manager**: Full access including criteria configuration and batch deletion

## Technical Details

### Models

- `batch.intake`: Main batch processing records
- `batch.intake.applicant`: Individual applicant records
- `batch.intake.eligibility.criteria`: Configurable eligibility rules

### Wizards

- `batch.intake.upload.wizard`: File upload interface
- `batch.intake.export.wizard`: Results export interface

### Dependencies

**Odoo Modules**: `base`, `mail`  
**Python Packages**: `openpyxl`, `xlrd`

## Troubleshooting

### File Upload Errors

- **Invalid file type**: Ensure file is .xlsx, .xls, or .csv
- **Parsing errors**: Check that column names match expected format
- **Missing required fields**: Ensure "Name" column exists

### Eligibility Issues

- **All pending**: No eligibility criteria configured - create one first
- **Unexpected results**: Review criteria configuration and validation notes

## Support

For issues or questions:
- **Email**: support@edafa.sa
- **Website**: https://www.edafa.sa

## License

OEEL-1

---

**Version**: 19.0.1.0.0  
**Author**: Edafa  
**Category**: Education

