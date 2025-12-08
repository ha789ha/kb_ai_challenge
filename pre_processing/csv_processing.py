import pandas as pd
from model.generation import Gpt 
from tqdm import tqdm

input_csv_path = "Kb/pre_processing/kin_crawling.csv"
output_csv_path = "Kb/pre_processing/kin_crawling_with_consideration.csv"

prompt = "당신은 민원에 전문적으로 답변하는 법률 전문가입니다."

user_prompt = f"""
당신은 민원에 전문적으로 답변하는 법률 전문가입니다.

민원 질문과 전문가의 답변을 바탕으로, 법률 전문가가 판단을 내리기 전에 반드시 확인해야 할 핵심 쟁점이나 전제조건, 사실관계를 파악하기 위해 민원인에게 되묻는 follow-up 질문을 생성하세요.

- 질문 생략 조건
1. 원 질문이 이미 충분히 구체적인 경우
2. 답변이 법리 판단 없이 상식 수준에서 마무리된 경우
3. 답변이 애매하고 쟁점이 뚜렷하지 않은 경우

- 예시: 
input : 
    민원 질문 : 3월에 축구를 하다 누군가가 발을 차서 무릎으로 넘어져 십자인대 재건술을 마친 상태인데 축구 중이라 고의는 아니었겠지만은 그 사람한테서 보험금이나 보상을 청구 할 수 있나요? 몇개월 간 걷지도 못하도 목발 짚는데 억울하네요,
    전문가 답변 : 발을 차서 부상을 입은 것이라면 그 상대방의 배상책임이 인정될 수 있으며 가입한 보험(일상생활배상책임보험) 등이 있다면 그 보험으로 처리도 가능합니다. ​ 다만, 친선축구 경기 중 부상을 입었다거나 발을 차서 부상을 입었다는 정도로는 상대방 혹은 그 보험회사가 배상책임이 있지 않다고 주장할 가능성도 있으므로 ​ 통상적인 경기 방법이 아닌 상당히 위험한 행위 등을 한 것이라는 점을 입증할 수 있도록 해야 배상을 받을 가능성이 높아지게 됩니다.

output: 경기 중 상대방의 행위가 통상적인 수준을 넘어선 비정상적이거나 위험한 플레이였다고 볼 만한 구체적인 정황이 있을까요?
"""



def generate_consideration_csv(input_csv_path: str, output_csv_path: str, generation_model: Gpt):
    df = pd.read_csv(input_csv_path)

    # 입력 컬럼 체크(문제 예방)
    required = {"date", "question", "answer", "url"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"입력 CSV에 필요한 컬럼이 없습니다: {sorted(missing)}")

    consideration_list = []

    for _, row in tqdm(df.iterrows(), total=len(df), desc="LLM 생성"):
        question = str(row['question'])
        answer = str(row['answer'])

        try:
            consideration = model.generate(prompt, user_prompt)
        except Exception as e:
            consideration = f"ERROR: {str(e)}"

        consideration_list.append(str(consideration).strip())

    # 최종 컬럼만 선택
    out = pd.DataFrame({
        "question": df["question"].astype(str),
        "answer": df["answer"].astype(str),
        "consideration": consideration_list
    })

    out.to_csv(output_csv_path, index=False, encoding='utf-8-sig')
    print(f"저장 완료: {output_csv_path} (rows={len(out)})")

if __name__ == "__main__":
    model = Gpt()
    generate_consideration_csv(input_csv_path, output_csv_path, model)
