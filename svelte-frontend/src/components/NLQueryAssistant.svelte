<script>
    import { onMount } from 'svelte';
    import axios from 'axios';
  
    // Component state
    let query = '';
    let results = null;
    let sqlQuery = '';
    let loading = false;
    let error = null;
    let metadata = {};
    let userMessage = '';
    let expanded = true;
    let historyExpanded = false;
    let queryHistory = [];
  
    // Function to process natural language query
    async function processQuery() {
      if (!query.trim()) {
        error = "Please enter a query.";
        return;
      }
  
      loading = true;
      error = null;
      results = null;
      sqlQuery = '';
      userMessage = '';
  
      try {
        const response = await axios.post('http://localhost:8000/api/nl-query/process', {
          query: query
        });
  
        // Update component state with response data
        results = response.data.results;
        sqlQuery = response.data.sql_query;
        metadata = response.data.metadata || {};
        error = response.data.error;
        userMessage = response.data.user_message;
  
        // Add query to history if successful
        if (!error && results) {
          queryHistory = [
            { 
              query, 
              sqlQuery, 
              timestamp: new Date().toLocaleTimeString(),
              resultCount: results.length
            },
            ...queryHistory.slice(0, 9) // Keep last 10 queries
          ];
        }
      } catch (err) {
        console.error('Error processing query:', err);
        error = err.response?.data?.detail || "An error occurred while processing your query.";
      } finally {
        loading = false;
      }
    }
  
    // Function to get table headers from results
    function getHeaders(results) {
      if (!results || results.length === 0) return [];
      return Object.keys(results[0]);
    }
  
    // Function to reuse a query from history
    function useHistoryQuery(historyItem) {
      query = historyItem.query;
      processQuery();
    }
  </script>
  
  <div class="nl-query-assistant">
    <h2>Database Query Assistant</h2>
    <p class="description">Ask a question about your data in natural language</p>
  
    <div class="query-container">
      <input 
        type="text" 
        bind:value={query} 
        placeholder="e.g., 'Show all employees in AAP department'"
        on:keydown={(e) => e.key === 'Enter' && processQuery()}
      />
      <button class="search-button" on:click={processQuery} disabled={loading}>
        {loading ? 'Processing...' : 'Search'}
      </button>
    </div>
  
    {#if error}
      <div class="error">
        <p>{error}</p>
      </div>
    {/if}
  
    {#if userMessage}
      <div class="user-message">
        <h3>Results Summary:</h3>
        <p>{userMessage}</p>
      </div>
    {/if}
  
    {#if sqlQuery}
      <div class="sql-query">
        <h3>Generated SQL:</h3>
        <pre>{sqlQuery}</pre>
      </div>
    {/if}
  
    {#if results && results.length > 0}
      <div class="results">
        <div class="results-header">
          <h3>Results: {results.length} {results.length === 1 ? 'row' : 'rows'}</h3>
          {#if metadata && metadata.execution_time_seconds}
            <span class="execution-time">({metadata.execution_time_seconds}s)</span>
          {/if}
        </div>
        
        <div class="table-container">
          <table>
            <thead>
              <tr>
                {#each getHeaders(results) as header}
                  <th>{header}</th>
                {/each}
              </tr>
            </thead>
            <tbody>
              {#each results as row}
                <tr>
                  {#each getHeaders(results) as header}
                    <td>{row[header] !== null ? row[header] : '-'}</td>
                  {/each}
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
      </div>
    {:else if results && results.length === 0}
      <div class="no-results">
        <p>No results found for your query.</p>
      </div>
    {/if}
  
    <!-- Query History Section -->
    {#if queryHistory.length > 0}
      <div class="history-section">
        <div class="history-header" on:click={() => historyExpanded = !historyExpanded}>
          <h3>Query History</h3>
          <span>{historyExpanded ? '−' : '+'}</span>
        </div>
        
        {#if historyExpanded}
          <ul class="history-list">
            {#each queryHistory as item}
              <li on:click={() => useHistoryQuery(item)}>
                <div class="history-query">{item.query}</div>
                <div class="history-meta">
                  <span>{item.timestamp}</span>
                  <span>{item.resultCount} results</span>
                </div>
              </li>
            {/each}
          </ul>
        {/if}
      </div>
    {/if}
  </div>
  
  <style>
    .nl-query-assistant {
      font-family: 'Arial', sans-serif;
      border: 1px solid #ddd;
      border-radius: 8px;
      background-color: white;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
      margin: 20px 0;
      padding: 20px;
    }
  
    h2 {
      margin-top: 0;
      color: #ff3e00;
      font-size: 1.5rem;
    }
  
    .description {
      color: #555;
      margin-bottom: 15px;
    }
  
    .query-container {
      display: flex;
      margin: 15px 0;
    }
  
    input {
      flex-grow: 1;
      padding: 12px;
      border: 1px solid #ccc;
      border-radius: 4px 0 0 4px;
      font-size: 1rem;
    }
  
    .search-button {
      padding: 0 20px;
      background-color: #ff3e00;
      color: white;
      border: none;
      border-radius: 0 4px 4px 0;
      cursor: pointer;
      font-size: 1rem;
      white-space: nowrap;
    }
  
    .search-button:disabled {
      background-color: #ccc;
      cursor: not-allowed;
    }
  
    .error {
      color: #d32f2f;
      margin: 15px 0;
      padding: 12px;
      background-color: #ffebee;
      border-radius: 4px;
    }
  
    .user-message {
      margin: 15px 0;
      padding: 15px;
      background-color: #e8f5e9;
      border-radius: 4px;
      text-align: left;
    }
  
    .user-message h3 {
      margin-top: 0;
      color: #2e7d32;
      font-size: 1rem;
      margin-bottom: 8px;
    }
  
    .sql-query {
      text-align: left;
      margin: 15px 0;
      padding: 15px;
      background-color: #f5f5f5;
      border-radius: 4px;
      overflow-x: auto;
    }
  
    .sql-query h3 {
      margin-top: 0;
      font-size: 1rem;
      margin-bottom: 8px;
    }
  
    pre {
      margin: 0;
      white-space: pre-wrap;
      font-family: 'Courier New', monospace;
      font-size: 0.9rem;
    }
  
    .results-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      text-align: left;
    }
  
    .results-header h3 {
      margin: 0;
      font-size: 1rem;
    }
  
    .execution-time {
      font-size: 0.8rem;
      color: #777;
    }
  
    .table-container {
      overflow-x: auto;
      margin-top: 10px;
    }
  
    table {
      width: 100%;
      border-collapse: collapse;
    }
  
    th, td {
      padding: 10px 15px;
      border: 1px solid #ddd;
      text-align: left;
    }
  
    th {
      background-color: #f2f2f2;
      font-weight: bold;
    }
  
    tr:nth-child(even) {
      background-color: #f9f9f9;
    }
  
    .no-results {
      margin: 15px 0;
      padding: 15px;
      background-color: #f5f5f5;
      border-radius: 4px;
      color: #555;
    }
  
    .history-section {
      margin-top: 20px;
      border-top: 1px solid #eee;
      padding-top: 15px;
    }
  
    .history-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      cursor: pointer;
      text-align: left;
    }
  
    .history-header h3 {
      margin: 0;
      font-size: 1rem;
    }
  
    .history-list {
      list-style: none;
      padding: 0;
      margin: 10px 0 0 0;
    }
  
    .history-list li {
      padding: 10px;
      border: 1px solid #eee;
      border-radius: 4px;
      margin-bottom: 8px;
      cursor: pointer;
      transition: background-color 0.2s;
      text-align: left;
    }
  
    .history-list li:hover {
      background-color: #f0f0f0;
    }
  
    .history-query {
      font-weight: bold;
      margin-bottom: 5px;
    }
  
    .history-meta {
      display: flex;
      justify-content: space-between;
      font-size: 0.8rem;
      color: #777;
    }
  </style>