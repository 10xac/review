# 10 Academy Trainee API Documentation

## Overview

The 10 Academy Trainee API is a FastAPI-based REST API designed to manage trainee registration, batch processing, and user management for the 10 Academy platform. The API provides endpoints for creating individual trainees, processing batch uploads, handling webhooks, and managing user authentication.

## Table of Contents

1. [Architecture](#architecture)
2. [Authentication & Authorization](#authentication--authorization)
3. [API Endpoints](#api-endpoints)
4. [Data Models](#data-models)
5. [Services & Components](#services--components)
6. [Configuration](#configuration)
7. [Error Handling](#error-handling)
8. [Deployment](#deployment)

## Architecture

The API follows a layered architecture pattern:

```
├── main.py                 # FastAPI application entry point with CORS configuration
├── routes/                 # API route handlers
│   ├── trainee_routes.py   # Individual trainee creation endpoints
│   ├── batch_routes.py     # Batch processing endpoints
│   └── webhook_routes.py   # Webhook handling endpoints
├── controllers/            # Business logic controllers
│   └── trainee_controller.py
├── services/               # Core business services
│   ├── trainee_service.py  # Individual trainee processing
│   ├── batch_service.py    # Batch processing logic
│   ├── email_service.py    # Email notifications
│   └── webhook_service.py  # Webhook notifications
├── models/                 # Pydantic data models
│   └── trainee.py         # All data models and schemas
├── core/                   # Core functionality
│   ├── auth.py            # Authentication & authorization
│   ├── config.py          # Application configuration
│   ├── error_handlers.py  # Custom error handlers
│   └── logging_config.py  # Logging configuration
└── utils/                  # Utility functions
    └── password_generator.py
```

## Authentication & Authorization

### Authentication

The API uses JWT Bearer token authentication with Strapi as the authentication backend.

**Headers Required:**
```
Authorization: Bearer <jwt_token>
```

### Authorization Levels

1. **Public Access**: No authentication required
2. **Authenticated User**: Valid JWT token required
3. **Admin Access**: JWT token with "Authenticated" or "Staff" role required

### Authentication Flow

1. Client obtains JWT token from Strapi authentication system
2. Token is validated against Strapi's GraphQL endpoint
3. User information and role are extracted from the response
4. Access is granted based on role requirements

## API Endpoints

### 1. Trainee Management

#### Create Single Trainee (Public)
```http
POST /trainee/single
```

**Description:** Creates a single trainee with basic validation.

**Request Body:**
```json
{
  "config": {
    "run_stage": "prod",
    "batch": "5",
    "role": "trainee",
    "group_id": "12",
    "is_mock": false
  },
  "trainee": {
    "name": "John Doe",
    "email": "john.doe@example.com",
    "password": "password",
    "nationality": "Kenya",
    "gender": "Male",
    "date_of_birth": "1995-01-01",
    "vulnerable": "No"
  }
}
```

#### Create Admin Trainee (Admin Required)
```http
POST /trainee/admin-single
```

**Description:** Creates a trainee with admin privileges and optional email notifications.

**Authentication:** Bearer token with admin role required

**Features:**
- Mock user creation (for testing)
- Real user creation with welcome emails
- Admin-level validation

### 2. Batch Processing

#### Process Batch Upload (Admin Required)
```http
POST /trainee/batch
```

**Description:** Processes a CSV file containing multiple trainee records.

**Authentication:** Bearer token with admin role required

**Form Data Parameters:**
- `file`: CSV file (required)
- `run_stage`: Environment stage (default: "dev")
- `batch`: Batch identifier
- `role`: User role (default: "trainee")
- `group_id`: Group identifier
- `delimiter`: CSV delimiter (default: ",")
- `encoding`: File encoding (default: "utf-8")
- `chunk_size`: Processing chunk size (default: 20)
- `is_mock`: Mock mode flag (default: false)
- `login_url`: Login URL for welcome emails

**CSV Format:**
Required columns: `name`, `email`

Optional columns: `nationality`, `gender`, `date_of_birth`, `vulnerable`, `bio`, `city_of_residence`, `status`, `other_info`

**Response:**
```json
{
  "success": true,
  "message": "Batch processing started",
  "data": {
    "status": "processing",
    "batch": "batch_5"
  },
  "batch_info": {
    "batch": "batch_5",
    "admin_email": "admin@example.com"
  }
}
```

### 3. Webhook Handling

#### Webhook Endpoint
```http
POST /webhook
```

**Description:** Receives webhook notifications for batch processing status updates.

**Headers:**
- `X-Webhook-Signature`: Optional HMAC signature for verification

**Request Body:**
```json
{
  "status": "success|partial_success|failed",
  "batch": "batch_identifier",
  "total_processed": 100,
  "successful": 95,
  "failed": 5,
  "errors": [...],
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## Data Models

### Core Models

#### TraineeInfo
```python
{
  "name": str,                    # Required
  "email": str,                   # Required, validated format
  "password": Optional[str],      # Optional, defaults to email
  "status": Optional[str],        # Default: "Accepted"
  "nationality": Optional[str],
  "gender": Optional[str],
  "date_of_birth": Optional[str],
  "vulnerable": Optional[str],
  "city_of_residence": Optional[str],
  "bio": Optional[str],
  "other_info": Optional[Dict]    # Additional custom fields
}
```

#### ConfigInfo
```python
{
  "run_stage": str,               # Environment: dev, prod, etc.
  "batch": Optional[str],         # Batch identifier
  "role": str,                    # Default: "trainee"
  "is_mock": bool,               # Mock mode flag
  "group_id": Optional[str],      # Group identifier
  "login_url": Optional[str]      # Login URL for emails
}
```

#### BatchConfig
```python
{
  "run_stage": str,
  "batch": Optional[str],
  "role": str,
  "is_mock": bool,
  "group_id": Optional[str],
  "delimiter": str,               # CSV delimiter
  "encoding": str,                # File encoding
  "chunk_size": int,              # Processing chunk size
  "login_url": str,               # Login URL
  "admin_email": Optional[str],   # Admin notification email
  "callback_url": Optional[str],  # Webhook callback URL
  "webhook_secret": Optional[str] # Webhook signature secret
}
```

### Response Models

#### TraineeResponse
```python
{
  "success": bool,
  "message": str,
  "data": Optional[Dict],
  "error": Optional[ErrorDetail],
  "alluser_id": Optional[str],
  "profile": Optional[Dict],
  "trainee": Optional[Dict],
  "batch_info": Optional[Dict]
}
```

#### BatchProcessingResponse
```python
{
  "success": bool,
  "message": str,
  "data": Optional[Dict],
  "error": Optional[BatchErrorDetail],
  "batch_info": Optional[Dict],
  "total_processed": int,
  "successful": int,
  "failed": int,
  "failed_trainees": List[Dict],
  "successful_trainees": List[Dict],
  "error_details": List[Dict]
}
```

## Services & Components

### 1. TraineeService

**Purpose:** Handles individual trainee creation and management.

**Key Methods:**
- `create_trainee_services()`: Main trainee creation workflow
- `create_unconfirmed_user()`: Creates unconfirmed Strapi user
- `_insert_user_and_alluser()`: Creates user and alluser records
- `_insert_profile()`: Creates profile information
- `_insert_trainee()`: Creates trainee record

**Features:**
- Resource cleanup on failure
- Mock vs. real user creation
- Integration with Strapi authentication system

### 2. BatchService

**Purpose:** Handles batch processing of multiple trainees from CSV files.

**Key Methods:**
- `process_batch_trainees()`: Main batch processing workflow
- `_process_batch_records()`: Processes all records in batch
- `_process_trainee_record()`: Processes individual trainee record
- `_read_csv_file()`: Validates and reads CSV file
- `_send_notifications()`: Sends email and webhook notifications

**Features:**
- CSV validation and processing
- Chunk-based processing
- Email notifications to admins
- Webhook notifications
- Comprehensive error handling
- Resource cleanup

### 3. EmailService

**Purpose:** Handles email notifications for trainees and admins.

**Features:**
- Welcome emails for trainees
- Batch processing summary emails for admins
- CSV attachment with processing results
- Template-based email generation

### 4. WebhookService

**Purpose:** Sends webhook notifications for batch processing status.

**Features:**
- HMAC signature verification
- Retry mechanism for failed webhooks
- Configurable headers and endpoints

### 5. AuthService

**Purpose:** Handles authentication and authorization.

**Key Functions:**
- `get_current_user()`: Validates JWT token and extracts user info
- `verify_admin_access()`: Verifies admin-level permissions

**Features:**
- Strapi GraphQL integration
- Role-based access control
- Request context extraction

## Configuration

### Environment Variables

The API uses environment-based configuration through the `STRAPI_STAGE` variable:

```python
STRAPI_STAGE = "dev|prod|simulation|kaim|u2j|apply|tenacious|demo"
```

### Strapi Integration

Different stages connect to different Strapi instances:

- **dev**: dev-cms (Development)
- **prod**: cms (Production)
- **simulation**: simulation-cms
- **kaim**: kaimcms
- **u2j**: u2jcms
- **apply**: apply-cms
- **tenacious**: tenaciouscms
- **demo**: democms

### CORS Configuration

The API allows traffic from:
- Any subdomain of `10academy.org`
- Any subdomain of `gettenacious.com`
- Localhost origins for development

**CORS Regex Pattern:**
```regex
^https?://([\w\-]+\.)*?(10academy\.org|gettenacious\.com)(:\d+)?$
```

## Error Handling

### Error Response Format

All errors follow a consistent format:

```json
{
  "success": false,
  "message": "Error occurred during operation",
  "error": {
    "error_type": "ERROR_TYPE",
    "error_message": "Detailed error message",
    "error_location": "operation_location",
    "error_data": {
      "additional": "context"
    }
  }
}
```

### Error Types

- **VALIDATION_ERROR**: Input validation failures
- **AUTH_ERROR**: Authentication/authorization failures
- **USER_CREATION_ERROR**: User creation failures
- **ALLUSER_CREATION_ERROR**: AllUser creation failures
- **PROFILE_CREATION_ERROR**: Profile creation failures
- **TRAINEE_CREATION_ERROR**: Trainee creation failures
- **BATCH_PROCESSING_ERROR**: Batch processing failures
- **REQUEST_ERROR**: HTTP request failures
- **INTERNAL_SERVER_ERROR**: Unexpected server errors

### Custom Exception Handlers

- **ValidationError Handler**: Handles Pydantic validation errors
- **RequestValidationError Handler**: Handles FastAPI request validation errors

## Deployment

### Docker Configuration

The API includes Docker configuration for containerized deployment:

```dockerfile
# See Dockerfile for complete configuration
FROM python:3.11-slim
# ... (container setup)
```

### Dependencies

Key dependencies include:
- **FastAPI**: Web framework
- **Pydantic**: Data validation
- **Pandas**: CSV processing
- **HTTPX**: Async HTTP client
- **Uvicorn**: ASGI server

### Build Script

Use the provided build script for deployment:

```bash
./build.sh
```

### Environment Setup

1. Set `STRAPI_STAGE` environment variable
2. Configure Strapi tokens in AWS SSM Parameter Store
3. Set up email service credentials
4. Configure webhook endpoints if needed

## Usage Examples

### Create Single Trainee

```python
import httpx

async def create_trainee():
    data = {
        "config": {
            "run_stage": "dev",
            "batch": "test_batch",
            "role": "trainee",
            "is_mock": True
        },
        "trainee": {
            "name": "Jane Doe",
            "email": "jane.doe@example.com",
            "nationality": "Kenya",
            "gender": "Female"
        }
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://api-url/trainee/single",
            json=data
        )
        return response.json()
```

### Process Batch Upload

```python
import httpx

async def process_batch():
    files = {"file": ("trainees.csv", open("trainees.csv", "rb"), "text/csv")}
    data = {
        "run_stage": "dev",
        "batch": "batch_001",
        "is_mock": "false",
        "chunk_size": "25"
    }
    headers = {"Authorization": "Bearer your-jwt-token"}
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://api-url/trainee/batch",
            files=files,
            data=data,
            headers=headers
        )
        return response.json()
```

## Monitoring & Logging

The API includes comprehensive logging for:
- Authentication events
- Batch processing progress
- Email notifications
- Error tracking
- Performance monitoring

Logs are structured with contextual information for easy analysis and debugging.

## Security Considerations

1. **JWT Validation**: All protected endpoints validate JWT tokens
2. **Role-Based Access**: Admin endpoints require appropriate roles
3. **CORS Protection**: Strict origin validation
4. **Input Validation**: Comprehensive data validation using Pydantic
5. **Resource Cleanup**: Automatic cleanup of partially created resources
6. **Webhook Signatures**: Optional HMAC verification for webhooks

## API Versioning

The current API version is v1. Future versions will maintain backward compatibility where possible.

## Support & Maintenance

For issues, questions, or contributions, please refer to the project repository or contact the 10 Academy development team.
