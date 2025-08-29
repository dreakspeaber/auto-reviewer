# GCP Module Test Suite

This directory contains comprehensive tests for the `gcp.py` module.

## Test Files

- `test_gcp.py` - Main test suite for the GCP class
- `run_tests.py` - Test runner script with additional options

## Running Tests

### Using pytest directly:
```bash
# Activate virtual environment
source ../venv/bin/activate

# Run all tests
python -m pytest test_gcp.py

# Run with verbose output
python -m pytest test_gcp.py -v

# Run with coverage (requires pytest-cov)
python -m pytest test_gcp.py --cov=gcp --cov-report=term-missing
```

### Using the test runner script:
```bash
# Activate virtual environment
source ../venv/bin/activate

# Run basic tests
python run_tests.py

# Run with verbose output
python run_tests.py -v

# Run with coverage
python run_tests.py -c
```

## Test Coverage

The test suite covers the following functionality:

### GCP Class Initialization
- ✅ Proper initialization with API key
- ✅ Error handling for missing API key
- ✅ Default attribute initialization

### Configuration Method
- ✅ Configuration without response schema
- ✅ Configuration with response schema
- ✅ Custom model configuration
- ✅ Default model setting
- ✅ GenerateContentConfig setup with schema
- ✅ GenerateContentConfig setup without schema

### Stream Generation
- ✅ Async stream generation with chunks
- ✅ Empty response handling
- ✅ Message history management
- ✅ Response text accumulation

### Response Cleaning
- ✅ Response cleaning without schema (returns raw text)
- ✅ Response cleaning with Pydantic schema
- ✅ Response cleaning with complex nested schemas
- ✅ Custom text parameter handling
- ✅ JSON validation with schema
- ✅ Schema validation error handling (invalid JSON)
- ✅ Schema validation error handling (missing fields)
- ✅ Schema validation error handling (wrong data types)

### End-to-End Testing
- ✅ Complete flow with simple schema: config → generate → clean
- ✅ Complete flow with complex schema: config → generate → clean
- ✅ Full integration testing with mocked API responses

## Test Structure

The tests use:
- **pytest** as the testing framework
- **pytest-asyncio** for async test support
- **unittest.mock** for mocking external dependencies
- **Pydantic BaseModel** for schema testing

## Test Statistics

- **Total Tests**: 18 test cases
- **Coverage**: All public methods and edge cases
- **Schema Validation**: Comprehensive Pydantic model testing
- **Error Handling**: Both success and failure scenarios
- **Integration**: End-to-end workflow testing

## Dependencies

Required packages (already in requirements.txt):
- pytest==8.2.0
- pytest-asyncio==0.24.0

## Notes

- Tests are designed to run without actual API calls (all external dependencies are mocked)
- The test suite validates both success and error scenarios
- Async functionality is properly tested with appropriate mocking
- Pydantic schema validation is tested with sample data

## Adding New Tests

When adding new functionality to the GCP class:

1. Add corresponding test methods to `TestGCP` class
2. Use appropriate fixtures for setup
3. Mock external dependencies
4. Test both success and failure scenarios
5. Update this README if needed
