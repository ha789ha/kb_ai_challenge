<br>

# ⚖️ LawChain — AI 금융 분쟁 민원 도우미

<br>

## 📘 프로젝트 소개

**LawChain**은 금융 분쟁 해결에 어려움을 겪는 사용자를 위해, 복잡한 민원 처리 과정을 돕는 **AI 법률 어시스턴트**입니다.

사용자의 상황을 바탕으로 **유사 판례를 검색** 후 챗봇과의 대화를 통해 **법적 쟁점**을 진단합니다. 최종적으로는 이를 통합한 **민원 작성 보고서**를 통해
비전문가도 금융 분쟁 민원을 직접 작성할 수 있습니다.

<br>

## 📅 Project Info

* **기간:** 2025.07.07 ~ 2025.09.10
* **공모전:** [7회 KB AI Challenge](https://kb-aichallenge.com/)

<br>

## 👥 팀원 구성

<div align="center">

|                                                                                                                **이하준**                                                                                                                |                                                                                                               **전현아**                                                                                                              |
| :-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------: | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------: |
| <a href="https://github.com/ha789ha"><img src="https://github.com/user-attachments/assets/12001451-71f2-4341-8f49-1405be1a2fd0" height="150" width="150" style="border-radius: 50%;"/></a><br/>[@ha789ha](https://github.com/ha789ha) | <a href="https://github.com/HyunaJ"><img src="https://github.com/user-attachments/assets/7ed446d7-fd84-43d8-9f8e-8fd86420270a" height="150" width="150" style="border-radius: 50%;"/></a><br/>[@HyunaJ](https://github.com/HyunaJ) |

</div>

<br>


## 🛠️ 1. 개발 환경

* **Frontend:** Streamlit
* **Backend:** Python
* **AI Framework:** LangChain
* **LLM:** OpenAI `gpt-4o`
* **Embedding Model:** OpenAI `text-embedding-3-small`
* **Vector DB:** FAISS
* **협업 툴:** Notion, GitHub

<br>


## 💡 2. 핵심 기능

### 1️⃣ RAG 기반 판례 검색 & Query Rewriting

* 사용자의 모호한 질문을 법률적 구조('상황-문제-질문-키워드')로 재작성
* 판례 PDF를 요약·임베딩하여 **유사도 검색 기반 Top-K 시스템 구축**

### 2️⃣ 대화형 쟁점 진단 에이전트

* 검색된 판례 + 사용자 상황을 비교하여
  핵심 사실 관계를 파악하고
  대화를 통해 **쟁점을 자동 정리**

### 3️⃣ 맞춤형 민원 보고서 생성

* **사건 요약 → 판례 비교 → 예상 결과**까지 포함된
  **민원 보고서 자동 생성**

<br>


## 👤 3. 역할 분담

### **이하준**

* 검색 → 쟁점 진단 → 보고서 생성으로 이어지는 **멀티 에이전트 파이프라인 설계**
* FAISS 기반 벡터 DB 구축 및 Query Rewriting 알고리즘 개발

### **전현아**

* 금융감독원/전문가 상담 데이터 **크롤링 및 데이터셋 구축**
* Google Search API 기반 **웹 검색 에이전트 개발**

<br>

## 🛠️ 4. 프로젝트 구조 및 실행

### 📂 Directory Structure

```bash
LawChain/
├── app.py                  # Streamlit 메인 실행 파일
├── crawling_data/          # 크롤링 결과 데이터 저장소 (자동 생성)
├── pre_processing/         # 데이터 수집 및 전처리 스크립트
│   ├── crawling.py         # 금융감독원 판례 크롤링
│   └── naver_crawling_2.py # 네이버 eXpert QA 크롤링
├── summary/                # 판례 요약 에이전트
├── db/                     # 메타데이터 저장소
├── faiss/                  # Vector DB 저장소
├── model/                  # LLM 및 API 설정
│   ├── generation.py       # OpenAI API 설정
│   └── google.py           # Google Search API 설정
├── report_layout/          # 민원 보고서 템플릿
└── requirements.txt        # 의존성 패키지 목록
```

### 🚀 실행 방법 

**1. 환경 설정**

```bash
# 1. Repository Clone
git clone https://github.com/ha789ha/LawChain.git
cd LawChain

# 2. Conda Environment Create & Activate
conda create -n lawchain python=3.10
conda activate lawchain

# 3. Install Dependencies
pip install -r requirements.txt
```

**2. 데이터 수집**

  * 아래 스크립트를 실행하면 `crawling_data/` 폴더에 데이터가 자동으로 수집 및 저장됩니다.

<!-- end list -->

```bash
cd pre_processing
python crawling.py          # 금융감독원 판례 수집
python naver_crawling_2.py  # 네이버 QA 데이터 수집
cd ..
```

**3. API 키 설정 (Configuration)**

  * **OpenAI API Key 설정:** `model/generation.py`

    ```python
    # model/generation.py 내부
    openai.api_key = "sk-..."  # 본인의 OpenAI Key 입력
    ```

  * **Google Search API Key 설정:** `model/google.py`

    ```python
    # model/google.py 내부
    google_api_key = "..."     # Google Search API Key 입력
    search_engine_id = "..."             # Custom Search Engine ID 입력
    ```

**4. 서비스 실행**

```bash
streamlit run app.py
```

<br>


## 🏗️ 5. Architecture Overview

<div align="center">
  <img src="https://github.com/user-attachments/assets/3f91c6fd-25b4-4c05-94b0-2f9dc9dc4703" width="100%" style="border-radius: 12px; border: 1px solid #e5e5e5;" />
</div>

<br>

### 🔹 1) Retrieval

질의 재구성 → 임베딩 매칭 → 유사 판례 Top-K 검색

### 🔹 2) Issue Diagnosis

대화를 통해 누락 정보 파악 → 핵심 쟁점 자동 도출

### 🔹 3) Report Generation

수집 정보 + 판례 기반 → 민원 보고서 형태로 구조화 생성

<br>


## 🎬 6. 시연 영상

<div align="center">
  <a href="https://github.com/user-attachments/assets/944bc76a-6dce-4d6d-9ccc-93200d032a5b">
    <img src="https://github.com/user-attachments/assets/944bc76a-6dce-4d6d-9ccc-93200d032a5b" 
         width="80%" 
         style="border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); position: relative;" />
  </a>
</div>

<br>

