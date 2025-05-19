<script>
    import { onMount } from 'svelte';
    import axios from 'axios';
  
    // Component state
    let location = '';
    let date = '';
    let occasion = '';
    let preferences = '';
    let loading = false;
    let error = null;
    let recommendation = null;
    
    // Get today's date in YYYY-MM-DD format for the date input's min value
    const today = new Date().toISOString().split('T')[0];
    
    // Get date 5 days from now for the max value (OpenWeatherMap free tier limit)
    const fiveDaysFromNow = new Date();
    fiveDaysFromNow.setDate(fiveDaysFromNow.getDate() + 5);
    const maxDate = fiveDaysFromNow.toISOString().split('T')[0];
    
    // Default date to today
    onMount(() => {
      date = today;
    });
  
    // Predefined locations for easy selection
    const popularLocations = [
      'New York, US',
      'London, UK',
      'Tokyo, JP',
      'Sydney, AU',
      'Paris, FR',
      'Berlin, DE',
      'Toronto, CA',
      'Singapore, SG'
    ];
  
    // Function to get dress recommendations
    async function getDressRecommendation() {
      if (!location) {
        error = "Please enter a location.";
        return;
      }
  
      if (!date) {
        error = "Please select a date.";
        return;
      }
  
      loading = true;
      error = null;
      recommendation = null;
  
      try {
        const response = await axios.post('http://localhost:8000/api/weather-assistant/dress-recommendation', {
          user_id: 1, // Hardcoded for demo
          location,
          date,
          occasion,
          preferences
        });
  
        recommendation = response.data;
      } catch (err) {
        console.error('Error getting dress recommendations:', err);
        error = err.response?.data?.detail || "An error occurred while getting recommendations.";
      } finally {
        loading = false;
      }
    }
  
    // Function to use a popular location
    function usePopularLocation(loc) {
      location = loc;
    }
  
    // Function to format temperature
    function formatTemp(temp) {
      return `${Math.round(temp)}°C`;
    }
  </script>
  
  <div class="weather-dress-assistant">
    <h2>Weather-Based Dress Assistant</h2>
    <p class="description">Get clothing recommendations based on weather forecast</p>
  
    <div class="form-container">
      <div class="form-group">
        <label for="location">Location</label>
        <div class="location-input">
          <input 
            id="location"
            type="text" 
            bind:value={location} 
            placeholder="e.g., 'New York, US'"
          />
        </div>
        <div class="popular-locations">
          <p>Popular locations:</p>
          <div class="location-chips">
            {#each popularLocations as loc}
              <button 
                class="location-chip" 
                on:click={() => usePopularLocation(loc)}
                class:selected={location === loc}
              >
                {loc}
              </button>
            {/each}
          </div>
        </div>
      </div>
  
      <div class="form-group">
        <label for="date">Date</label>
        <input 
          id="date"
          type="date" 
          bind:value={date}
          min={today}
          max={maxDate}
        />
        <p class="note">Forecasts available for the next 5 days</p>
      </div>
  
      <div class="form-row">
        <div class="form-group">
          <label for="occasion">Occasion (optional)</label>
          <input 
            id="occasion"
            type="text" 
            bind:value={occasion} 
            placeholder="e.g., 'Business meeting', 'Casual outing'"
          />
        </div>
  
        <div class="form-group">
          <label for="preferences">Style preferences (optional)</label>
          <input 
            id="preferences"
            type="text" 
            bind:value={preferences} 
            placeholder="e.g., 'Casual', 'Professional', 'Comfortable'"
          />
        </div>
      </div>
  
      <button 
        class="submit-button" 
        on:click={getDressRecommendation} 
        disabled={loading || !location || !date}
      >
        {loading ? 'Getting recommendations...' : 'Get Recommendations'}
      </button>
    </div>
  
    {#if error}
      <div class="error">
        <p>{error}</p>
      </div>
    {/if}
  
    {#if recommendation}
      <div class="recommendation">
        <div class="weather-info">
          <h3>Weather in {recommendation.location} on {recommendation.date}</h3>
          <div class="weather-details">
            <div class="weather-detail">
              <strong>Temperature:</strong> {formatTemp(recommendation.temperature)}
            </div>
            <div class="weather-detail">
              <strong>Conditions:</strong> {recommendation.conditions}
            </div>
          </div>
        </div>
        
        <div class="outfit-recommendation">
          <h3>Clothing Recommendations</h3>
          <p class="summary">{recommendation.recommendations.summary}</p>
          
          {#if recommendation.recommendations.outfit && Object.keys(recommendation.recommendations.outfit).length > 0}
            <div class="outfit-items">
              {#each Object.entries(recommendation.recommendations.outfit) as [category, item]}
                {#if item && item.length > 0}
                  <div class="outfit-category">
                    <strong>{category.charAt(0).toUpperCase() + category.slice(1)}:</strong>
                    {#if Array.isArray(item[0])}
                      <ul>
                        {#each item as accessory}
                          <li>{accessory[1]}</li>
                        {/each}
                      </ul>
                    {:else}
                      <span>{item[1]}</span>
                    {/if}
                  </div>
                {/if}
              {/each}
            </div>
          {/if}
          
          {#if recommendation.recommendations.tips && recommendation.recommendations.tips.length > 0}
            <div class="tips">
              <h4>Additional Tips:</h4>
              <ul>
                {#each recommendation.recommendations.tips as tip}
                  <li>{tip}</li>
                {/each}
              </ul>
            </div>
          {/if}
        </div>
      </div>
    {/if}
  </div>
  
  <style>
    .weather-dress-assistant {
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
  
    .form-container {
      display: flex;
      flex-direction: column;
      gap: 15px;
      margin-bottom: 20px;
    }
  
    .form-row {
      display: flex;
      gap: 15px;
    }
  
    .form-group {
      display: flex;
      flex-direction: column;
      flex: 1;
    }
  
    label {
      font-weight: bold;
      margin-bottom: 5px;
      text-align: left;
    }
  
    input {
      padding: 10px;
      border: 1px solid #ccc;
      border-radius: 4px;
      font-size: 1rem;
    }
  
    .location-input {
      position: relative;
    }
  
    .popular-locations {
      margin-top: 10px;
    }
  
    .popular-locations p {
      margin: 0 0 5px 0;
      font-size: 0.8rem;
      color: #666;
      text-align: left;
    }
  
    .location-chips {
      display: flex;
      flex-wrap: wrap;
      gap: 5px;
    }
  
    .location-chip {
      background-color: #f0f0f0;
      border: 1px solid #ddd;
      border-radius: 16px;
      padding: 4px 12px;
      font-size: 0.8rem;
      cursor: pointer;
      transition: all 0.2s;
    }
  
    .location-chip:hover {
      background-color: #e0e0e0;
    }
  
    .location-chip.selected {
      background-color: #ff3e00;
      color: white;
      border-color: #ff3e00;
    }
  
    .note {
      margin: 5px 0 0 0;
      font-size: 0.8rem;
      color: #666;
      text-align: left;
    }
  
    .submit-button {
      padding: 12px 20px;
      background-color: #ff3e00;
      color: white;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      font-size: 1rem;
      margin-top: 10px;
    }
  
    .submit-button:disabled {
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
  
    .recommendation {
      margin-top: 20px;
      border-top: 1px solid #eee;
      padding-top: 20px;
    }
  
    .weather-info {
      margin-bottom: 20px;
    }
  
    .weather-info h3 {
      margin-top: 0;
      color: #333;
      font-size: 1.2rem;
    }
  
    .weather-details {
      display: flex;
      gap: 20px;
      margin-top: 10px;
    }
  
    .weather-detail {
      padding: 10px;
      background-color: #f5f5f5;
      border-radius: 4px;
    }
  
    .outfit-recommendation h3 {
      margin-top: 0;
      color: #333;
      font-size: 1.2rem;
    }
  
    .summary {
      margin-top: 0;
      padding: 15px;
      background-color: #fff8e1;
      border-radius: 4px;
      border-left: 4px solid #ffd54f;
      text-align: left;
    }
  
    .outfit-items {
      margin: 15px 0;
      text-align: left;
    }
  
    .outfit-category {
      margin-bottom: 10px;
    }
  
    .outfit-category ul {
      margin: 5px 0 0 0;
      padding-left: 20px;
    }
  
    .tips {
      margin-top: 20px;
      text-align: left;
    }
  
    .tips h4 {
      margin-top: 0;
      color: #333;
      font-size: 1rem;
    }
  
    .tips ul {
      margin-top: 5px;
      padding-left: 20px;
    }
  
    .tips li {
      margin-bottom: 5px;
    }
  
    @media (max-width: 600px) {
      .form-row {
        flex-direction: column;
      }
    }
  </style>