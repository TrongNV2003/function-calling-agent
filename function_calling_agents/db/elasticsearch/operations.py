import pymupdf
from enum import Enum
from pydantic import BaseModel
from typing import Optional, Any
from fastapi.responses import JSONResponse
from langchain.text_splitter import RecursiveCharacterTextSplitter

from agents.config.setting import elastic_config
from agents.db.elasticsearch.connector import connect_db, check_connection


class ElasticsearchProvider:
    def __init__(self) -> None:
        self.client = connect_db()
        self.check_connection = check_connection(self.client)
   

    # BM25 retrieval
    def bm25_search(self, query_input: str, top_k: int) -> list:
        """
        Tìm kiếm sử dụng BM25 với multi_match query.
        params:
            query_input: Câu truy vấn từ người dùng.
            threshold: Ngưỡng điểm BM25 để lọc kết quả.
        return: 
            Danh sách các đoạn text liên quan.
        """
        query_body = {
            "size": top_k,
            "query": {
                "multi_match": {
                    "query": query_input,
                    "fields": ["text"],  # Chỉ tìm trên field 'text'
                    "type": "best_fields",  # Sử dụng best_fields để ưu tiên BM25
                    "fuzziness": "AUTO"  # Cho phép tìm kiếm gần đúng (tùy chọn)
                }
            }
        }
        top_docs = self._retrieval(query_body)
        return top_docs


    def upsert_text(self, document: str, index_name: str) -> dict:
        for doc in self._splitter(document):
            output = self._upsert(text=doc, index_name=index_name)
        return output


    def upsert_files(self, pdf_file: str, doc_type: str, index_name: str):
        if doc_type == "pdf":
            pdf_content = self._load_pdf(pdf_file, index_name)
            return pdf_content
        else:
            return {"message": "Invalid document type."}
            

    def _load_pdf(self, pdf_file: str, index_name: str) -> dict:
        pdf_document = ""
        with pymupdf.open(pdf_file, filetype="pdf") as pdf_reader:
            for page_num in range(pdf_reader.page_count):
                page = pdf_reader[page_num]
                pdf_document += page.get_text()
        
        for document in self._splitter(pdf_document):
            output = self._upsert(document, index_name=index_name)
        return output

 
    def _upsert(self, text: str, index_name: str, document_id: Optional[str] = None) -> dict:
        doc = {
            "text": text
        }
        
        if document_id and self._get_point_by_id(index_name, document_id):
            response = self.client.update(
                index=index_name,
                id=document_id,
                body=doc
            )
        else:
            response = self.client.index(index=index_name, body=doc)
            
        return response


    def _splitter(self, text: str) -> list:
        docs = []
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=512,
            chunk_overlap=32,
        )
        chunks = text_splitter.split_text(text)
        for chunk in chunks:
            docs.append(chunk)
        return docs
                  

    def _retrieval(self, query_body: dict) -> list:
        results = self.client.search(index=elastic_config.index_name, body=query_body)
        try:
            if not results['hits']['hits']:
                return {"message": "No labels found for the given document type."}

            top_docs = [
                    {
                        "text": hit['_source']['text'],
                        "score": hit['_score']
                    } for hit in results['hits']['hits']
                ]
                
            return top_docs
        
        except Exception as e:
            return [{"error": f"Failed to retrieve documents: {str(e)}"}]
    
    
    def delete_index(self, index_name: str):
        try:
            self.client.indices.delete(index=index_name)
            return {"message": f"Index {index_name} deleted successfully."}
        except Exception as e:
            return {"error": f"Failed to delete index {index_name}: {str(e)}"}
    
    
    def _get_point_by_id(self, index_name: str, id: str):
        index_name = index_name.lower()
        try:
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