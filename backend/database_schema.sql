-- ============================================
-- LEGID Database Schema - BigQuery / PostgreSQL
-- ============================================

-- Users Table
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),  -- NULL for OAuth users
    display_name VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('client', 'lawyer', 'admin')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    email_verified BOOLEAN DEFAULT FALSE,
    oauth_provider VARCHAR(50),  -- 'google', 'microsoft', NULL for email/password
    avatar_url TEXT,
    phone_number VARCHAR(50),
    INDEX idx_email (email),
    INDEX idx_role (role)
);

-- Conversations Table
CREATE TABLE conversations (
    conversation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL DEFAULT 'New Chat',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE,
    law_category VARCHAR(100),
    jurisdiction VARCHAR(100),
    tags TEXT[],  -- Array of tags for categorization
    INDEX idx_user_id (user_id),
    INDEX idx_updated_at (updated_at DESC),
    INDEX idx_user_updated (user_id, updated_at DESC)
);

-- Messages Table
CREATE TABLE messages (
    message_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(conversation_id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    attachments JSONB,  -- Array of attachment metadata
    metadata JSONB,  -- Additional metadata (citations, confidence, etc.)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tokens_used INTEGER,
    processing_time_ms INTEGER,
    INDEX idx_conversation_id (conversation_id),
    INDEX idx_created_at (created_at),
    INDEX idx_conversation_created (conversation_id, created_at)
);

-- User Preferences Table
CREATE TABLE user_preferences (
    user_id UUID PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
    theme VARCHAR(20) DEFAULT 'dark' CHECK (theme IN ('dark', 'light')),
    font_size VARCHAR(20) DEFAULT 'medium' CHECK (font_size IN ('small', 'medium', 'large')),
    response_style VARCHAR(20) DEFAULT 'detailed' CHECK (response_style IN ('concise', 'detailed', 'legal')),
    language VARCHAR(10) DEFAULT 'en',
    auto_read_responses BOOLEAN DEFAULT FALSE,
    law_category VARCHAR(100),
    jurisdiction VARCHAR(100),
    province VARCHAR(50),
    country VARCHAR(10) DEFAULT 'CA',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Images Table (for image uploads and generations)
CREATE TABLE images (
    image_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    conversation_id UUID REFERENCES conversations(conversation_id) ON DELETE SET NULL,
    message_id UUID REFERENCES messages(message_id) ON DELETE SET NULL,
    file_path TEXT NOT NULL,
    file_name VARCHAR(255),
    file_size_bytes BIGINT,
    mime_type VARCHAR(100),
    ocr_text TEXT,  -- Extracted text from OCR
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_conversation_id (conversation_id),
    INDEX idx_created_at (created_at DESC)
);

-- Attachments Table
CREATE TABLE attachments (
    attachment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id UUID NOT NULL REFERENCES messages(message_id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    file_name VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    file_size_bytes BIGINT,
    mime_type VARCHAR(100),
    file_type VARCHAR(50),  -- 'pdf', 'docx', 'image', etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_message_id (message_id),
    INDEX idx_user_id (user_id)
);

-- Usage Tracking Table (for billing and limits)
CREATE TABLE usage_tracking (
    usage_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    conversation_id UUID REFERENCES conversations(conversation_id) ON DELETE SET NULL,
    action_type VARCHAR(50) NOT NULL,  -- 'chat', 'upload', 'case_lookup', etc.
    tokens_used INTEGER,
    cost_usd DECIMAL(10, 4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB,
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at DESC),
    INDEX idx_user_created (user_id, created_at DESC)
);

-- ============================================
-- BIGQUERY VERSION (if using BigQuery instead)
-- ============================================

/*
-- Users
CREATE TABLE legid.users (
    user_id STRING NOT NULL,
    email STRING NOT NULL,
    password_hash STRING,
    display_name STRING NOT NULL,
    role STRING NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    last_login_at TIMESTAMP,
    is_active BOOL DEFAULT TRUE,
    email_verified BOOL DEFAULT FALSE,
    oauth_provider STRING,
    avatar_url STRING,
    phone_number STRING
)
PARTITION BY DATE(created_at)
CLUSTER BY user_id, email;

-- Conversations
CREATE TABLE legid.conversations (
    conversation_id STRING NOT NULL,
    user_id STRING NOT NULL,
    title STRING NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    is_deleted BOOL DEFAULT FALSE,
    law_category STRING,
    jurisdiction STRING,
    tags ARRAY<STRING>
)
PARTITION BY DATE(created_at)
CLUSTER BY user_id, updated_at;

-- Messages
CREATE TABLE legid.messages (
    message_id STRING NOT NULL,
    conversation_id STRING NOT NULL,
    user_id STRING NOT NULL,
    role STRING NOT NULL,
    content STRING NOT NULL,
    attachments JSON,
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    tokens_used INT64,
    processing_time_ms INT64
)
PARTITION BY DATE(created_at)
CLUSTER BY conversation_id, created_at;

-- User Preferences
CREATE TABLE legid.user_preferences (
    user_id STRING NOT NULL,
    theme STRING DEFAULT 'dark',
    font_size STRING DEFAULT 'medium',
    response_style STRING DEFAULT 'detailed',
    language STRING DEFAULT 'en',
    auto_read_responses BOOL DEFAULT FALSE,
    law_category STRING,
    jurisdiction STRING,
    province STRING,
    country STRING DEFAULT 'CA',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
CLUSTER BY user_id;
*/

-- ============================================
-- INDEXES FOR PERFORMANCE
-- ============================================

CREATE INDEX idx_conversations_user_updated ON conversations(user_id, updated_at DESC) WHERE is_deleted = FALSE;
CREATE INDEX idx_messages_conversation_created ON messages(conversation_id, created_at);
CREATE INDEX idx_users_email ON users(email) WHERE is_active = TRUE;

-- ============================================
-- VIEWS FOR COMMON QUERIES
-- ============================================

CREATE VIEW conversation_summary AS
SELECT 
    c.conversation_id,
    c.user_id,
    c.title,
    c.created_at,
    c.updated_at,
    COUNT(m.message_id) as message_count,
    MAX(m.created_at) as last_message_at,
    (SELECT content FROM messages WHERE conversation_id = c.conversation_id AND role = 'user' ORDER BY created_at DESC LIMIT 1) as last_user_message
FROM conversations c
LEFT JOIN messages m ON c.conversation_id = m.conversation_id
WHERE c.is_deleted = FALSE
GROUP BY c.conversation_id, c.user_id, c.title, c.created_at, c.updated_at;
