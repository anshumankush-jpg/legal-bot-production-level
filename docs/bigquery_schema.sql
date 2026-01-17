-- LegalAI BigQuery Schema
-- Dataset: legalai
-- Tables: identity_users, lawyer_applications, login_events

-- Create dataset (run once)
-- CREATE SCHEMA IF NOT EXISTS legalai;

-- ============================================================================
-- Table 1: identity_users
-- Stores user identity mapping and roles
-- ============================================================================
CREATE TABLE IF NOT EXISTS `legalai.identity_users` (
  user_id STRING NOT NULL,                    -- UUID v4 (our internal stable ID)
  auth_provider STRING NOT NULL,              -- google|microsoft|email
  auth_uid STRING NOT NULL,                   -- Provider's UID
  email STRING NOT NULL,
  display_name STRING,
  photo_url STRING,
  role STRING NOT NULL,                       -- customer|lawyer|admin
  lawyer_status STRING,                       -- not_applicable|pending|approved|rejected
  is_active BOOLEAN DEFAULT TRUE,
  is_verified BOOLEAN DEFAULT FALSE,          -- Email verified
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
  last_login_at TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  env STRING NOT NULL,                        -- dev|staging|prod
  metadata JSON                               -- Additional flexible data
)
PARTITION BY DATE(created_at)
CLUSTER BY role, lawyer_status
OPTIONS(
  description="User identity and role mapping for LegalAI",
  require_partition_filter=false
);

