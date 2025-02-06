import os
from abc import ABC, abstractmethod

# The Abstract Base Class for verifying potential query candidates
class BaseGoogleVerifier(ABC):
    """
    Abstract base class that defines the structure for a Google verifier.
    Subclasses must implement the `search` method.
    The `verify` method orchestrates how results are fetched and analyzed.
    """
    
    @abstractmethod
    def search(self, prompt: str) -> dict:
        """
        Fetches search results for the given prompt (query) from a search engine.
        :param prompt: The query string to search for.
        :return: A dictionary containing search results (with 'organic_results' key).
        """
        pass

    def verify(self, prompt: str):
        """
        Orchestrates the verification process for the given prompt:
          1. Calls `search` to retrieve results.
          2. Analyzes the results to check for relevant info.
          3. Prints or returns an analysis.
        
        :param prompt: The query string to verify.
        """
        print(f"Verifying prompt: {prompt}")
        
        # 1. Retrieve search results
        results = self.search(prompt)
        
        # 2. Extract "organic_results" (list of dicts with 'title', 'link', 'snippet')
        organic_results = results.get("organic_results", [])
        
        # 3. Print or analyze them
        for i, result in enumerate(organic_results[:10], start=1):
            title = result.get("title", "")
            link = result.get("link", "")
            snippet = result.get("snippet", "")
            
            print(f"\nResult {i}")
            print(f"Title: {title}")
            print(f"Link: {link}")
            print(f"Snippet: {snippet}")
        
        # 4. Return an overall result structure
        verification_result = {
            "prompt": prompt,
            "result_count": len(organic_results),
            "analysis": "Basic snippet printout complete."
        }
        
        return verification_result


# 2) SerpApi Implementation
from serpapi import GoogleSearch

