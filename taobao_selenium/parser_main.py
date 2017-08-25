from html_operate_base import TaobaoMainPageModel, TaobaoSearchPageModel
from setting import *
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities

def browser_setup():
    dcap = dict(DesiredCapabilities.PHANTOMJS)
    dcap["phantomjs.page.settings.userAgent"] = (USER_AGENT)
    args = SERVICE_ARGS
    browser = webdriver.PhantomJS(desired_capabilities= dcap, service_args= args)
    browser.maximize_window()
    return browser

def browser_teardown(browser):
    print('当前访问页面：',browser.current_url, 'brwoser quit...')
    browser.quit()

def save_data(data):
    for i in data:
        print('<DATA>', i)


def main(url, key_word):
    browser = browser_setup()
    try:
        main_page = TaobaoMainPageModel(browser, url, key_word)
        main_page._open()
        is_success = main_page.search_key_word()

        if is_success:
            search_page = TaobaoSearchPageModel(browser)
            data = search_page.get_parse_data()
            save_data(data)
            while search_page.goto_next():
                data = search_page.get_parse_data()
                save_data(data)

    finally:
        browser_teardown(browser)

if __name__ == '__main__':
    main(START_URL, KEY_WORD)
