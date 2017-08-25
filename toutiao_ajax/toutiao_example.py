from urllib.parse import urlencode
import requests, json, time, re
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
from setting import *
from sql_base import ImageBase, DataOperateModel
from multiprocessing.pool import Pool
from functools import partial


def get_response(url, timeout= TIME_OUT):
    header = HEAHER
    try:
        time.sleep(timeout)
        response = requests.get(url, params=header)
        if response.status_code == 200:
            return response
        return None
    except RequestException as e:
        print('网页访问异常：', e)
        return None


def get_main_page(offset, key_word):
    data = {'offset': offset, 'format': 'json', 'keyword': key_word, 'autoload': 'true', 'count': 20, 'cur_tab': 1}
    url = "https://www.toutiao.com/search_content/?" + urlencode(data)
    return get_response(url)


def parse_main_page(response):
    print('获取内容：', response.url)
    if response:
        data = json.loads(response.text)
        if data and 'data' in data.keys():
            item = data.get('data')
            print('获取个数：', len(item))
            for i in item:
                yield i.get('article_url')


def get_detail_page(url):
    if url and url.startswith('http'):
        return get_response(url), url
    return None, url


def parse_detail_page(response, url):
    if response:
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.select('title')[0].get_text()
        print('parse page:', title)
        items = soup.select('.article-content') or soup.select('#gallery')
        if items:
            imgs = items[0].find_all('img')
            for i in imgs:
                src = 'alt-src' if items[0].get('id') == 'gallery' else 'src'
                yield {'title': title, 'url': url, 'img_src': i.get(src)}
        else:
            pattern = re.compile(r'var gallery = (.*?);', re.S)
            result = re.search(pattern, response.text)
            if result:
                try:
                    data = json.loads(result.group(1))
                except Exception as e:
                    print(e)
                    return None
                if data and 'sub_images' in data.keys():
                    for src in (i.get('url') for i in data.get('sub_images')):
                        yield {'title': title, 'url': url, 'img_src': src}
            else:
                print('<parse page failed>', url, response.status_code)
                return None


def image_download(path, url):
    response = get_response(url)
    content = response.content
    file_path = path + r'\{}.{}'.format(os.path.basename(url), 'jpg')
    with open(file_path, 'wb') as f:
        print('下载图片：', url)
        f.write(content)


def extractor(page, key_word):
    art_links = parse_main_page(get_main_page(page, key_word))
    if art_links:
        for link in art_links:
            result = get_detail_page(link)
            data = parse_detail_page(*result)
            for item in data:
                yield {'title':item['title'], 'url':item['url'], 'img_src':item['img_src']}


def extract_data(database, source):
    if source:
        for item in source:
            yield database(item)


def downloader_link(path, url):
    try:
        image_download(path, url)
    except:
        pass


def main(key_word):
    ImageBase.set_table_name(TABLE_NAME)
    print(ImageBase.__tablename__)
    db_oob = DataOperateModel(DB_URL, ImageBase)
    db_oob.sql_setup()

    downloader = partial(downloader_link, IMAGES_PATH)

    try:
        for page in (index * 20 for index in range(MAX_PAGE)):
            receive = extractor(page, key_word)
            data_dl = (item.get('img_src') for item in receive)
            data_sv = extract_data(ImageBase, receive)

            with Pool(PROCESS_dl_NUM) as dl:
                dl.map(downloader, data_dl)

            db_oob.save_data(data_sv)

    finally:
        db_oob.sql_teardown()


if __name__ == '__main__':
    main(KEY_WORD)
