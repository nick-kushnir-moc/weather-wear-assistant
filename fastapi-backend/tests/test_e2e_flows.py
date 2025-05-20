mport pytest
from playwright.sync_api import Page, expect
import os
import time
from unittest.mock import patch

# URL Configuration
BASE_URL = os.getenv("TEST_BASE_URL", "http://localhost:3000")
API_URL = os.getenv("TEST_API_URL", "http://localhost:8000")

# Skip these tests if E2E flag is not set (to avoid running in every test suite)
pytestmark = pytest.mark.skipif(
    os.getenv("ENABLE_E2E_TESTS") != "true",
    reason="E2E tests are disabled. Set ENABLE_E2E_TESTS=true to run them."
)

@pytest.mark.e2e
class TestNLQueryE2E:
    """End-to-end tests for Natural Language Query feature"""
    
    def test_nl_query_submission_and_results(self, page: Page):
        """Test the full flow of submitting a query and viewing results"""
        # Set up API interception to provide consistent results
        page.route(f"{API_URL}/api/nl-query/process", lambda route: route.fulfill(
            status=200,
            json={
                "original_query": "Show all employees in AAP department",
                "sql_query": 'SELECT e.id, e.name, d.name as department_name FROM "employees" e JOIN "departments" d ON e.dept_id = d.id WHERE d.name = \'AAP\';',
                "results": [
                    {"id": 1, "name": "John Doe", "department_name": "AAP"},
                    {"id": 2, "name": "Jane Smith", "department_name": "AAP"}
                ],
                "user_message": "Found 2 employees in the AAP department: John Doe and Jane Smith.",
                "metadata": {"execution_time_seconds": 0.123, "row_count": 2}
            }
        ))
        
        # Navigate to the application
        page.goto(f"{BASE_URL}")
        
        # Wait for the page to load
        page.wait_for_selector("h1:has-text('Personal AI Assistant')")
        
        # Find and interact with the NL Query component
        page.click("text=Database Query")  # Click tab if using tabs
        
        # Enter a query
        query_input = page.locator("input[placeholder*='Show']")
        query_input.fill("Show all employees in AAP department")
        
        # Submit the query
        page.click("button:has-text('Search')")
        
        # Wait for results to appear
        page.wait_for_selector("h3:has-text('Results')")
        
        # Verify SQL query appears
        sql_element = page.locator(".sql-query pre")
        expect(sql_element).to_contain_text("SELECT")
        expect(sql_element).to_contain_text("employees")
        expect(sql_element).to_contain_text("AAP")
        
        # Verify results table appears
        results_table = page.locator("table")
        expect(results_table).to_be_visible()
        
        # Verify result count
        row_count = page.locator("tbody tr").count()
        assert row_count == 2, f"Expected 2 rows in results, got {row_count}"
        
        # Verify table contains expected data
        expect(page.locator("tbody tr:first-child")).to_contain_text("John Doe")
        expect(page.locator("tbody tr:nth-child(2)")).to_contain_text("Jane Smith")
        
        # Screenshot for verification
        page.screenshot(path=f"test-results/nl-query-results.png")
    
    def test_nl_query_error_handling(self, page: Page):
        """Test error handling when query processing fails"""
        # Mock an error response
        page.route(f"{API_URL}/api/nl-query/process", lambda route: route.fulfill(
            status=200,
            json={
                "original_query": "This will cause an error",
                "sql_query": "",
                "results": [],
                "error": "Failed to process query: LLM processing error",
                "metadata": {}
            }
        ))
        
        # Navigate to the application
        page.goto(f"{BASE_URL}")
        
        # Find and interact with the NL Query component
        page.click("text=Database Query")  # Click tab if using tabs
        
        # Enter a problematic query
        query_input = page.locator("input[placeholder*='Show']")
        query_input.fill("This will cause an error")
        
        # Submit the query
        page.click("button:has-text('Search')")
        
        # Wait for error message to appear
        error_message = page.locator(".error")
        expect(error_message).to_be_visible()
        expect(error_message).to_contain_text("Failed to process query")
        
        # Verify no results table appears
        results_table = page.locator("table")
        expect(results_table).not_to_be_visible()
        
        # Screenshot for verification
        page.screenshot(path=f"test-results/nl-query-error.png")

