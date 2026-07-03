# Batch Intake Module

A module for managing batch intakes for training programs.

## Features

- Batch intake creation and management
- Student enrollment tracking
- Capacity management with enrollment limits
- Progress tracking and statistics
- State management (Draft, Open, Closed, Cancelled)
- Integration with res.partner for student management

## Models

### batch.intake
Main model for batch intake management with the following features:
- Batch name and code (auto-generated)
- Start and end dates
- Maximum capacity and current enrollment tracking
- State workflow management
- Student relationship tracking

### res.partner (extended)
Extended to include `batch_intake_id` field for linking students to batch intakes.

## Security

- **Batch Intake Manager**: Full access to all batch intake functionality
- **Batch Intake User**: Access to batch intake management (read/write/create, no delete)

## Usage

1. Create a new batch intake with start/end dates and capacity
2. Open the batch to allow enrollments
3. Enroll students by linking them to the batch intake
4. Monitor enrollment progress and statistics
5. Close the batch when enrollment period ends

## Views

- Form view with status bar and student list
- List view with enrollment statistics
- Kanban view grouped by state
- Search view with filters and grouping options