-- Unique constraint simulation (BigQuery doesn't support PRIMARY KEY)
-- Ensure uniqueness via application logic: upsert by (auth_uid, auth_provider, env)

-- ============================================================================
-- Table 2: lawyer_applications
-- Stores lawyer verification applications
-- ============================================================================
CREATE TABLE IF NOT EXISTS `legalai.lawyer_applications` (
  application_id STRING NOT NULL,             -- UUID for application
  user_id STRING NOT NULL,                    -- FK to identity_users.user_id
  
  -- Personal Information
  full_name STRING NOT NULL,
  email STRING NOT NULL,
  phone_number STRING,
  
  -- Jurisdiction
  country STRING NOT NULL,                    -- Canada|USA
  jurisdiction STRING NOT NULL,               -- Province/State (e.g., Ontario, California)
  
  -- Bar Information
  bar_number STRING NOT NULL,                 -- Bar council or state bar number
  regulator_name STRING NOT NULL,             -- e.g., "Law Society of Ontario", "State Bar of California"
  bar_admission_date DATE,
  
  -- Professional Details
  practice_areas ARRAY<STRING>,               -- ["Criminal Law", "Family Law"]
  years_of_experience INT64,
  firm_name STRING,
  firm_address STRING,
  website_url STRING,
  
  -- Documents (GCS URLs)
  bar_license_url STRING NOT NULL,            -- Required: Bar license/certificate
  government_id_url STRING,                   -- Recommended: Gov't photo ID
  credentials_url STRING,                     -- Optional: Additional credentials
  
  -- Application Status
  status STRING NOT NULL DEFAULT 'pending',   -- pending|approved|rejected
  reviewer_id STRING,                         -- Admin who reviewed
  reviewer_notes STRING,                      -- Why approved/rejected
  submitted_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
  reviewed_at TIMESTAMP,
  
  -- Metadata
  env STRING NOT NULL,
  metadata JSON
)
PARTITION BY DATE(submitted_at)
CLUSTER BY status, country, jurisdiction
OPTIONS(
  description="Lawyer verification applications for LegalAI"
);

-- ============================================================================
-- Table 3: login_events
-- Audit log for login activity
-- ============================================================================
CREATE TABLE IF NOT EXISTS `legalai.login_events` (
  event_id STRING NOT NULL,                   -- UUID
  user_id STRING NOT NULL,
  auth_provider STRING NOT NULL,
  event_type STRING NOT NULL,                 -- login|logout|failed_login|token_refresh
  ip_address STRING,
  user_agent STRING,
  country STRING,                             -- Geolocation
  city STRING,
  success BOOLEAN DEFAULT TRUE,
  failure_reason STRING,                      -- If success=false
  timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
  env STRING NOT NULL,
  metadata JSON
)
PARTITION BY DATE(timestamp)
CLUSTER BY user_id, event_type
OPTIONS(
  description="Login audit trail for LegalAI"
);

-- ============================================================================
-- Table 4: user_sessions
-- Active sessions for security tracking
-- ============================================================================
CREATE TABLE IF NOT EXISTS `legalai.user_sessions` (
  session_id STRING NOT NULL,                 -- UUID
  user_id STRING NOT NULL,
  auth_token_hash STRING NOT NULL,            -- SHA256 hash of token
  refresh_token_hash STRING,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
  expires_at TIMESTAMP NOT NULL,
  last_activity_at TIMESTAMP,
  ip_address STRING,
  user_agent STRING,
  is_active BOOLEAN DEFAULT TRUE,
  revoked_at TIMESTAMP,
  revoke_reason STRING,
  env STRING NOT NULL
)
PARTITION BY DATE(created_at)
CLUSTER BY user_id, is_active
OPTIONS(
  description="Active user sessions for LegalAI"
);

-- ============================================================================
-- Table 5: rbac_permissions
-- Role-based access control permissions
-- ============================================================================
CREATE TABLE IF NOT EXISTS `legalai.rbac_permissions` (
  permission_id STRING NOT NULL,
  role STRING NOT NULL,                       -- customer|lawyer|admin
  resource STRING NOT NULL,                   -- /tools/document-generator, /leads/*
  action STRING NOT NULL,                     -- read|write|delete|execute
  allowed BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  env STRING NOT NULL
)
CLUSTER BY role, resource;

-- ============================================================================
-- MERGE (UPSERT) QUERIES
-- ============================================================================

-- Example: Upsert identity_users
-- MERGE `legalai.identity_users` AS target
-- USING (
--   SELECT
--     @user_id AS user_id,
--     @auth_provider AS auth_provider,
--     @auth_uid AS auth_uid,
--     @email AS email,
--     @display_name AS display_name,
--     @photo_url AS photo_url,
--     @role AS role,
--     @lawyer_status AS lawyer_status,
--     TRUE AS is_active,
--     @is_verified AS is_verified,
--     CURRENT_TIMESTAMP() AS created_at,
--     CURRENT_TIMESTAMP() AS last_login_at,
--     CURRENT_TIMESTAMP() AS updated_at,
--     @env AS env,
--     NULL AS metadata
-- ) AS source
-- ON target.auth_uid = source.auth_uid 
--    AND target.auth_provider = source.auth_provider 
--    AND target.env = source.env
-- WHEN MATCHED THEN
--   UPDATE SET
--     last_login_at = source.last_login_at,
--     updated_at = source.updated_at,
--     display_name = source.display_name,
--     photo_url = source.photo_url,
--     is_verified = source.is_verified
-- WHEN NOT MATCHED THEN
--   INSERT (
--     user_id, auth_provider, auth_uid, email, display_name, photo_url,
--     role, lawyer_status, is_active, is_verified, created_at, last_login_at,
--     updated_at, env, metadata
--   )
--   VALUES (
--     source.user_id, source.auth_provider, source.auth_uid, source.email,
--     source.display_name, source.photo_url, source.role, source.lawyer_status,
--     source.is_active, source.is_verified, source.created_at, source.last_login_at,
--     source.updated_at, source.env, source.metadata
--   );

-- ============================================================================
-- SAMPLE RBAC PERMISSIONS (Insert these)
-- ============================================================================

-- Customer permissions
INSERT INTO `legalai.rbac_permissions` (permission_id, role, resource, action, allowed, env)
VALUES
  (GENERATE_UUID(), 'customer', '/app/*', 'read', TRUE, 'prod'),
  (GENERATE_UUID(), 'customer', '/api/chat', 'execute', TRUE, 'prod'),
  (GENERATE_UUID(), 'customer', '/tools/*', 'read', FALSE, 'prod');

-- Lawyer (verified) permissions
INSERT INTO `legalai.rbac_permissions` (permission_id, role, resource, action, allowed, env)
VALUES
  (GENERATE_UUID(), 'lawyer', '/lawyer/dashboard', 'read', TRUE, 'prod'),
  (GENERATE_UUID(), 'lawyer', '/tools/document-generator', 'execute', TRUE, 'prod'),
  (GENERATE_UUID(), 'lawyer', '/tools/amendment-generator', 'execute', TRUE, 'prod'),
  (GENERATE_UUID(), 'lawyer', '/leads/*', 'read', TRUE, 'prod'),
  (GENERATE_UUID(), 'lawyer', '/leads/*', 'write', TRUE, 'prod');

-- Admin permissions
INSERT INTO `legalai.rbac_permissions` (permission_id, role, resource, action, allowed, env)
VALUES
  (GENERATE_UUID(), 'admin', '/*', 'read', TRUE, 'prod'),
  (GENERATE_UUID(), 'admin', '/*', 'write', TRUE, 'prod'),
  (GENERATE_UUID(), 'admin', '/admin/*', 'execute', TRUE, 'prod');

-- ============================================================================
-- VIEWS FOR ANALYTICS
-- ============================================================================

CREATE OR REPLACE VIEW `legalai.v_active_lawyers` AS
SELECT
  u.user_id,
  u.email,
  u.display_name,
  a.full_name,
  a.jurisdiction,
  a.bar_number,
  a.practice_areas,
  a.status AS application_status,
  u.last_login_at
FROM `legalai.identity_users` u
JOIN `legalai.lawyer_applications` a
  ON u.user_id = a.user_id
WHERE u.role = 'lawyer'
  AND u.lawyer_status = 'approved'
  AND u.is_active = TRUE;

CREATE OR REPLACE VIEW `legalai.v_pending_lawyers` AS
SELECT
  u.user_id,
  u.email,
  a.full_name,
  a.jurisdiction,
  a.bar_number,
  a.submitted_at,
  DATE_DIFF(CURRENT_DATE(), DATE(a.submitted_at), DAY) AS days_pending
FROM `legalai.identity_users` u
JOIN `legalai.lawyer_applications` a
  ON u.user_id = a.user_id
WHERE u.role = 'lawyer'
  AND u.lawyer_status = 'pending'
  AND a.status = 'pending'
ORDER BY a.submitted_at ASC;

CREATE OR REPLACE VIEW `legalai.v_login_stats` AS
SELECT
  DATE(timestamp) AS login_date,
  auth_provider,
  event_type,
  COUNT(*) AS event_count,
  COUNT(DISTINCT user_id) AS unique_users
FROM `legalai.login_events`
WHERE DATE(timestamp) >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
GROUP BY login_date, auth_provider, event_type
ORDER BY login_date DESC;

-- ============================================================================
-- Table 6: conversations
-- ChatGPT-like conversation storage (user-scoped)
-- ============================================================================
CREATE TABLE IF NOT EXISTS `legalai.conversations` (
  conversation_id STRING NOT NULL,            -- UUID
  user_id STRING NOT NULL,                    -- FK to identity_users.user_id
  title STRING,                               -- Auto-generated or user-edited
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
  is_archived BOOLEAN DEFAULT FALSE,
  is_pinned BOOLEAN DEFAULT FALSE,
  message_count INT64 DEFAULT 0,
  env STRING NOT NULL,
  metadata JSON                               -- { model, custom_instructions, etc. }
)
PARTITION BY DATE(created_at)
CLUSTER BY user_id, updated_at
OPTIONS(
  description="User conversations (ChatGPT-like chat history)"
);

-- ============================================================================
-- Table 7: messages
-- Individual messages within conversations
-- ============================================================================
CREATE TABLE IF NOT EXISTS `legalai.messages` (
  message_id STRING NOT NULL,                 -- UUID
  conversation_id STRING NOT NULL,            -- FK to conversations
  user_id STRING NOT NULL,                    -- Redundant for security scoping
  role STRING NOT NULL,                       -- 'user' | 'assistant' | 'system' | 'tool'
  content STRING,                             -- Message text
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
  tokens_used INT64,                          -- For usage tracking
  model_used STRING,                          -- e.g., 'gpt-4o-mini'
  env STRING NOT NULL,
  metadata JSON                               -- { citations, tool_calls, etc. }
)
PARTITION BY DATE(created_at)
CLUSTER BY conversation_id, user_id
OPTIONS(
  description="Messages within conversations"
);

-- ============================================================================
-- Table 8: attachments
-- User-uploaded files (images, PDFs, documents)
-- ============================================================================
CREATE TABLE IF NOT EXISTS `legalai.attachments` (
  attachment_id STRING NOT NULL,              -- UUID
  user_id STRING NOT NULL,
  conversation_id STRING,                     -- Nullable (can upload before chat)
  file_name STRING NOT NULL,
  file_type STRING NOT NULL,                  -- MIME type
  file_size INT64,                            -- Bytes
  gcs_url STRING NOT NULL,                    -- gs://bucket/path
  gcs_bucket STRING,
  gcs_path STRING,
  sha256 STRING,                              -- Checksum for deduplication
  status STRING DEFAULT 'completed',          -- 'uploading' | 'completed' | 'failed'
  uploaded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
  env STRING NOT NULL,
  metadata JSON                               -- { ocr_text, width, height, etc. }
)
PARTITION BY DATE(uploaded_at)
CLUSTER BY user_id, conversation_id
OPTIONS(
  description="User-uploaded files and images"
);

-- ============================================================================
-- Table 9: activity_events
-- User activity audit log (search, clicks, downloads, etc.)
-- ============================================================================
CREATE TABLE IF NOT EXISTS `legalai.activity_events` (
  event_id STRING NOT NULL,
  user_id STRING NOT NULL,
  event_type STRING NOT NULL,                 -- 'search', 'view_conversation', 'download_doc', etc.
  event_subtype STRING,
  payload JSON,                               -- Flexible event data
  ip_address STRING,
  user_agent STRING,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
  env STRING NOT NULL
)
PARTITION BY DATE(created_at)
CLUSTER BY user_id, event_type
OPTIONS(
  description="User activity and analytics events"
);

-- ============================================================================
-- INDEXES (for faster queries)
-- Note: BigQuery doesn't have explicit indexes, but clustering provides similar benefits
-- ============================================================================

-- Conversations by user + recent
-- Already clustered by user_id, updated_at

-- Messages by conversation
-- Already clustered by conversation_id, user_id

-- Search optimization: Consider creating a separate search index table if needed
CREATE TABLE IF NOT EXISTS `legalai.search_index` (
  index_id STRING NOT NULL,
  user_id STRING NOT NULL,
  conversation_id STRING,
  message_id STRING,
  attachment_id STRING,
  searchable_text STRING,                     -- Combined text for full-text search
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
  env STRING NOT NULL
)
PARTITION BY DATE(created_at)
CLUSTER BY user_id
OPTIONS(
  description="Search index for fast user-scoped full-text search"
);

-- ============================================================================
-- VIEWS FOR CHAT HISTORY
-- ============================================================================

CREATE OR REPLACE VIEW `legalai.v_user_conversations` AS
SELECT
  c.conversation_id,
  c.user_id,
  c.title,
  c.created_at,
  c.updated_at,
  c.is_archived,
  c.is_pinned,
  c.message_count,
  (SELECT content FROM `legalai.messages` 
   WHERE conversation_id = c.conversation_id 
   ORDER BY created_at ASC LIMIT 1) AS first_message,
  (SELECT created_at FROM `legalai.messages` 
   WHERE conversation_id = c.conversation_id 
   ORDER BY created_at DESC LIMIT 1) AS last_message_at
FROM `legalai.conversations` c
WHERE c.is_archived = FALSE
ORDER BY c.updated_at DESC;

CREATE OR REPLACE VIEW `legalai.v_user_activity_summary` AS
SELECT
  user_id,
  COUNT(DISTINCT CASE WHEN event_type = 'login' THEN DATE(created_at) END) AS login_days,
  COUNT(DISTINCT CASE WHEN event_type = 'new_conversation' THEN event_id END) AS conversations_created,
  COUNT(DISTINCT CASE WHEN event_type = 'send_message' THEN event_id END) AS messages_sent,
  COUNT(DISTINCT CASE WHEN event_type = 'upload_file' THEN event_id END) AS files_uploaded,
  COUNT(DISTINCT CASE WHEN event_type = 'search' THEN event_id END) AS searches_performed,
  MAX(created_at) AS last_activity_at
FROM `legalai.activity_events`
WHERE DATE(created_at) >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
GROUP BY user_id;
