# Student Documents Portal

A dedicated Odoo module for managing student document requests with full portal functionality.

## Overview

This module provides a complete document management system for students, allowing them to:
- Submit document upload requests
- Request academy-issued documents
- Track request status
- View and download their documents

## Features

### For Students (Portal Users)
- **Submit Document Requests**: Upload documents or request documents from the academy
- **Track Status**: Monitor the progress of document requests in real-time
- **View History**: Access complete history of all document requests
- **Download Documents**: Download completed documents directly from the portal
- **Email Notifications**: Receive automatic updates when request status changes

### For Administrators
- **Request Management**: Review and process document requests
- **Status Tracking**: Update request status (Draft → Submitted → In Progress → Completed/Rejected)
- **Communication**: Add admin responses and notes visible to students
- **Document Attachment**: Attach processed documents for student download
- **Email Templates**: Automatic notifications at each stage

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

