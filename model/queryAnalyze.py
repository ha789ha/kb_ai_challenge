
from model.generation import Gpt
from typing import Dict, Any
import json

class QueryAnalyzer:
    
    def __init__(self):
        self.gpt = Gpt()
        self.prompt_template = """
당신은 금융 소비자 권익 보호 전문가입니다. 
제공된 판례와 전문가 상담 QA 쌍을 기반으로 사용자의 금융 관련 문의를 분석하여 핵심 쟁점을 파악해주세요.

#중요사항
쟁점과 고려사항은 1개부터 여러 개까지 상황에 따라 유동적으로 작성
- 불필요한 내용으로 개수를 맞추지 마세요
- 실질적으로 중요한 내용만 포함하세요
- 정중한 말투면서도, 사용자가 이해할 수 있도록 알기 쉽게 적어주세요

# 실제 분석 요청
사용자 문의: {user_query}
판례: {case_summary}
전문가 상담 QA : {QA_summary}

아래 예시를 참고하여 다음 JSON 형식으로 정확히 응답해주세요:
{{
    "overview": "문의를 한 문장으로 요약",
    "issues": [
        "판례를 기반으로 파악되는 핵심 법적/제도적 쟁점들을 나열"
    ],
    "considerations": [
        "판례와 비교하여 사건 해결에 필요한 추가 확인사항들을 질문 형태로 나열"
    ]
}}

#예시
input: 
사용자 문의: 온라인 강의 수강신청했는데, 갑자기 회사가 폐업하고 연락이 안 돼요 ㅠㅠ 환급받고 싶어요
판례: 
1. 쟁점 - 이커머스 교육 업체 대표자의 사망으로 인해 계약 이행이 불가능한 상태에서 소비자에게 귀책사유가 없는 경우, 결제 수단과 절차에 따라 환불 가능한지 여부
2. 결과 요약 - 소비자들은 수백만 원 상당의 온라인 교육을 결제했지만,서비스가 제공되지 않아 계약 해지 및 환불을 요구. 피해자 다수가 모여 한국소비자원과 결제대행사(PG사)를 통해 협의가 이뤄졌고, 최종적으로 342명의 피해자에게 총 12억 원 환불이 이루어짐.
3. 관련 약관 또는 법률 - 사업자의 사실상 폐업 상태임에도 불구하고 여신전문금융업법 상 결제대행사의 법적책임을 강조하여 소비자 피해 회복 
4. 특이 사항 - 동일한 소비자 피해에 대한 일괄 구제로 효율적인 분쟁 해결 도모

output:
{{
    "overview": "문의해주신 사건은 연락두절로 중단된 온라인 교육 계약대금 환급 사건으로 확인됩니다.",
    "issues": [
        "계약 이행이 불가능한 상태에서 고객님에게 귀책사유가 없는 경우, 결제 수단과 절차에 따라 환불 가능성이 있음",
        "피해자 다수가 함께 대응하면 협상력이 커짐 (소비자원, PG사 중재 등)"
    ],
    "considerations": [
        "업체가 일방적으로 서비스를 중단하고 연락이 두절되었나요?",
        "결제가 PG사나 카드사 등을 통해 이루어졌나요?",
        "동일한 피해를 입은 소비자가 더 있나요?"
    ]
}}

"""
    
    #def analyze_query(self, user_query: str, case_summary: str) -> Dict[str, Any]:
    def analyze_query(self, user_query: str, case_summary: str, QA_summary: str = ""):
        # None 방어
        if QA_summary is None:
            QA_summary = ""
        prompt = self.prompt_template.format(user_query=user_query, case_summary=case_summary,QA_summary=QA_summary)
        system_prompt = "당신은 금융 소비자 권익 보호 전문가입니다. 고려할 질문은 정중한 말투면서도, 사용자가 이해할 수 있도록 간결하고 알기 쉽게 적어주세요. JSON 형식으로 정확히 응답해주세요."
        
        try:
            analysis_result = self.gpt.generate(system_prompt, prompt)
            
            # JSON 파싱 시도
            try:
                parsed_analysis = json.loads(analysis_result)
                return {
                    "original_query": user_query,
                    "analysis": parsed_analysis,
                    "success": True
                }
            except json.JSONDecodeError:
                # JSON 파싱 실패 시 원본 텍스트 반환
                return {
                    "original_query": user_query,
                    "analysis": analysis_result,  # 원본 텍스트
                    "success": False,
                    "error": "JSON 파싱 실패"
                }
                
        except Exception as e:
            return {
                "original_query": user_query,
                "analysis": f"생성 중 오류 발생: {str(e)}",
                "processed_query": user_query,
                "success": False,
                "error": str(e)
            }

