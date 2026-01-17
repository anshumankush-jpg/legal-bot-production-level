-- ========================================
-- LEGALAI/LEGID BigQuery Schema
-- Complete profile and identity system
-- ========================================

-- Dataset: legalai
-- Tables: identity_users, user_profiles, user_consent, access_requests

-- ========================================
-- 1. IDENTITY_USERS TABLE
-- ========================================
-- Manages user authentication and identity mappings
CREATE TABLE IF NOT EXISTS `legalai.identity_users` (
  user_id STRING NOT NULL,
  auth_provider STRING NOT NULL,  -- 'google', 'microsoft', 'email'
  auth_uid STRING NOT NULL,       -- Provider-specific user ID
  email STRING NOT NULL,
  role STRING NOT NULL,           -- 'customer', 'lawyer', 'admin'
  lawyer_status STRING NOT NULL,  -- 'not_applicable', 'pending', 'approved', 'rejected'
  is_provisioned BOOL NOT NULL DEFAULT FALSE,
  env STRING NOT NULL,            -- 'dev', 'prod'
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
  last_login_at TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP()
);

-- Indexes for fast lookups
-- Primary key: user_id
-- Unique index on (auth_provider, auth_uid) for OAuth lookups
-- Index on email for email-based lookups
-- Index on (env, is_provisioned) for access control

-- MERGE/UPSERT query for identity_users
-- Use this when a user logs in
MERGE `legalai.identity_users` AS target
USING (
  SELECT
    @user_id AS user_id,
    @auth_provider AS auth_provider,
    @auth_uid AS auth_uid,
    @email AS email,
    @role AS role,
    @lawyer_status AS lawyer_status,
    @is_provisioned AS is_provisioned,
    @env AS env
) AS source
ON target.user_id = source.user_id
WHEN MATCHED THEN
  UPDATE SET
    last_login_at = CURRENT_TIMESTAMP(),
    updated_at = CURRENT_TIMESTAMP()
WHEN NOT MATCHED THEN
  INSERT (user_id, auth_provider, auth_uid, email, role, lawyer_status, is_provisioned, env, created_at, last_login_at, updated_at)
  VALUES (source.user_id, source.auth_provider, source.auth_uid, source.email, source.role, source.lawyer_status, source.is_provisioned, source.env, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP());


-- ========================================
-- 2. USER_PROFILES TABLE
-- ========================================
-- Stores user profile information and preferences
CREATE TABLE IF NOT EXISTS `legalai.user_profiles` (
  user_id STRING NOT NULL,
  display_name STRING,
  username STRING,              -- Unique, lowercase, 3-20 chars
  avatar_url STRING,
  phone STRING,
  address_line_1 STRING,
  address_line_2 STRING,
  city STRING,
  province_state STRING,
  postal_zip STRING,
  country STRING,
  preferences_json STRING,      -- JSON string: {"theme": "dark", "response_style": "balanced", "legal_tone": "neutral", "font_size": "medium", "auto_read_responses": false, "language": "en"}
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP()
);

-- Indexes
-- Primary key: user_id
-- Unique index on username (case-insensitive if needed)

-- MERGE/UPSERT query for user_profiles
MERGE `legalai.user_profiles` AS target
USING (
  SELECT
    @user_id AS user_id,
    @display_name AS display_name,
    @username AS username,
    @avatar_url AS avatar_url,
    @phone AS phone,
    @address_line_1 AS address_line_1,
    @address_line_2 AS address_line_2,
    @city AS city,
    @province_state AS province_state,
    @postal_zip AS postal_zip,
    @country AS country,
    @preferences_json AS preferences_json
) AS source
ON target.user_id = source.user_id
WHEN MATCHED THEN
  UPDATE SET
    display_name = COALESCE(source.display_name, target.display_name),
    username = COALESCE(source.username, target.username),
    avatar_url = COALESCE(source.avatar_url, target.avatar_url),
    phone = COALESCE(source.phone, target.phone),
    address_line_1 = COALESCE(source.address_line_1, target.address_line_1),
    address_line_2 = COALESCE(source.address_line_2, target.address_line_2),
    city = COALESCE(source.city, target.city),
    province_state = COALESCE(source.province_state, target.province_state),
    postal_zip = COALESCE(source.postal_zip, target.postal_zip),
    country = COALESCE(source.country, target.country),
    preferences_json = COALESCE(source.preferences_json, target.preferences_json),
    updated_at = CURRENT_TIMESTAMP()
WHEN NOT MATCHED THEN
  INSERT (user_id, display_name, username, avatar_url, phone, address_line_1, address_line_2, city, province_state, postal_zip, country, preferences_json, updated_at)
  VALUES (source.user_id, source.display_name, source.username, source.avatar_url, source.phone, source.address_line_1, source.address_line_2, source.city, source.province_state, source.postal_zip, source.country, source.preferences_json, CURRENT_TIMESTAMP());


-- ========================================
-- 3. USER_CONSENT TABLE
-- ========================================
-- Tracks user consent for cookies and data usage
CREATE TABLE IF NOT EXISTS `legalai.user_consent` (
  user_id STRING NOT NULL,
  necessary BOOL NOT NULL DEFAULT TRUE,
  analytics BOOL NOT NULL DEFAULT FALSE,
  marketing BOOL NOT NULL DEFAULT FALSE,
  functional BOOL NOT NULL DEFAULT FALSE,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP()
);

