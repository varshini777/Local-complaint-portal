CREATE DATABASE IF NOT EXISTS local_complaint_portal
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE local_complaint_portal;

SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS activity_logs;
DROP TABLE IF EXISTS feedback;
DROP TABLE IF EXISTS notifications;
DROP TABLE IF EXISTS complaint_updates;
DROP TABLE IF EXISTS complaints;
DROP TABLE IF EXISTS complaint_categories;
DROP TABLE IF EXISTS wards;
DROP TABLE IF EXISTS system_settings;
DROP TABLE IF EXISTS users;

SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE users (
  user_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
  full_name VARCHAR(120) NOT NULL,
  email VARCHAR(150) NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  phone VARCHAR(20) DEFAULT NULL,
  role ENUM('citizen', 'officer', 'admin') NOT NULL DEFAULT 'citizen',
  security_question VARCHAR(255) DEFAULT NULL,
  security_answer_hash VARCHAR(255) DEFAULT NULL,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (user_id),
  UNIQUE KEY uq_users_email (email),
  KEY idx_users_email (email),
  KEY idx_users_role (role),
  KEY idx_users_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE wards (
  ward_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
  ward_name VARCHAR(120) NOT NULL,
  ward_code VARCHAR(30) NOT NULL,
  assigned_officer_id INT UNSIGNED DEFAULT NULL,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (ward_id),
  UNIQUE KEY uq_wards_ward_code (ward_code),
  KEY idx_wards_assigned_officer_id (assigned_officer_id),
  KEY idx_wards_is_active (is_active),
  CONSTRAINT fk_wards_assigned_officer
    FOREIGN KEY (assigned_officer_id)
    REFERENCES users (user_id)
    ON DELETE SET NULL
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE complaint_categories (
  category_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
  category_name VARCHAR(100) NOT NULL,
  description VARCHAR(255) DEFAULT NULL,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (category_id),
  UNIQUE KEY uq_complaint_categories_name (category_name),
  KEY idx_complaint_categories_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE complaints (
  complaint_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
  complaint_number VARCHAR(30) NOT NULL,
  title VARCHAR(200) NOT NULL,
  description TEXT NOT NULL,
  category_id INT UNSIGNED NOT NULL,
  priority ENUM('Low', 'Medium', 'High', 'Emergency') NOT NULL DEFAULT 'Medium',
  status ENUM('Submitted', 'Assigned', 'In Progress', 'Resolved', 'Closed') NOT NULL DEFAULT 'Submitted',
  escalation_level ENUM('Normal', 'Urgent', 'Critical') NOT NULL DEFAULT 'Normal',
  location VARCHAR(255) NOT NULL,
  ward_id INT UNSIGNED NOT NULL,
  citizen_id INT UNSIGNED NOT NULL,
  assigned_officer_id INT UNSIGNED DEFAULT NULL,
  before_image_path VARCHAR(255) DEFAULT NULL,
  after_image_path VARCHAR(255) DEFAULT NULL,
  resolution_notes TEXT DEFAULT NULL,
  work_performed TEXT DEFAULT NULL,
  materials_used TEXT DEFAULT NULL,
  additional_remarks TEXT DEFAULT NULL,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  submitted_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  assigned_at TIMESTAMP NULL DEFAULT NULL,
  resolved_at TIMESTAMP NULL DEFAULT NULL,
  closed_at TIMESTAMP NULL DEFAULT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (complaint_id),
  UNIQUE KEY uq_complaints_complaint_number (complaint_number),
  KEY idx_complaints_complaint_number (complaint_number),
  KEY idx_complaints_status (status),
  KEY idx_complaints_priority (priority),
  KEY idx_complaints_category_id (category_id),
  KEY idx_complaints_ward_id (ward_id),
  KEY idx_complaints_citizen_id (citizen_id),
  KEY idx_complaints_assigned_officer_id (assigned_officer_id),
  KEY idx_complaints_escalation_level (escalation_level),
  KEY idx_complaints_submitted_at (submitted_at),
  KEY idx_complaints_is_active (is_active),
  CONSTRAINT fk_complaints_category
    FOREIGN KEY (category_id)
    REFERENCES complaint_categories (category_id)
    ON DELETE RESTRICT
    ON UPDATE CASCADE,
  CONSTRAINT fk_complaints_ward
    FOREIGN KEY (ward_id)
    REFERENCES wards (ward_id)
    ON DELETE RESTRICT
    ON UPDATE CASCADE,
  CONSTRAINT fk_complaints_citizen
    FOREIGN KEY (citizen_id)
    REFERENCES users (user_id)
    ON DELETE RESTRICT
    ON UPDATE CASCADE,
  CONSTRAINT fk_complaints_assigned_officer
    FOREIGN KEY (assigned_officer_id)
    REFERENCES users (user_id)
    ON DELETE SET NULL
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE complaint_updates (
  update_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
  complaint_id INT UNSIGNED NOT NULL,
  updated_by INT UNSIGNED DEFAULT NULL,
  status ENUM('Submitted', 'Assigned', 'In Progress', 'Resolved', 'Closed') NOT NULL,
  action VARCHAR(120) NOT NULL,
  remarks TEXT DEFAULT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (update_id),
  KEY idx_complaint_updates_complaint_id (complaint_id),
  KEY idx_complaint_updates_updated_by (updated_by),
  KEY idx_complaint_updates_status (status),
  KEY idx_complaint_updates_created_at (created_at),
  CONSTRAINT fk_complaint_updates_complaint
    FOREIGN KEY (complaint_id)
    REFERENCES complaints (complaint_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT fk_complaint_updates_updated_by
    FOREIGN KEY (updated_by)
    REFERENCES users (user_id)
    ON DELETE SET NULL
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE notifications (
  notification_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
  user_id INT UNSIGNED NOT NULL,
  complaint_id INT UNSIGNED DEFAULT NULL,
  message TEXT NOT NULL,
  notification_type ENUM('Complaint Submitted', 'Complaint Assigned', 'Status Updated', 'Complaint Resolved', 'Complaint Closed', 'System') NOT NULL DEFAULT 'System',
  is_read BOOLEAN NOT NULL DEFAULT FALSE,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (notification_id),
  KEY idx_notifications_user_id (user_id),
  KEY idx_notifications_is_read (is_read),
  KEY idx_notifications_complaint_id (complaint_id),
  KEY idx_notifications_created_at (created_at),
  CONSTRAINT fk_notifications_user
    FOREIGN KEY (user_id)
    REFERENCES users (user_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT fk_notifications_complaint
    FOREIGN KEY (complaint_id)
    REFERENCES complaints (complaint_id)
    ON DELETE SET NULL
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE feedback (
  feedback_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
  complaint_id INT UNSIGNED NOT NULL,
  citizen_id INT UNSIGNED NOT NULL,
  rating TINYINT UNSIGNED NOT NULL,
  comment TEXT DEFAULT NULL,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (feedback_id),
  UNIQUE KEY uq_feedback_complaint_id (complaint_id),
  KEY idx_feedback_citizen_id (citizen_id),
  KEY idx_feedback_rating (rating),
  KEY idx_feedback_is_active (is_active),
  CONSTRAINT chk_feedback_rating
    CHECK (rating BETWEEN 1 AND 5),
  CONSTRAINT fk_feedback_complaint
    FOREIGN KEY (complaint_id)
    REFERENCES complaints (complaint_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT fk_feedback_citizen
    FOREIGN KEY (citizen_id)
    REFERENCES users (user_id)
    ON DELETE RESTRICT
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE activity_logs (
  log_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
  user_id INT UNSIGNED DEFAULT NULL,
  action VARCHAR(150) NOT NULL,
  ip_address VARCHAR(45) DEFAULT NULL,
  details TEXT DEFAULT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (log_id),
  KEY idx_activity_logs_user_id (user_id),
  KEY idx_activity_logs_action (action),
  KEY idx_activity_logs_created_at (created_at),
  CONSTRAINT fk_activity_logs_user
    FOREIGN KEY (user_id)
    REFERENCES users (user_id)
    ON DELETE SET NULL
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE system_settings (
  setting_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
  setting_key VARCHAR(100) NOT NULL,
  setting_value VARCHAR(255) NOT NULL,
  setting_type ENUM('string', 'integer', 'decimal', 'boolean') NOT NULL DEFAULT 'string',
  description VARCHAR(255) DEFAULT NULL,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (setting_id),
  UNIQUE KEY uq_system_settings_setting_key (setting_key),
  KEY idx_system_settings_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO complaint_categories (category_name, description) VALUES
  ('Road Damage', 'Complaints related to potholes, broken roads, and unsafe road surfaces.'),
  ('Garbage', 'Complaints related to garbage collection, dumping, and waste management.'),
  ('Drainage', 'Complaints related to blocked drains, sewage overflow, and drainage issues.'),
  ('Water Leakage', 'Complaints related to leaking public water pipes and water wastage.'),
  ('Streetlight', 'Complaints related to damaged, missing, or non-working streetlights.'),
  ('Electricity', 'Complaints related to public electrical faults and civic electrical issues.'),
  ('Public Safety', 'Complaints related to hazards, unsafe public spaces, and safety concerns.'),
  ('Others', 'Complaints that do not fit into the listed categories.');

INSERT INTO system_settings (setting_key, setting_value, setting_type, description) VALUES
  ('urgent_escalation_days', '7', 'integer', 'Number of days after which unresolved complaints become urgent.'),
  ('critical_escalation_days', '15', 'integer', 'Number of days after which unresolved complaints become critical.'),
  ('max_upload_size_mb', '5', 'integer', 'Maximum allowed upload size in megabytes.');
