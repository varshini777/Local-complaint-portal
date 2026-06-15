# Admin Manual

## Admin Role

The admin manages users, officers, wards, complaints, system settings, activity logs, and reports.

## Dashboard

The admin dashboard displays:

- Total users
- Total citizens
- Total officers
- Total complaints
- Pending complaints
- Resolved complaints
- Closed complaints
- Escalated complaints
- Recent complaints
- Recent users

## User Management

Admin can:

- View all users
- Search users
- Filter by role
- Activate users
- Deactivate users

Admin users cannot be deactivated through the normal user toggle flow.

## Officer Management

Admin can:

- Create officers
- Edit officer details
- Activate officers
- Deactivate officers

Officer fields:

- Name
- Email
- Phone
- Password
- Active status

## Ward Management

Admin can:

- Create wards
- Edit wards
- Activate or deactivate wards
- Assign officers to wards

Ward fields:

- Ward name
- Ward code
- Assigned officer
- Active status

## Complaint Management

Admin can:

- View all complaints
- Search by complaint number or title
- Filter by status, priority, category, ward, and officer
- Assign or reassign complaints to officers
- Close resolved complaints

Only resolved complaints can be closed.

## System Settings

Admin can manage:

- `urgent_escalation_days`
- `critical_escalation_days`
- `max_upload_size_mb`

## Activity Logs

Admin can filter activity logs by:

- User
- Action
- Date

Activity logs record important operations such as login, complaint submission, assignment, closure, password reset, and user creation.