-- Primary key: user_id

-- MERGE/UPSERT query for user_consent
MERGE `legalai.user_consent` AS target
USING (
  SELECT
    @user_id AS user_id,
    @necessary AS necessary,
    @analytics AS analytics,
    @marketing AS marketing,
    @functional AS functional
) AS source
ON target.user_id = source.user_id
WHEN MATCHED THEN
  UPDATE SET
    necessary = source.necessary,
    analytics = source.analytics,
    marketing = source.marketing,
    functional = source.functional,
    updated_at = CURRENT_TIMESTAMP()
WHEN NOT MATCHED THEN
  INSERT (user_id, necessary, analytics, marketing, functional, updated_at)
  VALUES (source.user_id, source.necessary, source.analytics, source.marketing, source.functional, CURRENT_TIMESTAMP());


-- ========================================
-- 4. ACCESS_REQUESTS TABLE
-- ========================================
-- Stores access requests from non-provisioned users
CREATE TABLE IF NOT EXISTS `legalai.access_requests` (
  id STRING NOT NULL,
  email STRING NOT NULL,
  name STRING,
  requested_role STRING NOT NULL,  -- 'customer', 'lawyer'
  reason STRING,
  organization STRING,
  status STRING NOT NULL DEFAULT 'pending',  -- 'pending', 'approved', 'rejected'
  reviewed_by_user_id STRING,
  reviewed_at TIMESTAMP,
  reviewer_notes STRING,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP()
);

-- Primary key: id
-- Index on email for finding existing requests
-- Index on status for admin dashboard queries

-- MERGE/UPSERT query for access_requests
MERGE `legalai.access_requests` AS target
USING (
  SELECT
    @id AS id,
    @email AS email,
    @name AS name,
    @requested_role AS requested_role,
    @reason AS reason,
    @organization AS organization,
    @status AS status
) AS source
ON target.id = source.id
WHEN MATCHED THEN
  UPDATE SET
    name = COALESCE(source.name, target.name),
    requested_role = source.requested_role,
    reason = COALESCE(source.reason, target.reason),
    organization = COALESCE(source.organization, target.organization),
    status = source.status,
    updated_at = CURRENT_TIMESTAMP()
WHEN NOT MATCHED THEN
  INSERT (id, email, name, requested_role, reason, organization, status, created_at, updated_at)
  VALUES (source.id, source.email, source.name, source.requested_role, source.reason, source.organization, source.status, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP());


-- ========================================
-- 5. CONVERSATIONS TABLE (OPTIONAL)
-- ========================================
-- Stores chat conversations, scoped by user_id
CREATE TABLE IF NOT EXISTS `legalai.conversations` (
  id STRING NOT NULL,
  user_id STRING NOT NULL,
  title STRING,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP()
);

-- Primary key: id
-- Index on user_id for fetching user's conversations


-- ========================================
-- 6. MESSAGES TABLE (OPTIONAL)
-- ========================================
-- Stores individual messages within conversations
CREATE TABLE IF NOT EXISTS `legalai.messages` (
  id STRING NOT NULL,
  conversation_id STRING NOT NULL,
  role STRING NOT NULL,  -- 'user', 'assistant', 'system'
  content STRING NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
  meta_data STRING  -- JSON string for additional metadata
);

-- Primary key: id
-- Index on conversation_id for fetching conversation messages


-- ========================================
-- EXAMPLE QUERIES
-- ========================================

-- Get user profile with identity information
SELECT
  iu.user_id,
  iu.email,
  iu.role,
  iu.lawyer_status,
  iu.is_provisioned,
  iu.last_login_at,
  up.display_name,
  up.username,
  up.avatar_url,
  up.preferences_json,
  uc.necessary,
  uc.analytics,
  uc.marketing
FROM `legalai.identity_users` iu
LEFT JOIN `legalai.user_profiles` up ON iu.user_id = up.user_id
LEFT JOIN `legalai.user_consent` uc ON iu.user_id = uc.user_id
WHERE iu.user_id = @user_id
  AND iu.env = @env;


-- Check if username is available
SELECT COUNT(*) as count
FROM `legalai.user_profiles`
WHERE LOWER(username) = LOWER(@username)
  AND user_id != @current_user_id;


-- Get user by OAuth provider
SELECT user_id, email, role, lawyer_status, is_provisioned
FROM `legalai.identity_users`
WHERE auth_provider = @auth_provider
  AND auth_uid = @auth_uid
  AND env = @env;


-- Get pending access requests (admin query)
SELECT id, email, name, requested_role, reason, organization, created_at
FROM `legalai.access_requests`
WHERE status = 'pending'
ORDER BY created_at DESC;


-- ========================================
-- NOTES
-- ========================================
-- 1. Use parameterized queries with @ placeholders to prevent SQL injection
-- 2. All timestamps are in UTC
-- 3. JSON fields (preferences_json, meta_data) should be validated before storage
-- 4. Username uniqueness is case-insensitive (use LOWER() in queries)
-- 5. For production, add partitioning on created_at/updated_at for large tables
-- 6. Consider adding audit_log table for tracking changes to sensitive data
-- 7. Set up scheduled queries to clean up old access_requests (e.g., > 30 days rejected)
