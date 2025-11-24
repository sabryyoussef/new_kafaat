# Student Documents Portal

A unified Odoo module for managing ALL student documents with both admin and portal functionality.

## Overview

This module provides **TWO complete document management workflows**:

### 1. Admin-Initiated Requests (`gr.document.request`)
Academy requests documents FROM students:
- Track required enrollment documents
- Set deadlines and priorities
- Manage compliance requirements
- Monitor student submissions

### 2. Student-Initiated Requests (`gr.document.request.portal`)  
Students manage their own documents:
- Submit document upload requests
- Request academy-issued documents
- Track request status
- View and download their documents

## Features

### For Administrators
**Admin-Initiated Workflow** (`gr.document.request`):
- **Create Document Requests**: Request specific documents from students
- **Set Deadlines**: Track submission deadlines and send reminders
- **Priority Management**: Mark documents as mandatory, high priority, urgent
- **Format Requirements**: Specify required format (original, certified copy, digital)
- **Review & Approve**: Verify submitted documents and approve/reject
- **Track Compliance**: Monitor which students have submitted required documents

**Student-Initiated Workflow** (`gr.document.request.portal`):
- **Process Requests**: Review student document uploads and requests
- **Status Updates**: Update status (Submitted → In Progress → Completed/Rejected)
- **Communication**: Add admin responses and notes visible to students
- **Document Handling**: Attach processed documents for student download

### For Students (Portal Users)
- **Submit Documents**: Proactively upload documents (transcripts, certificates, ID)
- **Request Documents**: Request academy-issued documents (certificates, transcripts)
- **Track Both Types**: See admin-requested documents AND self-initiated requests
- **Real-Time Status**: Monitor progress of all document interactions
- **Download**: Download completed/approved documents
- **Email Notifications**: Automatic updates at each stage
- **Complete History**: Access full history of all document exchanges

## Portal Routes

- `/my/documents` - List all document requests
- `/my/documents/new` - Submit new document request
- `/my/documents/<id>` - View request details

## Dependencies

- `grants_training_suite_v19` - Main training management module
- `portal` - Odoo portal framework
- `website` - Website builder
- `mail` - Messaging and chatter
- `documents` - Document management

## Installation

1. Place this module in your Odoo addons directory
2. Ensure `grants_training_suite_v19` is installed first
3. Update the Apps list
4. Install "Student Documents Portal"

## Configuration

No additional configuration required. The module inherits security groups from `grants_training_suite_v19`:
- Manager: Full access to all requests
- Agent: Can view and process requests
- Portal Users: Can only see their own requests

## Technical Details

### Models

- `gr.document.request.portal`: Main document request model with workflow

### Security

- Portal users can only view/edit their own requests
- Managers and agents have full access
- Record rules enforce data isolation

### Workflow States

1. **Draft**: Initial state (not used in portal)
2. **Submitted**: Student has submitted the request
3. **In Progress**: Admin is processing the request
4. **Completed**: Request fulfilled, documents available
5. **Rejected**: Request cannot be fulfilled

## Support

For issues or questions, contact the development team at Edafa.

## License

OEEL-1 (Odoo Enterprise Edition License)

