import os
import httpx
from typing import List, Dict, Any

class TavilySearchService:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("TAVILY_API_KEY", "")
        self.base_url = "https://api.tavily.com/search"

    async def search_court_info(self, state_name: str, county_name: str, court_name: str) -> Dict[str, Any]:
        """
        Executes a targeted search via Tavily API for official county court contact details,
        clerk numbers, emails, and Public Access Terminal (PAT) information.
        """
        if not self.api_key:
            # Fallback mock search results if API key is not configured
            return {
                "results": [
                    {
                        "title": f"{court_name} - {county_name}, {state_name} Official Site",
                        "url": f"https://www.{county_name.lower().replace(' ', '')}court.{state_name.lower()}.gov",
                        "content": f"Official court office for {court_name}, {county_name}, {state_name}. Main Clerk Phone: (555) 234-5678. Records direct: (555) 234-5679. Email: clerk@{county_name.lower().replace(' ', '')}court.gov. Public Access Terminals (PAT) are located on the 1st floor room 102. PAT Hours: Mon-Fri 8:30 AM to 4:00 PM. Copy fees: $0.50 per page. 4 workstation terminals available."
                    }
                ]
            }

        query = f"{county_name} {state_name} {court_name} clerk phone number email public access terminal hours website site:.gov OR site:.us OR site:.org"
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                response = await client.post(
                    self.base_url,
                    json={
                        "api_key": self.api_key,
                        "query": query,
                        "search_depth": "advanced",
                        "include_domains": [".gov", ".us", ".org"],
                        "max_results": 3
                    }
                )
                if response.status_code == 200:
                    return response.json()
                else:
                    print(f"[Tavily API Warning] HTTP {response.status_code}: {response.text}")
            except Exception as e:
                print(f"[Tavily API Error] {e}")

        # Fallback return on error
        return {"results": []}
