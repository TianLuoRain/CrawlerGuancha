import requests
import queue
import pymysql
from lxml import etree
import threading
import re

import timeTrans

class Crawler(threading.Thread):
    def __init__(self, url_queue):
        super(Crawler, self).__init__()
        self.url_queue = url_queue
        self.urls_existed = []

        # 连接Mysql数据库
        self.cnn = pymysql.connect(host='localhost', user='root', password='root', port=3307, database='guancha',
                                   charset='utf8mb4')
        self.cursor = self.cnn.cursor()
        self.sql = 'insert into guanchazhe(title, author, publish_time, content, url) values(%s, %s, %s, %s, %s)'

        # 获取已爬取的url数据并写入列表，用于判断
        sql = 'select url from guanchazhe'
        self.cursor.execute(sql)
        for url in self.cursor.fetchall():
            self.urls_existed.append(url[0])

    def run(self):
        self.spider()

    def check_url(self, url):

        if url in self.urls_existed:
            # 已存在就是不能存
            return False
        else:
            self.urls_existed.append(url)
            # 还没有就是可以存
            return True

    def spider(self):
        while not self.url_queue.empty():
            item = {}
            url = self.url_queue.get()
            if self.check_url(url):
                # print(f'正在爬取{url}')
                response = requests.get(url)  # 爬取内容
                response.encoding = "utf-8"
                html = etree.HTML(response.text)
                results = html.xpath('//ul/li[contains(@class,"left left-main")]')

                for result in results:  # 解析网页
                    item['url'] = url
                    author = result.xpath('./ul/li/div[contains(@class,author-intro)]/p/a/text()')#左列个人作者以此结构为主
                    if not author:
                        author = html.xpath('//div[contains(@class,"time")]/span[3]/text()')      #中列其他官媒以此结构为主
                    if not author:
                        self.get_right_news(response.text, item)                                        #右列部分是这，但不全是
                        continue
                    item['author'] = author[0]

                    item['title'] = result.xpath('./h3/text()')[0]

                    item['publish_time'] = result.xpath('./div[contains(@class,"time")]/span[1]/text()')[0]

                    content = result.xpath('./div[contains(@class,"content")]/p/text()')
                    content = ''.join(content)
                    content = re.sub('\s', '', content)
                    item['content'] = content
                    # 解析后提取目标信息存储在item字典
                self.save_to_sql(item)  # 存入数据库

    def get_right_news(self, text, item):
        str = re.search('window.location.href=".*?"', text).group()
        link = re.split('"', str)[1] + '&page=0'

        response = requests.get(url=link)
        response.encoding = "utf-8"
        html = etree.HTML(response.text)
        item['author'] = \
        html.xpath('//div[contains(@class,"article-content")]/div[2]/div[@class="user-main"]/h4/a/text()')[0]

        item['title'] = html.xpath('//div[@class="article-content"]/h1/text()')[0]

        item['publish_time'] =timeTrans.main(html.xpath('//span[@class="time1"]/text()')[0])


        content = html.xpath('//div[@class="article-txt-content"]/p/text()')
        content = ''.join(content)
        content = re.sub('\s', '', content)
        item['content'] = content


    def save_to_sql(self, item):
        self.cursor.execute(self.sql,
                            [item['title'], item['author'], item['publish_time'], item['content'], item['url']])
        self.cnn.commit()

def add_urls(urls, queue):
    for url in urls:
        if re.findall('http',url):
            queue.put(url)
        else:
            url = 'https://www.guancha.cn' + url
            queue.put(url)


def get_url(queue):
    url = 'https://www.guancha.cn/'
    response = requests.get(url).text
    html = etree.HTML(response)

    headline_url=html.xpath('//div[contains(@class,"content-headline")]/h3/a/@href')
    left_urls = html.xpath('//ul[contains(@class, "Review-item")]/li/a[contains(@class, "module-img")]/@href')
    middle_urls = html.xpath('//ul[contains(@class, "img-List")]/li/h4[contains(@class, "module-title")]/a/@href')
    right_urls=html.xpath('//ul[contains(@class, "fengwen-list")]/li/h4[contains(@class, "module-title")]/a/@href')

    add_urls(headline_url,queue)
    add_urls(left_urls, queue)
    add_urls(middle_urls, queue)
    add_urls(right_urls,queue)
    '''这是右侧列表，其中风闻社区的网页处理暂未完成''''''真nm难整，佛了'''


def main():
    threads = []
    '''
    观察者网有较弱的限制访问频次措施
    如果不使用多线程，程序运行一次只能获取几条数据
    '''
    url_que = queue.Queue()
    get_url(url_que)

    for i in range(5):
        crawler = Crawler(url_que)
        threads.append(crawler)
        crawler.start()


    crawler.cursor.close()
    crawler.cnn.close()
