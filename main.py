import pymysql.cursors
import datetime,time
import json

import news

news.main()

cnn = pymysql.connect(host='localhost', user='root', password='root', port=3307, database='guancha',
                                   charset='utf8mb4')
cursor=cnn.cursor()

'''
cursor.execute('select title,author,publish_time,url from guanchazhe ORDER BY publish_time DESC')
results=[]
for i in range(cursor.rowcount):
    record=cursor.fetchone()
    result= {'title': record[0], 'author': record[1], 'publish_time': record[2].strftime('%Y-%m-%d %H:%M:%S'),
             'url': record[3]}
    results.append(result)
    print(result['title'],'\t',result['author'],'\t',result['publish_time'],'\t',result['url'])
'''

keyword=input('请输入您想搜索的关键词：')
cursor.execute(
    'select title,author,publish_time,url from guanchazhe WHERE title like "%'+keyword+'%" OR content LIKE "%'+keyword+'%" OR author LIKE "%'+keyword+'%" ORDER BY publish_time DESC'
)
for i in range(cursor.rowcount):
    record=cursor.fetchone()
    result= {'title': record[0], 'author': record[1], 'publish_time': record[2].strftime('%Y-%m-%d %H:%M:%S'),
             'url': record[3]}
    print(result['title'], '\t', result['author'], '\t', result['publish_time'], '\t', result['url'])

cursor.close()
cnn.close()