from smolagents import Tool
from smolagents import CodeAgent, HfApiModel

from langchain.docstore.document import Document
from langchain_community.retrievers import BM25Retriever
from langchain.text_splitter import RecursiveCharacterTextSplitter

from function_calling_agents.db.elasticsearch.operations import ElasticsearchProvider

class Retriever(Tool):
    name = "retrieval_engine"
    description = "Uses semantic search to retrieve relevant documents."
    inputs = {
        "query": {
            "type": "string",
            "description": "The query to retrieve. This should be a query related to provided documents.",
        },
        "top_k": {
            "type": "int",
            "description": "The number of documents to retrieve.",
        }
    }
    output_type = "string"

    def __init__(self):
        self.elastic_provider = ElasticsearchProvider()

    def forward(self, query: str, top_k: int) -> str:
        retrieval = self.elastic_provider.bm25_search(query, top_k)

        if not retrieval or isinstance(retrieval[0], dict) and ("message" in retrieval[0] or "error" in retrieval[0]):
            return "No relevant documents found or an error occurred during retrieval."
        
        output_lines = ["Relevant documents:"]
        for i, doc in enumerate(retrieval):
            if "text" in doc:
                output_lines.append(f"\n=== Document {i} (score: {doc['score']:.3f}) ===\n{doc['text']}")
            else:
                output_lines.append(f"\n=== Document {i} ===\n[Invalid document format]")
        
        return "\n".join(output_lines)

# class RetrieverTool(Tool):
#     name = "retriever"
#     description = "Uses semantic search to retrieve relevant party planning ideas for Alfred’s superhero-themed party at Wayne Manor."
#     inputs = {
#         "query": {
#             "type": "string",
#             "description": "The query to perform. This should be a query related to party planning or superhero themes.",
#         }
#     }
#     output_type = "string"

#     def __init__(self, docs, **kwargs):
#         super().__init__(**kwargs)
#         self.retriever = BM25Retriever.from_documents(
#             docs, k=5  # Retrieve the top 5 documents
#         )

#     def forward(self, query: str) -> str:
#         assert isinstance(query, str), "Your search query must be a string"

#         docs = self.retriever.invoke(
#             query,
#         )
#         return "\nRetrieved ideas:\n" + "".join(
#             [
#                 f"\n\n===== Idea {str(i)} =====\n" + doc.page_content
#                 for i, doc in enumerate(docs)
#             ]
#         )
    
# if __name__ == "__main__":
#     party_ideas = [
#         {"text": "A superhero-themed masquerade ball with luxury decor, including gold accents and velvet curtains.", "source": "Party Ideas 1"},
#         {"text": "Hire a professional DJ who can play themed music for superheroes like Batman and Wonder Woman.", "source": "Entertainment Ideas"},
#         {"text": "For catering, serve dishes named after superheroes, like 'The Hulk's Green Smoothie' and 'Iron Man's Power Steak.'", "source": "Catering Ideas"},
#         {"text": "Decorate with iconic superhero logos and projections of Gotham and other superhero cities around the venue.", "source": "Decoration Ideas"},
#         {"text": "Interactive experiences with VR where guests can engage in superhero simulations or compete in themed games.", "source": "Entertainment Ideas"}
#     ]

#     source_docs = [
#         Document(page_content=doc["text"], metadata={"source": doc["source"]})
#         for doc in party_ideas
#     ]

#     text_splitter = RecursiveCharacterTextSplitter(
#         chunk_size=512,
#         chunk_overlap=50,
#         add_start_index=True,
#         strip_whitespace=True,
#         separators=["\n\n", "\n", ".", " ", ""],
#     )
#     docs_processed = text_splitter.split_documents(source_docs)

#     party_planning_retriever = RetrieverTool(docs_processed)

#     agent = CodeAgent(tools=[party_planning_retriever], model=HfApiModel())

#     response = agent.run(
#         "Find ideas for a luxury superhero-themed party, including entertainment, catering, and decoration options."
#     )

#     print(response)