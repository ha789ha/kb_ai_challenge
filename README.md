# 📌 단계별 멀티 에이전트 기반 금융 분쟁 민원 작성 어시스턴트


## 📌 Project Info

- **프로젝트 기간:** 2025.07.07 ~ 2025.09.10
  
- **공모전:** [KB AI Challenge](https://kb-aichallenge.com/)
  
- **프로젝트 목적:** 비전문가도 금융 분쟁 민원을 쉽게 작성할 수 있도록 멀티 에이전트가 판례 검색부터 보고서 생성까지 단계별로 자동 지원하는 AI 민원 작성 어시스턴트 개발

## 프로젝트 배경 및 목표
- 금융감독원에서는 금융 분쟁 해결을 위해 분쟁조정기구를 설피하고 있으나 방대한 유사 판례를 분석하고 민원 작성을 하는데 부담감을 느낌
- 기존 검색 시스템도 키워드 방식으로 이루어져 서술형 질의의 의미를 정확히 처리하지 못함
- 이에 따라 역할 특화 에이전트 구조를 통해 질의 재작성, 유사판례검색, 쟁점도출, 최종보고서생성 등을 단계적으로 자동화하는 시스템 기획

## 팀원 구성

<div align="center">

| **이하준** | **전현아** |
| :--------: | :--------: |
| <a href="https://github.com/ha789ha"><img src="https://github.com/user-attachments/assets/12001451-71f2-4341-8f49-1405be1a2fd0" height="150" width="150" style="border-radius: 50%;"/></a><br/>[@ha789ha](https://github.com/ha789ha) | <a href="https://github.com/HyunaJ"><img src="https://github.com/user-attachments/assets/7ed446d7-fd84-43d8-9f8e-8fd86420270a" height="150" width="150" style="border-radius: 50%;"/></a><br/>[@HyunaJ](https://github.com/HyunaJ) |

</div>

## 1.  개발 환경
- **Frontend:** Streamlit  
- **Backend:** Python  
- **AI Framework:** LangChain  
- **LLM:** OpenAI `gpt-4o` 
- **Embedding Model:** OpenAI `text-embedding-3-small` 
- **Vector DB:** FAISS
- **협업 툴:** Notion

## 2. 💡 핵심 기능 (Key Features)

### 1️⃣ RAG 기반 판례 검색 및 질의 최적화 (Rewriting & Search)

- **Query Rewriting:**  
  모호한 질문을 **'상황 - 문제 - 질문 - 키워드'**의 법률적 구조로 자동 변환하여 검색 정확도 향상
- **Vector Search:**  
  방대한 판례 PDF를 요약 후 임베딩하여, 단순 키워드 매칭이 아닌 **의미론적 유사도 기반** 판례 검색 제공

### 2️⃣ 대화형 쟁점 진단 에이전트 (Interactive Issue Diagnosis)

- **Dynamic Follow-up:**  
  검색된 판례와 사용자 상황을 비교하여, 법적 판단에 필요한 **쟁점** 을 파악하고 대화를 통해 사실관계 파악 유도

### 3️⃣ 맞춤형 민원 보고서 자동 생성 (Automated Report Generation)

- **Structured Output:**  
  수집된 정보를 기반으로 **[사건 요약 → 유사 판례 비교 → 예상 결과/법적 판단 근거]** 구조의 완결된 보고서 자동 생성

## 3. 역할 분담

### 이하준
- Langchain을 활용한 검색 -> 진단 -> 보고서 생성으로 이루어지는 단계별 에이전트 파이프라인 설계
- Faiss 기반의 벡터 DB 구축 및 정확도 향상을 위한 Query Rewriting 알고리즘 설계
  
<br>
    
### 전현아
- 데이터 크롤링을 통해 금융감독원 판례 및 실제 전문가들의 상담 데이터셋 구축
- 최신화 된 법률 정보를 실시간으로 보완하기 위해 Google Search API를 연동한 웹 검색 에이전트 구현

<br>

## 4. 프로젝트 구조
```bash
bash
LawChain/
├── app.py                  # Streamlit 메인 실행 파일 (Front-end & Agent Orchestration)
├── crawling_data/          # 금융감독원 판례 및 네이버 eXpert 크롤링 데이터 수집
├── pre_processing/         # 데이터 정제 및 Query Rewriting 로직
├── summary/                # 판례 요약(Summarizing Agent) 및 텍스트 데이터 처리
├── db/                     # 정형 데이터(Metadata) 저장소
├── faiss/                  # 의미 기반 검색을 위한 벡터 데이터베이스 (Vector DB)
├── model/                  # LLM 모델 설정 및 API 핸들러
├── report_layout/          # 최종 민원 보고서 생성 템플릿 및 레이아웃 설정
├── .streamlit/             # Streamlit UI/UX 테마 설정 (config.toml)
└── requirements.txt        # 프로젝트 의존성 라이브러리 목록
```
## 5. 아키텍처


