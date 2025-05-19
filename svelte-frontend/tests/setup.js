import '@testing-library/jest-dom';
import { vi } from 'vitest';

// Set up global mocks
global.ResizeObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}));

// Mock fetch or other browser APIs if needed
global.fetch = vi.fn();

// Setup any test-specific utilities
beforeAll(() => {
  // Setup before all tests
});

afterAll(() => {
  // Cleanup after all tests
});

beforeEach(() => {
  // Reset mocks before each test
  vi.resetAllMocks();
});