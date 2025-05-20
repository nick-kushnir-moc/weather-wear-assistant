class NLQueryPage {
    constructor(page) {
      this.page = page;
      
      // Element selectors
      this.selectors = {
        tabButton: 'button:has-text("Database Query")',
        queryInput: 'input[placeholder*="Show"]',
        searchButton: 'button:has-text("Search")',
        resultsTable: 'table',
        resultRows: 'tbody tr',
        sqlQueryDisplay: '.sql-query pre',
        errorMessage: '.error',
        userMessage: '.user-message',
        historyHeader: 'h3:has-text("Query History")',
        historyItems: '.history-list li'
      };
    }
    
    // Navigation
    async goto() {
      await this.page.goto('/');
      await this.page.waitForSelector('h1:has-text("Personal AI Assistant")');
      await this.page.click(this.selectors.tabButton);
      await this.page.waitForSelector(this.selectors.queryInput);
    }
    
    // Actions
    async enterQuery(query) {
      await this.page.fill(this.selectors.queryInput, query);
    }
    
    async submitQuery() {
      await this.page.click(this.selectors.searchButton);
    }
    
    async enterAndSubmitQuery(query) {
      await this.enterQuery(query);
      await this.submitQuery();
    }
    
    async openQueryHistory() {
      await this.page.click(this.selectors.historyHeader);
    }
    
    async clickHistoryItem(index = 0) {
      await this.openQueryHistory();
      const items = await this.page.$$(this.selectors.historyItems);
      if (items.length > index) {
        await items[index].click();
      } else {
        throw new Error(`History item at index ${index} does not exist`);
      }
    }
    
    // Getters
    async getErrorMessage() {
      const errorElement = await this.page.$(this.selectors.errorMessage);
      if (errorElement) {
        return await errorElement.innerText();
      }
      return null;
    }
    
    async getSqlQuery() {
      const sqlElement = await this.page.$(this.selectors.sqlQueryDisplay);
      if (sqlElement) {
        return await sqlElement.innerText();
      }
      return null;
    }
    
    async getUserMessage() {
      const messageElement = await this.page.$(this.selectors.userMessage);
      if (messageElement) {
        return await messageElement.innerText();
      }
      return null;
    }
    
    async getResultsCount() {
      const rows = await this.page.$$(this.selectors.resultRows);
      return rows.length;
    }
    
    async getResultData() {
      const rows = await this.page.$$(this.selectors.resultRows);
      const data = [];
      
      for (const row of rows) {
        const cells = await row.$$('td');
        const rowData = {};
        
        // Get table headers
        const headers = await this.page.$$('th');
        const headerTexts = await Promise.all(headers.map(h => h.innerText()));
        
        for (let i = 0; i < cells.length; i++) {
          const cellText = await cells[i].innerText();
          rowData[headerTexts[i]] = cellText;
        }
        
        data.push(rowData);
      }
      
      return data;
    }
    
    async hasResults() {
      return await this.page.isVisible(this.selectors.resultsTable);
    }
    
    async waitForResults() {
      await this.page.waitForSelector(this.selectors.resultsTable, { state: 'visible', timeout: 10000 });
    }
    
    async waitForError() {
      await this.page.waitForSelector(this.selectors.errorMessage, { state: 'visible', timeout: 10000 });
    }
    
    async screenshot(path) {
      await this.page.screenshot({ path });
    }
  }
  
  export default NLQueryPage;