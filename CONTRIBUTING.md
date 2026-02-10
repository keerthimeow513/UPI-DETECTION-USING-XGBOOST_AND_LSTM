# Contributing Guide

Thank you for your interest in contributing to the UPI Fraud Detection System! This guide will help you get started with development.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Testing Requirements](#testing-requirements)
- [Pull Request Process](#pull-request-process)
- [Commit Message Guidelines](#commit-message-guidelines)
- [Documentation Guidelines](#documentation-guidelines)
- [Issue Tracking](#issue-tracking)

## Code of Conduct

This project adheres to the Contributor Covenant Code of Conduct. By participating, you are expected to uphold this code.

### Our Standards

- **Be respectful**: Inclusive language and behavior
- **Be collaborative**: Work together constructively
- **Be welcoming**: Open to newcomers and diverse perspectives
- **Be professional**: Professional and courteous interactions

### Unacceptable Behavior

- Harassment or discrimination
- Personal attacks
- Unwelcome sexual attention
- Any other conduct inappropriate in a professional setting

## Getting Started

### Types of Contributions

We welcome various types of contributions:

- 🐛 **Bug fixes**
- ✨ **New features**
- 📝 **Documentation improvements**
- 🎨 **UI/UX improvements**
- ⚡ **Performance optimization**
- 🔒 **Security enhancements**
- 🧪 **Test coverage improvements**

### First-time Contributors

If you're new to open source:

1. Look for issues labeled `good first issue`
2. Comment on the issue to express interest
3. Fork the repository
4. Create a feature branch
5. Make your changes
6. Submit a pull request

## Development Setup

### Prerequisites

- Python 3.8+
- Git
- Docker (optional)
- Redis (optional)

### Setting Up Development Environment

#### 1. Fork and Clone

```bash
# Fork the repository on GitHub

# Clone your fork
git clone https://github.com/YOUR-USERNAME/UPI_FRAUD_DETECTION.git
cd UPI_FRAUD_DETECTION

# Add upstream remote
git remote add upstream https://github.com/ORIGINAL-OWNER/UPI_FRAUD_DETECTION.git
```

#### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Linux/Mac:
source venv/bin/activate

# Windows:
venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip
```

#### 3. Install Development Dependencies

```bash
# Install all dependencies
pip install -r requirements.txt

# Install development tools
pip install pytest pytest-cov pytest-asyncio
pip install black isort flake8 mypy
pip install pre-commit
```

#### 4. Set Up Pre-commit Hooks

```bash
# Install pre-commit hooks
pre-commit install

# Run initial check
pre-commit run --all-files
```

#### 5. Configure Environment

```bash
# Copy environment file
cp .env.example .env

# Edit with your settings
nano .env
```

#### 6. Verify Installation

```bash
# Run tests to verify setup
python -m pytest tests/ -v

# Start the API to verify it works
uvicorn 04_inference.api:app --reload
```

## Coding Standards

### Python Style Guide

We follow **PEP 8** with additional conventions.

#### Code Formatting

Use `black` for formatting:

```bash
# Format code
black 04_inference/api.py

# Check formatting
black --check 04_inference/api.py
```

#### Import Sorting

Use `isort` for import sorting:

```bash
# Sort imports
isort 04_inference/api.py

# Check import order
isort --check-only 04_inference/api.py
```

#### Linting

Use `flake8` for linting:

```bash
# Run linter
flake8 04_inference/api.py

# With configuration
flake8 --config .flake8 04_inference/
```

#### Type Hints

Use type hints for all function signatures:

```python
from typing import Dict, List, Optional

def predict_fraud(
    self,
    transaction_data: Dict[str, float],
    user_id: Optional[str] = None
) -> Dict[str, float]:
    """Process fraud prediction for a transaction."""
    pass
```

### Code Style Rules

#### Naming Conventions

| Type | Convention | Example |
|------|-----------|---------|
| Variables | snake_case | `transaction_amount` |
| Functions | snake_case | `calculate_risk_score` |
| Classes | PascalCase | `FraudDetectionService` |
| Constants | UPPER_SNAKE_CASE | `MAX_TRANSACTION_AMOUNT` |
| Private methods | _snake_case | `_validate_input` |
| Module-level private | __snake_case | `__init_subclass__` |

#### Documentation Strings

Use Google-style docstrings:

```python
def calculate_risk_score(
    self,
    amount: float,
    device_id: str,
    location: Tuple[float, float]
) -> float:
    """Calculate fraud risk score for a transaction.
    
    Args:
        amount: Transaction amount in INR
        device_id: Device identifier
        location: Tuple of (latitude, longitude)
    
    Returns:
        Risk score between 0.0 and 1.0
    
    Raises:
        ValueError: If amount is negative
    
    Example:
        >>> score = service.calculate_risk_score(5000.0, "device123", (12.97, 77.59))
        >>> 0.0 <= score <= 1.0
    """
    pass
```

#### File Structure

Follow the project structure:

```
project/
├── 04_inference/
│   ├── __init__.py          # Package initialization
│   ├── api.py              # FastAPI endpoints
│   ├── service.py          # Business logic
│   └── schemas.py          # Pydantic schemas
├── utils/
│   ├── __init__.py
│   ├── preprocessing.py
│   └── logger.py
├── tests/
│   ├── __init__.py
│   ├── unit/
│   └── integration/
```

### Git Workflow

#### Branch Naming

| Branch Type | Naming Convention | Example |
|-------------|-------------------|---------|
| Feature | `feature/description` | `feature/add-websocket-support` |
| Bugfix | `bugfix/issue-description` | `bugfix/fix-rate-limiting` |
| Hotfix | `hotfix/urgent-fix` | `hotfix/security-patch` |
| Release | `release/version` | `release/v1.0.0` |

#### Branch Management

```bash
# Create feature branch
git checkout -b feature/new-dashboard

# Make changes
git add .
git commit -m "feat: Add new dashboard component"

# Sync with upstream
git fetch upstream
git rebase upstream/main

# Push changes
git push origin feature/new-dashboard
```

## Testing Requirements

### Test Coverage Requirements

| Type | Minimum Coverage | Location |
|------|-----------------|----------|
| Unit tests | 80% | `tests/unit/` |
| Integration tests | 70% | `tests/integration/` |
| Overall | 75% | `tests/` |

### Writing Tests

#### Unit Tests

```python
# tests/unit/test_service.py
import pytest
from 04_inference.service import FraudDetectionService

class TestFraudDetectionService:
    """Unit tests for FraudDetectionService."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config_path = "07_configs/config.yaml"
        self.service = FraudDetectionService(self.config_path)
    
    def test_predict_valid_transaction(self):
        """Test prediction with valid transaction data."""
        transaction = {
            "SenderUPI": "user@upi",
            "ReceiverUPI": "merchant@upi",
            "Amount": 1000.0,
            "DeviceID": "82:4e:8e:2a:9e:28",
            "Latitude": 12.97,
            "Longitude": 77.59,
            "Hour": 14
        }
        
        result = self.service.predict(transaction)
        
        assert "risk_score" in result
        assert 0.0 <= result["risk_score"] <= 1.0
        assert result["verdict"] in ["ALLOW", "FLAG", "BLOCK"]
    
    def test_predict_invalid_amount(self):
        """Test prediction with invalid amount."""
        transaction = {
            "Amount": -100.0,  # Invalid
            # ... other fields
        }
        
        with pytest.raises(ValueError):
            self.service.predict(transaction)
```

#### Integration Tests

```python
# tests/integration/test_api.py
import pytest
from fastapi.testclient import TestClient
from 04_inference.api import app

@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)

def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"

def test_predict_endpoint(client):
    """Test prediction endpoint."""
    transaction = {
        "SenderUPI": "user@upi",
        "ReceiverUPI": "merchant@upi",
        "Amount": 5000.0,
        "DeviceID": "82:4e:8e:2a:9e:28",
        "Latitude": 12.97,
        "Longitude": 77.59,
        "Hour": 14
    }
    
    response = client.post("/predict", json=transaction)
    
    assert response.status_code == 200
    data = response.json()
    assert "transaction_id" in data
    assert "risk_score" in data
    assert "verdict" in data
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=04_inference --cov-report=html

# Run specific test file
pytest tests/unit/test_service.py -v

# Run specific test
pytest tests/unit/test_service.py::TestFraudDetectionService::test_predict_valid_transaction -v

# Run tests in parallel
pytest tests/ -n auto

# Generate JUnit report
pytest tests/ --junitxml=test-results.xml
```

### CI/CD Pipeline

```yaml
# .github/workflows/ci.yml
name: CI Pipeline

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.8", "3.9", "3.10", "3.11"]
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      
      - name: Run tests
        run: |
          pytest tests/ --cov=04_inference --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
```

## Pull Request Process

### Before Submitting

1. **Ensure tests pass**
   ```bash
   pytest tests/ -v
   ```

2. **Check formatting**
   ```bash
   black --check .
   isort --check .
   flake8 .
   ```

3. **Update documentation**
   - Update README if needed
   - Add docstrings for new functions
   - Update API documentation

4. **Sync with upstream**
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

### Creating a Pull Request

1. **Create descriptive title**
   - Use conventional commit format
   - Be specific about changes

2. **Write detailed description**
   - What changes were made
   - Why these changes were needed
   - How to test the changes
   - Screenshots for UI changes

3. **Link related issues**
   - Reference issue numbers: `Fixes #123`

4. **Request review**
   - Assign reviewers
   - Add relevant labels

### PR Template

```markdown
## Description
Brief description of changes made.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests added/updated
- [ ] All tests pass
- [ ] Manual testing completed

## Checklist
- [ ] My code follows the style guidelines
- [ ] I have performed a self-review
- [ ] I have commented my code
- [ ] I have made corresponding changes
- [ ] I have updated documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix works
```

### Review Process

1. **Automated checks**
   - CI pipeline passes
   - Test coverage maintained
   - No linting errors

2. **Code review**
   - Design review
   - Security review
   - Performance review

3. **Addressing feedback**
   - Make requested changes
   - Respond to comments
   - Re-request review

### Merge Strategies

| Branch | Merge Strategy |
|--------|---------------|
| Feature → Main | Squash and merge |
| Release → Main | Merge commit |
| Hotfix → Main | Squash and merge |

## Commit Message Guidelines

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

| Type | Description |
|------|-------------|
| feat | New feature |
| fix | Bug fix |
| docs | Documentation only |
| style | Formatting changes |
| refactor | Code restructuring |
| test | Adding tests |
| chore | Maintenance tasks |

### Examples

```
feat(api): Add rate limiting endpoint

Implemented rate limiting for the prediction API using slowapi.
Added configuration options in config.yaml.

Fixes #123
```

```
docs(readme): Update installation instructions

Added new prerequisites section
Updated Python version requirement to 3.8+
```

## Documentation Guidelines

### When to Update Documentation

- New features
- API changes
- Configuration changes
- Bug fixes affecting usage
- Architecture changes

### Documentation Files

| File | Purpose |
|------|---------|
| README.md | Main project documentation |
| API_DOCUMENTATION.md | API reference |
| ARCHITECTURE.md | System architecture |
| DEPLOYMENT.md | Deployment guide |
| SECURITY.md | Security documentation |
| CONTRIBUTING.md | This file |

### Docstring Requirements

All public functions and classes must have docstrings:

```python
def public_function(param1: str, param2: int) -> bool:
    """Short description of function.
    
    Longer description if needed.
    
    Args:
        param1: Description of param1
        param2: Description of param2
    
    Returns:
        Description of return value
    
    Example:
        >>> result = public_function("test", 5)
        >>> result
        True
    """
    pass
```

## Issue Tracking

### Issue Types

| Label | Description |
|-------|-------------|
| `bug` | Something isn't working |
| `enhancement` | New feature or improvement |
| `documentation` | Documentation improvements |
| `good first issue` | Good for newcomers |
| `help wanted` | Extra attention needed |
| `priority: high` | High priority |
| `priority: low` | Low priority |

### Creating Issues

Use issue templates for consistent information:

```markdown
## Bug Report
**Describe the bug**
Clear description of the bug.

**To Reproduce**
Steps to reproduce the behavior:
1. Run '...'
2. Click on '...'
3. See error

**Expected behavior**
What you expected to happen.

**Environment**
- OS: [e.g., Ubuntu 20.04]
- Python version: [e.g., 3.9]
- Package version: [e.g., 1.0.0]

**Additional context**
Screenshots, logs, etc.
```

## Recognition

Contributors are recognized in:

- [CONTRIBUTORS.md](CONTRIBUTORS.md)
- Release notes
- Project documentation

## Questions?

- Check existing documentation
- Search existing issues
- Open a new issue with question label
- Reach out to maintainers

---

**Thank you for contributing to the UPI Fraud Detection System!**
