from model.retriever import EmbeddingModel
from model.generation import Gpt
from model.queryAnalyze import QueryAnalyzer
from model.finalgen import FinalGen
from model.google import get_google_results,get_keywords_from_query
from model.retrieverCSV import * # 전문가 QA 추가


import base64
import os
import json
import pickle
import uuid
import re
from PyPDF2 import PdfReader
import time
import streamlit as st
from openai import OpenAI

# 모델
embedding = EmbeddingModel()
generation_model = Gpt()
analyzer = QueryAnalyzer()
final_gen = FinalGen()

DB_PATH = "Kb/db/faiss_csv"
CSV_PATH = "Kb/kin_crawling2.csv"

db = CsvQAVectorDB(db_path=DB_PATH)

# 프롬프트
system_prompt = '당신은 유능한 법률 전문가로 모든 대답은 한국어로 하도록 하세요'

# 수정 
#def rewrite_query(query):
def rewrite_query(query: str, google_summary: str) -> str:
    rewrite_prompt = f'''
        당신은 법률 상담 어시스턴트입니다.

        아래에 사용자가 작성한 민원 글이 주어집니다.  
        이 민원 글에서 **판례 검색에 필요한 핵심 정보를 추출하여 Structured Query 형태로 재구성하세요.**  
        반드시 다음과 같은 구조를 지켜서 작성하세요:

        1. 상황(Situation): 민원이 발생하게 된 배경과 사건 요약
        2. 문제(Problem): 민원인이 궁금해하는 핵심 쟁점
        3. 질문(Question): 판례 검색을 위한 명확한 질의
        4. 키워드(Keywords): 검색에 필요한 핵심 용어들 (콤마로 구분)

        민원 글:
        """
        {query}
        """
        
        구글 검색 내용:
        """
        {google_summary}
        """

        Output Example:
        1. 상황(Situation): [여기에 상황 요약]
        2. 문제(Problem): [여기에 문제 요약]
        3. 질문(Question): [여기에 판례 검색용 질의]
        4. 키워드(Keywords): [키워드1, 키워드2, 키워드3, ...]

        중요: 내용 축약이나 누락 없이 민원에서 필요한 정보를 모두 포함하세요. 감정적 표현은 제외하고, 사건/사실/질문 중심으로 정리하세요.


        '''
        
    rewrite_prompt = generation_model.generate(system_prompt, rewrite_prompt)
        
    return rewrite_prompt

def first_generation_prompt(re_query, text):
    prompt = f'''
    아래의 판결문은 회사와 분쟁을 겪고 있는 민원인과 가장 관련 있는 것으로 검색된 판례와 민원인의 민원글입니다. 
    민원글의 상황과 판결문의 상황을 유사도를 0 ~ 100까지 점수로 판결하고 유사점과 차이점을 말하도록 하세요.
    
    
    ## 민원글
    {re_query}
    
    ## 판결문
    {text}

'''
    return prompt

def chat_message(role, content, delay=0.5):
    with st.chat_message(role):
        st.markdown(content)
    time.sleep(delay)
    
    
def render_case_summaries(case_summaries):
    case_cards_html = ""
    for idx, case in enumerate(case_summaries, start=1):
        issue = case.get('쟁점', '')
        summary = case.get('결과 요약', '')
        laws = case.get('관련 약관 혹은 법률', [])
        notes = case.get('특이 사항', [])

        card_html = f"""
        <div class="case-card">
            <div class="case-card-title">사건 {idx}</div>
            <div class="case-section"><strong>⚖️ 쟁점</strong><br>{issue}</div>
            <div class="case-section"><strong>📄 결과 요약</strong><br>{summary}</div>
            </div>
        </div>
        """
        case_cards_html += card_html


    return case_cards_html
    
# 세션상태에 채팅 히스토리 추가
if 'consideration_idx' not in st.session_state:
    st.session_state.consideration_idx = 0
if 'answers' not in st.session_state:
    st.session_state.answers = []
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'analysis_done' not in st.session_state:
    st.session_state.analysis_done = False

