-- LegalAI BigQuery Schema
-- ChatGPT-like conversation persistence + managed identity

-- =============================================================================
-- DATASET CREATION
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS `legalai`
OPTIONS(
  location="us-central1",
  description="LegalAI production database - conversations, identity, analytics"
);

-- =============================================================================
-- IDENTITY & AUTH TABLES
-- =============================================================================

-- Identity Users: Canonical user mapping (external auth → internal user_id)
-- CRITICAL: This is the ALLOWLIST - only users in this table can access the app
CREATE TABLE IF NOT EXISTS `legalai.identity_users` (
  user_id STRING NOT NULL,              -- Internal UUID (managed identity)
  auth_provider STRING NOT NULL,         -- 'google' | 'microsoft' | 'email'
  auth_uid STRING NOT NULL,              -- Provider's UID (e.g., 'google:12345')
  email STRING NOT NULL,
  role STRING NOT NULL,                  -- 'customer' | 'lawyer' | 'admin'
  lawyer_status STRING,                  -- 'not_applicable' | 'pending' | 'approved' | 'rejected'
  full_name STRING,
  is_allowed BOOL NOT NULL DEFAULT TRUE, -- ALLOWLIST FLAG: must be TRUE to login
  profile_completed BOOL NOT NULL DEFAULT FALSE, -- Profile setup status
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
  last_login_at TIMESTAMP,
  env STRING NOT NULL,                   -- 'dev' | 'prod'
  metadata JSON,                         -- Additional user metadata
  PRIMARY KEY (user_id) NOT ENFORCED
)
OPTIONS(
  description="User identity mapping - ALLOWLIST for app access"
);

-- Indexes for fast lookups
CREATE UNIQUE INDEX IF NOT EXISTS idx_auth_uid_provider 
ON `legalai.identity_users`(auth_uid, auth_provider, env);

CREATE INDEX IF NOT EXISTS idx_email 
ON `legalai.identity_users`(email, env);

CREATE INDEX IF NOT EXISTS idx_role 
ON `legalai.identity_users`(role, env);

CREATE INDEX IF NOT EXISTS idx_is_allowed 
ON `legalai.identity_users`(is_allowed, env);

