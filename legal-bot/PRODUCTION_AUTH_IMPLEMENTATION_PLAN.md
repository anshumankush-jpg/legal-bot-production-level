# LegalAI Production Authentication System - Implementation Plan

## Executive Summary
This document provides a complete implementation plan for building a production-grade authentication system with role-based access control for LegalAI, supporting both Customer and Lawyer portals with BigQuery integration.

## Current Stack Analysis
- **Frontend**: React 18 + Vite + JavaScript (not Next.js/TypeScript as assumed)
- **Backend**: FastAPI + Python
- **Auth**: Currently has basic JWT auth with OAuth support
- **Database**: SQLite (dev) + Firebase Admin SDK available

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     LegalAI Auth Flow                        │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  1. User visits /auth                                        │
│     ├─> Choose: Customer or Lawyer                          │
│     ├─> Login: Google/Microsoft/Email                       │
│     └─> Generates unique user_id (UUID)                     │
│                                                               │
│  2. Backend validates & creates user                         │
│     ├─> Store in BigQuery (identity_users table)            │
│     ├─> Generate JWT with role                              │
│     └─> Return token + user data                            │
│                                                               │
│  3. Route based on role + status                             │
│     ├─> Customer → /app (chat portal)                       │
│     ├─> Lawyer (unverified) → /lawyer/onboarding            │
│     └─> Lawyer (verified) → /lawyer/dashboard               │
│                                                               │
│  4. Middleware protects routes                               │
│     ├─> Check JWT validity                                  │
│     ├─> Verify role permissions                             │
│     └─> Check lawyer verification status                    │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Implementation Phases

### Phase 1: BigQuery Setup & Schema
### Phase 2: Backend Auth Enhancement
### Phase 3: Frontend Auth UI
### Phase 4: Lawyer Verification System
### Phase 5: Admin Review Portal
### Phase 6: Security & Rate Limiting
### Phase 7: Environment Configuration
### Phase 8: Testing & Documentation

---

## PHASE 1: BigQuery Setup & Schema

### 1.1 BigQuery Dataset & Tables SQL

Create file: `/docs/bigquery_schema.sql`

```sql
-- Create dataset
CREATE SCHEMA IF NOT EXISTS `legalai`
OPTIONS(
  location="us-central1",
  description="LegalAI production database"
);

-- Identity Users Table
CREATE TABLE IF NOT EXISTS `legalai.identity_users` (
  user_id STRING NOT NULL,
  auth_provider STRING NOT NULL,  -- 'google' | 'microsoft' | 'email'
  auth_uid STRING NOT NULL,        -- Provider's UID
  email STRING NOT NULL,
  role STRING NOT NULL,             -- 'customer' | 'lawyer'
  lawyer_status STRING,             -- 'not_applicable' | 'pending' | 'approved' | 'rejected'
  full_name STRING,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
  last_login_at TIMESTAMP,
  env STRING NOT NULL,              -- 'dev' | 'prod'
  metadata JSON,                    -- Additional user metadata
  PRIMARY KEY (user_id) NOT ENFORCED
)
OPTIONS(
  description="User identity and authentication mapping"
);

-- Create unique index on auth_uid + provider
CREATE UNIQUE INDEX IF NOT EXISTS idx_auth_uid 
ON `legalai.identity_users`(auth_uid, auth_provider);

-- Create index on email
CREATE INDEX IF NOT EXISTS idx_email 
ON `legalai.identity_users`(email);

-- Lawyer Applications Table
CREATE TABLE IF NOT EXISTS `legalai.lawyer_applications` (
  application_id STRING NOT NULL,
  user_id STRING NOT NULL,
  full_name STRING NOT NULL,
  email STRING NOT NULL,
  
  -- Jurisdiction
  country STRING NOT NULL,          -- 'Canada' | 'USA'
  jurisdiction STRING NOT NULL,     -- Province/State code
  
  -- Credentials
  bar_number STRING NOT NULL,
  regulator_name STRING NOT NULL,   -- e.g., "Law Society of Ontario"
  practice_areas ARRAY<STRING>,
  years_of_experience INT64,
  
  -- Firm Information
  firm_name STRING,
  firm_website STRING,
  
  -- Documents
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

-- Create index on user_id
CREATE INDEX IF NOT EXISTS idx_lawyer_user_id 
ON `legalai.lawyer_applications`(user_id);

-- Create index on status
CREATE INDEX IF NOT EXISTS idx_lawyer_status 
ON `legalai.lawyer_applications`(status);

-- Login Events Table (for analytics)
CREATE TABLE IF NOT EXISTS `legalai.login_events` (
  event_id STRING NOT NULL,
  user_id STRING NOT NULL,
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
```