@pytest.mark.e2e
class TestWeatherAssistantE2E:
    """End-to-end tests for Weather-based Clothing Assistant feature"""
    
    def test_weather_dress_recommendation_flow(self, page: Page):
        """Test the full flow of getting weather-based clothing recommendations"""
        # Set up API interception
        page.route(f"{API_URL}/api/weather-assistant/dress-recommendation", lambda route: route.fulfill(
            status=200,
            json={
                "date": "2023-10-20",
                "location": "London, UK",
                "weather_summary": "Cloudy with temperature of 15.5°C",
                "temperature": 15.5,
                "conditions": "Cloudy",
                "recommendations": {
                    "summary": "It's a cool, cloudy day. Dress in layers.",
                    "outfit": {
                        "top": [3, "Black hoodie"],
                        "bottom": [1, "Blue jeans"],
                        "footwear": [1, "White sneakers"]
                    },
                    "tips": ["Bring a light jacket in case it gets colder"]
                }
            }
        ))
        
        # Navigate to the application
        page.goto(f"{BASE_URL}")
        
        # Wait for the page to load
        page.wait_for_selector("h1:has-text('Personal AI Assistant')")
        
        # Find and interact with the Weather Assistant component
        page.click("text=Weather Assistant")  # Click tab if using tabs
        
        # Fill in the form
        page.locator("input#location").fill("London, UK")
        page.locator("input#date").fill("2023-10-20")
        page.locator("input#occasion").fill("Casual day out")
        
        # Submit the form
        page.click("button:has-text('Get Recommendations')")
        
        # Wait for recommendation to appear
        page.wait_for_selector(".recommendation")
        
        # Verify weather info displays correctly
        weather_info = page.locator(".weather-info")
        expect(weather_info).to_contain_text("London, UK")
        expect(weather_info).to_contain_text("15.5°C")
        expect(weather_info).to_contain_text("Cloudy")
        
        # Verify outfit recommendations
        outfit_section = page.locator(".outfit-recommendation")
        expect(outfit_section).to_contain_text("Black hoodie")
        expect(outfit_section).to_contain_text("Blue jeans")
        expect(outfit_section).to_contain_text("White sneakers")
        
        # Verify tips
        tips_section = page.locator(".tips")
        expect(tips_section).to_contain_text("Bring a light jacket")
        
        # Screenshot for verification
        page.screenshot(path=f"test-results/weather-recommendation.png")
    
    def test_weather_error_handling(self, page: Page):
        """Test error handling when weather service fails"""
        # Mock an error response
        page.route(f"{API_URL}/api/weather-assistant/dress-recommendation", lambda route: route.fulfill(
            status=500,
            json={
                "detail": "Weather forecast not available for the specified date. Please choose a date within the next 5 days."
            }
        ))
        
        # Navigate to the application
        page.goto(f"{BASE_URL}")
        
        # Find and interact with the Weather Assistant component
        page.click("text=Weather Assistant")  # Click tab if using tabs
        
        # Fill in the form with problematic data
        page.locator("input#location").fill("London, UK")
        page.locator("input#date").fill("2030-01-01")  # Far future date
        
        # Submit the form
        page.click("button:has-text('Get Recommendations')")
        
        # Wait for error message to appear
        error_message = page.locator(".error")
        expect(error_message).to_be_visible()
        expect(error_message).to_contain_text("Weather forecast not available")
        
        # Verify recommendation section doesn't appear
        recommendation = page.locator(".recommendation")
        expect(recommendation).not_to_be_visible()
        
        # Screenshot for verification
        page.screenshot(path=f"test-results/weather-error.png")