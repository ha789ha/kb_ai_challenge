import json
import os
from model.generation import Gpt
from tqdm import tqdm
from PyPDF2 import PdfReader
from json.decoder import JSONDecodeError

# 시스템 프롬프트
prompt = '''
    당신은 법률 전문가로 금융분쟁조정위원회에서 발행한 조정결정서의 내용을 요약해야 합니다.
'''
model = Gpt()

folder_path = 'Kb/pdf_documents'
output_folder = 'Kb/summary'

# summary 폴더가 없으면 생성
os.makedirs(output_folder, exist_ok=True)

for filename in tqdm(os.listdir(folder_path)):
    if not filename.lower().endswith('.pdf'):
        continue  # PDF 파일만 처리

    output_filename = os.path.splitext(filename)[0] + '.json'
    output_path = os.path.join(output_folder, output_filename)

    # 이미 요약된 파일이 있다면 건너뛰기
    if os.path.exists(output_path):
        print(f"이미 처리된 파일입니다: {output_filename}")
        continue

    file_path = os.path.join(folder_path, filename)
    reader = PdfReader(file_path)
    text = "\n".join(page.extract_text() or "" for page in reader.pages)

    user_prompt = f'''
    아래 원본 문서를 읽고, 각 항목에 맞게 간결하고 핵심만 요약하세요.  
    각 항목의 의미는 다음과 같습니다:

    1. 쟁점: 핵심적으로 판단해야 하는 법적 또는 사실적 쟁점  
    2. 결과 요약: 조정기관이 확인한 사실과 그에 따른 판단 결과를 핵심 근거와 함께 요약  
    3. 관련 약관 혹은 법률: 본 사건에 적용된 약관 조항이나 법률 명칭을 나열  
    4. 특이 사항: 사건에서 특히 주목할 만한 점이나 참고할 사항

    ## 원본 문서  
    {text}

    ## 요약문 예시 (JSON 형식)
    {{
    "쟁점": "‘경막외신경감압(성형)술’이 보험약관 수술분류표상 ‘신경관혈수술’(2종 수술)에 해당하는지 여부",
    "결과 요약": "금융분쟁조정위원회는 해당 시술이 카테터를 이용한 비관혈적 시술로 1종 수술에 해당한다고 판단하여 신청인의 청구를 기각함",
    "관련 약관 혹은 법률": [
        "무배당다이렉트케어프리보험 수술특약 약관 제13조(수술의 정의와 장소)",
        "제14조(보험금 지급사유)",
        "별표4 수술분류표 (57번 ‘신경관혈수술’, 87번 ‘카테터 이용 수술’)"
    ],
    "특이 사항": [
        "시술 방식(카테터 삽입 후 약물 주입)이 관혈적 수술(절개 및 절제 등)과 다르다는 점을 들어 2종 수술로 인정할 수 없다고 판단함",
        "전문의 자문을 통해 비수술적 치료로 평가됨"
    ]
    }}
    '''

    try:
        result = model.generate(prompt, user_prompt)
        json_result = json.loads(result)
    except JSONDecodeError as e:
        print(f"✗ JSON 파싱 실패: {filename} → 건너뜀\n에러: {e}")
        continue
    except Exception as e:
        print(f"✗ 예기치 않은 오류 발생: {filename} → 건너뜀\n에러: {e}")
        continue

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(json_result, f, ensure_ascii=False, indent=4)
        print(f"✓ 저장 완료: {output_filename}")
