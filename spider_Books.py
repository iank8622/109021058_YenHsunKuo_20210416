from bs4 import BeautifulSoup
from random import randint
import sys
import requests
import time
import csv

URL = 'https://search.books.com.tw/search/query/key/{0}/cat/all'

# 以sys.argv方法輸入關鍵字(keywd)
def generate_search_url(url, keywd):
    return url.format(keywd)

# 置入假身份
def get_resource(url):
    headers = {
        "user-agent" : "Mozilla/5.0 (Windoes NT 10.0; Win64; x64) AppWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"
    }
    return requests.get(url, headers=headers)

# 解析為soup
def parse_html(r):
    if r.status_code == requests.codes.ok:
        return BeautifulSoup(r.text, 'lxml')
    else:
        print('HTTP requests error!!')

# 取得關鍵字下書籍之解析(soup)資料
def get_bd(book_id):
    BDURL = 'https://www.books.com.tw/products/{0}?sloc=main'
    url = BDURL.format(book_id)
    print('Scraping book detail...')
    r = get_resource(url)
    soup = parse_html(r)
    return soup

# 爬蟲
def web_scraping_bot(url):
    booklist = []
    print('...')
    soup = parse_html(get_resource(url))
    # 找到<table>下 id = itemlist_table 下之所有<tbody>下之內容 並使其變成物件
    for book in soup.find('table', id='itemlist_table').find_all('tbody'):
        # 取的物件中"id"下之資訊 並以'_'split [-1]取最後一個元素 該元素為本書id (get同時已成為text)
        book_id = book.get('id').split('_')[-1]
        # 在物件中找尋<div>下 class_="box_1" 中之<a>下之"title"內容
        # .a 為soup的另一種find()法
        book_title = book.find('div', attrs={'class': 'box_1'}).a.get('title')

        # 降低請求頻率以防止伺服器阻擋
        delay = randint(10, 20)
        print('Scraping delay {0} sec...'.format(delay))
        time.sleep(delay)

        bd = get_bd(book_id)
        # attrs={'class': 'type02_p003'}) 同class_='type02_p003'
        for item in bd.find('div', attrs={'class': 'type02_p003'}).find_all('li'):
            # 如果此關鍵字在變成文檔的item中
            if '作者' in item.text:
                # 將item變成文檔 並取代
                book_author = item.text.replace('  ', '')[3:]
                break
        # attrs={'class': 'price01'}) 同class_='price01'
        book_price = int(bd.find('strong', attrs={'class': 'price01'}).text)
        for item in bd.find('div', attrs={'class': 'bd'}).find_all('li'):
            if 'ISBN' in item.text:
                book_ISBN = item.text.replace('  ', '')[5:]
                break
        
        booklist.append({'book_title': book_title, 'book_author': book_author, 'book_price': book_price, 'book_ISBN': book_ISBN})
    return booklist

if __name__ == '__main__':
    if len(sys.argv) > 1:
        url = generate_search_url(URL, sys.argv[1])
        booklist = web_scraping_bot(url)
        # *將list中所有元素分次輸出
        print(*booklist, sep='\n')