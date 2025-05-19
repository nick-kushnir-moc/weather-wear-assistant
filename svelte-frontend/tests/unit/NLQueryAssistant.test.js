import { render, fireEvent, screen, waitFor } from '@testing-library/svelte';
import { vi } from 'vitest';
import { tick } from 'svelte';
import { get } from 'svelte/store';
import NLQueryAssistant from '../../src/components/NLQueryAssistant.svelte';
import axios from 'axios';

// Mock axios
vi.mock('axios');

describe('NLQueryAssistant.svelte', () => {
  // Setup before each test
  beforeEach(() => {
    // Reset axios mocks
    vi.resetAllMocks();
  });

  test('renders correctly with initial empty state', () => {
    const { getByText, getByPlaceholderText } = render(NLQueryAssistant);
    
    // Check that component title is rendered
    expect(getByText('Database Query Assistant')).toBeInTheDocument();
    
    // Check that input field is rendered
    const inputElement = getByPlaceholderText(/Show all employees/i);
    expect(inputElement).toBeInTheDocument();
    
    // Check that search button is rendered
    const searchButton = getByText('Search');
    expect(searchButton).toBeInTheDocument();
    expect(searchButton).not.toBeDisabled();
  });

  test('displays error when submitting empty query', async () => {
    const { getByText, getByPlaceholderText } = render(NLQueryAssistant);
    
    // Get the input field and search button
    const inputElement = getByPlaceholderText(/Show all employees/i);
    const searchButton = getByText('Search');
    
    // Submit with empty query
    await fireEvent.click(searchButton);
    
    // Check that error message is displayed
    expect(getByText('Please enter a query.')).toBeInTheDocument();
  });

  test('processes query and displays results correctly', async () => {
    // Mock the API response
    const mockResponse = {
      data: {
        original_query: 'Show all employees in AAP department',
        sql_query: 'SELECT * FROM "employees" WHERE department = "AAP";',
        results: [
          { id: 1, name: 'John Doe', department: 'AAP' },
          { id: 2, name: 'Jane Smith', department: 'AAP' }
        ],
        user_message: 'Found 2 employees in the AAP department.',
        metadata: {
          execution_time_seconds: 0.5,
          row_count: 2
        }
      }
    };
    
    // Setup the mock response
    axios.post.mockResolvedValueOnce(mockResponse);
    
    // Render the component
    const { getByText, getByPlaceholderText, getAllByRole } = render(NLQueryAssistant);
    
    // Type a query
    const inputElement = getByPlaceholderText(/Show all employees/i);
    await fireEvent.input(inputElement, { target: { value: 'Show all employees in AAP department' } });
    
    // Submit the query
    const searchButton = getByText('Search');
    await fireEvent.click(searchButton);
    
    // Wait for results to be displayed
    await waitFor(() => {
      // Check SQL query is displayed
      expect(getByText(/SELECT \* FROM "employees" WHERE department = "AAP";/i)).toBeInTheDocument();
      
      // Check user message is displayed
      expect(getByText('Found 2 employees in the AAP department.')).toBeInTheDocument();
      
      // Check results table is displayed
      expect(getByText('Results: 2 rows')).toBeInTheDocument();
      
      // Check table has correct number of rows (header + 2 data rows)
      const tableRows = getAllByRole('row');
      expect(tableRows.length).toBe(3);
      
      // Check first row data
      expect(getByText('John Doe')).toBeInTheDocument();
      expect(getByText('Jane Smith')).toBeInTheDocument();
    });
    
    // Verify axios was called correctly
    expect(axios.post).toHaveBeenCalledTimes(1);
    expect(axios.post).toHaveBeenCalledWith(
      'http://localhost:8000/api/nl-query/process',
      { query: 'Show all employees in AAP department' }
    );
  });

  test('displays error when API request fails', async () => {
    // Mock API failure
    axios.post.mockRejectedValueOnce({ 
      response: { 
        data: { detail: 'Internal server error' } 
      } 
    });
    
    // Render the component
    const { getByText, getByPlaceholderText } = render(NLQueryAssistant);
    
    // Type a query
    const inputElement = getByPlaceholderText(/Show all employees/i);
    await fireEvent.input(inputElement, { target: { value: 'Show all employees' } });
    
    // Submit the query
    const searchButton = getByText('Search');
    await fireEvent.click(searchButton);
    
    // Wait for error to be displayed
    await waitFor(() => {
      expect(getByText('Internal server error')).toBeInTheDocument();
    });
  });

  test('disables search button during query processing', async () => {
    // Mock a delayed API response
    axios.post.mockImplementationOnce(() => {
      return new Promise(resolve => {
        setTimeout(() => {
          resolve({
            data: {
              original_query: 'Show all employees',
              sql_query: 'SELECT * FROM "employees";',
              results: [],
              metadata: {}
            }
          });
        }, 500);
      });
    });
    
    // Render the component
    const { getByText, getByPlaceholderText } = render(NLQueryAssistant);
    
    // Type a query
    const inputElement = getByPlaceholderText(/Show all employees/i);
    await fireEvent.input(inputElement, { target: { value: 'Show all employees' } });
    
    // Submit the query
    const searchButton = getByText('Search');
    await fireEvent.click(searchButton);
    
    // Check that button is disabled and shows "Processing..."
    await waitFor(() => {
      expect(getByText('Processing...')).toBeInTheDocument();
      expect(getByText('Processing...')).toBeDisabled();
    });
    
    // Wait for processing to complete
    await waitFor(() => {
      expect(getByText('Search')).toBeInTheDocument();
      expect(getByText('Search')).not.toBeDisabled();
    }, { timeout: 1000 });
  });
});

