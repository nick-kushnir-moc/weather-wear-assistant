class WeatherPage {
    constructor(page) {
      this.page = page;
      
      // Element selectors
      this.selectors = {
        tabButton: 'button:has-text("Weather Assistant")',
        locationInput: 'input#location',
        dateInput: 'input#date',
        occasionInput: 'input#occasion',
        preferencesInput: 'input#preferences',
        submitButton: 'button:has-text("Get Recommendations")',
        popularLocations: '.location-chip',
        recommendationSection: '.recommendation',
        weatherInfo: '.weather-info',
        temperature: '.weather-detail:has-text("Temperature")',
        conditions: '.weather-detail:has-text("Conditions")',
        outfitSection: '.outfit-recommendation',
        outfitItems: '.outfit-category',
        tipsList: '.tips ul li',
        errorMessage: '.error'
      };
    }
    
    // Navigation
    async goto() {
      await this.page.goto('/');
      await this.page.waitForSelector('h1:has-text("Personal AI Assistant")');
      await this.page.click(this.selectors.tabButton);
      await this.page.waitForSelector(this.selectors.locationInput);
    }
    
    // Actions
    async fillForm(location, date, occasion = '', preferences = '') {
      await this.page.fill(this.selectors.locationInput, location);
      
      // Only fill date if provided (otherwise use default)
      if (date) {
        await this.page.fill(this.selectors.dateInput, date);
      }
      
      if (occasion) {
        await this.page.fill(this.selectors.occasionInput, occasion);
      }
      
      if (preferences) {
        await this.page.fill(this.selectors.preferencesInput, preferences);
      }
    }
    
    async selectPopularLocation(locationName) {
      const locationElements = await this.page.$$(this.selectors.popularLocations);
      for (const element of locationElements) {
        const text = await element.innerText();
        if (text.includes(locationName)) {
          await element.click();
          return;
        }
      }
      throw new Error(`Popular location "${locationName}" not found`);
    }
    
    async submitForm() {
      await this.page.click(this.selectors.submitButton);
    }
    
    async getRecommendation(location, date, occasion = '', preferences = '') {
      await this.fillForm(location, date, occasion, preferences);
      await this.submitForm();
    }
    
    // Getters
    async getWeatherSummary() {
      const infoElement = await this.page.$(this.selectors.weatherInfo);
      if (infoElement) {
        return await infoElement.innerText();
      }
      return null;
    }
    
    async getOutfitRecommendations() {
      const outfitItems = await this.page.$$(this.selectors.outfitItems);
      const outfitData = {};
      
      for (const item of outfitItems) {
        const text = await item.innerText();
        const [category, value] = text.split(':').map(s => s.trim());
        outfitData[category.toLowerCase()] = value;
      }
      
      return outfitData;
    }
    
    async getTips() {
      const tips = await this.page.$$(this.selectors.tipsList);
      return Promise.all(tips.map(tip => tip.innerText()));
    }
    
    async getErrorMessage() {
      const errorElement = await this.page.$(this.selectors.errorMessage);
      if (errorElement) {
        return await errorElement.innerText();
      }
      return null;
    }
    
    async isSubmitButtonEnabled() {
      const button = await this.page.$(this.selectors.submitButton);
      return !(await button.isDisabled());
    }
    
    // Wait helpers
    async waitForRecommendation() {
      await this.page.waitForSelector(this.selectors.recommendationSection, { state: 'visible', timeout: 10000 });
    }
    
    async waitForError() {
      await this.page.waitForSelector(this.selectors.errorMessage, { state: 'visible', timeout: 10000 });
    }
    
    async hasRecommendation() {
      return await this.page.isVisible(this.selectors.recommendationSection);
    }
    
    async screenshot(path) {
      await this.page.screenshot({ path });
    }
  }
  
  export default WeatherPage;