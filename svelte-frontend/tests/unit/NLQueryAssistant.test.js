import { render, screen, fireEvent, waitFor } from '@testing-library/svelte';
import { vi } from 'vitest';
import NLQueryAssistant from '../../src/components/NLQueryAssistant.svelte';
import axios from 'axios';

// Mock axios
vi.mock('axios');

describe('NLQueryAssistant Component', () => {
  // Reset mocks before each test
  beforeEach(() => {
    vi.resetAllMocks();
  });

  test('renders correctly with initial state', () => {
    const { getByText, getByPlaceholderText } = render(NLQueryAssistant);
    
    // Verify heading and description are present
    expect(getByText('Database Query Assistant')).toBeInTheDocument();
    expect(getByText(/Ask a question about your data/i)).toBeInTheDocument();
    
    // Verify input and button are present
    const inputElement = getByPlaceholderText(/Show me all employees/i);
    expect(inputElement).toBeInTheDocument();
    expect(inputElement.value).toBe('');
    
    const searchButton = getByText('Search');
    expect(searchButton).toBeInTheDocument();
    expect(searchButton).not.toBeDisabled();
    
    // Verify no results are shown initially
    expect(screen.queryByText('Results:')).not.toBeInTheDocument();
    expect(screen.queryByText('Generated SQL:')).not.toBeInTheDocument();
  });

  test('shows validation error when submitting empty query', async () => {
    const { getByText } = render(NLQueryAssistant);
    
    // Submit with empty query
    const searchButton = getByText('Search');
    await fireEvent.click(searchButton);
    
    // Verify error message
    expect(getByText('Please enter a query.')).toBeInTheDocument();
  });
  
  test('process query and display results', async () => {
    // Mock axios post response
    axios.post.mockResolvedValueOnce({
      data: {
        original_query: "Show all employees in AAP department",
        sql_query: 'SELECT e.id, e.name, d.name as department_name FROM "employees" e JOIN "departments" d ON e.dept_id = d.id WHERE d.name = \'AAP\';',
        results: [
          {id: 1, name: "John Doe", department_name: "AAP"},
          {id: 2, name: "Jane Smith", department_name: "AAP"}
        ],
        user_message: "Found 2 employees in the AAP department.",
        metadata: {execution_time_seconds: 0.123, row_count: 2}
      }
    });
    
    const { getByText, getByPlaceholderText } = render(NLQueryAssistant);
    
    // Enter query text
    const inputElement = getByPlaceholderText(/Show me all employees/i);
    await fireEvent.input(inputElement, { target: { value: 'Show all employees in AAP department' } });
    
    // Submit query
    const searchButton = getByText('Search');
    await fireEvent.click(searchButton);
    
    // Verify axios was called with correct parameters
    expect(axios.post).toHaveBeenCalledWith(
      'http://localhost:8000/api/nl-query/process',
      { query: 'Show all employees in AAP department' }
    );
    
    // Wait for results to appear
    await waitFor(() => {
      // Verify SQL query is displayed
      expect(screen.getByText('Generated SQL:')).toBeInTheDocument();
      
      // Verify results are displayed
      expect(screen.getByText('Results: 2 rows')).toBeInTheDocument();
      
      // Verify table contains the correct data
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText('Jane Smith')).toBeInTheDocument();
    });
  });
  
  test('handles API error gracefully', async () => {
    // Mock axios post to return error
    axios.post.mockRejectedValueOnce({
      response: {
        data: {
          detail: 'An error occurred while processing your query.'
        }
      }
    });
    
    const { getByText, getByPlaceholderText } = render(NLQueryAssistant);
    
    // Enter query text
    const inputElement = getByPlaceholderText(/Show me all employees/i);
    await fireEvent.input(inputElement, { target: { value: 'This will cause an error' } });
    
    // Submit query
    const searchButton = getByText('Search');
    await fireEvent.click(searchButton);
    
    // Wait for error message to appear
    await waitFor(() => {
      expect(screen.getByText('An error occurred while processing your query.')).toBeInTheDocument();
    });
    
    // Verify no results are shown
    expect(screen.queryByText('Results:')).not.toBeInTheDocument();
  });
  
  test('adds successful queries to history', async () => {
    // Mock axios post response
    axios.post.mockResolvedValueOnce({
      data: {
        original_query: "Show all employees",
        sql_query: 'SELECT * FROM "employees";',
        results: [{id: 1, name: "John Doe"}],
        metadata: {row_count: 1}
      }
    });
    
    const { getByText, getByPlaceholderText } = render(NLQueryAssistant);
    
    // Enter and submit query
    const inputElement = getByPlaceholderText(/Show me all employees/i);
    await fireEvent.input(inputElement, { target: { value: 'Show all employees' } });
    await fireEvent.click(getByText('Search'));
    
    // Wait for results and check query history
    await waitFor(async () => {
      // Find and click the Query History element to expand it
      const historyHeader = screen.getByText('Query History');
      await fireEvent.click(historyHeader);
      
      // Verify query appears in history
      expect(screen.getByText('Show all employees')).toBeInTheDocument();
      expect(screen.getByText('1 results')).toBeInTheDocument();
    });
  });
});