# Backend Tests

Comprehensive test suite for Demo Copilot backend using pytest.

## Prerequisites

Before running tests, ensure you have:

1. **Python 3.11+** installed
2. **Virtual environment** set up
3. **Dependencies** installed

## Setup

### 1. Create and Activate Virtual Environment

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Linux/macOS
# OR
venv\Scripts\activate     # On Windows
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
pip install -r requirements-test.txt
```

### 3. Set Environment Variables

Create a `.env` file or export:

```bash
export TEST_DATABASE_URL="postgresql+asyncpg://user:pass@localhost/demo_copilot_test"
export ANTHROPIC_API_KEY="your_key_here"
export ELEVENLABS_API_KEY="your_key_here"
```

## Running Tests

### Run All Tests

```bash
pytest
```

### Run Specific Test File

```bash
pytest tests/test_browser_controller.py
pytest tests/test_voice_engine.py
pytest tests/test_question_handler.py
pytest tests/test_api.py
```

### Run with Coverage

```bash
pytest --cov=agents --cov=api --cov-report=html
```

View coverage report at `htmlcov/index.html`

### Run Without Slow Tests

```bash
pytest -m "not slow"
```

### Run Only Integration Tests

```bash
pytest -m "integration"
```

### Run with Verbose Output

```bash
pytest -v
pytest -vv  # Extra verbose
```

## Test Structure

```
tests/
├── conftest.py                    # Shared fixtures and configuration
├── test_browser_controller.py     # Browser automation tests
├── test_voice_engine.py           # Voice/TTS tests
├── test_question_handler.py       # Question handling tests
└── test_api.py                    # API endpoint tests
```

## Fixtures

Available fixtures (defined in `conftest.py`):

- `event_loop` - Async event loop for tests
- `test_engine` - Test database engine
- `test_db` - Test database session
- `client` - HTTP test client
- `sample_demo_request` - Sample demo start request
- `mock_anthropic_response` - Mock Anthropic API response

## Configuration

Test configuration is in `pytest.ini`:

- **testpaths**: `tests` directory
- **asyncio_mode**: `auto` (automatic async test detection)
- **markers**: `slow`, `integration`

## Common Issues

### No module named 'agents' or 'api'

Make sure you're in the `backend` directory and have activated the virtual environment.

### Database connection errors

Ensure PostgreSQL is running and `TEST_DATABASE_URL` is set correctly.

### Import errors

Install all dependencies:
```bash
pip install -r requirements.txt
pip install -r requirements-test.txt
```

### Playwright browser not found

Install Playwright browsers:
```bash
playwright install chromium
```

## CI/CD Integration

### GitHub Actions

```yaml
- name: Run backend tests
  run: |
    cd backend
    pip install -r requirements.txt
    pip install -r requirements-test.txt
    pytest --cov=agents --cov=api
```

## Coverage Goals

- **Agents**: >80% coverage
- **API**: >90% coverage
- **Overall**: >75% coverage
