import pytest
import os
import sys
from unittest.mock import patch, MagicMock

# Add the project root to path to ensure imports work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import your FastAPI app and other necessary components
from main import app
from db import get_db

# Test client for FastAPI app
@pytest.fixture
def client():
    from fastapi.testclient import TestClient
    return TestClient(app)

# Mock database connection
@pytest.fixture
def mock_db():
    """Create a mock database connection for testing"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    
    # Configure fetchall for general query results
    mock_cursor.fetchall.return_value = [
        {"id": 1, "name": "John Doe", "dept_id": 1, "department_name": "AAP"},
        {"id": 2, "name": "Jane Smith", "dept_id": 2, "department_name": "CBD"}
    ]
    
    # Configure fetchone for single row queries
    mock_cursor.fetchone.return_value = (1, "John Doe")
    
    # Override the get_db dependency
    app.dependency_overrides[get_db] = lambda: mock_conn
    yield mock_conn
    app.dependency_overrides = {}

# Mock OpenAI API client
@pytest.fixture
def mock_openai():
    """Create a mock OpenAI client"""
    with patch('openai.OpenAI') as mock_client:
        # Create the nested structure needed
        client_instance = MagicMock()
        chat_completions = MagicMock()
        response = MagicMock()
        choice = MagicMock()
        message = MagicMock()
        
        # Set up the message content
        message.content = "This is a mock response from the OpenAI API."
        
        # Build the nested structure
        choice.message = message
        response.choices = [choice]
        chat_completions.create.return_value = response
        client_instance.chat.completions = chat_completions
        
        # Return mocked client instance
        mock_client.return_value = client_instance
        yield mock_client

# Mock LangChain OpenAI
@pytest.fixture
def mock_langchain():
    """Create a mock LangChain OpenAI LLM"""
    with patch('langchain_community.llms.OpenAI') as mock_llm:
        # Create the mock LLM instance
        llm_instance = MagicMock()
        
        # Configure the run method to return predictable response
        llm_instance.run.return_value = "Mock LangChain response"
        
        # Return the mock instance from the constructor
        mock_llm.return_value = llm_instance
        yield mock_llm

# Mock LangChain LLMChain
@pytest.fixture
def mock_llm_chain():
    """Create a mock LangChain LLMChain"""
    with patch('langchain.chains.LLMChain') as mock_chain:
        # Create the mock chain instance
        chain_instance = MagicMock()
        
        # Configure the run method to return predictable response
        chain_instance.run.return_value = "Mock LLMChain response"
        
        # Return the mock chain instance from the constructor
        mock_chain.return_value = chain_instance
        yield mock_chain

# Preset mock responses for specific LLM queries
@pytest.fixture
def mock_sql_generation():
    """Mock for SQL generation from natural language"""
    with patch('routers.nl_query.process_natural_language_query') as mock_fn:
        mock_fn.return_value = """
        SELECT e.id, e.name, d.name as department_name 
        FROM "employees" e 
        JOIN "departments" d ON e.dept_id = d.id 
        WHERE d.name = 'AAP';
        """
        yield mock_fn

@pytest.fixture
def mock_weather_forecast():
    """Mock for weather forecast data"""
    with patch('routers.weather_assistant.get_weather_forecast') as mock_fn:
        # Return a weather forecast
        mock_fn.return_value = {
            "temperature": 15.5,
            "feels_like": 14.0,
            "humidity": 65,
            "conditions": "Cloudy",
            "description": "overcast clouds",
            "wind_speed": 10,
            "summary": "Cloudy with temperature of 15.5°C"
        }
        yield mock_fn

# Mock the responses library for HTTP request mocking
@pytest.fixture
def mock_http_responses():
    """Set up mocked HTTP responses using the responses library"""
    import responses
    with responses.RequestsMock() as rsps:
        yield rsps