// svelte-frontend/tests/unit/WeatherDressAssistant.test.js
import { render, fireEvent, screen, waitFor } from '@testing-library/svelte';
import { vi } from 'vitest';
import { tick } from 'svelte';
import WeatherDressAssistant from '../../src/components/WeatherDressAssistant.svelte';
import axios from 'axios';

// Mock axios
vi.mock('axios');

describe('WeatherDressAssistant.svelte', () => {
  // Setup before each test
  beforeEach(() => {
    // Reset axios mocks
    vi.resetAllMocks();
    
    // Mock Date.now() to return a consistent date for testing
    const mockDate = new Date('2023-10-20T12:00:00Z');
    vi.spyOn(global, 'Date').mockImplementation(() => mockDate);
  });

  afterEach(() => {
    // Restore Date
    vi.restoreAllMocks();
  });

  test('renders correctly with initial state', () => {
    const { getByText, getByLabelText } = render(WeatherDressAssistant);
    
    // Check that component title is rendered
    expect(getByText('Weather-Based Dress Assistant')).toBeInTheDocument();
    
    // Check that form fields are rendered
    expect(getByLabelText('Location')).toBeInTheDocument();
    expect(getByLabelText('Date')).toBeInTheDocument();
    expect(getByLabelText('Occasion (optional)')).toBeInTheDocument();
    
    // Check that the submit button is rendered
    const submitButton = getByText('Get Recommendations');
    expect(submitButton).toBeInTheDocument();
    // Button should be disabled initially because location is empty
    expect(submitButton).toBeDisabled();
  });

  test('enables button when location and date are filled', async () => {
    const { getByText, getByLabelText } = render(WeatherDressAssistant);
    
    // Get form fields
    const locationInput = getByLabelText('Location');
    const dateInput = getByLabelText('Date');
    const submitButton = getByText('Get Recommendations');
    
    // Initially button should be disabled
    expect(submitButton).toBeDisabled();
    
    // Fill in required fields
    await fireEvent.input(locationInput, { target: { value: 'London, UK' } });
    await fireEvent.input(dateInput, { target: { value: '2023-10-21' } });
    
    // Now button should be enabled
    expect(submitButton).not.toBeDisabled();
  });

  test('selects a popular location when clicked', async () => {
    const { getByText, getByLabelText } = render(WeatherDressAssistant);
    
    // Get location input and a popular location chip
    const locationInput = getByLabelText('Location');
    const londonChip = getByText('London, UK');
    
    // Click on the London location chip
    await fireEvent.click(londonChip);
    
    // Check that the location input was updated
    expect(locationInput.value).toBe('London, UK');
    
    // The London chip should now have the selected class
    expect(londonChip.classList.contains('selected')).toBe(true);
  });

  test('fetches and displays clothing recommendations', async () => {
    // Mock successful API response
    const mockResponse = {
      data: {
        date: '2023-10-21',
        location: 'London, UK',
        weather_summary: 'Cloudy with temperature of 15.5°C',
        temperature: 15.5,
        conditions: 'Cloudy',
        recommendations: {
          summary: 'It\'s a cool, cloudy day. Dress in layers for comfort.',
          outfit: {
            top: [3, 'Black hoodie'],
            bottom: [1, 'Blue jeans'],
            footwear: [1, 'White sneakers'],
            accessories: [
              [4, 'Black sunglasses']
            ]
          },
          tips: [
            'Bring a light jacket in case it gets colder',
            'Dress in layers that can be removed if it gets warmer'
          ]
        }
      }
    };
    
    // Setup mock response
    axios.post.mockResolvedValueOnce(mockResponse);
    
    // Render the component
    const { getByText, getByLabelText, getAllByRole } = render(WeatherDressAssistant);
    
    // Fill in the form
    const locationInput = getByLabelText('Location');
    const dateInput = getByLabelText('Date');
    const occasionInput = getByLabelText('Occasion (optional)');
    
    await fireEvent.input(locationInput, { target: { value: 'London, UK' } });
    await fireEvent.input(dateInput, { target: { value: '2023-10-21' } });
    await fireEvent.input(occasionInput, { target: { value: 'Casual day out' } });
    
    // Submit the form
    const submitButton = getByText('Get Recommendations');
    await fireEvent.click(submitButton);
    
    // Wait for recommendations to be displayed
    await waitFor(() => {
      // Check weather info is displayed
      expect(getByText('Weather in London, UK on 2023-10-21')).toBeInTheDocument();
      expect(getByText('Temperature: 15.5°C')).toBeInTheDocument();
      expect(getByText('Conditions: Cloudy')).toBeInTheDocument();
      
      // Check recommendations are displayed
      expect(getByText('Clothing Recommendations')).toBeInTheDocument();
      expect(getByText('It\'s a cool, cloudy day. Dress in layers for comfort.')).toBeInTheDocument();
      
      // Check outfit items are displayed
      expect(getByText('Black hoodie')).toBeInTheDocument();
      expect(getByText('Blue jeans')).toBeInTheDocument();
      expect(getByText('White sneakers')).toBeInTheDocument();
      
      // Check tips are displayed
      expect(getByText('Additional Tips:')).toBeInTheDocument();
      expect(getByText('Bring a light jacket in case it gets colder')).toBeInTheDocument();
    });
    
    // Verify axios was called correctly
    expect(axios.post).toHaveBeenCalledTimes(1);
    expect(axios.post).toHaveBeenCalledWith(
      'http://localhost:8000/api/weather-assistant/dress-recommendation',
      {
        user_id: 1, // Default user ID
        location: 'London, UK',
        date: '2023-10-21',
        occasion: 'Casual day out',
        preferences: ''
      }
    );
  });

  test('displays error when API request fails', async () => {
    // Mock API failure
    axios.post.mockRejectedValueOnce({ 
      response: { 
        data: { detail: 'Weather forecast not available for this date' } 
      } 
    });
    
    // Render the component
    const { getByText, getByLabelText } = render(WeatherDressAssistant);
    
    // Fill in the form
    const locationInput = getByLabelText('Location');
    const dateInput = getByLabelText('Date');
    
    await fireEvent.input(locationInput, { target: { value: 'London, UK' } });
    await fireEvent.input(dateInput, { target: { value: '2030-01-01' } }); // Far future date
    
    // Submit the form
    const submitButton = getByText('Get Recommendations');
    await fireEvent.click(submitButton);
    
    // Wait for error to be displayed
    await waitFor(() => {
      expect(getByText('Weather forecast not available for this date')).toBeInTheDocument();
    });
  });

  test('displays loading state during API request', async () => {
    // Mock a delayed API response
    axios.post.mockImplementationOnce(() => {
      return new Promise(resolve => {
        setTimeout(() => {
          resolve({
            data: {
              date: '2023-10-21',
              location: 'London, UK',
              weather_summary: 'Cloudy',
              temperature: 15.5,
              conditions: 'Cloudy',
              recommendations: { 
                summary: 'Dress warmly',
                outfit: {},
                tips: []
              }
            }
          });
        }, 500);
      });
    });
    
    // Render the component
    const { getByText, getByLabelText } = render(WeatherDressAssistant);
    
    // Fill in the form
    const locationInput = getByLabelText('Location');
    const dateInput = getByLabelText('Date');
    
    await fireEvent.input(locationInput, { target: { value: 'London, UK' } });
    await fireEvent.input(dateInput, { target: { value: '2023-10-21' } });
    
    // Submit the form
    const submitButton = getByText('Get Recommendations');
    await fireEvent.click(submitButton);
    
    // Check that button is disabled and shows loading text
    await waitFor(() => {
      expect(getByText('Getting recommendations...')).toBeInTheDocument();
      expect(getByText('Getting recommendations...')).toBeDisabled();
    });
    
    // Wait for loading to complete
    await waitFor(() => {
      expect(getByText('Get Recommendations')).toBeInTheDocument();
      expect(getByText('Get Recommendations')).not.toBeDisabled();
    }, { timeout: 1000 });
  });
});