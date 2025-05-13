import requests
from smolagents.tools import Tool

class SearchEngine(Tool):
    name = "search_engine"
    description = "Search engine using Google Custom Search API for searching information."
    inputs = {
        "query": {
            "type": "string",
            "description": "The search query."
        }
    }
    output_type = "string"

    def __init__(self, api_key, search_engine_id=None, endpoint=None, max_results=6):
        super().__init__()
        self.api_key = api_key
        self.search_engine_id = search_engine_id
        self.max_results = max_results
        self.endpoint = endpoint or "https://www.googleapis.com/customsearch/v1"

    def forward(self, query: str) -> str:
        params = {
            "key": self.api_key,
            "cx": self.search_engine_id,
            "q": query,
            "num": self.max_results
        }
        response = requests.get(self.endpoint, params=params)

        if response.status_code != 200:
            return f"Error: {response.status_code}, {response.text}"

        results = response.json().get("items", [])
        if not results:
            return "No results found! Try a less restrictive or shorter query."

        postprocessed_results = [
            f"[{result['title']}]({result['link']})\n{result.get('snippet', '')}"
            for result in results
        ]
        return "## Search Results\n\n" + "\n\n".join(postprocessed_results)