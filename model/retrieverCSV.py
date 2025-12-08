from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
import pandas as pd
import os


class CsvQAVectorDB:
    def __init__(self, db_path="./db/faiss_csv", model_name="text-embedding-3-large"):
        self.db_path = db_path
        self.embeddings = OpenAIEmbeddings(model=model_name)
        self.vs = None

    def build_from_csv(self, csv_path: str, save=True, encoding="utf-8-sig"): 
        df = pd.read_csv(csv_path, encoding=encoding)
        # 필수 컬럼 확인
        for col in ["question", "answer", "consideration"]:
            if col not in df.columns:
                raise ValueError(f"CSV에 '{col}' 컬럼이 필요합니다.")

        docs = []
        for i, row in df.iterrows():
            q = str(row["question"]).strip()
            a = str(row["answer"]).strip()
            c = str(row["consideration"]).strip()
            if not q:
                continue
            docs.append(Document(
                page_content=q,
                metadata={"row_id": int(i), "answer": a, "consideration": c}
            ))

        self.vs = FAISS.from_documents(docs, self.embeddings)
        if save:
            os.makedirs(self.db_path, exist_ok=True)
            self.vs.save_local(self.db_path)

    def load(self):
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"벡터DB가 없습니다: {self.db_path} (먼저 build_from_csv 실행)")
        self.vs = FAISS.load_local(self.db_path, self.embeddings, allow_dangerous_deserialization=True)

    def ensure_loaded(self):
        if self.vs is None:
            self.load()

    def search_top1(self, query: str):
        """유사 질문 Top-1. 없으면 None."""
        self.ensure_loaded()
        results = self.vs.similarity_search_with_score(query, k=1)
        if not results:
            return None

        doc, score = results[0]
        return {
            "question": doc.page_content,
            "answer": doc.metadata.get("answer", ""),
            "consideration": doc.metadata.get("consideration", ""),
            "row_id": doc.metadata.get("row_id"),
            "score": float(score)
        }


if __name__ == "__main__":
    
    CSV_PATH = "kin_crawling2.csv"
    DB_PATH  = "db/faiss_csv"

    print(f"[ENV] OPENAI_API_KEY set: {'OPENAI_API_KEY' in os.environ}")
    db = CsvQAVectorDB(db_path=DB_PATH)

    index_file = os.path.join(DB_PATH, "index.faiss")
    if not (os.path.exists(DB_PATH) and os.path.exists(index_file)):
        print("[INFO] Building FAISS index from CSV ...")
        db.build_from_csv(CSV_PATH)  # 처음 한 번만 임베딩 생성
        print(f"[INFO] Saved to {DB_PATH}")
    else:
        print("[INFO] Loading existing FAISS index ...")
        db.load()
        print(f"[INFO] Loaded from {DB_PATH}")

    # 간단 확인용 질의
    #test_query = "일상생활배상책임보험에서 상대방이 현금 요구하면 가능한가요?"
    #top1 = db.search_top1(test_query)
    #print("[TOP1]", top1)
