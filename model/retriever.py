from langchain_openai import OpenAIEmbeddings
import faiss
import numpy as np
#from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from PyPDF2 import PdfReader
from tqdm import tqdm
from typing import List
import json
from langchain.docstore.document import Document




class EmbeddingModel:
    def __init__(self, top_k=3, openai_api_key=None, db_path="./db/faiss", summary_folder="./summary"):
        self.top_k = top_k
        self.db_path = db_path
        self.summary_folder = summary_folder
        self.model = OpenAIEmbeddings(model='text-embedding-3-large')

    def load_json_summaries(self) -> List[Document]:
        """summary 폴더 안의 모든 JSON 파일을 Document 형태로 로드"""
        documents = []
        for filename in tqdm(os.listdir(self.summary_folder), desc="Loading JSON summaries"):
            if not filename.lower().endswith(".json"):
                continue

            filepath = os.path.join(self.summary_folder, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = json.load(f)

                # JSON 전체를 문자열로 변환하여 embedding
                text_content = json.dumps(content, ensure_ascii=False)
                documents.append(Document(
                    page_content=text_content,
                    metadata={"source": filename}
                ))
            except Exception as e:
                print(f"{filename} 로드 실패: {e}")

        return documents

    def build_or_load_vectorstore(self):
        """벡터스토어 로드 또는 생성"""
        if os.path.exists(self.db_path):
            return FAISS.load_local(self.db_path, self.model, allow_dangerous_deserialization=True)

        documents = self.load_json_summaries()
        if not documents:
            raise ValueError(f"{self.summary_folder} 폴더에서 불러올 JSON 문서가 없습니다.")

        vector_store = self.batch_embed_documents(documents, self.model)
        vector_store.save_local(self.db_path)
        return vector_store

    def retrieve_json_summaries(self, query: str) -> List[dict]:
        """쿼리와 가장 유사한 JSON 요약 k개 반환"""
        vector_store = FAISS.load_local(self.db_path, self.model, allow_dangerous_deserialization=True)
        results = vector_store.similarity_search(query, k=self.top_k)

        summaries = []
        for match in results:
            try:
                filepath = os.path.join(self.summary_folder, match.metadata['source'])
                with open(filepath, 'r', encoding='utf-8') as f:
                    summaries.append(json.load(f))
            except Exception as e:
                summaries.append({"error": f"{match.metadata['source']} 읽기 실패: {str(e)}"})

        return summaries

    def batch_embed_documents(self, documents: List[Document], embedding_model, batch_size=500):
        """대용량 문서를 배치 단위로 임베딩 후 벡터스토어 생성"""
        all_vectors = []
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i+batch_size]
            print(f'Embedding batch {i//batch_size + 1}: {len(batch)} documents')
            vector_store = FAISS.from_documents(batch, embedding_model)
            all_vectors.append(vector_store)

        merged_store = all_vectors[0]
        for store in all_vectors[1:]:
            merged_store.merge_from(store)
        return merged_store