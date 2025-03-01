import pymupdf
from enum import Enum
from pydantic import BaseModel
from typing import Optional, Any
from fastapi.responses import JSONResponse
from config.yaml_loader import load_config
from db.elasticsearch.connector import connect_db
from langchain.text_splitter import RecursiveCharacterTextSplitter

config = load_config()

class ElasticsearchProvider:
    def __init__(self) -> None:
        self.client = connect_db()
    
    def upsert_input(self, text, index_name, document_id: Optional[str] = None):
        # Tạo doc để upsert vào Elasticsearch
        doc = {
            "text": text
        }
        
        if document_id and self.get_point_by_id(index_name, document_id):
            response = self.client.update(
                index=index_name,
                id=document_id,
                body=doc
            )
            return response
        else:
            response = self.client.index(index=index_name, body=doc)
            return response
    
    
    def upsert_from_text(self, documents: str, index_name: str):
        for document in self.splitter(documents):
            output = self.upsert_input(document, index_name=index_name)
        return output


    def upsert_from_files(self, pdf_file: str, doc_type: str, index_name: str):
        # nếu là thơ thì xuống dòng, nếu là document thì không cần
        if doc_type == "Thơ":
            pdf_content = self.process_pdf_file(pdf_file)
        elif doc_type == "Văn bản":
            pdf_content = self.process_pdf_file(pdf_file)
            pdf_content = self.clean_pdf_text(pdf_content)
        else:
            return {"message": "Invalid document type."}
            
        self.upsert_from_text(pdf_content, index_name)
        

    def process_pdf_file(self, pdf_file: str):
        pdf_document = ""
        with pymupdf.open(stream=pdf_file, filetype="pdf") as pdf_reader:
            for page_num in range(pdf_reader.page_count):
                page = pdf_reader[page_num]
                pdf_document += page.get_text()
        return pdf_document


    def splitter(self, text: str):
        docs = []
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size = 512
        )
        chunks = text_splitter.split_text(text)
        for chunk in chunks:
            docs.append(chunk)
        return docs
    
    
    def clean_pdf_text(self, text: str):
        text = text.replace("\n", "")
        return text
    
    
# search theo embedding 
    # def embedding_search(self, query_input, threshold):
    #     """
    #     Vector search (Cosine similarity)
    #     """
    #     text_embedding = model.embedding_query(query_input)
    #     query_body = {
    #         "size": 10,
    #         "query": {
    #             "bool": {
    #                 "must": [
    #                     {
    #                         "script_score": {
    #                             "query": {"match_all": {}},
    #                             "script": {
    #                                 "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
    #                                 "params": {
    #                                     "query_vector": text_embedding
    #                                 }
    #                             }
    #                         }
    #                     }
    #                 ]
    #             }
    #         }
    #     }
    #     top_label = self.retrieval(query_body, threshold)
    #     return top_label
              
              
# search theo text thuần 
    def text_search(self, query_input, threshold):
        """
        Logic BM25, search theo text (tương tự TF-IDF)
        """
        query_body = {
            "size": 3,
            "query": {
                    "multi_match": {
                        "query": query_input,
                        "fields": ["text"]
                    }
                }
        }  
        top_label = self.retrieval(query_body, threshold)
        return top_label
    
    
    def retrieval(self, query_body, threshold):
        results = self.client.search(index=config["elasticsearch"]["index_name"], body=query_body)

        if not results['hits']['hits']:
            return {"message": "No labels found for the given document type."}

        top_label = [hit['_source']['text'] for hit in results['hits']['hits'] if hit['_score'] >= threshold]
        
        if not top_label:
            top_label = [hit['_source']['text'] for hit in results['hits']['hits'][:1]]
        return top_label
    
    
    def delete_index(self, index_name):
        self.client.indices.delete(index=index_name)
    
    
    def get_point_by_id(self, index_name: str, id: str):
        index_name = index_name.lower()
        try:
            # Execute the search query
            response = self.client.get(index=index_name, id=id)
            return response['_source']
        except Exception as e:
            return JSONResponse({"error": f"Failed to search documents by ID from index {index_name}"}, status_code=500)

    
    def convert_to_serializable(self, obj: Any) -> Any:
        """Chuyển đổi các đối tượng không thể serialize thành dạng đơn giản."""
        if isinstance(obj, BaseModel):
            return obj.dict()  # Convert Pydantic BaseModel sang dict
        elif isinstance(obj, Enum):
            return obj.value  # Convert Enum to value
        elif isinstance(obj, list):
            return [self.convert_to_serializable(item) for item in obj]
        elif isinstance(obj, dict):
            return {key: self.convert_to_serializable(value) for key, value in obj.items()}
        else:
            return obj