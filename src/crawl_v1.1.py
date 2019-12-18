#!/usr/bin/env python
# coding:utf-8

from bs4 import BeautifulSoup
import bs4
import requests
import csv
import time
import re
import random


url0 = "https://bj.zu.ke.com/zufang/daxing/erp5000/"

url = "https://bj.zu.ke.com/zufang/pg{page}erp5000/#contentList"

### 将数据保存到excel中
csv_file = open("rent_v5.2.csv", "w", newline='', encoding='utf-8')
csv_writer = csv.writer(csv_file, delimiter=',')



page = 0

while True:
    page += 1

    print("fetch: ", url.format(page=page))

    time.sleep(random.randint(1, 6))
    response = requests.get(url.format(page=page))
    demo = response.text
    soup = BeautifulSoup(demo, "html.parser")

    if page == 1:
        # totalpage = int(html0.select('.content__pg')[0]['data-totalpage'])
        totalpage = int(soup.find_all('div', 'content__pg')[0].attrs['data-totalpage'])


# r = requests.get(url0)
# demo = r.text
# soup = BeautifulSoup(demo, "html.parser")
# attri = soup.find(class='link')
# soup.find_all(='content__list--item--aside')
# for tr in soup.a.find_all('title'):
#     print(tr)

# rst = re.split(r'[一二三四五六七八九十]*店', '大一学一店 潇三湘二区 北京六区')
# house_location = house_title.split(' ')[0].replace('整租·', '')
    for houseInfo in soup.find_all('div', 'content__list--item--main'):
        print(houseInfo)
        if isinstance(houseInfo, bs4.element.Tag):                          #提升程序稳健性，有可能出现不是标签的字符
            # house_title = houseInfo.get('title')
            # house_title = houseInfo('p')[0].contents[1].string.replace('\n       ','')
            house_t = houseInfo('p')[0].contents[1].string
            house_title = re.split(r'^\s*|\s*$', house_t)[1]
            # house_url = 'https://bj.zu.ke.com' + houseInfo.get('href')
            house_url = 'https://bj.zu.ke.com' + houseInfo('p')[0].contents[1].get('href')
            if '整租' in house_title:
                house_loc = house_title.split(' ')[0].replace('整租·', '')
            elif '独栋' in house_title:
                house_loc = house_title.split(' ')[1]                        #基于爬取到的房源名称，处理得到房源地址

            house_location = re.split(r'[一二三四五六七八九十]*店', house_loc) #删除地址后面的几号点，否则地图上搜不到

            ## 提取房屋价格
            house_price = houseInfo('em')[0].contents[0].string + '元/月'
            csv_writer.writerow([house_title, house_location[0], house_price, house_url])  # 将数据写入CSV文件
    if page == totalpage:
        break
# print(soup.a.prettify())

csv_file.close()
print('page=', page)
print('---crawling finished---')

def  getHTMLText(url):
    try:
        r = requests.get(url, timeout=1)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r.text
    except:
        return "Get url text error！！！"



# def getTextInfo(uList, html):
#     html = BeautifulSoup(html, "html.parser")
#     for tr in html.find('tbody').children:
#         if isinstance(tr, bs4.element.Tag):
#             tds = tr('td')
#             uList.append([tds[0].string, tds[1].string, tds[3].string])
