import '@testing-library/jest-dom';
import { expect, afterEach, vi } from 'vitest';
import { cleanup } from '@testing-library/svelte';
import { setupServer } from 'msw/node';
import { rest } from 'msw';

// Mock server setup for API calls
export const server = setupServer(
  // Mock API endpoints for NL Query
  rest.post('http://localhost:8000/api/nl-query/process', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        original_query: "Show all employees in AAP department",
        sql_query: 'SELECT e.id, e.name, d.name as department_name FROM "employees" e JOIN "departments" d ON e.dept_id = d.id WHERE d.name = \'AAP\';',
        results: [
          {id: 1, name: "John Doe", department_name: "AAP"},
          {id: 2, name: "Jane Smith", department_name: "AAP"}
        ],
        user_message: "Found 2 employees in the AAP department.",
        metadata: {execution_time_seconds: 0.123, row_count: 2}
      })
    );
  }),
  
  // Mock API endpoints for Weather Assistant
  rest.post('http://localhost:8000/api/weather-assistant/dress-recommendation', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        date: "2023-10-20",
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
      })
    );
  })
);

// Start mock server before tests
beforeAll(() => server.listen());

// Clean up after each test
afterEach(() => {
  cleanup();
  server.resetHandlers();
});

// Close server after all tests
afterAll(() => server.close());

// Mock global fetch
global.fetch = vi.fn();

// Mock window.alert
global.alert = vi.fn();

// Mock any browser APIs that might not be available in JSDOM
global.ResizeObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}));