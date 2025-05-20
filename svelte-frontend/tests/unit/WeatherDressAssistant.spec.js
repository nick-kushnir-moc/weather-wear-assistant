import { render, screen, fireEvent, waitFor } from '@testing-library/svelte';
import { vi } from 'vitest';
import WeatherDressAssistant from '../../src/components/WeatherDressAssistant.svelte';
import axios from 'axios';

// Mock axios
vi.mock('axios');

// Mock Date for consistent testing
const MOCK_DATE = new Date('2023-10-15');
const MOCK_DATE_ISO = MOCK_DATE.toISOString().split('T')[0]; // '2023-10-15'

// Establish helper to create future date
const createFutureDate = (daysAhead) => {
  const date = new Date(MOCK_DATE);
  date.setDate(date.getDate() + daysAhead);
  return date.toISOString().split('T')[0];
};

describe('WeatherDressAssistant Component', () => {
  // Setup mocks before each test
  beforeEach(() => {
    vi.resetAllMocks();
    
    // Mock Date.now() to return our fixed date
    vi.spyOn(Date, 'now').mockImplementation(() => MOCK_DATE.getTime());
    
    // Mock new Date() to return our fixed date
    global.Date = class extends Date {
      constructor(...args) {
        if (args.length === 0) {
          return new global.actualDate(MOCK_DATE);
        }
        return new global.actualDate(...args);
      }
      
      static now() {
        return MOCK_DATE.getTime();
      }
    };
    global.actualDate = Date;
  });
  
  // Restore Date after tests
  afterEach(() => {
    vi.restoreAllMocks();
    global.Date = global.actualDate;
  });

  test('renders correctly with initial state', () => {
    const { getByText, getByLabelText } = render(WeatherDressAssistant);
    
    // Verify heading and description are present
    expect(getByText('Weather-Based Dress Assistant')).toBeInTheDocument();
    expect(getByText(/Get clothing recommendations/)).toBeInTheDocument();
    
    // Verify form elements
    expect(getByLabelText('Location')).toBeInTheDocument();
    expect(getByLabelText('Date')).toBeInTheDocument();
    
    // Verify initial date value is today
    expect(getByLabelText('Date').value).toBe(MOCK_DATE_ISO);
    
    // Verify button is disabled initially (no location)
    const button = getByText('Get Recommendations');
    expect(button).toBeInTheDocument();
    expect(button).toBeDisabled();
    
    // Verify no recommendations are shown initially
    expect(screen.queryByText(/Weather in/)).not.toBeInTheDocument();
  });
  
  test('enables button when required fields are filled', async () => {
    const { getByText, getByLabelText } = render(WeatherDressAssistant);
    
    // Enter location
    const locationInput = getByLabelText('Location');
    await fireEvent.input(locationInput, { target: { value: 'London, UK' } });
    
    // Verify button is enabled
    const button = getByText('Get Recommendations');
    expect(button).not.toBeDisabled();
  });

  test('disables future dates beyond forecast range', () => {
    const { getByLabelText } = render(WeatherDressAssistant);
    
    // Get the date input
    const dateInput = getByLabelText('Date');
    
    // Verify min attribute is today
    expect(dateInput.min).toBe(MOCK_DATE_ISO);
    
    // Verify max attribute is 5 days from today
    const expectedMaxDate = createFutureDate(5);
    expect(dateInput.max).toBe(expectedMaxDate);
  });
  
  test('allows selection of popular locations', async () => {
    const { getByText, getByLabelText } = render(WeatherDressAssistant);
    
    // Click a popular location
    const londonChip = getByText('London, UK');
    await fireEvent.click(londonChip);
    
    // Verify location input is updated
    const locationInput = getByLabelText('Location');
    expect(locationInput.value).toBe('London, UK');
    
    // Verify button is enabled
    const button = getByText('Get Recommendations');
    expect(button).not.toBeDisabled();
  });
  
  test('sends request and displays recommendations', async () => {
    // Mock axios post response
    axios.post.mockResolvedValueOnce({
      data: {
        date: "2023-10-15",
        location: "London, UK",
        weather_summary: "Cloudy with temperature of 15.5°C",
        temperature: 15.5,
        conditions: "Cloudy",
        recommendations: {
          summary: "It's a cool, cloudy day. Dress in layers.",
          outfit: {
            top: [3, "Black hoodie"],
            bottom: [1, "Blue jeans"],
            footwear: [1, "White sneakers"]
          },
          tips: ["Bring a light jacket in case it gets colder"]
        }
      }
    });
    
    const { getByText, getByLabelText } = render(WeatherDressAssistant);
    
    // Fill the form
    const locationInput = getByLabelText('Location');
    await fireEvent.input(locationInput, { target: { value: 'London, UK' } });
    
    const occasionInput = getByLabelText('Occasion (optional)');
    await fireEvent.input(occasionInput, { target: { value: 'Casual day out' } });
    
    // Submit the form
    const button = getByText('Get Recommendations');
    await fireEvent.click(button);
    
    // Verify axios was called with correct parameters
    expect(axios.post).toHaveBeenCalledWith(
      'http://localhost:8000/api/weather-assistant/dress-recommendation',
      {
        user_id: 1, // Hardcoded in component
        location: 'London, UK',
        date: MOCK_DATE_ISO,
        occasion: 'Casual day out',
        preferences: ''
      }
    );
    
    // Wait for recommendations to appear
    await waitFor(() => {
      // Verify weather info
      expect(screen.getByText(/Weather in London, UK/)).toBeInTheDocument();
      expect(screen.getByText(/15.5°C/)).toBeInTheDocument();
      expect(screen.getByText(/Cloudy/)).toBeInTheDocument();
      
      // Verify outfit recommendations
      expect(screen.getByText("It's a cool, cloudy day. Dress in layers.")).toBeInTheDocument();
      expect(screen.getByText("Black hoodie")).toBeInTheDocument();
      expect(screen.getByText("Blue jeans")).toBeInTheDocument();
      expect(screen.getByText("White sneakers")).toBeInTheDocument();
      
      // Verify tips
      expect(screen.getByText("Bring a light jacket in case it gets colder")).toBeInTheDocument();
    });
  });
  
  test('handles API error gracefully', async () => {
    // Mock axios post to return error
    axios.post.mockRejectedValueOnce({
      response: {
        data: {
          detail: 'Weather forecast not available for the specified date.'
        }
      }
    });
    
    const { getByText, getByLabelText } = render(WeatherDressAssistant);
    
    // Fill the form
    const locationInput = getByLabelText('Location');
    await fireEvent.input(locationInput, { target: { value: 'InvalidLocation' } });
    
    // Submit the form
    const button = getByText('Get Recommendations');
    await fireEvent.click(button);
    
    // Wait for error message to appear
    await waitFor(() => {
      expect(screen.getByText('Weather forecast not available for the specified date.')).toBeInTheDocument();
    });
    
    // Verify no recommendations are shown
    expect(screen.queryByText(/Weather in/)).not.toBeInTheDocument();
  });
  
  test('formats temperature correctly', async () => {
    // Mock axios post response with decimal temperature
    axios.post.mockResolvedValueOnce({
      data: {
        date: "2023-10-15",
        location: "London, UK",
        weather_summary: "Cloudy with temperature of 15.5°C",
        temperature: 15.5, 
        conditions: "Cloudy",
        recommendations: { summary: "Test", outfit: {}, tips: [] }
      }
    });
    
    const { getByText, getByLabelText } = render(WeatherDressAssistant);
    
    // Fill and submit the form
    await fireEvent.input(getByLabelText('Location'), { target: { value: 'London, UK' } });
    await fireEvent.click(getByText('Get Recommendations'));
    
    // Wait for response and check temperature formatting
    await waitFor(() => {
      // Should be rounded to whole number
      expect(screen.getByText(/16°C/)).toBeInTheDocument();
    });
  });
});