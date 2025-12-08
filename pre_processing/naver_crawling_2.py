import requests, bs4, re, pandas as pd, time, random, pathlib, sys
from tqdm import tqdm

UID    = 'n1VgbqDmz2IdYyFKM3jwGYdJNHRMN7JkvU2w97AJ1ls%3D'  # 프로필 ID
BASE   = 'https://kin.naver.com'
CSV    = pathlib.Path(__file__).with_name('kin_ParkHanseok_2.csv')
BATCH  = 40                         # 모아서 저장할 레코드 수
SLEEP  = (1.0, 2.0)                 # 요청 간 랜덤 지연(초)
MAX_PG = 600                        # ‘답변 보기’ 페이지 보유 최대 수
DEBUG  = True                       # True → HTML 덤프·로그 ON

sess = requests.Session()
sess.headers.update({
    'User-Agent': 'Mozilla/5.0',
    'Referer': BASE
})

def answer_links():
    for pg in range(1, MAX_PG + 1):
        url = f'{BASE}/userinfo/answerList.naver?u={UID}&page={pg}'
        html = sess.get(url, timeout=10).text
        soup = bs4.BeautifulSoup(html, 'html.parser')

        anchors = soup.find_all(
            'a',
            href=re.compile(r'^/qna/mydetail\.naver\?.*answerNo=\d+')
        )
        links = {
            BASE + a['href'].replace('/qna/mydetail.naver?', '/qna/detail.naver?')
            for a in anchors
        }  # ← 괄호 위치 정렬

        if not links:
            break

        for link in links:
            yield link
        time.sleep(random.uniform(*SLEEP))

def parse_qna(url: str) -> dict | None:
    html = sess.get(url, timeout=10).text

    # JS-리다이렉트 페이지라면 realRedirectURL 추출 후 재요청
    if 'realRedirectURL' in html:
        m = re.search(r"realRedirectURL\s*=\s*'([^']+)'", html)
        if m:
            url = m.group(1)
            html = sess.get(url, timeout=10).text

    s = bs4.BeautifulSoup(html, 'html.parser')

    # 질문
    # 신/구 UI 혼재 대비 다중 셀렉터 폴백
    qdetail_tag = (
        s.select_one('div.questionDetail') or
        s.select_one('div.c-heading__content._questionContentsText') or
        s.select_one('div._questionContentsText') or
        s.select_one('div.c-heading__content')
    )
    if not qdetail_tag:
        return None
    question_body = qdetail_tag.get_text(' ', strip=True)

    # 답변 
    ans_no  = re.search(r'answerNo=(\d+)', url).group(1)
    target  = f'answer_{ans_no}'                    # id="answer_8" 식
    ans_blk = s.find(id=target)
    if not ans_blk:
        for blk in s.select('div.answer_area, div.answerArea_contentWrap_answer'):
            if '박한석손해사정사' in blk.get_text():
                ans_blk = blk
                break
    if not ans_blk:
        return None

    body = ans_blk.select_one(
        'div.se-main-container, div._endContentsText, div.c-heading__content'
    )
    if not body:
        return None

    date_tag = ans_blk.select_one('span.c-user-date, span.date')
    date_txt = date_tag.get_text(strip=True) if date_tag else ''

    return {
        'date':     date_txt,
        'question': question_body,
        'answer':   body.get_text(' ', strip=True),
        'url':      url
    }

def write_batch(batch: list[dict]):
    if not batch:
        return
    CSV.parent.mkdir(exist_ok=True)
    df = pd.DataFrame(batch)
    df.to_csv(
        CSV, mode='a', index=False, encoding='utf-8-sig',
        header=not CSV.exists() or CSV.stat().st_size == 0
    )

def crawl():
    if CSV.exists() and CSV.stat().st_size > 0:
        seen = set(pd.read_csv(CSV, usecols=['url'])['url'])   # ← URL 중복 방지
    else:
        seen = set()

    batch = []
    for link in tqdm(answer_links(), desc='Q&A 수집'):
        item = parse_qna(link)
        if item and item['url'] not in seen:
            print(f"\n● {item['date']}")
            print(f"  Q: {item['question'][:80]}…")  # ← 본문 미리보기
            print(f"  A: {item['answer'][:80]}…\n")
            batch.append(item)
            seen.add(item['url'])

        if len(batch) >= BATCH:
            write_batch(batch); batch.clear()
        time.sleep(random.uniform(*SLEEP))

    write_batch(batch)
    print(f'\n총 {len(seen):,}건 저장 완료 → {CSV.name}')

if __name__ == '__main__':
    try:
        crawl()
    except KeyboardInterrupt:
        sys.exit('\n[중단] 작업이 취소되었습니다.')
