# ENEM Pipeline Tests

This directory contains comprehensive tests for the ENEM microdata ETL pipeline.

## Test Structure

- `unit/` - Unit tests for individual components
- `integration/` - Integration tests (if any)
- `test_execution.log` - Test execution logs

## Running Tests

### Prerequisites

1. Install test dependencies:
```bash
pip install -r requirements-test.txt
```

2. Set up environment variables (optional for database tests):
```bash
# Copy the template and fill in your values
cp config/env.template .env
```

### Basic Test Execution

Run all tests (excluding database tests):
```bash
pytest
```

Run all tests including database tests (if database is configured):
```bash
pytest --run-database
```

### Test Categories

#### Unit Tests (No Database Required)
These tests can run without any database configuration:
```bash
pytest -m "not database"
```

#### Database Tests (Optional)
These tests require database configuration:
```bash
pytest -m "database"
```

### Environment Variables for Database Tests

To run database tests, you need to set the following environment variables:

```bash
export DB_USER=your_username
export DB_PASSWORD=your_password
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=your_database
```

Or create a `.env` file in the project root:
```env
DB_USER=your_username
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_database
```

### Test Execution Options

#### Run Specific Test Categories
```bash
# Run only unit tests (no database)
pytest -m "not database"

# Run only database tests
pytest -m "database"

# Run only fast tests
pytest -m "not slow"

# Run only integration tests
pytest -m "integration"
```

#### Run Specific Test Files
```bash
# Run specific test file
pytest tests/unit/test_assertions.py

# Run specific test class
pytest tests/unit/test_assertions.py::TestConfiguration

# Run specific test method
pytest tests/unit/test_assertions.py::TestConfiguration::test_environment_variables
```

#### Verbose Output
```bash
# More detailed output
pytest -v

# Even more detailed output
pytest -vv

# Show print statements
pytest -s
```

#### Test Coverage
```bash
# Run with coverage (requires pytest-cov)
pytest --cov=src --cov-report=html --cov-report=term-missing
```

### Test Markers

The following markers are available:

- `@pytest.mark.database` - Tests that require database configuration
- `@pytest.mark.slow` - Tests that are slow to run
- `@pytest.mark.integration` - Integration tests

### Logging

Test execution logs are written to:
- Console output (INFO level)
- `tests/test_execution.log` (DEBUG level)

### Troubleshooting

#### Database Connection Issues
If you encounter database connection errors:

1. **Skip database tests entirely:**
   ```bash
   pytest -m "not database"
   ```

2. **Check environment variables:**
   ```bash
   echo $DB_USER $DB_HOST $DB_PORT $DB_NAME
   ```

3. **Verify database is running:**
   ```bash
   # For PostgreSQL
   pg_isready -h $DB_HOST -p $DB_PORT
   ```

#### Test Failures
1. Check the test logs in `tests/test_execution.log`
2. Run tests with verbose output: `pytest -v`
3. Run specific failing tests: `pytest tests/unit/test_assertions.py::TestClassName::test_method_name`

### Continuous Integration

For CI/CD pipelines, you can:

1. **Run without database tests:**
   ```bash
   pytest -m "not database"
   ```

2. **Run with database tests (if database is available):**
   ```bash
   pytest --run-database
   ```

3. **Run with coverage:**
   ```bash
   pytest --cov=src --cov-report=xml --cov-report=term-missing
   ```

### Adding New Tests

When adding new tests:

1. **For database-dependent tests:**
   ```python
   @pytest.mark.database
   def test_database_operation(self):
       if not has_database_config():
           pytest.skip("Database configuration not available")
       # Your test code here
   ```

2. **For unit tests (no database):**
   ```python
   def test_unit_operation(self):
       # Your test code here
   ```

3. **For slow tests:**
   ```python
   @pytest.mark.slow
   def test_slow_operation(self):
       # Your test code here
   ```

### Test Data

Test data is generated dynamically using fixtures. No external data files are required for running the tests. 