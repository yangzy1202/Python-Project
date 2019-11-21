from bs4 import BeautifulSoup
from w3lib.html import remove_tags
import requests
import csv
import time
import lxml

url0 = 'https://bj.zu.ke.com/zufang/brp0erp1500/#contentList'
url = 'https://bj.zu.ke.com/zufang/pg{page}brp0erp1500/#contentList'

page = 0 # 页数序号，初始为0
response0 = requests.get(url0)
html0 = BeautifulSoup(response0.text,features='lxml')
totalpage = int(html0.select('.content__pg')[0]['data-totalpage'])
print('total page = ', totalpage) # 所需爬取的总页码数，用来控制循环结束

csv_file = open('rent.csv','w', newline='')
csv_writer = csv.writer(csv_file, delimiter=',')

while True:
    page += 1
    print('fetch: ', url.format(page=page))
    time.sleep(1)
    response = requests.get(url.format(page=page))
    html = BeautifulSoup(response.text,features='lxml')
    house_list = html.select('.content__list--item--aside') # 根据网站源码选择爬取时使用的关键词，爬取房源信息
    price_list = remove_tags(str(html.select('.content__list--item-price em'))).strip('[').strip(']').replace(' ','').split(',') #爬取房源月租列表
    i = 0 # 为从月租列表中提取月租置初值
    for house in house_list:
        house_title = house['title'] # 爬取房源名称
        house_url = 'https://bj.zu.ke.com' + house['href'] # 爬取房源连接
        if '整租' in house_title:
            house_location = house_title.split(' ')[0].replace('整租·', '')
        elif '独栋' in house_title:
            house_location = house_title.split(' ')[1]  # 基于爬取到的房源名称，处理得到房源地址
        house_price = price_list[i] + '元/月' # 从月租列表中提取月租
        i += 1
        csv_writer.writerow([house_title, house_location, house_price, house_url]) # 将数据写入CSV文件
    if page == totalpage:
        break # 爬取最后一页后跳出循环

csv_file.close()
print('---crawling finished---')