class GoogleVerifierSerpAPI(BaseGoogleVerifier):
    """
    Concrete implementation using SerpApi for the 'search' step.
    Docs: https://serpapi.com/
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("SERPAPI_KEY")
        if not self.api_key:
            raise ValueError("A valid SerpApi API key must be provided or set in environment.")

    def search(self, prompt: str) -> dict:
        # Prepare API parameters
        params = {
            "engine": "google",
            "q": prompt,
            "hl": "en",   # Language
            "gl": "us",   # Country
            "api_key": self.api_key
        }
        
        # Get the result from SerpApi
        search = GoogleSearch(params)
        results = search.get_dict()
        
        # SerpApi returns a JSON dict that often has "organic_results"
        # We'll just return the full dict here. 
        return results


# 3) Selenium Implementation
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

class GoogleVerifierSelenium(BaseGoogleVerifier):
    """
    Concrete implementation using Selenium WebDriver to control a local browser.
    """
    
    def __init__(self, driver_path=None, headless=True):
        """
        :param driver_path: Path to browser driver (e.g., chromedriver). If None, uses default.
        :param headless: Whether to run Chrome in headless mode.
        """
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument("--headless")
        
        # You may need to specify the driver path or ensure it's on your system PATH
        self.driver = webdriver.Chrome(executable_path=driver_path, options=options)
        self.driver.implicitly_wait(5)  # Wait up to 5s for elements
    
    def search(self, prompt: str) -> dict:
        # 1. Navigate to Google
        self.driver.get("https://www.google.com")
        
        # You might need to handle cookies popup depending on region.
        # 2. Find the search box and enter the prompt
        search_box = self.driver.find_element(By.NAME, "q")
        search_box.send_keys(prompt)
        search_box.send_keys(Keys.RETURN)
        
        # 3. Wait briefly for results to load (or use explicit waits)
        time.sleep(2)
        
        # 4. Collect the results
        #    The main container for each search result often has class "g" or "MjjYud"
        result_elements = self.driver.find_elements(By.CSS_SELECTOR, "div.g")
        
        organic_results = []
        for elem in result_elements:
            # Title is usually in a child <h3>
            title_elem = elem.find_element(By.CSS_SELECTOR, "h3") if elem.find_elements(By.CSS_SELECTOR, "h3") else None
            link_elem = elem.find_element(By.CSS_SELECTOR, "a") if elem.find_elements(By.CSS_SELECTOR, "a") else None
            snippet_elem = elem.find_element(By.CSS_SELECTOR, ".VwiC3b") if elem.find_elements(By.CSS_SELECTOR, ".VwiC3b") else None
            
            title_text = title_elem.text if title_elem else ""
            link_href = link_elem.get_attribute("href") if link_elem else ""
            snippet_text = snippet_elem.text if snippet_elem else ""
            
            # Skip empty or irrelevant items
            if not title_text.strip():
                continue
            
            organic_results.append({
                "title": title_text,
                "link": link_href,
                "snippet": snippet_text
            })
        
        # Return our standardized dict
        return {"organic_results": organic_results}


# 4) Playwright Implementation
import asyncio
from playwright.sync_api import sync_playwright

class GoogleVerifierPlaywright(BaseGoogleVerifier):
    """
    Concrete implementation using Playwright (synchronous style via 'sync_playwright').
    """
    
    def __init__(self, headless=True):
        """
        :param headless: Whether to run the browser in headless mode.
        """
        self.headless = headless

    def search(self, prompt: str) -> dict:
        """
        Uses Playwright to launch a browser, perform a search on Google,
        and scrape result titles/snippets.
        """
        # We'll do a synchronous approach using sync_playwright() context manager
        # If you prefer async, you can adapt to async/await.
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            context = browser.new_context()
            page = context.new_page()
            
            # 1. Go to Google
            page.goto("https://www.google.com")
            
            # 2. Type the query in the search box
            # Depending on location, you might see consent popups. 
            page.fill('input[name="q"]', prompt)
            page.keyboard.press("Enter")
            
            # 3. Wait for results to load
            page.wait_for_selector("h3", timeout=6000)
            
            # 4. Extract search results
            #    Each result is typically wrapped in something containing <h3> for the title
            #    We can gather snippets from the "span" or ".VwiC3b" class elements
            result_elements = page.query_selector_all('div.g')
            organic_results = []
            
            for elem in result_elements:
                # Title is typically the inner text of <h3>
                h3 = elem.query_selector('h3')
                a_tag = elem.query_selector('a')
                snippet = elem.query_selector('.VwiC3b')
                
                title_text = h3.inner_text() if h3 else ""
                link_href = a_tag.get_attribute("href") if a_tag else ""
                snippet_text = snippet.inner_text() if snippet else ""
                
                # Skip empty
                if not title_text.strip():
                    continue
                
                organic_results.append({
                    "title": title_text,
                    "link": link_href,
                    "snippet": snippet_text
                })
            
            browser.close()
            
            return {"organic_results": organic_results}

# -----------------------------------------------------------
# Example usage (uncomment one at a time to test each variant)
# -----------------------------------------------------------
if __name__ == "__main__":
    # Example prompt
    test_prompt = (
        "Which theater in Boston, often overshadowed by more famous venues, "
        "is officially recorded as the city’s oldest operating theater?"
    )
    
    # -- 1) Using SerpApi --
    # serp_verifier = GoogleVerifierSerpAPI(api_key="<YOUR_SERPAPI_KEY>")
    # serp_results = serp_verifier.verify(test_prompt)
    # print("SerpApi verification:", serp_results)
    
    # -- 2) Using Selenium --
    # NOTE: Make sure you have Selenium and ChromeDriver installed
    # sel_verifier = GoogleVerifierSelenium(headless=True)
    # sel_results = sel_verifier.verify(test_prompt)
    # print("Selenium verification:", sel_results)
    # sel_verifier.driver.quit()  # Close the browser when done
    
    # -- 3) Using Playwright --
    # NOTE: pip install playwright && playwright install
    # play_verifier = GoogleVerifierPlaywright(headless=True)
    # play_results = play_verifier.verify(test_prompt)
    # print("Playwright verification:", play_results)
    
    pass
