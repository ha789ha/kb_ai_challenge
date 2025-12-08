import win32com.client
import time
import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm
import win32com.client as win32

df = pd.DataFrame(
    {'권역': [],
     '유형': [],
     '제목': [],
     '담당부서': [],
     '등록일': [],
     '첨부파일': []
     }
)


for idx in tqdm(range(1, 82)):
    url = f'https://www.fss.or.kr/fss/bbs/B0000390/list.do?menuNo=&bbsId=&cl1Cd=&cl2Cd=&cl3Cd=&pageIndex={idx}&paramDeptname=&viewType=BODY&searchCnd=22&searchWrd='
    
    download_url = './documents'
    
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    div_tag = soup.find('div', class_='bd-list')
    table = div_tag.find('table')
    content = table.find('tbody')
    
    
    
    for tr in content.find_all('tr'):
        tds = tr.find_all('td')
        if len(tds) < 7:
            continue  # td 개수가 부족하면 skip

        # 각 컬럼  처리
        유형 = tds[2].get_text(strip=True)
        권역 = tds[1].get_text(strip=True)
        제목_tag = tds[3].find('a')
        제목 = 제목_tag.get_text(strip=True) if 제목_tag else ''
        담당부서 = tds[4].get_text(strip=True)
        등록일 = tds[5].get_text(strip=True)

        # 첨부파일 처리
        file_tag = tds[6].find('a', class_='file-single')
        if file_tag and file_tag['href']:
            file_name = file_tag.find('span', class_='name').get_text(strip=True)
            file_url = 'https://www.fss.or.kr' + file_tag['href']  # 절대경로로 변환

            # 로컬에 저장
            try:
                r = requests.get(file_url)
                local_path = os.path.join(download_url, file_name)
                with open(local_path, 'wb') as f:
                    f.write(r.content)
            except Exception as e:
                print(f'파일 다운로드 실패: {file_name}, 이유: {e}')
                local_path = ''
        else:
            local_path = ''

        # df에 한 행 추가
        df.loc[len(df)] = [권역, 유형, 제목, 담당부서, 등록일, local_path]
    
    time.sleep(0.2)
        
df.to_csv('documents.csv')

