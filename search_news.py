# -*- coding: utf-8 -*-
# @Author: wang
# @Date:   2018-01-17 10:15:25
# @Last Modified by:   wangfpp
# @Last Modified time: 2018-08-11 10:48:34
import requests#接口请求模块
from bs4 import BeautifulSoup#网页解析模块
import logging
import time
import os,sys
import re
curr_path = os.path.dirname(os.path.abspath(__file__))
comm_path = os.path.dirname(curr_path)
if comm_path not in sys.path:
    sys.path.append(comm_path)
logger = logging.getLogger(__name__)
logger.setLevel(level = logging.INFO)
handler = logging.FileHandler("{}/log.txt".format(curr_path))
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
total = 0
class ClassName(object):
    """获取base_url http://www.chinanews.com/的新闻材料"""
    def __init__(self,base_url,path):#Class类初始化函数  base_url为解读的新闻网页的主页
        self.base_url = base_url
        self.path = path
        pass
    def classify_news(self,url):
        self.classify_a = []
        Header = {
            'Host': 'www.chinanews.com',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7,da;q=0.6',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
        }
        req = requests.get(url, headers = Header)
        if req.status_code == 200:
            req_content = req.content
            soup = BeautifulSoup(req_content, 'html.parser')
            classify_a_tag = soup.find_all('ul', class_ = 'nav_navcon')
            for a in classify_a_tag[0].find_all('a'):
                self.classify_a.append(a.get('href')) 
            self.filter_a_href(self.classify_a) 
        else:
            logger.error('搜索新闻类别标签出错:{}'.format(url))
        for i in self.classify_a:
            self.get_href(i)
    def get_href(self,url):#获取 网页的a标签的 href  过滤后 进行解析其新闻文本
        #try:
        self.alink = alink = []
        req = requests.get(url)
        req_content = req.content
        soup = BeautifulSoup(req_content, 'html.parser')
        a_tag = soup.find_all('a')
        for href in a_tag:
            if href.get('href'):
                alink.append(href.get('href'))
        self.filter_a_href(self.alink)#对获取的a标签进行过滤
        for uri in self.alink:
            file_name = (re.sub(self.base_url, '', os.path.splitext(uri)[0], 0) + "{0}").replace('/','_').format('.txt')
            if self.is_have_file(file_name):
                if re.match('.*([a-zA-Z]/[0-9]{4}/[0-9]{2}-[0-9]{2}/[0-9]{7}.shtml$)',uri) != None:
                    #print ('正在提取:{0}的文字').format(uri)
                    self.get_text(uri, file_name)
        # except:
        #     logger.error('搜索新闻a标签出错:{} error'.format(url))
    def get_text (self,url, name):#获取新闻网页的新闻内容
        #try:
        req = requests.get(url)
        req.encoding = 'GB2312'
        html = req.text
        soup = BeautifulSoup(html, 'html.parser')
        content = soup.find_all('div', class_ = 'left_zw')
        title = soup.find_all('h1', style="display:block; position:relative; text-align:center; clear:both")
        if len(title) > 0:
            for item in title:
                try:
                    self.save_text(item.string.encode('utf-8')+'\n',name)
                    global total
                    total += 1
                    # except:
                    #     logger.error('get text error:{}'.format(url))
                    #     print ('\033[0;31m 网页获取错误\033[0m {0}').format(url)
                except Exception as e:
                    logger.error('{}:{}'.format(e,url))
        for item in content:
            for txt_contene in item.contents:
                if txt_contene.string and len(txt_contene.string) > 5:
                    if txt_contene.string is not None:
                        self.save_text(txt_contene.string.strip().encode('utf-8'),name)
                        #print txt_contene.string,('保存新闻内容到:{0}').format(name)
                        #self.save_text(txt_contene.string,name)
    def save_text(self,txt,filename):#保存新闻内容到txt文件中
        f = open(self.path + '/title_audiotxt/' + filename, 'a')
        f.write(txt)
        f.close()
    
    def is_have_file(self,filename):#判断是否已经存在此新闻 节省资源
        file_list = os.listdir(self.path + '/title_audiotxt/')
        if filename in file_list:
            return False
        else:
            return True

    def filter_a_href (self,arr):#过滤a标签
        for a in  range(len(arr)):
            if arr[a].find('//', 0, 2) != -1:
                arr[a] = 'http:' + arr[a]
            if arr[a].find('/', 0, 1) != -1:
                arr[a] = 'http://www.chinanews.com' + arr[a]
        for item in range(len(arr))[::-1]:
            if not 'http://www.chinanews.com' in arr[item] or 'shipin' in arr[item]:
                del arr[item] 


if __name__ == '__main__':
    #logging.basicConfig(level=logging.DEBUG)
    oldTime = time.time()
    base_url = 'http://www.chinanews.com/'
    a = ClassName(base_url,'.')
    a.classify_news(base_url)
    newTime = time.time()
    logger.info('进行搜索,搜索用时:{}s,保存新闻{}个'.format(newTime-oldTime,total))
        
  			
  		

				

