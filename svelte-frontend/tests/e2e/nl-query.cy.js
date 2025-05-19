describe('Natural Language Query Assistant', () => {
    beforeEach(() => {
      // Visit the application
      cy.visit('/');
      
      // Mock the API endpoints
      cy.intercept('POST', 'http://localhost:8000/api/nl-query/process', (req) => {
        // Check the request query
        const { query } = req.body;
        
        // Return different mock responses based on the query
        if (query.includes('employees in AAP')) {
          req.reply({
            statusCode: 200,
            body: {
              original_query: query,
              sql_query: 'SELECT e.id, e.name, d.name AS department_name FROM "employees" e JOIN "departments" d ON e.dept_id = d.id WHERE d.name = \'AAP\';',
              results: [
                { id: 1, name: 'John Doe', department_name: 'AAP' },
                { id: 2, name: 'Jane Smith', department_name: 'AAP' }
              ],
              user_message: 'Found 2 employees in the AAP department.',
              metadata: {
                execution_time_seconds: 0.123,
                row_count: 2
              }
            }
          });
        } else if (query.includes('departments')) {
          req.reply({
            statusCode: 200,
            body: {
              original_query: query,
              sql_query: 'SELECT * FROM "departments";',
              results: [
                { id: 1, name: 'AAP' },
                { id: 2, name: 'CBD' },
                { id: 3, name: 'CCP' }
              ],
              user_message: 'There are 3 departments: AAP, CBD, and CCP.',
              metadata: {
                execution_time_seconds: 0.056,
                row_count: 3
              }
            }
          });
        } else if (query.includes('error')) {
          req.reply({
            statusCode: 200,
            body: {
              original_query: query,
              sql_query: '',
              results: [],
              error: 'Failed to process query: Test error',
              metadata: {}
            }
          });
        } else {
          req.reply({
            statusCode: 200,
            body: {
              original_query: query,
              sql_query: 'SELECT * FROM "employees";',
              results: [
                { id: 1, name: 'John Doe', dept_id: 1 },
                { id: 2, name: 'Jane Smith', dept_id: 2 },
                { id: 3, name: 'Bob Johnson', dept_id: 1 },
                { id: 4, name: 'Alice Brown', dept_id: 3 }
              ],
              user_message: 'Found 4 employees.',
              metadata: {
                execution_time_seconds: 0.087,
                row_count: 4
              }
            }
          });
        }
      }).as('nlQuery');
    });
  
    it('loads the NL Query component successfully', () => {
      // Check that the component is visible
      cy.contains('Database Query Assistant').should('be.visible');
      cy.get('input[placeholder*="Show all employees"]').should('be.visible');
      cy.contains('button', 'Search').should('be.visible');
    });
  
    it('submits a query and displays results correctly', () => {
      // Type a query
      cy.get('input[placeholder*="Show all employees"]')
        .type('Show me all employees in AAP department');
      
      // Submit the query
      cy.contains('button', 'Search').click();
      
      // Wait for the API response
      cy.wait('@nlQuery');
      
      // Check that the SQL query is displayed
      cy.contains('Generated SQL:')
        .next()
        .should('contain', 'SELECT e.id, e.name, d.name AS department_name');
      
      // Check that the results summary is displayed
      cy.contains('Found 2 employees in the AAP department.');
      
      // Check that the results table is displayed with correct data
      cy.contains('Results: 2 rows');
      cy.contains('th', 'id');
      cy.contains('th', 'name');
      cy.contains('th', 'department_name');
      cy.contains('td', 'John Doe');
      cy.contains('td', 'Jane Smith');
      cy.contains('td', 'AAP');
    });
  
    it('shows appropriate error messages', () => {
      // Test with an empty query
      cy.contains('button', 'Search').click();
      cy.contains('Please enter a query.');
      
      // Test with a query that triggers an error
      cy.get('input[placeholder*="Show all employees"]')
        .clear()
        .type('This will cause an error');
      
      cy.contains('button', 'Search').click();
      
      // Wait for the API response
      cy.wait('@nlQuery');
      
      // Check that the error message is displayed
      cy.contains('Failed to process query: Test error');
    });
  
    it('adds queries to history and allows reusing them', () => {
      // Submit a query
      cy.get('input[placeholder*="Show all employees"]')
        .type('Show me all departments');
      
      cy.contains('button', 'Search').click();
      
      // Wait for the API response
      cy.wait('@nlQuery');
      
      // Check that results are displayed
      cy.contains('There are 3 departments: AAP, CBD, and CCP.');
      
      // Submit another query
      cy.get('input[placeholder*="Show all employees"]')
        .clear()
        .type('Show me all employees in AAP department');
      
      cy.contains('button', 'Search').click();
      
      // Wait for the API response
      cy.wait('@nlQuery');
      
      // Check that the history section exists
      cy.contains('Query History').should('be.visible');
      
      // Expand the history section
      cy.contains('Query History').click();
      
      // Check that both queries are in the history
      cy.contains('Show me all departments');
      cy.contains('Show me all employees in AAP department');
      
      // Click on the first history item
      cy.contains('Show me all departments').click();
      
      // Wait for the API response
      cy.wait('@nlQuery');
      
      // Check that the results for the first query are displayed again
      cy.contains('There are 3 departments: AAP, CBD, and CCP.');
    });
  
    it('handles loading state correctly', () => {
      // Setup a delayed response
      cy.intercept('POST', 'http://localhost:8000/api/nl-query/process', (req) => {
        // Delay the response by 1 second
        setTimeout(() => {
          req.reply({
            statusCode: 200,
            body: {
              original_query: req.body.query,
              sql_query: 'SELECT * FROM "employees";',
              results: [{ id: 1, name: 'Test' }],
              metadata: {}
            }
          });
        }, 1000);
      }).as('delayedQuery');
      
      // Type a query
      cy.get('input[placeholder*="Show all employees"]')
        .type('Show me all employees');
      
      // Submit the query
      cy.contains('button', 'Search').click();
      
      // Check that the button shows loading state
      cy.contains('button', 'Processing...').should('be.disabled');
      
      // Wait for the loading to complete
      cy.contains('button', 'Search', { timeout: 3000 }).should('be.visible');
    });
  });
  
  // svelte-frontend/cypress/e2e/weather-assistant.cy.js
  describe('Weather Dress Assistant', () => {
    beforeEach(() => {
      // Visit the application
      cy.visit('/');
      
      // Mock the date to be consistent
      const today = new Date('2023-10-20').toISOString().split('T')[0];
      cy.clock(new Date('2023-10-20').getTime());
      
      // Mock the API endpoint
      cy.intercept('POST', 'http://localhost:8000/api/weather-assistant/dress-recommendation', (req) => {
        // Extract request data
        const { location, date, occasion } = req.body;
        
        // Return mock response
        req.reply({
          statusCode: 200,
          body: {
            date: date,
            location: location,
            weather_summary: 'Cloudy with temperature of 15.5°C',
            temperature: 15.5,
            conditions: 'Cloudy',
            recommendations: {
              summary: `It's a cool, cloudy day in ${location}. Dress warmly for your ${occasion || 'day'}.`,
              outfit: {
                top: [3, 'Black hoodie'],
                bottom: [1, 'Blue jeans'],
                footwear: [1, 'White sneakers'],
                accessories: [
                  [4, 'Black sunglasses'],
                  [5, 'Blue umbrella']
                ]
              },
              tips: [
                'Bring a light jacket in case it gets colder',
                'An umbrella might be useful as clouds could bring light rain'
              ]
            }
          }
        });
      }).as('weatherRequest');
      
      // Mock error cases
      cy.intercept('POST', 'http://localhost:8000/api/weather-assistant/dress-recommendation', (req) => {
        if (req.body.location === 'ErrorCity') {
          req.reply({
            statusCode: 500,
            body: {
              detail: 'Weather forecast not available for this location.'
            }
          });
        }
      }).as('weatherError');
    });
  
    it('loads the Weather Assistant component successfully', () => {
      // Check that the component is visible
      cy.contains('Weather-Based Dress Assistant').should('be.visible');
      cy.get('label').contains('Location').should('be.visible');
      cy.get('label').contains('Date').should('be.visible');
      cy.contains('button', 'Get Recommendations').should('be.visible');
    });
  
    it('requires location before enabling the submit button', () => {
      // Check that button is initially disabled
      cy.contains('button', 'Get Recommendations').should('be.disabled');
      
      // Enter a location
      cy.get('label').contains('Location').next('input').type('London, UK');
      
      // Check that button is now enabled
      cy.contains('button', 'Get Recommendations').should('be.enabled');
      
      // Clear the location
      cy.get('label').contains('Location').next('input').clear();
      
      // Check that button is disabled again
      cy.contains('button', 'Get Recommendations').should('be.disabled');
    });
  
    it('allows selecting a popular location', () => {
      // Click on a popular location
      cy.contains('New York, US').click();
      
      // Check that the location input was updated
      cy.get('label').contains('Location').next('input').should('have.value', 'New York, US');
      
      // Check that the button is now enabled
      cy.contains('button', 'Get Recommendations').should('be.enabled');
      
      // Check that the selected location has the selected class
      cy.contains('New York, US').should('have.class', 'selected');
    });
  
    it('submits the form and displays recommendations', () => {
      // Fill in the form
      cy.get('label').contains('Location').next('input').type('London, UK');
      cy.get('label').contains('Occasion').next('input').type('Business meeting');
      
      // Submit the form
      cy.contains('button', 'Get Recommendations').click();
      
      // Wait for the API response
      cy.wait('@weatherRequest');
      
      // Check that weather information is displayed
      cy.contains('Weather in London, UK on').should('be.visible');
      cy.contains('Temperature: 15.5°C').should('be.visible');
      cy.contains('Conditions: Cloudy').should('be.visible');
      
      // Check that clothing recommendations are displayed
      cy.contains('Clothing Recommendations').should('be.visible');
      cy.contains('It\'s a cool, cloudy day in London, UK. Dress warmly for your Business meeting.').should('be.visible');
      
      // Check outfit items
      cy.contains('Black hoodie').should('be.visible');
      cy.contains('Blue jeans').should('be.visible');
      cy.contains('White sneakers').should('be.visible');
      
      // Check accessories
      cy.contains('Black sunglasses').should('be.visible');
      cy.contains('Blue umbrella').should('be.visible');
      
      // Check tips
      cy.contains('Additional Tips:').should('be.visible');
      cy.contains('Bring a light jacket in case it gets colder').should('be.visible');
      cy.contains('An umbrella might be useful').should('be.visible');
    });
  
    it('displays an error message when the API request fails', () => {
      // Fill in the form with a location that will trigger an error
      cy.get('label').contains('Location').next('input').type('ErrorCity');
      
      // Submit the form
      cy.contains('button', 'Get Recommendations').click();
      
      // Check that error message is displayed
      cy.contains('Weather forecast not available for this location.').should('be.visible');
    });
  
    it('shows loading state during API request', () => {
      // Setup a delayed response
      cy.intercept('POST', 'http://localhost:8000/api/weather-assistant/dress-recommendation', (req) => {
        // Delay the response by 1 second
        setTimeout(() => {
          req.reply({
            statusCode: 200,
            body: {
              date: req.body.date,
              location: req.body.location,
              weather_summary: 'Sunny',
              temperature: 25,
              conditions: 'Clear',
              recommendations: {
                summary: 'It\'s a warm day.',
                outfit: {
                  top: [1, 'White t-shirt'],
                  bottom: [2, 'Khaki shorts'],
                  footwear: [3, 'Sandals']
                },
                tips: ['Stay hydrated']
              }
            }
          });
        }, 1000);
      }).as('delayedWeatherRequest');
      
      // Fill in the form
      cy.get('label').contains('Location').next('input').type('New York, US');
      
      // Submit the form
      cy.contains('button', 'Get Recommendations').click();
      
      // Check that button shows loading state
      cy.contains('button', 'Getting recommendations...').should('be.disabled');
      
      // Wait for loading to complete
      cy.contains('button', 'Get Recommendations', { timeout: 3000 }).should('be.visible');
      
      // Check that results are displayed
      cy.contains('It\'s a warm day.').should('be.visible');
    });
  });
  
  // svelte-frontend/cypress/e2e/app-flow.cy.js
  describe('Full Application E2E Flow', () => {
    beforeEach(() => {
      // Visit the application
      cy.visit('/');
      
      // Mock API endpoints
      cy.intercept('POST', 'http://localhost:8000/api/nl-query/process', {
        statusCode: 200,
        body: {
          original_query: 'Show me all employees',
          sql_query: 'SELECT * FROM "employees";',
          results: [
            { id: 1, name: 'John Doe', dept_id: 1 },
            { id: 2, name: 'Jane Smith', dept_id: 2 }
          ],
          user_message: 'Found 2 employees.',
          metadata: { execution_time_seconds: 0.1, row_count: 2 }
        }
      }).as('nlQuery');
      
      cy.intercept('POST', 'http://localhost:8000/api/weather-assistant/dress-recommendation', {
        statusCode: 200,
        body: {
          date: '2023-10-20',
          location: 'London, UK',
          weather_summary: 'Sunny with temperature of 20°C',
          temperature: 20,
          conditions: 'Clear',
          recommendations: {
            summary: 'It\'s a pleasant day. Dress lightly.',
            outfit: {
              top: [1, 'White t-shirt'],
              bottom: [2, 'Khaki shorts'],
              footwear: [3, 'Sandals']
            },
            tips: ['Wear sunscreen', 'Stay hydrated']
          }
        }
      }).as('weatherQuery');
    });
  
    it('navigates between the two assistants', () => {
      // Check that both components are visible
      cy.contains('Database Query Assistant').should('be.visible');
      cy.contains('Weather-Based Dress Assistant').should('be.visible');
      
      // Interact with NL Query Assistant
      cy.get('input[placeholder*="Show all employees"]').type('Show me all employees');
      cy.contains('button', 'Search').click();
      cy.wait('@nlQuery');
      cy.contains('Found 2 employees.').should('be.visible');
      
      // Interact with Weather Assistant
      cy.get('label').contains('Location').next('input').type('London, UK');
      cy.contains('button', 'Get Recommendations').click();
      cy.wait('@weatherQuery');
      cy.contains('It\'s a pleasant day. Dress lightly.').should('be.visible');
    });
  
    it('completes a full user journey using both tools', () => {
      // Step 1: Ask about employees in a department
      cy.get('input[placeholder*="Show all employees"]').type('Show me employees in the AAP department');
      cy.contains('button', 'Search').click();
      cy.wait('@nlQuery');
      
      // Step 2: Check today's weather for an employee's location
      cy.get('label').contains('Location').next('input').type('London, UK');
      cy.contains('button', 'Get Recommendations').click();
      cy.wait('@weatherQuery');
      
      // Step 3: Return to query assistant and ask another question
      cy.get('input[placeholder*="Show all employees"]').clear().type('Show all departments');
      cy.contains('button', 'Search').click();
      cy.wait('@nlQuery');
      
      // Step 4: Check query history
      cy.contains('Query History').click();
      cy.contains('Show me employees in the AAP department').should('be.visible');
      cy.contains('Show all departments').should('be.visible');
      
      // Step 5: Use a query from history
      cy.contains('Show me employees in the AAP department').click();
      cy.wait('@nlQuery');
      
      // Verify the application state after the journey
      cy.contains('Found 2 employees.').should('be.visible');
      cy.get('label').contains('Location').next('input').should('have.value', 'London, UK');
    });
  
    it('handles error states gracefully', () => {
      // Mock error responses
      cy.intercept('POST', 'http://localhost:8000/api/nl-query/process', {
        statusCode: 200, // The API returns 200 with error in the body
        body: {
          original_query: 'Invalid query',
          sql_query: '',
          results: [],
          error: 'Could not process query',
          metadata: {}
        }
      }).as('nlQueryError');
      
      cy.intercept('POST', 'http://localhost:8000/api/weather-assistant/dress-recommendation', {
        statusCode: 500,
        body: {
          detail: 'Weather API unavailable'
        }
      }).as('weatherError');
      
      // Test NL Query error
      cy.get('input[placeholder*="Show all employees"]').type('Invalid query');
      cy.contains('button', 'Search').click();
      cy.wait('@nlQueryError');
      cy.contains('Could not process query').should('be.visible');
      
      // Test Weather Assistant error
      cy.get('label').contains('Location').next('input').type('London, UK');
      cy.contains('button', 'Get Recommendations').click();
      cy.wait('@weatherError');
      cy.contains('Weather API unavailable').should('be.visible');
      
      // Verify we can still use the application after errors
      cy.get('input[placeholder*="Show all employees"]').clear().type('Show me all employees');
      cy.contains('button', 'Search').click();
      // Mock a successful response for this retry
      cy.intercept('POST', 'http://localhost:8000/api/nl-query/process', {
        statusCode: 200,
        body: {
          original_query: 'Show me all employees',
          sql_query: 'SELECT * FROM "employees";',
          results: [{ id: 1, name: 'John Doe' }],
          user_message: 'Found 1 employee.',
          metadata: { row_count: 1 }
        }
      }).as('nlQueryRetry');
      cy.wait('@nlQueryRetry');
      cy.contains('Found 1 employee.').should('be.visible');
    });
  
    it('tests responsive layout', () => {
      // Test on desktop viewport (default)
      cy.contains('Database Query Assistant').should('be.visible');
      cy.contains('Weather-Based Dress Assistant').should('be.visible');
      
      // Test on tablet viewport
      cy.viewport('ipad-2');
      cy.contains('Database Query Assistant').should('be.visible');
      cy.contains('Weather-Based Dress Assistant').should('be.visible');
      
      // Test on mobile viewport
      cy.viewport('iphone-6');
      cy.contains('Database Query Assistant').should('be.visible');
      cy.contains('Weather-Based Dress Assistant').should('be.visible');
      
      // Check that forms adjust correctly on mobile
      cy.get('input[placeholder*="Show all employees"]').should('be.visible');
      cy.contains('button', 'Search').should('be.visible');
      
      // Verify tables are responsive
      cy.get('input[placeholder*="Show all employees"]').type('Show me all employees');
      cy.contains('button', 'Search').click();
      cy.wait('@nlQuery');
      
      // The results table should be visible and should fit on mobile screen
      cy.contains('Results:').should('be.visible');
      cy.get('table').should('be.visible');
    });
  });
  
  // cypress.config.js
  const { defineConfig } = require('cypress');
  
  module.exports = defineConfig({
    e2e: {
      baseUrl: 'http://localhost:5000', // Adjust to your Svelte app's dev server port
      setupNodeEvents(on, config) {
        // implement node event listeners here
      },
      viewportWidth: 1280,
      viewportHeight: 720,
      // Customize screenshots and video recording
      screenshotOnRunFailure: true,
      video: false, // Set to true if you want videos
      videoUploadOnPasses: false
    },
    component: {
      devServer: {
        framework: 'svelte',
        bundler: 'vite',
      },
    }
  });