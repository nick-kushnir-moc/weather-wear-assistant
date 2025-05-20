import { test, expect } from '@playwright/test';
import WeatherPage from '../page-objects/weather.page';

test.describe('Weather-Based Dress Assistant', () => {
  let weatherPage;
  
  test.beforeEach(async ({ page }) => {
    // Initialize the page object
    weatherPage = new WeatherPage(page);
    
    // Mock current date to ensure consistent testing
    await page.addInitScript(() => {
      const mockDate = new Date('2023-10-15');
      Date.now = () => mockDate.getTime();
      const originalDate = Date;
      global.Date = class extends Date {
        constructor(...args) {
          if (args.length === 0) {
            return new originalDate(mockDate);
          }
          return new originalDate(...args);
        }
        static now() {
          return mockDate.getTime();
        }
      };
      global.Date.prototype = originalDate.prototype;
    });
    
    // Set up API route mocking
    await page.route('**/api/weather-assistant/dress-recommendation', async route => {
      const requestBody = JSON.parse(route.request().postData());
      const location = requestBody.location || '';
      
      // Mock different responses based on location
      if (location.includes('Error') || location.includes('Invalid')) {
        await route.fulfill({
          status: 500,
          contentType: 'application/json',
          body: JSON.stringify({
            detail: 'Weather forecast not available for the specified location.'
          })
        });
      } else if (location.includes('Cold') || location === 'Moscow, RU') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            date: requestBody.date,
            location: location,
            weather_summary: 'Snow with temperature of -5.0°C',
            temperature: -5.0,
            conditions: 'Snow',
            recommendations: {
              summary: 'It\'s very cold with snow. Wear warm layers and protect against snow.',
              outfit: {
                top: [5, 'Brown wool coat'],
                bottom: [1, 'Blue jeans'],
                footwear: [2, 'Brown leather boots'],
                accessories: [
                  [1, 'Black wool hat'],
                  [2, 'Red wool scarf'],
                  [3, 'Black leather gloves']
                ]
              },
              tips: [
                'Layer clothing for maximum warmth',
                'Keep extremities covered to prevent frostbite',
                'Wear waterproof footwear for snow'
              ]
            }
          })
        });
      } else if (location.includes('Hot') || location === 'Dubai, AE') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            date: requestBody.date,
            location: location,
            weather_summary: 'Clear with temperature of 35.0°C',
            temperature: 35.0,
            conditions: 'Clear',
            recommendations: {
              summary: 'It\'s very hot and sunny. Wear light, breathable clothing and protect from the sun.',
              outfit: {
                top: [1, 'White cotton t-shirt'],
                bottom: [2, 'Khaki shorts'],
                footwear: [3, 'Brown leather sandals'],
                accessories: [
                  [4, 'Black sunglasses']
                ]
              },
              tips: [
                'Wear light colors to reflect sunlight',
                'Stay hydrated throughout the day',
                'Use sunscreen and seek shade when possible'
              ]
            }
          })
        });
      } else {
        // Default response (mild weather)
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            date: requestBody.date,
            location: location,
            weather_summary: 'Cloudy with temperature of 15.5°C',
            temperature: 15.5,
            conditions: 'Cloudy',
            recommendations: {
              summary: 'It\'s a cool, cloudy day. Dress in layers.',
              outfit: {
                top: [3, 'Black hoodie'],
                bottom: [1, 'Blue jeans'],
                footwear: [1, 'White sneakers'],
                accessories: []
              },
              tips: [
                'Bring a light jacket in case it gets colder',
                'An umbrella is not necessary, but could be useful just in case'
              ]
            }
          })
        });
      }
    });
    
    // Navigate to the Weather Assistant page
    await weatherPage.goto();
  });
  
  test('renders the component correctly', async () => {
    // Verify the page title and input exists
    await expect(weatherPage.page.locator('h2')).toContainText('Weather-Based Dress Assistant');
    await expect(weatherPage.page.locator(weatherPage.selectors.locationInput)).toBeVisible();
    await expect(weatherPage.page.locator(weatherPage.selectors.dateInput)).toBeVisible();
    
    // Verify submit button is disabled initially (no location)
    const isEnabled = await weatherPage.isSubmitButtonEnabled();
    expect(isEnabled).toBe(false);
    
    // Take a screenshot
    await weatherPage.screenshot('test-results/weather-initial.png');
  });
  
  test('enables submit button when location is filled', async () => {
    // Fill location
    await weatherPage.page.fill(weatherPage.selectors.locationInput, 'London, UK');
    
    // Verify button is enabled
    const isEnabled = await weatherPage.isSubmitButtonEnabled();
    expect(isEnabled).toBe(true);
  });
  
  test('submits form and displays recommendations for mild weather', async () => {
    // Fill and submit form
    await weatherPage.getRecommendation('London, UK', '2023-10-16', 'Casual day out');
    
    // Wait for recommendations to appear
    await weatherPage.waitForRecommendation();
    
    // Verify weather info is displayed
    const weatherSummary = await weatherPage.getWeatherSummary();
    expect(weatherSummary).toContain('London, UK');
    expect(weatherSummary).toContain('15.5°C');
    expect(weatherSummary).toContain('Cloudy');
    
    // Verify outfit recommendations
    const outfit = await weatherPage.getOutfitRecommendations();
    expect(outfit.top).toContain('Black hoodie');
    expect(outfit.bottom).toContain('Blue jeans');
    expect(outfit.footwear).toContain('White sneakers');
    
    // Verify tips
    const tips = await weatherPage.getTips();
    expect(tips.length).toBeGreaterThan(0);
    expect(tips[0]).toContain('Bring a light jacket');
    
    // Take a screenshot
    await weatherPage.screenshot('test-results/weather-mild-recommendation.png');
  });
  
  test('displays recommendations for cold weather', async () => {
    // Fill and submit form
    await weatherPage.getRecommendation('Moscow, RU', '2023-10-16');
    
    // Wait for recommendations to appear
    await weatherPage.waitForRecommendation();
    
    // Verify weather info is displayed
    const weatherSummary = await weatherPage.getWeatherSummary();
    expect(weatherSummary).toContain('Moscow, RU');
    expect(weatherSummary).toContain('-5.0°C');
    expect(weatherSummary).toContain('Snow');
    
    // Verify outfit recommendations
    const outfit = await weatherPage.getOutfitRecommendations();
    expect(outfit.top).toContain('Brown wool coat');
    expect(outfit.bottom).toContain('Blue jeans');
    expect(outfit.footwear).toContain('Brown leather boots');
    
    // Verify tips
    const tips = await weatherPage.getTips();
    expect(tips.length).toBeGreaterThan(0);
    expect(tips.some(tip => tip.includes('Layer'))).toBeTruthy();
    
    // Take a screenshot
    await weatherPage.screenshot('test-results/weather-cold-recommendation.png');
  });
  
  test('displays recommendations for hot weather', async () => {
    // Fill and submit form
    await weatherPage.getRecommendation('Dubai, AE', '2023-10-16');
    
    // Wait for recommendations to appear
    await weatherPage.waitForRecommendation();
    
    // Verify weather info is displayed
    const weatherSummary = await weatherPage.getWeatherSummary();
    expect(weatherSummary).toContain('Dubai, AE');
    expect(weatherSummary).toContain('35.0°C');
    expect(weatherSummary).toContain('Clear');
    
    // Verify outfit recommendations
    const outfit = await weatherPage.getOutfitRecommendations();
    expect(outfit.top).toContain('White cotton t-shirt');
    expect(outfit.bottom).toContain('Khaki shorts');
    expect(outfit.footwear).toContain('Brown leather sandals');
    
    // Verify tips
    const tips = await weatherPage.getTips();
    expect(tips.length).toBeGreaterThan(0);
    expect(tips.some(tip => tip.includes('hydrated') || tip.includes('sun'))).toBeTruthy();
    
    // Take a screenshot
    await weatherPage.screenshot('test-results/weather-hot-recommendation.png');
  });
  
  test('handles API errors gracefully', async () => {
    // Fill and submit form with invalid location
    await weatherPage.getRecommendation('InvalidLocation', '2023-10-16');
    
    // Wait for error message to appear
    await weatherPage.waitForError();
    
    // Verify error message is displayed
    const errorMessage = await weatherPage.getErrorMessage();
    expect(errorMessage).toContain('Weather forecast not available');
    
    // Verify no recommendations are displayed
    const hasRecommendation = await weatherPage.hasRecommendation();
    expect(hasRecommendation).toBe(false);
    
    // Take a screenshot
    await weatherPage.screenshot('test-results/weather-error.png');
  });
  
  test('selects location from popular locations list', async () => {
    // Select a popular location
    await weatherPage.selectPopularLocation('London');
    
    // Verify location is filled
    const locationValue = await weatherPage.page.inputValue(weatherPage.selectors.locationInput);
    expect(locationValue).toBe('London, UK');
    
    // Verify submit button is enabled
    const isEnabled = await weatherPage.isSubmitButtonEnabled();
    expect(isEnabled).toBe(true);
    
    // Submit form and verify recommendations appear
    await weatherPage.submitForm();
    await weatherPage.waitForRecommendation();
    
    // Take a screenshot
    await weatherPage.screenshot('test-results/weather-popular-location.png');
  });
});