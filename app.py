import re
import httpcore
from bs4 import BeautifulSoup
import httpx
import asyncio
import json


def extract_int(string):
    return int(re.sub("[^0-9.\-]", "", string))


async def fetch_company(pathname):
    client = httpx.AsyncClient()
    while True:
        try:
            response = await client.get('https://work.mma.go.kr' + pathname)
        except httpcore._exceptions.TimeoutException:
            continue
        break

    soup = BeautifulSoup(response.content, 'html.parser')
    print(soup.select_one('#content > div:nth-child(1) > table > tbody > tr:nth-child(1) > td').text)
    return {
        'name': soup.select_one('#content > div:nth-child(1) > table > tbody > tr:nth-child(1) > td').text,
        'address': soup.select_one('#content > div:nth-child(1) > table > tbody > tr:nth-child(2) > td').text,
        'tel': soup.select_one(
            '#content > div:nth-child(1) > table > tbody > tr:nth-child(3) > td:nth-child(2)').text,
        'fax': soup.select_one(
            '#content > div:nth-child(1) > table > tbody > tr:nth-child(3) > td:nth-child(4)').text,
        'kind': soup.select_one(
            '#content > div:nth-child(2) > table > tbody > tr:nth-child(1) > td:nth-child(2)').text,
        'scale': soup.select_one(
            '#content > div:nth-child(2) > table > tbody > tr:nth-child(2) > td:nth-child(2)').text,
        'active_service': [
            extract_int(soup.select_one(
                '#content > div:nth-child(2) > table > tbody > tr:nth-child(3) > td:nth-child(2)').text),
            extract_int(soup.select_one(
                '#content > div:nth-child(2) > table > tbody > tr:nth-child(4) > td:nth-child(2)').text),
            extract_int(soup.select_one(
                '#content > div:nth-child(2) > table > tbody > tr:nth-child(5) > td:nth-child(2)').text),
        ],
        'recruit_service': [
            extract_int(soup.select_one(
                '#content > div:nth-child(2) > table > tbody > tr:nth-child(3) > td:nth-child(4)').text),
            extract_int(soup.select_one(
                '#content > div:nth-child(2) > table > tbody > tr:nth-child(4) > td:nth-child(4)').text),
            extract_int(soup.select_one(
                '#content > div:nth-child(2) > table > tbody > tr:nth-child(5) > td:nth-child(4)').text),
        ]
    }


async def main():
    data = {
        'al_eopjong_gbcd': '11111,11112',
        'eopjong_gbcd_list': '11111,11112',
        'eopjong_gbcd': '1',
        'pageUnit': '1000',
        'pageIndex': '1',
    }
    response = httpx.post('https://work.mma.go.kr/caisBYIS/search/byjjecgeomsaek.do', data=data)
    soup = BeautifulSoup(response.content, 'html.parser')
    select_rows = soup.select('#content > table > tbody > tr > th > a')

    print(len(select_rows))
    tasks = list()
    for row in select_rows:
        tasks.append(asyncio.create_task(fetch_company(row['href'])))

    res = await asyncio.gather(*tasks)
    print(res)
    with open('agent.json', 'w') as fp:
        json.dump(res, fp)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()