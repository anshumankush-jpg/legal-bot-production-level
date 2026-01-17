-- LEGID Production Database Schema for BigQuery
-- Run this script to create all required tables

-- ============================================================================
-- 1. USERS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS `legid_production.users` (
  user_id STRING NOT NULL,
  email STRING NOT NULL,
  password_hash STRING,  -- NULL for Google OAuth users
  display_name STRING,
  username STRING,
  role STRING NOT NULL,  -- Client, Lawyer, Admin
  avatar_url STRING,
  auth_provider STRING,  -- google, email
  google_id STRING,
  email_verified BOOL DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  last_login TIMESTAMP
)
OPTIONS(
  description="User accounts with authentication details"
);

-- ============================================================================
-- 2. USER PREFERENCES TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS `legid_production.user_preferences` (
  user_id STRING NOT NULL,
  theme STRING DEFAULT 'dark',  -- dark, light, system
  font_size STRING DEFAULT 'medium',  -- small, medium, large
  response_style STRING DEFAULT 'detailed',  -- concise, detailed, legal_format
  language STRING DEFAULT 'en',  -- en, fr, es, hi, pa, zh
  auto_read BOOL DEFAULT FALSE,
  cookies_accepted BOOL DEFAULT FALSE,
  notification_email BOOL DEFAULT TRUE,
  notification_push BOOL DEFAULT FALSE,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
OPTIONS(
  description="User personalization preferences"
);

-- ============================================================================
-- 3. CONVERSATIONS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS `legid_production.conversations` (
  conversation_id STRING NOT NULL,
  user_id STRING NOT NULL,
  title STRING,
  law_type STRING,
  law_category STRING,
  jurisdiction STRING,
  status STRING DEFAULT 'active',  -- active, archived, deleted
  message_count INT64 DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
OPTIONS(
  description="Chat conversations - each 'New Chat' creates a new conversation"
);

-- ============================================================================
-- 4. MESSAGES TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS `legid_production.messages` (
  message_id STRING NOT NULL,
  conversation_id STRING NOT NULL,
  user_id STRING NOT NULL,
  role STRING NOT NULL,  -- user, assistant, system
  content STRING,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  citations JSON,  -- Array of citation objects
  metadata JSON,  -- Additional metadata (confidence, chunks_used, etc.)
  edited_at TIMESTAMP,
  deleted BOOL DEFAULT FALSE
)
OPTIONS(
  description="Individual messages within conversations"
);

-- ============================================================================
-- 5. UPLOADS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS `legid_production.uploads` (
  upload_id STRING NOT NULL,
  user_id STRING NOT NULL,
  conversation_id STRING,  -- NULL for lawyer verification uploads
  type STRING NOT NULL,  -- image, doc, audio, lawyer_license, id_document
  filename STRING,
  file_size INT64,
  mime_type STRING,
  gcs_url STRING NOT NULL,
  gcs_bucket STRING,
  gcs_path STRING,
  ocr_text STRING,  -- Extracted text from images
  chunks_indexed INT64 DEFAULT 0,
  processing_status STRING DEFAULT 'pending',  -- pending, processing, completed, failed
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
OPTIONS(
  description="User-uploaded files stored in GCS"
);

-- ============================================================================
-- 6. LAWYER VERIFICATION TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS `legid_production.lawyer_verification` (
  user_id STRING NOT NULL,
  status STRING DEFAULT 'draft',  -- draft, submitted, under_review, approved, rejected
  bar_country STRING,
  bar_province_state STRING,
  bar_number STRING,
  license_upload_id STRING,  -- References uploads table
  id_upload_id STRING,  -- References uploads table
  additional_docs_upload_ids ARRAY<STRING>,
  reviewer_id STRING,  -- Admin who reviewed
  review_notes STRING,
  submitted_at TIMESTAMP,
  reviewed_at TIMESTAMP,
  approved_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
OPTIONS(
  description="Lawyer verification applications and status"
);

-- ============================================================================
-- 7. SESSIONS TABLE (Optional - can use Firestore instead)
-- ============================================================================
CREATE TABLE IF NOT EXISTS `legid_production.sessions` (
  session_id STRING NOT NULL,
  user_id STRING NOT NULL,
  token_hash STRING,
  device_info STRING,
  ip_address STRING,
  expires_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  is_active BOOL DEFAULT TRUE
)
OPTIONS(
  description="User sessions for JWT token tracking"
);

-- ============================================================================
-- 8. AUDIT LOG TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS `legid_production.audit_log` (
  log_id STRING NOT NULL,
  user_id STRING,
  action STRING NOT NULL,  -- login, logout, message_sent, upload, profile_edit, etc.
  resource_type STRING,  -- conversation, message, upload, user, etc.
  resource_id STRING,
  details JSON,
  ip_address STRING,
  user_agent STRING,
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
OPTIONS(
  description="Audit trail for all user actions"
);

-- ============================================================================
-- 9. COOKIE CONSENT TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS `legid_production.cookie_consent` (
  user_id STRING NOT NULL,
  consent_given BOOL DEFAULT FALSE,
  necessary_cookies BOOL DEFAULT TRUE,
  analytics_cookies BOOL DEFAULT FALSE,
  marketing_cookies BOOL DEFAULT FALSE,
  consent_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  ip_address STRING,
  user_agent STRING
)
OPTIONS(
  description="Cookie consent tracking for GDPR compliance"
);

-- ============================================================================
-- 10. ANALYTICS TABLE (Optional)
-- ============================================================================
CREATE TABLE IF NOT EXISTS `legid_production.analytics` (
  event_id STRING NOT NULL,
  user_id STRING,
  event_type STRING NOT NULL,  -- page_view, chat_sent, document_generated, etc.
  event_data JSON,
  session_id STRING,
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
OPTIONS(
  description="Analytics events for usage tracking"
);

-- ============================================================================
-- INDEXES (BigQuery uses clustering instead of traditional indexes)
-- ============================================================================

-- Cluster conversations by user_id and created_at for efficient queries
ALTER TABLE `legid_production.conversations`
SET OPTIONS (
  clustering_fields = "user_id, created_at"
);

-- Cluster messages by conversation_id for efficient retrieval
ALTER TABLE `legid_production.messages`
SET OPTIONS (
  clustering_fields = "conversation_id, created_at"
);

-- Cluster uploads by user_id
ALTER TABLE `legid_production.uploads`
SET OPTIONS (
  clustering_fields = "user_id, created_at"
);

-- ============================================================================
-- SAMPLE QUERIES FOR TESTING
-- ============================================================================

-- Get all conversations for a user
-- SELECT * FROM `legid_production.conversations`
-- WHERE user_id = 'user_123'
-- ORDER BY updated_at DESC
-- LIMIT 20;

-- Get all messages in a conversation
-- SELECT * FROM `legid_production.messages`
-- WHERE conversation_id = 'conv_456'
-- ORDER BY created_at ASC;

-- Search conversations by title or content
-- SELECT DISTINCT c.*
-- FROM `legid_production.conversations` c
-- JOIN `legid_production.messages` m ON c.conversation_id = m.conversation_id
-- WHERE c.user_id = 'user_123'
-- AND (c.title LIKE '%traffic%' OR m.content LIKE '%traffic%')
-- ORDER BY c.updated_at DESC;

-- Get user preferences
-- SELECT * FROM `legid_production.user_preferences`
-- WHERE user_id = 'user_123';

-- Count messages per conversation
-- SELECT conversation_id, COUNT(*) as message_count
-- FROM `legid_production.messages`
-- WHERE conversation_id IN ('conv_1', 'conv_2', 'conv_3')
-- GROUP BY conversation_id;