-- User Profiles: Mandatory profile information (address + personal details)
CREATE TABLE IF NOT EXISTS `legalai.user_profiles` (
  user_id STRING NOT NULL,              -- Links to identity_users
  unique_address_id STRING NOT NULL,     -- System-generated UUID for address
  
  -- Personal Information
  legal_name STRING NOT NULL,
  display_name STRING NOT NULL,
  email STRING NOT NULL,                 -- Denormalized from identity_users
  phone STRING,
  
  -- Address Information (REQUIRED)
  address_line1 STRING NOT NULL,
  address_line2 STRING,
  city STRING NOT NULL,
  province_state STRING NOT NULL,        -- Province (CA) or State (US)
  country STRING NOT NULL,               -- 'Canada' | 'USA'
  postal_zip STRING NOT NULL,
  
  -- Profile Photo
  profile_photo_url STRING,              -- GCS URL
  
  -- Metadata
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
  env STRING NOT NULL,
  
  PRIMARY KEY (user_id) NOT ENFORCED,
  FOREIGN KEY (user_id) REFERENCES `legalai.identity_users`(user_id) NOT ENFORCED
)
OPTIONS(
  description="User profile information - mandatory for app access"
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_profile_user 
ON `legalai.user_profiles`(user_id, env);

CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_address 
ON `legalai.user_profiles`(unique_address_id);

-- =============================================================================
-- CHATGPT-LIKE CONVERSATION TABLES
-- =============================================================================

-- Conversations: Top-level chat sessions
CREATE TABLE IF NOT EXISTS `legalai.conversations` (
  conversation_id STRING NOT NULL,
  user_id STRING NOT NULL,               -- ← USER SCOPING
  title STRING NOT NULL,                 -- Auto-generated or user-edited
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
  is_archived BOOL NOT NULL DEFAULT FALSE,
  is_pinned BOOL NOT NULL DEFAULT FALSE,
  law_category STRING,                   -- e.g., 'Traffic Law', 'Criminal Law'
  jurisdiction STRING,                   -- e.g., 'ON', 'CA'
  env STRING NOT NULL,
  metadata JSON,                         -- Additional conversation metadata
  PRIMARY KEY (conversation_id) NOT ENFORCED,
  FOREIGN KEY (user_id) REFERENCES `legalai.identity_users`(user_id) NOT ENFORCED
)
PARTITION BY DATE(created_at)
OPTIONS(
  description="User conversations (ChatGPT-like chat sessions)",
  partition_expiration_days=NULL  -- Keep forever
);

CREATE INDEX IF NOT EXISTS idx_conv_user_id 
ON `legalai.conversations`(user_id, env);

CREATE INDEX IF NOT EXISTS idx_conv_updated 
ON `legalai.conversations`(user_id, updated_at DESC);

-- Messages: Individual messages within conversations
CREATE TABLE IF NOT EXISTS `legalai.messages` (
  message_id STRING NOT NULL,
  conversation_id STRING NOT NULL,
  user_id STRING NOT NULL,               -- ← USER SCOPING (denormalized for security)
  role STRING NOT NULL,                  -- 'user' | 'assistant' | 'system' | 'tool'
  content STRING NOT NULL,               -- Message text
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
  env STRING NOT NULL,
  metadata JSON,                         -- Model, tokens, citations, etc.
  PRIMARY KEY (message_id) NOT ENFORCED,
  FOREIGN KEY (conversation_id) REFERENCES `legalai.conversations`(conversation_id) NOT ENFORCED,
  FOREIGN KEY (user_id) REFERENCES `legalai.identity_users`(user_id) NOT ENFORCED
)
PARTITION BY DATE(created_at)
OPTIONS(
  description="Chat messages within conversations",
  partition_expiration_days=NULL  -- Keep forever
);

CREATE INDEX IF NOT EXISTS idx_msg_conversation 
ON `legalai.messages`(conversation_id, created_at);

CREATE INDEX IF NOT EXISTS idx_msg_user 
ON `legalai.messages`(user_id, env);

-- Full-text search index (if using BigQuery Search)
-- Note: For production, consider using Elasticsearch/Meilisearch for better search
CREATE SEARCH INDEX IF NOT EXISTS idx_msg_search
ON `legalai.messages`(content)
OPTIONS(analyzer='STANDARD');

-- =============================================================================
-- ATTACHMENTS & FILES
-- =============================================================================

-- Attachments: Files/images uploaded by users
CREATE TABLE IF NOT EXISTS `legalai.attachments` (
  attachment_id STRING NOT NULL,
  user_id STRING NOT NULL,               -- ← USER SCOPING
  conversation_id STRING,                -- Nullable (can be standalone)
  file_name STRING NOT NULL,
  file_type STRING NOT NULL,             -- MIME type
  file_size_bytes INT64 NOT NULL,
  gcs_url STRING NOT NULL,               -- gs://bucket/path
  gcs_bucket STRING NOT NULL,
  gcs_path STRING NOT NULL,
  sha256 STRING NOT NULL,                -- File integrity check
  ocr_text STRING,                       -- Extracted text (if PDF/image)
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
  env STRING NOT NULL,
  metadata JSON,
  PRIMARY KEY (attachment_id) NOT ENFORCED,
  FOREIGN KEY (user_id) REFERENCES `legalai.identity_users`(user_id) NOT ENFORCED,
  FOREIGN KEY (conversation_id) REFERENCES `legalai.conversations`(conversation_id) NOT ENFORCED
)
PARTITION BY DATE(created_at)
OPTIONS(
  description="User file uploads (images, PDFs, documents)",
  partition_expiration_days=NULL
);

CREATE INDEX IF NOT EXISTS idx_attach_user 
ON `legalai.attachments`(user_id, env);

CREATE INDEX IF NOT EXISTS idx_attach_conversation 
ON `legalai.attachments`(conversation_id);

-- Full-text search on OCR text
CREATE SEARCH INDEX IF NOT EXISTS idx_attach_ocr_search
ON `legalai.attachments`(ocr_text)
OPTIONS(analyzer='STANDARD');

-- =============================================================================
-- LAWYER VERIFICATION TABLES
-- =============================================================================

-- Lawyer Applications: Verification submissions
CREATE TABLE IF NOT EXISTS `legalai.lawyer_applications` (
  application_id STRING NOT NULL,
  user_id STRING NOT NULL,
  full_name STRING NOT NULL,
  email STRING NOT NULL,
  
  -- Jurisdiction
  country STRING NOT NULL,               -- 'Canada' | 'USA'
  jurisdiction STRING NOT NULL,          -- Province/State code (e.g., 'ON', 'CA')
  
  -- Credentials
  bar_number STRING NOT NULL,
  regulator_name STRING NOT NULL,        -- e.g., "Law Society of Ontario"
  practice_areas ARRAY<STRING>,
  years_of_experience INT64,
  
  -- Firm Information
  firm_name STRING,
  firm_website STRING,
  
  -- Documents (GCS URLs)
  bar_license_url STRING NOT NULL,
  government_id_url STRING,
  additional_credentials_url STRING,
  
  -- Status
  status STRING NOT NULL DEFAULT 'pending',  -- 'pending' | 'approved' | 'rejected'
  reviewer_id STRING,
  reviewer_notes STRING,
  submitted_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
  reviewed_at TIMESTAMP,
  
  -- Metadata
  env STRING NOT NULL,
  metadata JSON,
  
  PRIMARY KEY (application_id) NOT ENFORCED,
  FOREIGN KEY (user_id) REFERENCES `legalai.identity_users`(user_id) NOT ENFORCED
)
OPTIONS(
  description="Lawyer verification applications"
);

CREATE INDEX IF NOT EXISTS idx_lawyer_app_user 
ON `legalai.lawyer_applications`(user_id);

CREATE INDEX IF NOT EXISTS idx_lawyer_app_status 
ON `legalai.lawyer_applications`(status, env);

-- =============================================================================
-- ANALYTICS & AUDIT TABLES
-- =============================================================================

-- Activity Events: User action tracking
CREATE TABLE IF NOT EXISTS `legalai.activity_events` (
  event_id STRING NOT NULL,
  user_id STRING,                        -- Nullable for anonymous events
  event_type STRING NOT NULL,            -- 'login', 'new_chat', 'send_message', 'upload_file', etc.
  event_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
  ip_address STRING,
  user_agent STRING,
  env STRING NOT NULL,
  payload JSON,                          -- Event-specific data
  PRIMARY KEY (event_id) NOT ENFORCED
)
PARTITION BY DATE(event_timestamp)
OPTIONS(
  description="User activity and audit log",
  partition_expiration_days=90  -- Keep 90 days
);

CREATE INDEX IF NOT EXISTS idx_events_user 
ON `legalai.activity_events`(user_id, event_timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_events_type 
ON `legalai.activity_events`(event_type, env);

-- Login Events: Specific login tracking
CREATE TABLE IF NOT EXISTS `legalai.login_events` (
  event_id STRING NOT NULL,
  user_id STRING,
  auth_provider STRING NOT NULL,
  login_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
  ip_address STRING,
  user_agent STRING,
  env STRING NOT NULL,
  success BOOL NOT NULL,
  failure_reason STRING,
  PRIMARY KEY (event_id) NOT ENFORCED
)
PARTITION BY DATE(login_at)
OPTIONS(
  description="Login event tracking",
  partition_expiration_days=90
);

-- =============================================================================
-- UPSERT PROCEDURES (MERGE STATEMENTS)
-- =============================================================================

-- Upsert User Identity
-- Usage: Execute this with query parameters
/*
MERGE `legalai.identity_users` T
USING (
  SELECT 
    @user_id AS user_id,
    @auth_provider AS auth_provider,
    @auth_uid AS auth_uid,
    @email AS email,
    @role AS role,
    @lawyer_status AS lawyer_status,
    @full_name AS full_name,
    CURRENT_TIMESTAMP() AS last_login_at,
    @env AS env,
    @metadata AS metadata
) S
ON T.auth_uid = S.auth_uid 
   AND T.auth_provider = S.auth_provider 
   AND T.env = S.env
WHEN MATCHED THEN
  UPDATE SET
    last_login_at = S.last_login_at,
    email = S.email,
    full_name = S.full_name,
    metadata = S.metadata
WHEN NOT MATCHED THEN
  INSERT (
    user_id, auth_provider, auth_uid, email, role, 
    lawyer_status, full_name, created_at, last_login_at, env, metadata
  )
  VALUES (
    S.user_id, S.auth_provider, S.auth_uid, S.email, S.role,
    S.lawyer_status, S.full_name, CURRENT_TIMESTAMP(), S.last_login_at, S.env, S.metadata
  );
*/

-- =============================================================================
-- EXAMPLE QUERIES
-- =============================================================================

-- Get user's conversations (sidebar)
/*
SELECT 
  conversation_id,
  title,
  updated_at,
  is_pinned,
  is_archived
FROM `legalai.conversations`
WHERE user_id = @user_id 
  AND env = @env
  AND is_archived = FALSE
ORDER BY is_pinned DESC, updated_at DESC
LIMIT 100;
*/

-- Get conversation messages
/*
SELECT 
  message_id,
  role,
  content,
  created_at,
  metadata
FROM `legalai.messages`
WHERE conversation_id = @conversation_id
  AND user_id = @user_id  -- Security check
  AND env = @env
ORDER BY created_at ASC;
*/

-- Search user's messages
/*
SELECT 
  m.message_id,
  m.conversation_id,
  m.content,
  c.title,
  m.created_at,
  SCORE(m.content, @search_query) AS relevance_score
FROM `legalai.messages` m
JOIN `legalai.conversations` c 
  ON m.conversation_id = c.conversation_id
WHERE m.user_id = @user_id
  AND m.env = @env
  AND SEARCH(m.content, @search_query)
ORDER BY relevance_score DESC, m.created_at DESC
LIMIT 50;
*/

-- Get user's attachments
/*
SELECT 
  attachment_id,
  conversation_id,
  file_name,
  file_type,
  gcs_url,
  created_at
FROM `legalai.attachments`
WHERE user_id = @user_id
  AND env = @env
ORDER BY created_at DESC
LIMIT 100;
*/

-- Admin: Get pending lawyer applications
/*
SELECT 
  a.application_id,
  a.user_id,
  a.full_name,
  a.email,
  a.country,
  a.jurisdiction,
  a.bar_number,
  a.regulator_name,
  a.submitted_at,
  u.email AS user_email
FROM `legalai.lawyer_applications` a
JOIN `legalai.identity_users` u ON a.user_id = u.user_id
WHERE a.status = 'pending'
  AND a.env = @env
ORDER BY a.submitted_at ASC;
*/

-- =============================================================================
-- SECURITY NOTES
-- =============================================================================

/*
CRITICAL SECURITY RULES:

1. USER SCOPING:
   - ALL queries MUST include: WHERE user_id = @user_id AND env = @env
   - Never trust user_id from client - always from verified JWT claims
   
2. MULTI-TENANT ISOLATION:
   - user_id is denormalized in messages/attachments for security
   - Even if conversation_id is leaked, user_id check prevents access
   
3. ENVIRONMENT ISOLATION:
   - Dev and prod data are separate (env column)
   - Prevents dev bugs from affecting prod data
   
4. AUDIT TRAIL:
   - All sensitive actions logged to activity_events
   - Partitioned by date for efficient querying
   
5. DATA RETENTION:
   - Conversations/messages: kept forever (user data)
   - Events: 90 days (compliance/debugging)
   - Adjust partition_expiration_days as needed
*/
