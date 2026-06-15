# Database Documentation

## Database

```text
local_complaint_portal
```

Engine:

```text
InnoDB
```

Charset:

```text
utf8mb4
```

## Tables

### users

Stores citizen, officer, and admin accounts.

Important fields:

- `user_id`
- `full_name`
- `email`
- `password_hash`
- `phone`
- `role`
- `security_question`
- `security_answer_hash`
- `is_active`
- `created_at`
- `updated_at`

Roles:

- `citizen`
- `officer`
- `admin`

### wards

Stores civic ward/area information.

Important fields:

- `ward_id`
- `ward_name`
- `ward_code`
- `assigned_officer_id`
- `is_active`

### complaint_categories

Stores complaint categories.

Default categories:

- Road Damage
- Garbage
- Drainage
- Water Leakage
- Streetlight
- Electricity
- Public Safety
- Others

### complaints

Stores complaint records.

Important fields:

- `complaint_id`
- `complaint_number`
- `title`
- `description`
- `category_id`
- `priority`
- `status`
- `escalation_level`
- `ward_id`
- `citizen_id`
- `assigned_officer_id`
- `before_image_path`
- `after_image_path`
- `resolution_notes`
- `work_performed`
- `materials_used`
- `additional_remarks`

Status values:

- Submitted
- Assigned
- In Progress
- Resolved
- Closed

Priority values:

- Low
- Medium
- High
- Emergency

Escalation values:

- Normal
- Urgent
- Critical

### complaint_updates

Stores complaint timeline events.

### notifications

Stores user notifications.

### feedback

Stores citizen feedback after complaint closure.

### activity_logs

Stores audit trail records.

### system_settings

Stores configurable values:

- `urgent_escalation_days`
- `critical_escalation_days`
- `max_upload_size_mb`

## Relationships

- One citizen can submit many complaints.
- One officer can be assigned many complaints.
- One ward can contain many complaints.
- One complaint can have many updates.
- One complaint can have one feedback record.
- One user can have many notifications.
- One user can have many activity logs.

