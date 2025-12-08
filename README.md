# 📌 단계별 멀티 에이전트 기반 금융 분쟁 민원 작성 어시스턴트


## 📘 프로젝트 소개

본 프로젝트는 **서술형 금융 민원을 자동 분석하여 유사 판례 검색 → 쟁점 도출 → 보고서 생성까지 전 과정을 자동화**하는
멀티 에이전트 기반 **AI 민원 작성 어시스턴트**입니다.

> 법률 지식이 부족한 일반인을 위해, “질의 재작성 → 판례 검색 → 쟁점 파악 → 보고서 생성”을 전문화된 에이전트가 단계별로 수행하도록 설계했습니다.

<br>

## 📅 Project Info

* **기간:** 2025.07.07 ~ 2025.09.10
* **공모전:** KB AI Challenge
* **목표:** 비전문가도 금융 분쟁 민원을 쉽게 제출할 수 있도록, 검색·진단·보고서를 자동 생성하는 상담형 AI 서비스 구축

<br>

---

## 👥 팀원 구성

<div align="center">

|                                                                                                                **이하준**                                                                                                                |                                                                                                               **전현아**                                                                                                              |
| :-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------: | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------: |
| <a href="https://github.com/ha789ha"><img src="https://github.com/user-attachments/assets/12001451-71f2-4341-8f49-1405be1a2fd0" height="150" width="150" style="border-radius: 50%;"/></a><br/>[@ha789ha](https://github.com/ha789ha) | <a href="https://github.com/HyunaJ"><img src="https://github.com/user-attachments/assets/7ed446d7-fd84-43d8-9f8e-8fd86420270a" height="150" width="150" style="border-radius: 50%;"/></a><br/>[@HyunaJ](https://github.com/HyunaJ) |

</div>

<br>

---

## 🛠️ 1. 개발 환경

* **Frontend:** Streamlit
* **Backend:** Python
* **AI Framework:** LangChain
* **LLM:** OpenAI `gpt-4o`
* **Embedding Model:** OpenAI `text-embedding-3-small`
* **Vector DB:** FAISS
* **협업 툴:** Notion, GitHub

<br>

---

## 💡 2. 핵심 기능 (Key Features)

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

---

## 👤 3. 역할 분담

### **이하준**

* 검색 → 쟁점 진단 → 보고서 생성으로 이어지는 **멀티 에이전트 파이프라인 설계**
* FAISS 기반 벡터 DB 구축 및 Query Rewriting 알고리즘 개발

### **전현아**

* 금융감독원/전문가 상담 데이터 **크롤링 및 데이터셋 구축**
* Google Search API 기반 **웹 검색 에이전트 개발**

<br>

---

## 📁 4. 프로젝트 구조

```bash
LawChain/
├── app.py                  # Streamlit 메인 실행 파일
├── crawling_data/          # 판례·상담 데이터 크롤링
├── pre_processing/         # 전처리 & Query Rewriting
├── summary/                # 판례 요약 에이전트
├── db/                     # 메타데이터 저장소
├── faiss/                  # Vector DB
├── model/                  # LLM 핸들러
├── report_layout/          # 민원 보고서 템플릿
└── requirements.txt
```

<br>

---

## 🏗️ 5. Architecture Overview

<div align="center">
  <img src="https://github.com/user-attachments/assets/3f91c6fd-25b4-4c05-94b0-2f9dc9dc4703" width="85%" style="border-radius: 12px; border: 1px solid #e5e5e5;" />
</div>

<br>

### 🔹 1) Retrieval

질의 재구성 → 임베딩 매칭 → 유사 판례 Top-K 검색

### 🔹 2) Issue Diagnosis

대화를 통해 누락 정보 파악 → 핵심 쟁점 자동 도출

### 🔹 3) Report Generation

수집 정보 + 판례 기반 → 민원 보고서 형태로 구조화 생성

<br>

---

## 🎬 6. 시연 영상

<div align="center">
  <a href="https://github.com/user-attachments/assets/944bc76a-6dce-4d6d-9ccc-93200d032a5b">
    <img src="https://github.com/user-attachments/assets/944bc76a-6dce-4d6d-9ccc-93200d032a5b" 
         width="80%" 
         style="border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); position: relative;" />
  </a>
</div>

<br>

---
