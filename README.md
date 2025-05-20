# WEATHER-WEAR-ASSIST

A modern AI-powered personal assistant application with natural language database querying and context-aware recommendations. This full-stack application integrates OpenAI's LLM capabilities with FastAPI and Svelte to create a responsive and intelligent user experience.

## Features

- **Natural Language Database Querying**: Convert plain English questions into SQL queries
- **Weather-Based Clothing Recommendations**: Get personalized outfit suggestions based on weather forecasts
- **AI Assistant**: Interactive chat interface for general assistance
- **Voice Input Support**: Speak your queries with audio transcription
- **Responsive UI**: Works on desktop and mobile devices

## Technology Stack

### Backend
- **FastAPI**: High-performance Python API framework
- **PostgreSQL**: Relational database for structured data
- **LangChain**: Framework for LLM application development
- **OpenAI API**: Powers the natural language understanding capabilities
- **SQLAlchemy**: SQL toolkit and ORM
- **Whisper**: Speech-to-text for voice input

### Frontend
- **Svelte**: Reactive UI framework for efficient rendering
- **Axios**: HTTP client for API requests
- **Tailwind CSS**: Utility-first CSS framework for styling

### Testing
- **pytest**: Backend testing framework
- **Vitest**: Frontend unit testing framework
- **Playwright**: End-to-end testing framework
- **Testing Library**: Component testing utilities
- **MSW**: API mocking for frontend tests

## Project Structure

```
project/
├── fastapi-backend/           # Backend application
│   ├── alembic/               # Database migrations
│   ├── models/                # Pydantic and database models
│   │   ├── nl_query.py        # NL query models
│   │   └── weather_assistant.py  # Weather assistant models
│   ├── routers/               # API endpoints
│   │   ├── nl_query.py        # Natural language query endpoints
│   │   └── weather_assistant.py  # Weather recommendation endpoints
│   ├── tests/                 # Backend tests
│   │   ├── conftest.py        # Test fixtures
│   │   ├── test_unit_*.py     # Unit tests
│   │   ├── test_integration_*.py  # Integration tests
│   │   └── test_e2e_*.py      # End-to-end tests
│   ├── db.py                  # Database connection setup
│   ├── configs.py             # Configuration settings
│   └── main.py                # Application entry point
├── svelte-frontend/           # Frontend application
│   ├── public/                # Static assets
│   ├── src/                   # Source code
│   │   ├── components/        # Svelte components
│   │   │   ├── NLQueryAssistant.svelte
│   │   │   └── WeatherDressAssistant.svelte
│   │   └── App.svelte         # Main application component
│   ├── tests/                 # Frontend tests
│   │   ├── unit/              # Component unit tests
│   │   └── e2e/               # End-to-end tests
│   ├── index.html             # HTML entry point
│   └── vite.config.js         # Vite configuration
└── README.md                  # Project documentation
```

## Getting Started

### Prerequisites

- Python 3.9+
- Node.js 16+
- PostgreSQL 13+
- OpenAI API key
- OpenWeatherMap API key (for weather features)

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/ai-personal-assistant.git
   cd ai-personal-assistant
   ```

2. **Create a virtual environment**
   ```bash
   cd fastapi-backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials and API keys
   ```

5. **Initialize the database**
   ```bash
   alembic upgrade head
   ```

6. **Start the backend server**
   ```bash
   uvicorn main:app --reload
   ```

### Frontend Setup

1. **Install dependencies**
   ```bash
   cd ../svelte-frontend
   npm install
   ```

2. **Start the development server**
   ```bash
   npm run dev
   ```

3. **Access the application**
   
   Open your browser and navigate to `http://localhost:3000`

## Testing

### Backend Tests

```bash
cd fastapi-backend

# Install test dependencies
pip install -r requirements-test.txt

# Run all tests
pytest

# Run specific test categories
pytest -m unit       # Unit tests only
pytest -m integration # Integration tests only
pytest -m llm        # LLM-specific tests

# Generate coverage report
pytest --cov=. --cov-report=html
```

### Frontend Tests

```bash
cd svelte-frontend

# Run unit tests
npm run test

# Run with watch mode
npm run test:watch

# Run end-to-end tests
npm run test:e2e

# Run end-to-end tests with UI
npx playwright test --ui
```

## API Documentation

