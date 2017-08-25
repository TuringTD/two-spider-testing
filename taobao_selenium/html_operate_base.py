from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


class HTMLParseModel(object):

    def __init__(self, browser, url):
        super(HTMLParseModel, self).__init__()
        self._browser = browser
        self._url = url if url.startswith('https://') else 'https://' + url
        self._wait = WebDriverWait(self._browser, 10)

    def _open(self, url = None):
        if url:
            self._browser.get(url)
        else:
            self._browser.get(self._url)

    def get_element(self, by, selector):
        '''
        获取页面可见元素
        :param by: element选择器类型
        :param selector: 选择器传入参数
        '''
        try:
            return self._wait.until(EC.visibility_of_all_elements_located((by, selector)))
        except Exception as e:
            print('get element failed', e)
            return None

    def get_clickable(self, by, selector):
        '''
        获取页面可点击元素
        :param by: element选择器类型
        :param selector: 选择器传入参数
        '''
        try:
            return self._wait.until(EC.element_to_be_clickable((by, selector)))
        except Exception as e:
            print('get clickable failed', e)
            return None

    def get_elements(self, by, selector):
        '''
        获取页面多个可见元素
        :param by: element选择器类型
        :param selector: 选择器传入参数
        '''
        try:
            return self._wait.until(EC.presence_of_all_elements_located((by, selector)))
        except Exception as e:
            print('get elements failed', e)
            return None

    def get_title(self):
        return self._browser.title

    def get_html(self, by, selector):
        '''
        判断业务内容是否加载完成并返回网页源代码
        :param by: element选择器类型
        :param selector: 选择器传入参数
        :return:
        '''
        if self._wait.until(EC.presence_of_all_elements_located((by, selector))):
            return self._browser.page_source
        else:
            return None


class TaobaoMainPageModel(HTMLParseModel):
    def __init__(self, browser, url, key_word= None):
        super(TaobaoMainPageModel, self).__init__(browser, url)
        self._key_word = key_word

    def search_key_word(self, key_word= None):
        if not key_word :
            if self._key_word:
                key_word = self._key_word
            else:
                raise Exception('miss key word arguments')
        try:
            input = self.get_element(By.CSS_SELECTOR, '#q')[0]
            if not input:
                raise Exception('input element is not found')
            input.clear()
            input.send_keys(key_word)
        except Exception as e:
            print('<send key word failed>', e)
            return  False
        try:
            self.get_clickable(By.CSS_SELECTOR, '.btn-search').click()
            return True
        except Exception as e:
            print('<search key word failed>', e)
            return False


from bs4 import BeautifulSoup

class TaobaoSearchPageModel(HTMLParseModel):
    def __init__(self, browser):
        self._browser = browser
        self._wait = WebDriverWait(self._browser, 10)

        if not '淘宝搜索' in self._browser.title:
            raise Exception('HTML content error')
        else:
            print('current page:', self._browser.current_url)

    def goto_next(self):
        for i in range(3):  # 页面可能出现无法回去相关网页元素，通过for尝试多次获取（3次）
            try:
                current_page = self.get_element(By.CSS_SELECTOR, 'li.item.active span')[0].text
                print('current page index:', current_page)
                if current_page == '100':
                    print('get all pages finished')
                    return False
                self.get_clickable(By.CSS_SELECTOR, '.next > a:nth-child(1)').click()
                return True
            except Exception as e:
                print('click failed', e)
                self._browser.implicitly_wait(200)
                print('try go to next page again')
                continue
        print('find element failed after try 3 times')
        return False

    def parse_item(self):
        try:
            source = self.get_html(By.CSS_SELECTOR, 'div.item > div')
        except Exception as e:
            print('get page source failed', e)
            return None
        soup = BeautifulSoup(source, 'html.parser')
        for item in  soup.select('div.item.J_MouserOnverReq'):
            yield {
                'title' : ''.join(item.select_one('div.title').get_text()).strip(),
                'price_unit' : list(item.select_one('div.price').stripped_strings)[0],
                'price_digit' : float(list(item.select_one('div.price').stripped_strings)[1]),
                'sales' : item.find('div', {'class':'deal-cnt'}).string,
                'data-nid' : item.find('a', {'class':'pic-link'}).get('data-nid'),
                'baoyou' : True if item.find('span', {'class':'baoyou-intitle icon-service-free'}) else False,
                'location' : item.find('div', {'class':'location'}).string
            }

    def get_parse_data(self):
        print('extract data:')
        if self.parse_item():
            for data in self.parse_item():
                yield data
        else:
            raise Exception('parse data failed')
