import { test, expect } from '@playwright/test';
import NLQueryPage from '../page-objects/nlquery.page';

test.describe('Natural Language Query Assistant', () => {
  let nlQueryPage;
  
  test.beforeEach(async ({ page }) => {
    // Initialize the page object
    nlQueryPage = new NLQueryPage(page);
    
    // Set up API route mocking
    await page.route('**/api/nl-query/process', async route => {
      const requestBody = JSON.parse(route.request().postData());
      const query = requestBody.query || '';
      
      // Mock different responses based on query content
      if (query.includes('error')) {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            original_query: query,
            sql_query: '',
            results: [],
            error: 'Failed to process query: LLM processing error',
            metadata: {}
          })
        });
      } else if (query.includes('empty')) {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            original_query: query,
            sql_query: 'SELECT * FROM employees WHERE name LIKE \'%NonExistent%\';',
            results: [],
            user_message: 'No results found matching your query.',
            metadata: { execution_time_seconds: 0.05, row_count: 0 }
          })
        });
      } else if (query.includes('employee') || query.includes('AAP')) {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            original_query: query,
            sql_query: 'SELECT e.id, e.name, d.name as department_name FROM "employees" e JOIN "departments" d ON e.dept_id = d.id WHERE d.name = \'AAP\';',
            results: [
              {id: 1, name: "John Doe", department_name: "AAP"},
              {id: 2, name: "Jane Smith", department_name: "AAP"}
            ],
            user_message: "Found 2 employees in the AAP department: John Doe and Jane Smith.",
            metadata: { execution_time_seconds: 0.123, row_count: 2 }
          })
        });
      } else {
        // Default response
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            original_query: query,
            sql_query: 'SELECT * FROM "employees";',
            results: [
              {id: 1, name: "John Doe", dept_id: 1},
              {id: 2, name: "Jane Smith", dept_id: 2},
              {id: 3, name: "Bob Johnson", dept_id: 1}
            ],
            user_message: "Found 3 employees.",
            metadata: { execution_time_seconds: 0.1, row_count: 3 }
          })
        });
      }
    });
    
    // Navigate to the NL Query page
    await nlQueryPage.goto();
  });
  
  test('renders the component correctly', async () => {
    // Verify the page title and input exists
    await expect(nlQueryPage.page.locator('h2')).toContainText('Database Query Assistant');
    await expect(nlQueryPage.page.locator(nlQueryPage.selectors.queryInput)).toBeVisible();
    await expect(nlQueryPage.page.locator(nlQueryPage.selectors.searchButton)).toBeVisible();
    
    // Take a screenshot
    await nlQueryPage.screenshot('test-results/nl-query-initial.png');
  });
  
  test('submits a query and displays results', async () => {
    // Enter and submit a query
    await nlQueryPage.enterAndSubmitQuery('Show all employees in AAP department');
    
    // Wait for results to appear
    await nlQueryPage.waitForResults();
    
    // Verify SQL query is displayed
    const sqlQuery = await nlQueryPage.getSqlQuery();
    expect(sqlQuery).toContain('SELECT');
    expect(sqlQuery).toContain('employees');
    expect(sqlQuery).toContain('AAP');
    
    // Verify results are displayed
    const hasResults = await nlQueryPage.hasResults();
    expect(hasResults).toBe(true);
    
    // Verify result count
    const resultCount = await nlQueryPage.getResultsCount();
    expect(resultCount).toBe(2);
    
    // Verify user message
    const userMessage = await nlQueryPage.getUserMessage();
    expect(userMessage).toContain('Found 2 employees');
    
    // Take a screenshot of the results
    await nlQueryPage.screenshot('test-results/nl-query-results.png');
  });
  
  test('handles query errors gracefully', async () => {
    // Enter and submit a query that will cause an error
    await nlQueryPage.enterAndSubmitQuery('This will cause an error');
    
    // Wait for error message to appear
    await nlQueryPage.waitForError();
    
    // Verify error message is displayed
    const errorMessage = await nlQueryPage.getErrorMessage();
    expect(errorMessage).toContain('Failed to process query');
    
    // Verify no results are displayed
    const hasResults = await nlQueryPage.hasResults();
    expect(hasResults).toBe(false);
    
    // Take a screenshot of the error
    await nlQueryPage.screenshot('test-results/nl-query-error.png');
  });
  
  test('handles empty result sets appropriately', async () => {
    // Enter and submit a query that will return no results
    await nlQueryPage.enterAndSubmitQuery('Show empty results');
    
    // Wait for message to appear
    await expect(nlQueryPage.page.locator('.no-results')).toBeVisible();
    
    // Verify empty results message
    const noResultsMessage = await nlQueryPage.page.locator('.no-results').innerText();
    expect(noResultsMessage).toContain('No results found');
    
    // Take a screenshot
    await nlQueryPage.screenshot('test-results/nl-query-empty-results.png');
  });
  
  test('adds successful queries to history and allows reuse', async () => {
    // Submit first query
    await nlQueryPage.enterAndSubmitQuery('Show all employees');
    await nlQueryPage.waitForResults();
    
    // Submit second query
    await nlQueryPage.enterAndSubmitQuery('Show all employees in AAP department');
    await nlQueryPage.waitForResults();
    
    // Open query history
    await nlQueryPage.openQueryHistory();
    
    // Verify history items
    const historyItems = await nlQueryPage.page.$$(nlQueryPage.selectors.historyItems);
    expect(historyItems.length).toBeGreaterThanOrEqual(2);
    
    // Verify first history item text
    const firstHistoryItemText = await historyItems[0].innerText();
    expect(firstHistoryItemText).toContain('Show all employees in AAP department');
    
    // Click on first history item
    await historyItems[0].click();
    
    // Verify the query was resubmitted and results appear
    await nlQueryPage.waitForResults();
    
    // Take a screenshot
    await nlQueryPage.screenshot('test-results/nl-query-history-reuse.png');
  });
  
  test('validates empty queries', async () => {
    // Submit empty query
    await nlQueryPage.submitQuery();
    
    // Verify error message
    const errorMessage = await nlQueryPage.getErrorMessage();
    expect(errorMessage).toContain('Please enter a query');
    
    // Take a screenshot
    await nlQueryPage.screenshot('test-results/nl-query-empty-validation.png');
  });
});