When the backend server is running, access the interactive API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Key API Endpoints

### Natural Language Query

- `POST /api/nl-query/process`: Process natural language query and return results
- `GET /api/nl-query/schema`: Get database schema information
- `POST /api/nl-query/transcribe-and-query`: Process audio query

### Weather-Based Clothing Assistant

- `POST /api/weather-assistant/dress-recommendation`: Get clothing recommendations based on weather

## LLM Integration

This project uses LLMs (Large Language Models) in several key ways:

1. **Natural Language to SQL**: Converts user queries to SQL statements
2. **SQL Query Understanding**: Provides user-friendly summaries of query results
3. **Weather-Based Recommendations**: Generates contextual clothing suggestions
4. **General Assistant**: Powers the conversational AI assistant

### Prompting Strategies

The application uses carefully designed prompts for different use cases:

- **SQL Generation**: Structured prompts with schema information
- **Clothing Recommendations**: Context-rich prompts with weather and inventory data
- **Error Handling**: Graceful degradation when LLM responses are unexpected

## Testing Strategy

The project implements a comprehensive testing strategy focused on reliability:

1. **Unit Tests**: Test individual functions in isolation
2. **Integration Tests**: Verify API endpoints with mocked dependencies
3. **Contract Tests**: Verify compatibility with external services
4. **End-to-End Tests**: Test complete user flows across the application

### LLM Testing Approach

Testing LLM interactions requires special consideration:

- **Deterministic Testing**: Mock LLM responses for consistency
- **Response Validation**: Verify the application handles different response types
- **Error Resilience**: Test how the app responds to LLM failures
- **Contract Verification**: Occasional tests against the real API to confirm compatibility

### Key Test Files