### 1.2 BigQuery Client Utility

Create file: `/backend/app/services/bigquery_client.py`

```python
"""BigQuery client for LegalAI identity and application management."""
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from google.cloud import bigquery
from google.oauth2 import service_account
import json
import logging

logger = logging.getLogger(__name__)

class BigQueryClient:
    """Client for BigQuery operations."""
    
    def __init__(self):
        """Initialize BigQuery client with service account."""
        # Load service account from environment or Secret Manager
        service_account_json = os.getenv('BIGQUERY_SERVICE_ACCOUNT_JSON')
        
        if service_account_json:
            # Parse JSON string
            credentials_info = json.loads(service_account_json)
            credentials = service_account.Credentials.from_service_account_info(
                credentials_info
            )
            self.client = bigquery.Client(
                credentials=credentials,
                project=credentials_info.get('project_id')
            )
        else:
            # Use default credentials (for local dev with gcloud auth)
            self.client = bigquery.Client()
        
        self.dataset_id = os.getenv('BIGQUERY_DATASET', 'legalai')
        self.env = os.getenv('ENVIRONMENT', 'dev')
    
    def upsert_user(self, user_data: Dict[str, Any]) -> str:
        """
        Upsert user into identity_users table.
        Returns user_id.
        """
        # Generate user_id if not provided
        user_id = user_data.get('user_id') or str(uuid.uuid4())
        
        # Prepare data
        data = {
            'user_id': user_id,
            'auth_provider': user_data['auth_provider'],
            'auth_uid': user_data['auth_uid'],
            'email': user_data['email'],
            'role': user_data['role'],
            'lawyer_status': user_data.get('lawyer_status', 
                'pending' if user_data['role'] == 'lawyer' else 'not_applicable'),
            'full_name': user_data.get('full_name', ''),
            'env': self.env,
            'metadata': json.dumps(user_data.get('metadata', {}))
        }
        
        # MERGE query for upsert
        query = f"""
        MERGE `{self.dataset_id}.identity_users` T
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
        ON T.auth_uid = S.auth_uid AND T.auth_provider = S.auth_provider
        WHEN MATCHED THEN
          UPDATE SET
            last_login_at = S.last_login_at,
            email = S.email,
            full_name = S.full_name
        WHEN NOT MATCHED THEN
          INSERT (
            user_id, auth_provider, auth_uid, email, role, 
            lawyer_status, full_name, created_at, last_login_at, env, metadata
          )
          VALUES (
            S.user_id, S.auth_provider, S.auth_uid, S.email, S.role,
            S.lawyer_status, S.full_name, CURRENT_TIMESTAMP(), S.last_login_at, S.env, S.metadata
          )
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("user_id", "STRING", data['user_id']),
                bigquery.ScalarQueryParameter("auth_provider", "STRING", data['auth_provider']),
                bigquery.ScalarQueryParameter("auth_uid", "STRING", data['auth_uid']),
                bigquery.ScalarQueryParameter("email", "STRING", data['email']),
                bigquery.ScalarQueryParameter("role", "STRING", data['role']),
                bigquery.ScalarQueryParameter("lawyer_status", "STRING", data['lawyer_status']),
                bigquery.ScalarQueryParameter("full_name", "STRING", data['full_name']),
                bigquery.ScalarQueryParameter("env", "STRING", data['env']),
                bigquery.ScalarQueryParameter("metadata", "STRING", data['metadata']),
            ]
        )
        
        try:
            query_job = self.client.query(query, job_config=job_config)
            query_job.result()  # Wait for completion
            logger.info(f"User upserted successfully: {user_id}")
            return user_id
        except Exception as e:
            logger.error(f"Error upserting user: {e}")
            raise
    
    def get_user_by_auth_uid(self, auth_uid: str, auth_provider: str) -> Optional[Dict]:
        """Get user by auth provider UID."""
        query = f"""
        SELECT *
        FROM `{self.dataset_id}.identity_users`
        WHERE auth_uid = @auth_uid 
          AND auth_provider = @auth_provider
          AND env = @env
        LIMIT 1
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("auth_uid", "STRING", auth_uid),
                bigquery.ScalarQueryParameter("auth_provider", "STRING", auth_provider),
                bigquery.ScalarQueryParameter("env", "STRING", self.env),
            ]
        )
        
        try:
            query_job = self.client.query(query, job_config=job_config)
            results = list(query_job.result())
            
            if results:
                row = results[0]
                return dict(row.items())
            return None
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Get user by user_id."""
        query = f"""
        SELECT *
        FROM `{self.dataset_id}.identity_users`
        WHERE user_id = @user_id AND env = @env
        LIMIT 1
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
                bigquery.ScalarQueryParameter("env", "STRING", self.env),
            ]
        )
        
        try:
            query_job = self.client.query(query, job_config=job_config)
            results = list(query_job.result())
            
            if results:
                return dict(results[0].items())
            return None
        except Exception as e:
            logger.error(f"Error getting user by ID: {e}")
            return None
    
    def create_lawyer_application(self, application_data: Dict[str, Any]) -> str:
        """Create lawyer application."""
        application_id = str(uuid.uuid4())
        
        # Insert query
        query = f"""
        INSERT INTO `{self.dataset_id}.lawyer_applications` (
          application_id, user_id, full_name, email, country, jurisdiction,
          bar_number, regulator_name, practice_areas, years_of_experience,
          firm_name, firm_website, bar_license_url, government_id_url,
          additional_credentials_url, status, env, metadata
        )
        VALUES (
          @application_id, @user_id, @full_name, @email, @country, @jurisdiction,
          @bar_number, @regulator_name, @practice_areas, @years_of_experience,
          @firm_name, @firm_website, @bar_license_url, @government_id_url,
          @additional_credentials_url, 'pending', @env, @metadata
        )
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("application_id", "STRING", application_id),
                bigquery.ScalarQueryParameter("user_id", "STRING", application_data['user_id']),
                bigquery.ScalarQueryParameter("full_name", "STRING", application_data['full_name']),
                bigquery.ScalarQueryParameter("email", "STRING", application_data['email']),
                bigquery.ScalarQueryParameter("country", "STRING", application_data['country']),
                bigquery.ScalarQueryParameter("jurisdiction", "STRING", application_data['jurisdiction']),
                bigquery.ScalarQueryParameter("bar_number", "STRING", application_data['bar_number']),
                bigquery.ScalarQueryParameter("regulator_name", "STRING", application_data['regulator_name']),
                bigquery.ArrayQueryParameter("practice_areas", "STRING", application_data.get('practice_areas', [])),
                bigquery.ScalarQueryParameter("years_of_experience", "INT64", application_data.get('years_of_experience', 0)),
                bigquery.ScalarQueryParameter("firm_name", "STRING", application_data.get('firm_name', '')),
                bigquery.ScalarQueryParameter("firm_website", "STRING", application_data.get('firm_website', '')),
                bigquery.ScalarQueryParameter("bar_license_url", "STRING", application_data['bar_license_url']),
                bigquery.ScalarQueryParameter("government_id_url", "STRING", application_data.get('government_id_url', '')),
                bigquery.ScalarQueryParameter("additional_credentials_url", "STRING", application_data.get('additional_credentials_url', '')),
                bigquery.ScalarQueryParameter("env", "STRING", self.env),
                bigquery.ScalarQueryParameter("metadata", "STRING", json.dumps(application_data.get('metadata', {}))),
            ]
        )
        
        try:
            query_job = self.client.query(query, job_config=job_config)
            query_job.result()
            logger.info(f"Lawyer application created: {application_id}")
            return application_id
        except Exception as e:
            logger.error(f"Error creating lawyer application: {e}")
            raise
    
    def update_lawyer_status(self, user_id: str, status: str, reviewer_id: str, notes: str = "") -> bool:
        """Update lawyer verification status."""
        query = f"""
        UPDATE `{self.dataset_id}.identity_users`
        SET lawyer_status = @status
        WHERE user_id = @user_id AND env = @env;
        
        UPDATE `{self.dataset_id}.lawyer_applications`
        SET 
          status = @status,
          reviewer_id = @reviewer_id,
          reviewer_notes = @notes,
          reviewed_at = CURRENT_TIMESTAMP()
        WHERE user_id = @user_id AND env = @env;
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("status", "STRING", status),
                bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
                bigquery.ScalarQueryParameter("reviewer_id", "STRING", reviewer_id),
                bigquery.ScalarQueryParameter("notes", "STRING", notes),
                bigquery.ScalarQueryParameter("env", "STRING", self.env),
            ]
        )
        
        try:
            query_job = self.client.query(query, job_config=job_config)
            query_job.result()
            logger.info(f"Lawyer status updated: {user_id} -> {status}")
            return True
        except Exception as e:
            logger.error(f"Error updating lawyer status: {e}")
            return False
    
    def log_login_event(self, event_data: Dict[str, Any]) -> None:
        """Log login event for analytics."""
        event_id = str(uuid.uuid4())
        
        query = f"""
        INSERT INTO `{self.dataset_id}.login_events` (
          event_id, user_id, auth_provider, ip_address, user_agent,
          env, success, failure_reason
        )
        VALUES (
          @event_id, @user_id, @auth_provider, @ip_address, @user_agent,
          @env, @success, @failure_reason
        )
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("event_id", "STRING", event_id),
                bigquery.ScalarQueryParameter("user_id", "STRING", event_data.get('user_id', '')),
                bigquery.ScalarQueryParameter("auth_provider", "STRING", event_data['auth_provider']),
                bigquery.ScalarQueryParameter("ip_address", "STRING", event_data.get('ip_address', '')),
                bigquery.ScalarQueryParameter("user_agent", "STRING", event_data.get('user_agent', '')),
                bigquery.ScalarQueryParameter("env", "STRING", self.env),
                bigquery.ScalarQueryParameter("success", "BOOL", event_data.get('success', True)),
                bigquery.ScalarQueryParameter("failure_reason", "STRING", event_data.get('failure_reason', '')),
            ]
        )
        
        try:
            query_job = self.client.query(query, job_config=job_config)
            query_job.result()
        except Exception as e:
            logger.error(f"Error logging login event: {e}")

# Singleton instance
_bigquery_client = None

def get_bigquery_client() -> BigQueryClient:
    """Get BigQuery client singleton."""
    global _bigquery_client
    if _bigquery_client is None:
        _bigquery_client = BigQueryClient()
    return _bigquery_client
```

---

## PHASE 2: Backend Auth Enhancement

This implementation is too large to fit in a single response. I've created a comprehensive implementation plan document. 

**Would you like me to continue with:**
1. Phase 2: Backend Auth API routes
2. Phase 3: Frontend Auth UI components
3. Phase 4: Lawyer verification system
4. Or focus on a specific component first?

The document I created provides the complete BigQuery schema and client utility. Let me know which part you'd like me to implement next, and I'll create the actual code files.
