# 10 Academy Review & User Management System

A comprehensive platform for managing the entire 10 Academy application lifecycle - from trainee applications and reviews to interviews, user management, and batch processing across multiple programs and environments.

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![Jupyter](https://img.shields.io/badge/Jupyter-Notebooks-orange.svg)](https://jupyter.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)

## 📋 Table of Contents

- [Overview](#overview)
- [System Components](#system-components)
- [Features](#features)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage Guide](#usage-guide)
- [API Documentation](#api-documentation)
- [Development](#development)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [Troubleshooting](#troubleshooting)
- [License](#license)

## 🎯 Overview

The 10 Academy Review & User Management System is a comprehensive platform that handles the complete student lifecycle across multiple 10 Academy programs. The system manages:

### **🎓 Program Management**
- **Multiple Program Support**: Intensive, U2J, KAIM, Simulation, Apply, Tenacious, and Demo programs
- **Batch Management**: Organize students into batches with specific configurations
- **Multi-Environment**: Dev, staging, and production environments for each program

### **📝 Application & Review Process**
- **Application Processing**: Import and process applications from Google Sheets
- **Review System**: Create review categories, assign reviewers, and manage review workflows
- **Interview Management**: Handle interview scheduling, tracking, and results
- **Question Mapping**: Dynamic question mapping based on batch and program requirements

### **👥 User Management**
- **Trainee Registration**: Individual and batch trainee creation
- **Staff Management**: Handle staff profiles and permissions
- **User Authentication**: Integration with Strapi CMS for secure authentication
- **Role-Based Access**: Support for trainees, staff, reviewers, and admins

### **🔧 Integration & Automation**
- **Google Sheets Integration**: Direct import from application forms
- **Email Notifications**: Automated welcome emails and notifications
- **Webhook Support**: Real-time status updates and callbacks
- **Multi-Platform**: Support for various 10 Academy platforms and domains

## 🏗️ System Components

### **1. 🌐 FastAPI Application (`/api/`)**
RESTful API for programmatic access to the system:
- **Trainee Management**: Individual and batch trainee creation
- **Authentication**: JWT-based security with role-based access
- **Webhook Integration**: Real-time notifications and callbacks
- **Interactive Documentation**: Auto-generated Swagger UI

### **2. 📓 Jupyter Notebooks (`/notebooks/`)**
Interactive tools for specific operations:
- `insert_all_users.ipynb` - General user insertion
- `Insert_intensive_trainees.ipynb` - Intensive program trainees
- `insert_Interview_accepted_trainees.ipynb` - Interview results processing
- `insert_kaim_trainees.ipynb` - KAIM program trainees
- `insert_reviewer.ipynb` - Reviewer account creation
- `Insert_simulation_trainees.ipynb` - Simulation program trainees
- `Insert_U2J_trainees.ipynb` - University to Job program trainees
- `insert_user_for_special_challenge.ipynb` - Special challenge participants
- `review_analysis.ipynb` - Review data analysis and insights

### **3. 🔧 Review Scripts (`/review_scripts/`)**
Core business logic modules:
- `communication_manager.py` - Strapi GraphQL query management
- `strapi_methods.py` - REST API interactions with Strapi
- `strapi_graphql.py` - GraphQL client for Strapi
- `insert_allusers.py` - Batch user insertion logic
- `insert_interview.py` - Interview process management
- `trainee_information_processor.py` - Trainee data processing
- `staff_information_processor.py` - Staff data processing

### **4. ⚙️ Configuration (`/run_configs/`)**
Program-specific configurations:
- `intensive_batch9_trainee_config.py` - Intensive program settings
- `kiam_trainee_config.py` - KAIM program settings
- `simulation_trainee_config.py` - Simulation program settings
- `u2j_trainee_config.py` - U2J program settings
- `u2j_staff_config.py` - U2J staff settings

### **5. 🛠️ Utilities (`/utils/`)**
Shared utility functions:
- `question_mapper.py` - Dynamic question mapping for different batches
- `gdrive.py` - Google Sheets integration
- `s3_utils.py` - AWS S3 file operations
- `secret.py` - Secure credential management
- `tenx_logger.py` - Centralized logging system

## ✨ Features

### **📝 Application & Review Management**
- **Google Sheets Integration**: Direct import from application forms
- **Dynamic Question Mapping**: Adapt questions based on batch and program
- **Review Categories**: Organize reviews by type and criteria
- **Reviewer Assignment**: Assign specific reviewers to applications
- **Interview Tracking**: Manage interview schedules and results

### **👥 User & Batch Management**
- **Multi-Program Support**: Handle Intensive, U2J, KAIM, Simulation, and more
- **Batch Processing**: Process hundreds of trainees simultaneously
- **Role-Based Access**: Trainees, staff, reviewers, and admin roles
- **Profile Management**: Complete user profiles with custom fields
- **Status Tracking**: Track application and trainee status throughout lifecycle

### **🔌 Integration & Automation**
- **Strapi CMS Integration**: Seamless content management system integration
- **Multi-Environment Support**: Dev, staging, production for each program
- **Email Notifications**: Automated welcome emails and status updates
- **Webhook Support**: Real-time callbacks for external systems
- **Google Drive Integration**: Direct access to application sheets

### **🔐 Security & Validation**
- **JWT Authentication**: Secure token-based authentication
- **CORS Protection**: Domain-specific access control
- **Data Validation**: Comprehensive input validation and sanitization
- **Resource Cleanup**: Automatic cleanup of failed operations
- **Environment Isolation**: Separate configurations for different environments

### **🛠️ Developer Experience**
- **Interactive Notebooks**: Jupyter notebooks for exploratory operations
- **API Documentation**: Auto-generated interactive documentation
- **Docker Support**: Complete containerization
- **Comprehensive Logging**: Structured logging for debugging and monitoring
- **Configuration Management**: Environment-specific configurations

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Docker & Docker Compose (recommended)
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/10xac/review.git
cd review
```

### 2. Quick Setup with Docker

```bash
# Build and start the application
./build.sh

# The API will be available at http://localhost:8000
```

### 3. Access the System

- **API Base URL**: http://localhost:8000
- **Interactive Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Jupyter Notebooks**: Launch with `jupyter notebook notebooks/`

## 🛠️ Installation

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/10xac/review.git
cd review

# Build and run with Docker Compose
docker-compose up --build -d

# Check logs
docker-compose logs -f
```

### Option 2: Local Development

```bash
# Clone the repository
git clone https://github.com/10xac/review.git
cd review

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt  # Core dependencies
pip install -r api/requirements.txt  # API dependencies

# Set environment variables
export STRAPI_STAGE=dev
export PORT=8000

# Run the API
./start.sh

# Or run Jupyter notebooks
jupyter notebook notebooks/
```

### Option 3: Production Setup

```bash
# Use the production build script
./build.sh

# Or manually with Docker Compose
docker-compose -f docker-compose.yml up -d --build
```

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `STRAPI_STAGE` | Environment stage (dev/prod/simulation/kaim/u2j/apply/tenacious/demo) | `dev` | Yes |
| `PORT` | API server port | `8000` | No |
| `HOST` | API server host | `0.0.0.0` | No |
| `WORKERS` | Number of worker processes | `4` | No |

### Multi-Program Support

The system supports multiple 10 Academy programs, each with its own Strapi instance:

| Program | STRAPI_STAGE | Description | Domain |
|---------|-------------|-------------|---------|
| **Development** | `dev` | Development environment | dev-cms.10academy.org |
| **Production** | `prod` | Main production environment | cms.10academy.org |
| **Simulation** | `simulation` | Simulation training program | simulation-cms.10academy.org |
| **KAIM** | `kaim` | Kigali AI & ML program | kaimcms.10academy.org |
| **U2J** | `u2j` | University to Job program | u2jcms.10academy.org |
| **Apply** | `apply` | Application system | apply-cms.10academy.org |
| **Tenacious** | `tenacious` | Tenacious program | cms.gettenacious.com |
| **Demo** | `demo` | Demo environment | democms.10academy.org |

### Program Configuration

Each program has its own configuration files in `/run_configs/`:

```bash
# Example: Configure for KAIM program
export STRAPI_STAGE=kaim

# Example: Configure for U2J program  
export STRAPI_STAGE=u2j

# Example: Configure for Simulation program
export STRAPI_STAGE=simulation
```

### CORS Configuration

The API is configured to accept requests from:
- Any subdomain of `10academy.org`
- Any subdomain of `gettenacious.com`
- Localhost (for development)

## 📚 Usage Guide

### **🌐 Using the API**

For detailed API documentation, see [API_DOCUMENTATION.md](./API_DOCUMENTATION.md)

#### Key API Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/trainee/single` | Create single trainee | No |
| `POST` | `/trainee/admin-single` | Create trainee (admin) | Yes |
| `POST` | `/trainee/batch` | Process batch CSV | Yes |
| `POST` | `/webhook` | Webhook handler | No |

#### Interactive API Documentation

Once the API is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### **📓 Using Jupyter Notebooks**

The system includes interactive notebooks for various operations:

#### 1. **General User Management**
```bash
# Launch Jupyter
jupyter notebook notebooks/

# Open insert_all_users.ipynb for general user operations
```

#### 2. **Program-Specific Operations**
```bash
# For KAIM program trainees
notebooks/insert_kaim_trainees.ipynb

# For U2J program trainees  
notebooks/Insert_U2J_trainees.ipynb

# For Intensive program trainees
notebooks/Insert_intensive_trainees.ipynb

# For Simulation program trainees
notebooks/Insert_simulation_trainees.ipynb
```

#### 3. **Review & Interview Management**
```bash
# Create reviewer accounts
notebooks/insert_reviewer.ipynb

# Process interview results
notebooks/insert_Interview_accepted_trainees.ipynb

# Analyze review data
notebooks/review_analysis.ipynb
```

### **⚙️ Using Configuration Scripts**

#### Program-Specific Configurations

Each program has its own configuration in `/run_configs/`:

```python
# Example: KAIM program configuration
from run_configs.kiam_trainee_config import *

# Example: U2J program configuration  
from run_configs.u2j_trainee_config import *

# Example: Simulation program configuration
from run_configs.simulation_trainee_config import *
```

#### Using Review Scripts

```python
# Import applications from Google Sheets
from review_scripts.insert_allusers import InsertAllUsers

# Initialize for specific program
inserter = InsertAllUsers(
    run_stage="kaim",
    sid_application="your_sheet_id",
    batch="batch-1",
    role="trainee"
)

# Process applications
inserter.insert_trainee_from_gsheet()
```

### **🔧 Common Workflows**

#### 1. **Setting Up a New Batch**

```bash
# 1. Configure environment
export STRAPI_STAGE=simulation

# 2. Update configuration file
# Edit run_configs/simulation_trainee_config.py

# 3. Run the appropriate notebook
jupyter notebook notebooks/Insert_simulation_trainees.ipynb
```

#### 2. **Processing Applications**

```bash
# 1. Set up Google Sheets integration
# Place service account JSON in appropriate location

# 2. Configure sheet ID in run_configs
# Update sheet_id and sheet_name

# 3. Run insertion script
python review_scripts/insert_allusers.py
```

#### 3. **Managing Reviews**

```bash
# 1. Create review categories and reviewers
jupyter notebook notebooks/insert_reviewer.ipynb

# 2. Process interview results
jupyter notebook notebooks/insert_Interview_accepted_trainees.ipynb

# 3. Analyze review data
jupyter notebook notebooks/review_analysis.ipynb
```

## 💡 Usage Examples

### **API Usage**

#### Create a Single Trainee
```bash
curl -X POST "http://localhost:8000/trainee/single" \
  -H "Content-Type: application/json" \
  -d '{
    "config": {
      "run_stage": "dev",
      "batch": "test_batch",
      "role": "trainee",
      "is_mock": true
    },
    "trainee": {
      "name": "John Doe",
      "email": "john.doe@example.com",
      "nationality": "Kenya",
      "gender": "Male"
    }
  }'
```

#### Process Batch Upload
```bash
curl -X POST "http://localhost:8000/trainee/batch" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@trainees.csv" \
  -F "run_stage=dev" \
  -F "batch=batch_001" \
  -F "is_mock=true"
```

#### CSV Format for Batch Upload
```csv
name,email,nationality,gender,date_of_birth
John Doe,john.doe@example.com,Kenya,Male,1995-01-01
Jane Smith,jane.smith@example.com,Uganda,Female,1996-02-15
```

### **Script Usage**

#### Using Review Scripts Directly
```python
from review_scripts.insert_interview import InsertInterview

# Initialize interview processor
interview_processor = InsertInterview(
    run_stage="kaim",
    batch=2,
    sid_interview_admited="your_sheet_id",
    sheet_name="Interview Results"
)

# Process interview results
interview_processor.insert_interview_from_gsheet()
```

#### Using Configuration Files
```python
# Load program-specific configuration
import sys
sys.path.append('run_configs')

from kiam_trainee_config import *

print(f"Batch: {batch}")
print(f"Sheet ID: {sheet_id}")
print(f"Run Stage: {run_stage}")
```

## 🔧 Development

### Project Structure

```
review/
├── api/                           # 🌐 FastAPI Application
│   ├── main.py                   # FastAPI app entry point with CORS
│   ├── routes/                   # API route handlers
│   │   ├── trainee_routes.py    # Trainee management endpoints
│   │   ├── batch_routes.py      # Batch processing endpoints
│   │   └── webhook_routes.py    # Webhook handling
│   ├── services/                 # Business logic services
│   │   ├── trainee_service.py   # Individual trainee processing
│   │   ├── batch_service.py     # Batch processing logic
│   │   ├── email_service.py     # Email notifications
│   │   └── webhook_service.py   # Webhook notifications
│   ├── models/                   # Pydantic data models
│   ├── core/                     # Core functionality
│   │   ├── auth.py              # JWT authentication
│   │   ├── config.py            # Configuration management
│   │   └── error_handlers.py    # Custom error handling
│   └── controllers/              # Request controllers
├── notebooks/                     # 📓 Jupyter Notebooks
│   ├── insert_all_users.ipynb   # General user management
│   ├── insert_kaim_trainees.ipynb # KAIM program trainees
│   ├── Insert_U2J_trainees.ipynb # U2J program trainees
│   ├── insert_reviewer.ipynb    # Reviewer management
│   ├── insert_Interview_accepted_trainees.ipynb # Interview processing
│   └── review_analysis.ipynb    # Review data analysis
├── review_scripts/               # 🔧 Core Business Logic
│   ├── communication_manager.py # Strapi GraphQL queries
│   ├── strapi_methods.py        # Strapi REST API client
│   ├── strapi_graphql.py        # GraphQL client
│   ├── insert_allusers.py       # Batch user insertion
│   ├── insert_interview.py      # Interview management
│   └── *_processor.py           # Data processing modules
├── run_configs/                  # ⚙️ Program Configurations
│   ├── kiam_trainee_config.py   # KAIM program settings
│   ├── u2j_trainee_config.py    # U2J program settings
│   ├── simulation_trainee_config.py # Simulation settings
│   └── intensive_batch*_config.py # Intensive program settings
├── utils/                        # 🛠️ Shared Utilities
│   ├── question_mapper.py       # Dynamic question mapping
│   ├── gdrive.py               # Google Sheets integration
│   ├── s3_utils.py             # AWS S3 operations
│   ├── secret.py               # Credential management
│   └── tenx_logger.py          # Centralized logging
├── logs/                         # 📝 Application Logs
├── docker-compose.yml           # 🐳 Docker configuration
├── Dockerfile                   # Container definition
├── API_DOCUMENTATION.md         # 📚 Detailed API docs
└── README.md                    # This comprehensive guide
```

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/
```

### Code Quality

```bash
# Install development dependencies
pip install black flake8 isort

# Format code
black api/
isort api/

# Check code quality
flake8 api/
```

### Development Workflow

1. **Create a feature branch**:
   ```bash
   git checkout main
   git pull origin main
   git checkout -b feature/your-feature-name
   ```

2. **Make changes and test**:
   ```bash
   # Make your changes
   # Test locally
   python -m pytest
   ```

3. **Commit and push**:
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   git push origin feature/your-feature-name
   ```

4. **Create pull request** to the main branch

## 🚀 Deployment

### Production Deployment

1. **Set environment variables**:
   ```bash
   export STRAPI_STAGE=prod
   export PORT=8000
   export WORKERS=4
   ```

2. **Deploy with Docker**:
   ```bash
   ./build.sh
   ```

3. **Monitor the deployment**:
   ```bash
   docker-compose logs -f
   ```

### Health Checks

The API includes health check endpoints:
- **Health**: `GET /health`
- **Metrics**: `GET /metrics`

### Monitoring

Check application logs:
```bash
# Docker logs
docker-compose logs -f api

# Local logs
tail -f logs/errors.log
tail -f logs/batch_processing.log
```

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

### Branch Naming Convention

- Feature branches: `feature/description`
- Bug fixes: `fix/description`
- Documentation: `docs/description`
- Refactoring: `refactor/description`

### Commit Message Format

```
type(scope): description

feat(api): add batch processing endpoint
fix(auth): resolve JWT validation issue
docs(readme): update installation instructions
```

### Pull Request Process

1. **Fork the repository**
2. **Create a feature branch** from `main`
3. **Make your changes** with tests
4. **Update documentation** if needed
5. **Submit a pull request** with a clear description

### Code Standards

- Follow PEP 8 for Python code
- Use type hints where possible
- Write docstrings for functions and classes
- Add tests for new functionality
- Update documentation for API changes

## 🔍 Troubleshooting

### Common Issues

#### 1. Docker Build Fails

```bash
# Clean Docker cache
docker system prune -a

# Rebuild from scratch
docker-compose build --no-cache
```

#### 2. Authentication Errors

```bash
# Check Strapi stage configuration
echo $STRAPI_STAGE

# Verify JWT token is valid
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/health
```

#### 3. CSV Processing Fails

- Ensure CSV has required columns: `name`, `email`
- Check file encoding (UTF-8 recommended)
- Verify file size is under 10MB

#### 4. Email Notifications Not Working

- Check AWS SES configuration
- Verify sender email is verified in SES
- Check logs for email service errors

### Debug Mode

Enable debug logging:

```bash
export LOG_LEVEL=DEBUG
./start.sh
```

### Getting Help

1. **Check the logs**: Look in `logs/` directory for error details
2. **Review documentation**: See [API_DOCUMENTATION.md](./API_DOCUMENTATION.md)
3. **Search issues**: Check existing GitHub issues
4. **Create an issue**: Report bugs or request features

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 📞 Support

For support, please:
1. Check this README and the API documentation
2. Contact the 10 Academy development team

