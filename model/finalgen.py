import time
import pdfkit
from jinja2 import Template
from model.generation import Gpt
from typing import Dict, Any, List
import json
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfbase import pdfutils
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import os
from datetime import datetime

class FinalGen:
    
    def __init__(self):
        self.gpt = Gpt()
        self._setup_korean_font()
        
    def _setup_korean_font(self):
        
        #폰트를 바꾸고 싶다면.....
        try:
            # 시스템에 있는 한글 폰트 등록 
            font_paths = [
                '/usr/share/fonts/truetype/nanum/NanumGothic.ttf'
            ]
            
            for font_path in font_paths:
                if os.path.exists(font_path):
                    pdfmetrics.registerFont(TTFont('Korean', font_path))
                    self.korean_font = 'Korean'
                    return
            
            
        except Exception as e:
            self.korean_font = 'Helvetica'
            print(f"폰트 설정 오류: {str(e)}")
        
    def collect_user_responses(self, considerations: List[str]) -> Dict[str, str]:
        """고려사항 리스트 반환 (Streamlit에서 처리)"""
        # Streamlit에서 사용할 고려사항 반환
        return {f"질문{i+1}": consideration for i, consideration in enumerate(considerations)}
    
    def process_user_responses(self, considerations: List[str], responses: List[str]) -> Dict[str, str]:
        """사용자 응답을 처리해서 구조화"""
        user_responses = {}
        for i, (consideration, response) in enumerate(zip(considerations, responses)):
            user_responses[f"질문{i+1}"] = {
                "question": consideration,
                "answer": response
            }
        return user_responses
    
    def generate_case_report_content(self, 
                                   original_query: str, 
                                   case_summary: str, 
                                   analysis_result: Dict[str, Any], 
                                   user_responses: Dict[str, str]) -> Dict[str, Any]:
        """사건 정리서 내용 생성 - JSON 형태로 반환"""
        
        # 사용자 응답을 텍스트로 변환
        responses_text = ""
        for key, value in user_responses.items():
            responses_text += f"Q: {value['question']}\nA: {value['answer']}\n\n"
        
        system_prompt = """당신은 경험 많은 변호사로서 법적 사건을 체계적으로 분석하고 정리하는 전문가입니다. JSON 형식을 정확히 지켜서 응답헤주세요"""
        prompt = f"""
        당신은 경험 많은 변호사로서 법적 사건을 체계적으로 분석하고 정리하는 전문가입니다.
        제공된 정보를 바탕으로 전문적이고 구조화된 사건 분석 보고서를 작성하세요.

        # 작성 규칙
        - JSON 형식으로만 출력
        - 각 값은 간결하지만 의미가 충분히 드러나도록 문장형으로 작성
        - 각 항목은 짧은 문장 한두 개로 구성 (예: "- ~~~ 사건입니다", "- ~~ 이렇습니다")
        - 불필요한 서술, 반복, 감정 표현 제외
        - 핵심 법적·사실적 정보만 포함
        - 각 항목은 2~4개 문장으로 제한
        - "공통점_차이점"은 "공통점"과 "차이점"을 별도의 key로 분리

        # 분석 요청
        원본 사건 내용: {original_query}
        유사 판례 요약: {case_summary}
        1차 분석 결과: {analysis_result.get('overview', 'N/A')}
        추가 확인된 정보: {responses_text}

        # 출력 형식
        {{
            "판례기반_내_사건_정리": [
                "2023년 12월 26일 차대차 사고로 다발성 골절이 발생한 사건입니다.",
                "응급수술 도중 심정지와 뇌손상으로 식물인간 상태로 전환되었습니다.",
                "대학병원에서 3개월간 치료받은 뒤 요양병원으로 전원하였고 익일 사망했습니다.",
                "사망진단서에는 ‘병사’로 기재되어 보험금 지급이 거절된 상태입니다."
            ],
            "유사_판례_정리": [
                "유사 판례에서는 ~~이 쟁점이었으며 교통사고 후 장기간 치료 중 사망한 경우 사고사로 인정하였습니다.",
            ],
            "공통점": [
                "두 사건 모두 교통사고 후 치료 과정에서 사망이 발생한 점이 공통적입니다."
            ],
            "차이점": [
                "유사 판례는 사망진단서에 사고사가 명기된 반면, 본 사건은 병사로 기록되어 보험금이 거절되었습니다."
            ],
            "고려해봐야_할_쟁점": [
                "사고와 사망 간 인과관계 입증 방법이 주요 쟁점입니다.",
                "사망진단서 내용 변경 절차 및 필요 서류 확보가 필요합니다."
            ],
            "예상_결과": [
                "의료기록과 부검소견으로 인과관계를 입증하면 승소 가능성이 높습니다.",
                "사망원인 정정 청구 및 금융감독원 분쟁조정위 신청이 유리한 전략입니다."
            ]
        }}

        주의:
        - JSON 외의 다른 텍스트는 절대 포함하지 마십시오.
        """

        try:
            response = self.gpt.generate(system_prompt, prompt)
            
            # JSON 파싱 시도
            try:
                sections = json.loads(response)
                return {
                    "success": True,
                    "sections": sections,
                    "raw_response": response
                }
            except json.JSONDecodeError as e:
                return {
                    "success": False,
                    "sections": {
                        "판례기반_내_사건_정리": ["JSON 파싱 실패로 내용을 추출할 수 없습니다."],
                        "유사_판례_정리": ["JSON 파싱 실패로 내용을 추출할 수 없습니다."], 
                        "공통점": ["JSON 파싱 실패로 내용을 추출할 수 없습니다."],
                        "차이점": ["JSON 파싱 실패로 내용을 추출할 수 없습니다."],
                        "고려해봐야_할_쟁점": ["JSON 파싱 실패로 내용을 추출할 수 없습니다."],
                        "예상_결과": ["JSON 파싱 실패로 내용을 추출할 수 없습니다."]
                    },
                    "raw_response": response,
                    "error": f"JSON 파싱 실패: {str(e)}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "sections": {
                    "판례기반_내_사건_정리": ["내용 생성 실패"],
                    "유사_판례_정리": ["내용 생성 실패"], 
                    "공통점": ["내용 생성 실패"],
                    "차이점": ["내용 생성 실패"],
                    "고려해봐야_할_쟁점": ["내용 생성 실패"],
                    "예상_결과": ["내용 생성 실패"]
                },
                "raw_response": None,
                "error": f"보고서 내용 생성 중 오류 발생: {str(e)}"
            }
    

    
    def create_pdf_report(self, 
                         sections: Dict[str, str],
                         original_query: str,
                         analysis_overview: str = None,
                         filename: str = None) -> Dict[str, Any]:
        """PDF 보고서 생성 - 결과 정보 반환"""
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"사건분석보고서_{timestamp}.pdf"

        if not filename.endswith('.pdf'):
            filename += '.pdf'
        
        # PDF 문서 생성
        doc = SimpleDocTemplate(filename, pagesize=A4)
        story = []
        
        # 스타일 설정
        styles = getSampleStyleSheet()
        
        # 한글 폰트 적용한 스타일 생성
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontName=self.korean_font,
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontName=self.korean_font,
            fontSize=14,
            spaceAfter=12,
            spaceBefore=20
        )
        
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontName=self.korean_font,
            fontSize=10,
            spaceAfter=12,
            alignment=TA_JUSTIFY
        )
        
        # 제목
        story.append(Paragraph("법적 사건 분석 보고서", title_style))
        story.append(Spacer(1, 20))
        
        # 사건 개요
        story.append(Paragraph("📋 사건 개요", heading_style))
        #story.append(Paragraph(original_query[:500] + "..." if len(original_query) > 500 else original_query, body_style))
        story.append(Paragraph(analysis_overview, body_style))
        story.append(Spacer(1, 20))
        
        # 각 섹션 추가
        section_titles = {
            "판례기반_내_사건_정리": "판례기반 내 사건 정리",
            "유사_판례_정리": "유사 판례 정리",
            "공통점_차이점": "공통점 & 차이점",
            "고려해봐야_할_쟁점": "고려해봐야 할 쟁점",
            "예상_결과": "예상 결과"
        }
        
        for key, title in section_titles.items():
            if key in sections and sections[key].strip():
                story.append(Paragraph(title, heading_style))
                story.append(Paragraph(sections[key], body_style))
                story.append(Spacer(1, 15))
        
        # 생성 정보
        story.append(Spacer(1, 30))
        story.append(Paragraph(f"생성일시: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M')}", body_style))
        
        # PDF 생성
        try:
            doc.build(story)
            return {
                "success": True,
                "filename": filename,
                "message": f"PDF 보고서가 생성되었습니다: {filename}"
            }
        except Exception as e:
            return {
                "success": False,
                "filename": None,
                "message": f"PDF 생성 중 오류: {str(e)}"
            }
    
    def _format_list(self, items: List[str]) -> str:
        """리스트를 텍스트로 포맷팅"""
        if not items:
            return "없음"
        
        formatted = ""
        for i, item in enumerate(items, 1):
            formatted += f"{i}. {item}\n"
        return formatted.strip()
    
    def run_full_process(self, 
                        original_query: str, 
                        case_summary: str, 
                        analysis_result: Dict[str, Any],
                        user_responses: Dict[str, str] = None) -> Dict[str, Any]:
        """전체 프로세스 실행 - Streamlit 호환"""
        
        # user_responses가 없으면 빈 딕셔너리 사용
        if user_responses is None:
            user_responses = {}
        
        # 보고서 내용 생성
        content_result = self.generate_case_report_content(
            original_query, 
            case_summary, 
            analysis_result, 
            user_responses
        )
        
        # 생성 성공 여부 확인
        if content_result["success"]:
            sections = content_result["sections"]
            # PDF 생성
            pdf_result = self.create_pdf_report(sections, original_query,analysis_overview=analysis_result.get("overview", ""))
        else:
            # 내용 생성 실패 시 기본 섹션으로 PDF 생성 시도
            sections = content_result["sections"]
            pdf_result = self.create_pdf_report(sections, original_query,analysis_overview=analysis_result.get("overview", ""))
        
        # 전체 결과 반환
        return {
            "content_generation": content_result,
            "sections": sections,
            "pdf_result": pdf_result,
            "user_responses": user_responses,
            "considerations": analysis_result.get('considerations', []),
            "overall_success": content_result["success"] and pdf_result["success"]
        }
    
    def generate_report_only(self,
                           original_query: str, 
                           case_summary: str, 
                           analysis_result: Dict[str, Any],
                           user_responses: Dict[str, str]) -> Dict[str, Any]:
        """사용자 응답을 받은 후 보고서만 생성 (Streamlit용)"""
        
        # 보고서 내용 생성
        content_result = self.generate_case_report_content(
            original_query, 
            case_summary, 
            analysis_result, 
            user_responses
        )
        
        # 생성 성공 여부 확인
        if content_result["success"]:
            sections = content_result["sections"]
        else:
            sections = content_result["sections"]
        
        # PDF 생성
        with open('Kb/report/report.html', 'r', encoding='utf-8') as f:
            html_template = f.read()
            

        template = Template(html_template)
        json_str = json.dumps(sections, ensure_ascii=False)

        rendered_html = template.render(json_data=json_str)

        with open('final_report.html', 'w', encoding='utf-8') as f:
            f.write(rendered_html)
        
        print('----')
        options={'page-size':'A5'}

        pdfkit.from_file('final_report.html', 'final_report.pdf', options=options)
        