# 이전 대화 내역 출력
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"], unsafe_allow_html=True)


st.markdown("""
<style>
.case-container {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
}
.case-card {
    background-color: #f9f9f9;
    border: 1px solid #ddd;
    border-radius: 10px;
    padding: 1rem;
    flex: 1 1 calc(33% - 1rem);
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    min-width: 300px;
}
.case-card-title {
    font-size: 1.2rem;
    font-weight: bold;
    margin-bottom: 0.5rem;
    color: #333;
}
.case-section {
    margin-bottom: 0.8rem;
    font-size: 0.95rem;
    line-height: 1.4;
}
.case-section ul {
    margin: 0.3rem 0 0 1.2rem;
    padding: 0;
}
</style>
""", unsafe_allow_html=True)


# 첫 질문 입력 받기
if not st.session_state.analysis_done:
    if query := st.chat_input("질문을 입력하세요"):
        st.chat_message("user").markdown(query)
        st.session_state.chat_history.append({"role": "user", "content": query})
        
        #키워드 반영
        keywords = get_keywords_from_query(query,generation_model)
        print(keywords)
        # 구글 검색 결과
        google_summary = get_google_results(keywords, num_results=2)
        print(google_summary)

        # Query Rewriting & Case Summary & Analysis (실제 RAG 연결 부분)
        re_query = rewrite_query(query,google_summary)
        print('---- rewriting 완료')
        case_summary = embedding.retrieve_json_summaries(re_query)
        
        #전문가 QA 쌍 추가
        QA_summary = db.search_top1(re_query)
        print(QA_summary)

        
        analyzer_result = analyzer.analyze_query(query, case_summary[0])
        
        
        if analyzer_result['success']:
            analysis = analyzer_result["analysis"]
            overview = analysis["overview"]
            issues = analysis['issues']
            considerations = analysis['considerations']

        # 유사 top 3
        combined_html = render_case_summaries(case_summary)
        
        with st.chat_message("assistant"):
            st.markdown(combined_html, unsafe_allow_html=True)

        # chat_history에 한번에 저장
        st.session_state.chat_history.append({"role": "assistant", "content": combined_html})


        # 첫 고려사항 질문
        first_consideration = analysis['considerations'][0]
        st.chat_message("assistant").markdown(first_consideration)
        st.session_state.chat_history.append({"role": "assistant", "content": first_consideration})

        # 분석 결과 저장
        st.session_state.analysis = analysis
        st.session_state.analysis_done = True

# 고려사항 멀티턴 Q&A 진행
elif st.session_state.consideration_idx < len(st.session_state.analysis['considerations']):
    user_reply = st.chat_input("답변을 입력하세요")
    if user_reply:
        st.chat_message("user").markdown(user_reply)
        st.session_state.chat_history.append({"role": "user", "content": user_reply})
        st.session_state.answers.append(user_reply)

        st.session_state.consideration_idx += 1
        if st.session_state.consideration_idx < len(st.session_state.analysis['considerations']):
            next_consideration = st.session_state.analysis['considerations'][st.session_state.consideration_idx]
            st.chat_message("assistant").markdown(next_consideration)
            st.session_state.chat_history.append({"role": "assistant", "content": next_consideration})
        else:
            with st.spinner('모든 고려사항 답변이 완료되었습니다! 보고서를 생성합니다.'):
                user_responses = final_gen.process_user_responses(
                    st.session_state.analysis['considerations'],
                    st.session_state.answers
                )

                result = final_gen.generate_report_only(
                    st.session_state.chat_history[0]['content'],
                    st.session_state.analysis['overview'],
                    st.session_state.analysis,
                    user_responses
                )

                with open('final_report.pdf', 'rb') as file:
                    file_bytes = file.read()
                    
                    
                    
            st.download_button(
                label = '최종 보고서 다운로드',
                data = file_bytes,
                file_name = '최종보고서.pdf',
                mime='application/pdf'
            )
                    
    
    
    
    