from generation import Gpt
import json

agent = Gpt()


def generate_answer(query, topk_list):
    
    
    prompt = f'''
    당신은 검색된 top k 문서에 대한 summary들과 query를 바탕으로 이것이 관련 있는지 판단하는 전문가입니다. 아래 3가지 행동 중 하나를
    고르도록 하세요

    1. query update: 관련 문서, 그리고 '분쟁 사례'라는 측면에서 비추어 보았을때 쿼리가 모호함, 이에 따라 쿼리를 분명하게 업데이트 해 줌
    2. not answerable: 관련 문서, 쿼리를 종합해보았을때 유사한 사례가 없음, 즉 새로운 사례임
    3. answerable: 쿼리와 summary를 살펴보았을때 답변하기 충분함

    # query:
    {query}

    # top k summaries
    {topk_list}

    # 응답 형식
        - query update 일시
        {{"reaction": "query update",
        "rewritten_query": "blabla"}}

        - not answerable 혹은 answerable 일 시
        {{"reaction": "answerable"}}   
    '''
    
    generation = agent.generate(prompt)
    json_response = json.loads(generation)
    
    return json_response
