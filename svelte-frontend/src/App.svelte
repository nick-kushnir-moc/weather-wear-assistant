<script>
	import { onMount } from 'svelte';
	import AiAssistant from './components/AiAssistant.svelte';
	import NLQueryAssistant from './components/NLQueryAssistant.svelte';
	import WeatherDressAssistant from './components/WeatherDressAssistant.svelte';
	import axios from 'axios';
  
	let responseData = '';
	let activeTab = 'nlquery';
  
	onMount(async () => {
  		try {
     		const response = await axios.get('http://localhost:8000/');
    		responseData = response.data.message;
    		console.log("API response:", response.data);  
  		} 	catch (error) {
    		console.error('Error fetching data:', error);
    		responseData = "Could not connect to API server";
  		}
	});
  
	function setActiveTab(tab) {
	  activeTab = tab;
	}
  </script>
  
  <div class="app-container">
	<!-- Left column: Main content -->
	<div class="main-column">
	  <h1>Personal AI Assistant</h1>
	  <p>{responseData}</p>
	  <AiAssistant />
	</div>
  
	<!-- Right column: AI Tools -->
	<div class="tools-column">
	  <div class="tools-header">
		<h2>AI Tools</h2>
		<div class="tabs">
		  <button 
			class="tab-button" 
			class:active={activeTab === 'nlquery'} 
			on:click={() => setActiveTab('nlquery')}
		  >
			Database Query
		  </button>
		  <button 
			class="tab-button" 
			class:active={activeTab === 'weather'} 
			on:click={() => setActiveTab('weather')}
		  >
			Weather Assistant
		  </button>
		</div>
	  </div>
  
	  <div class="tool-content">
		{#if activeTab === 'nlquery'}
		  <NLQueryAssistant />
		{:else if activeTab === 'weather'}
		  <WeatherDressAssistant />
		{/if}
	  </div>
	</div>
  </div>
  
  <style>
	:global(body) {
	  margin: 0;
	  padding: 0;
	  font-family: Arial, sans-serif;
	  background-color: #f8f9fa;
	}
  
	.app-container {
	  display: flex;
	  min-height: 100vh;
	}
  
	.main-column {
	  flex: 1;
	  padding: 2rem;
	  border-right: 1px solid #ddd;
	  background-color: white;
	}
  
	.tools-column {
	  width: 450px;
	  background-color: #f8f9fa;
	  overflow-y: auto;
	  display: flex;
	  flex-direction: column;
	}
  
	.tools-header {
	  padding: 1.5rem;
	  background-color: white;
	  border-bottom: 1px solid #ddd;
	  position: sticky;
	  top: 0;
	  z-index: 10;
	}
  
	h1 {
	  color: #ff3e00;
	  text-transform: uppercase;
	  font-size: 2.5em;
	  font-weight: 100;
	  margin-top: 0;
	}
  
	h2 {
	  color: #333;
	  font-size: 1.5rem;
	  margin-top: 0;
	  margin-bottom: 1rem;
	}
  
	.tabs {
	  display: flex;
	  border-bottom: 1px solid #ddd;
	}
  
	.tab-button {
	  padding: 0.75rem 1rem;
	  background: none;
	  border: none;
	  border-bottom: 2px solid transparent;
	  cursor: pointer;
	  font-size: 1rem;
	  color: #555;
	  transition: all 0.2s;
	}
  
	.tab-button:hover {
	  color: #ff3e00;
	}
  
	.tab-button.active {
	  color: #ff3e00;
	  border-bottom-color: #ff3e00;
	  font-weight: bold;
	}
  
	.tool-content {
	  padding: 1rem;
	  flex: 1;
	}
  
	@media (max-width: 900px) {
	  .app-container {
		flex-direction: column;
	  }
  
	  .main-column, .tools-column {
		width: 100%;
	  }
  
	  .tools-column {
		border-top: 1px solid #ddd;
		border-left: none;
	  }
	}
  </style>