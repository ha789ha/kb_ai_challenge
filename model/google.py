from model.generation import Gpt
import requests
import urllib.parse
import logging
import os
from requests.exceptions import RequestException

logger = logging.getLogger(__name__)


def get_keywords_from_query(query: str, generation_model: Gpt) -> list:
    system_prompt = '''
    사용자 민원 질문에서 법률 검색에 유용한 핵심 키워드를 3개 추출하세요. 
    사용자가 명시하지 않았더라도, 쟁점에 관련된 법률 개념/용어를 포함하세요.  
    예: 손해배상, 고의, 과실, 보험금, 계약해지, 고지의무위반, 불법행위, 산재, 위자료 등  
     
    감정 표현, 장황한 설명은 제외하고, 사건 핵심 요소만 추출하세요.  
    출력은 콤마(,)로 구분된 문자열입니다.

    - 예시
    Input : 3월에 축구를 하다 누군가가 발을 차서 무릎으로 넘어져 십자인대 재건술을 마친 상태인데 축구 중이라 고의는 아니었겠지만은 그 사람한테서 보험금이나 보상을 청구 할 수 있나요? 몇개월 간 걷지도 못하고 목발 짚는데 억울하네요
    Output : 손해배상청구,일상생활배상책임보험,스포츠 과실책임
    
    -실제 민원 질문 : {query}
    '''
    prompt = f"질문: \"\"\"\n{query}\n\"\"\""
    keywords_string = generation_model.generate(system_prompt, prompt)
    keywords = [kw.strip() for kw in keywords_string.split(',') if kw.strip()]
    return keywords

def get_google_results(keywords: list, num_results=2):
    google_api_key = 'YOUR_API_KEY'
    search_engine_id = ''

    search_query = " ".join(keywords)  # 키워드 문자열 병합
    encoded_query = urllib.parse.quote(search_query)
    url = f"https://www.googleapis.com/customsearch/v1?key={google_api_key}&cx={search_engine_id}&q={encoded_query}&num={num_results}"
    logger.info(f"Google Search URL: {url}")
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        results = response.json()
        
        search_results = []
        if "items" in results:
            for item in results["items"]:
                search_results.append(item.get("snippet", ""))
                #search_results.append(f"Title: {item['title']}\nLink: {item['link']}\nSnippet: {item['snippet']}\n")
            
            return "\n".join(search_results)
        else:
            logger.info("No items found in the search results")
            return "검색 결과가 없습니다."
        
    except RequestException as e:
        logger.error(f"Network error occurred during Google search")
        print("DEBUG URL:", url)
        return "네트워크 오류가 발생했습니다. 인터넷 연결을 확인해 주세요."
    
    except ValueError as e:
        logger.error(f"Value error occurred during Google search")
        return "검색어 형식이 올바르지 않습니다. 다시 입력해 주세요."
    
    except Exception as e:
        logger.error(f"An error occurred during Google search")
        return "예기치 않은 오류가 발생했습니다. 관리자에게 문의해주세요"
