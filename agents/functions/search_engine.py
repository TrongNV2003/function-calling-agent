from smolagents.tools import Tool

class SearchEngine(Tool):
    name = "search_engine"
    description = "Search engine for searching information."
    inputs = {
        "query": {
            "type": "string",
            "description": "The search query."
        }
    }
    output_type = "string"

    def __init__(self, max_results=6, **kwargs):
        super().__init__()
        self.max_results = max_results
        try:
            from duckduckgo_search import DDGS
        except ImportError as e:
            raise ImportError(
                "You must install package `duckduckgo_search` to run this tool: for instance run `pip install duckduckgo-search`."
            ) from e
        self.ddgs = DDGS(**kwargs)

    def forward(self, query: str) -> str:
        results = self.ddgs.text(query, max_results=self.max_results)
        if len(results) == 0:
            return "No results found! Try a less restrictive or shorter query."
        postprocessed_results = [f"[{result['title']}]({result['href']})\n{result['body']}" for result in results]
        return "## Search Results\n\n" + "\n\n".join(postprocessed_results)