- `test_unit_llm_interactions.py`: Tests LLM-specific functions
- `test_integration_llm_endpoints.py`: Tests API endpoints with mocked LLMs
- `NLQueryAssistant.spec.js`: Tests the query component
- `WeatherDressAssistant.spec.js`: Tests the weather component
- E2E test files: Test complete user journeys

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Run the tests to ensure they pass
4. Commit your changes (`git commit -m 'Add some amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenAI for providing the API powering the LLM capabilities
- The FastAPI and Svelte communities for their excellent documentation
- Weather data provided by OpenWeatherMap API

## Testing Environment Setup

### Prerequisites

- Python 3.9+
- Node.js 16+
- PostgreSQL 13+
- Test database (separate from development database)

### Installation

#### Backend Testing Dependencies

```bash
cd fastapi-backend
pip install -r requirements-test.txt
```

#### Frontend Testing Dependencies

```bash
cd svelte-frontend
npm install
```

### Environment Configuration

1. Create a `.env.test` file in the backend directory:

```
# .env.test
DATABASE_URL=postgresql://postgres:mocAi@localhost:5432/test_db
OPENAI_API_KEY=your_test_api_key
WEATHER_API_KEY=your_test_weather_api_key
ENVIRONMENT=test
```

2. Create a test database:

```bash
createdb test_db
```

## Backend Testing

### Running Tests

```bash
cd fastapi-backend

# Run all tests
pytest

# Run specific test types
pytest -m unit           # Run only unit tests
pytest -m integration    # Run only integration tests
pytest -m llm            # Run only LLM-related tests

# Run a specific test file
pytest tests/test_unit_llm_interactions.py

# Run a specific test function
pytest tests/test_unit_llm_interactions.py::TestNLQueryLLMFunctions::test_clean_sql_query
```

### Coverage Reports

```bash
# Generate terminal report
pytest --cov=.

# Generate HTML report
pytest --cov=. --cov-report=html
# Then view htmlcov/index.html in your browser
```

### Key Test Files

- `tests/conftest.py`: Common test fixtures
- `tests/test_unit_llm_interactions.py`: Unit tests for LLM functions
- `tests/test_integration_llm_endpoints.py`: API endpoint tests
- `tests/test_e2e_flows.py`: Backend end-to-end tests
- `tests/test_llm_contracts.py`: Tests with real API calls

## Frontend Testing

### Running Tests

```bash
cd svelte-frontend

# Run unit tests
npm run test

# Run with watch mode
npm run test:watch

# Generate coverage report
npm run test:coverage
```

### Key Test Files

- `tests/setup/test-setup.js`: Test environment setup
- `tests/unit/NLQueryAssistant.spec.js`: NL Query component tests
- `tests/unit/WeatherDressAssistant.spec.js`: Weather component tests

## End-to-End Testing

### Running E2E Tests

```bash
cd svelte-frontend

# Run all E2E tests
npm run test:e2e

# Run in UI mode
npx playwright test --ui

# Run a specific E2E test file
npx playwright test tests/e2e/specs/nlquery.spec.js

# Test against specific browsers
npx playwright test --project=chromium
npx playwright test --project="Mobile Chrome"
```

### Key E2E Test Files

- `tests/e2e/page-objects/nlquery.page.js`: NL Query page object
- `tests/e2e/page-objects/weather.page.js`: Weather page object
- `tests/e2e/specs/nlquery.spec.js`: NL Query E2E tests
- `tests/e2e/specs/weather.spec.js`: Weather E2E tests

## LLM-Specific Testing

LLM testing presents unique challenges due to non-deterministic responses, API costs, and service dependencies.

### Best Practices

1. **Mock LLM responses** for deterministic tests:
   - Use the provided fixtures in `conftest.py`
   - Create realistic mock responses

2. **Test error handling thoroughly**:
   - Empty responses
   - Malformed responses
   - API errors
   - Rate limit errors

3. **Contract tests** for compatibility verification:
   - Run only when needed (`pytest -m contract`)
   - Use small/cheap models
   - Set the `ENABLE_LIVE_LLM_TESTS=true` environment variable

### Example: Testing LLM Function

```python
def test_process_natural_language_query(mock_llm_chain):
    """Test with a mocked LLM Chain"""
    # Configure mock
    chain_instance = mock_llm_chain.return_value
    chain_instance.run.return_value = "SELECT * FROM employees;"
    
    # Call function
    result = process_natural_language_query("Show all employees")
    
    # Assertions
    assert "SELECT" in result
    assert "FROM" in result
    assert "employees" in result
```

## CI/CD Integration

### GitHub Actions Configuration

Use the provided `.github/workflows/tests.yml` file:

```yaml
name: Run Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: mocAi
          POSTGRES_DB: test_db
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r fastapi-backend/requirements.txt
        pip install -r fastapi-backend/requirements-test.txt
    
    - name: Run backend tests
      run: |
        cd fastapi-backend
        pytest --cov=. --cov-report=xml
      env:
        DATABASE_URL: postgresql://postgres:mocAi@localhost:5432/test_db
        OPENAI_API_KEY: ${{ secrets.TEST_OPENAI_API_KEY }}
        WEATHER_API_KEY: ${{ secrets.TEST_WEATHER_API_KEY }}
        ENVIRONMENT: test
    
    - name: Set up Node.js
      uses: actions/setup-node@v3
      with:
        node-version: 16
    
    - name: Install frontend dependencies
      run: |
        cd svelte-frontend
        npm install
    
    - name: Run frontend tests
      run: |
        cd svelte-frontend
        npm run test
    
    - name: Install Playwright browsers
      run: |
        cd svelte-frontend
        npx playwright install --with-deps
    
    - name: Run E2E tests
      run: |
        cd svelte-frontend
        npm run test:e2e
```

## Troubleshooting

### Common Issues and Solutions

#### Backend Tests

1. **Database Connection Errors**
   - Check PostgreSQL is running
   - Verify test database exists
   - Check credentials in `.env.test`

2. **OpenAI API Errors**
   - Ensure mocks are properly configured
   - Check if `OPENAI_API_KEY` is set for contract tests

3. **Missing Test Dependencies**
   - Run `pip install -r requirements-test.txt`

#### Frontend Tests

1. **DOM Testing Errors**
   - Ensure JSDOM environment is properly configured
   - Check component mounting

2. **Network Request Errors**
   - Verify MSW is properly set up for API mocking

#### E2E Tests

1. **Browser Launch Errors**
   - Run `npx playwright install`
   - Ensure browser dependencies are installed

2. **Selector Errors**
   - Update selectors to match current UI
   - Use more robust selectors (test IDs)

3. **Timeout Errors**
   - Increase timeout settings
   - Use proper waiting conditions

### Where to Get Help

- Check the project documentation
- Review test logs and error messages
- Create an issue in the project repository