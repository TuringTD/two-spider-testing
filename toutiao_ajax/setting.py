# 爬虫参数设置

# 搜索关键字
KEY_WORD = '美女'
# 获取最大页面数量
MAX_PAGE = 20
# 网络访问延迟
TIME_OUT = 1

# 使用进程数量
PROCESS_dl_NUM = 2
# PROCESS_SV_NUM = 1

# 图片存储位置
# IMAGES_PATH = r'C:\Users\Administrator\Desktop\Images'
import os
IMAGES_PATH = os.getcwd() + r'\images'

# database设置
DB_URL = 'mysql+mysqlconnector://root:tiger@localhost:3306/test'
TABLE_NAME = 'tt_img'

# 访问头部设置
HEAHER = {
    'Accept': 'text/html,application/xhtml+xml,application/xml', 'Accept-Encoding': "gzip",
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'
}