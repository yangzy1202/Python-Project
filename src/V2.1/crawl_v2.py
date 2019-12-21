#!/usr/bin/env python
# coding:utf-8
# import Overlap as Overlap
import pyecharts.options as opts
from pyecharts.charts import Bar, Line
# from pyecharts.chart import overlap
import pyecharts
from bs4 import BeautifulSoup
import bs4
import requests
import csv
import time
import re
import random
import numpy as np

import argparse
import os

import configparser


import pandas as pd
import matplotlib.pyplot as plt






#######   获取房源网页
def  getHTMLText(url):
    try:
        time.sleep(random.randint(1, 6))
        r = requests.get(url)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r.text
    except:
        return ""

#  获取北京市不同区域名称和其拼音形成的字典信息
def get_houseArea(uList, url):
    html = getHTMLText(url)
    if html == '':
        return "请检查网络连接！！！"
    soup = BeautifulSoup(html, "html.parser")
    # a = soup.find_all('a')
    for tr in soup.find('ul','').children:
        if isinstance(tr, bs4.element.Tag):
            tds = tr('a')
            uList.append(tds[0].get('href'))

    ul = soup.find('ul','').text
    area_list = re.split(r'\n+', ul)                # 利用正则去掉字符串中的换行符
    print("before:",area_list)
    while '' in area_list:
        area_list.remove('')                        # 移除空字符信息
    area_list = area_list[:14]                      # 后面区域在北京没有租房信息
    print(area_list)

    InforDict ={}
    for i in range(len(area_list)):
        key = area_list[i]
        value = uList[i]
        InforDict[key] = value

    return InforDict



# 按照指定区域获取房源信息数据，提供给后端API使用

def getHouseInfo(InforDict, areaInBJ):
    page = 0
    #  根据区域选择要保存的文件名称
    region_param_url = InforDict[areaInBJ]
    csv_file = open(areaInBJ+"_rent_v2.0test.csv", "w", newline='',encoding='utf-8')
    csv_writer = csv.writer(csv_file, delimiter=',')
    # csv_writer = csv.writerows(areaInBJ)
    # csv_writer.writerow([areaInBJ,areaInBJ,areaInBJ,areaInBJ])
    ## 拼接某个区域的url地址
    # for url_area_index in uList[1]:
    url_area = "https://bj.zu.ke.com" + region_param_url + "pg{page}erp5000/"

    # html = getHTMLText(url_area)
    # url = "https://bj.zu.ke.com/zufang/pg{page}erp5000/#contentList"
    while True:
        page += 1
        print("fetch: ", url_area.format(page=page))
        time.sleep(random.randint(1, 6))
        response = requests.get(url_area.format(page=page))
        demo = response.text

        soup = BeautifulSoup(demo, "html.parser")

        if page == 1:
            # totalpage = int(html0.select('.content__pg')[0]['data-totalpage'])
            totalpage = int(soup.find_all('div', 'content__pg')[0].attrs['data-totalpage'])
            print(totalpage)
        for houseInfo in soup.find_all('div', 'content__list--item--main'):
            # print(houseInfo)
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

    csv_file.close()
    print('page=', page)
    print('---crawling finished---')


####  获得所有区域房屋信息
def getAllHouseInfo(InforDict, saveFileName):
    csv_file = open(saveFileName, "w", newline='')
    csv_writer = csv.writer(csv_file, delimiter=',')
    # csv_writer = csv.writerows(areaInBJ)
    csv_writer.writerow(['region', 'name', 'position', 'price', 'webAddr'])
    for key in InforDict:
        if key == '不限':
            continue
        page = 0
        #  根据区域选择要保存的文件名称
        region_param_url = InforDict[key]

        ## 拼接某个区域的url地址

        url_area = "https://bj.zu.ke.com" + region_param_url + "pg{page}erp5000/"

        while True:
            page += 1
            print("fetch: ", url_area.format(page=page))
            time.sleep(random.randint(1, 6))
            response = requests.get(url_area.format(page=page))
            demo = response.text

            soup = BeautifulSoup(demo, "html.parser")

            if page == 1:
                # totalpage = int(html0.select('.content__pg')[0]['data-totalpage'])
                totalpage = int(soup.find_all('div', 'content__pg')[0].attrs['data-totalpage'])
                print(totalpage)
            for houseInfo in soup.find_all('div', 'content__list--item--main'):
                # print(houseInfo)
                if isinstance(houseInfo, bs4.element.Tag):                           #提升程序稳健性，有可能出现不是标签的字符
                    # house_title = houseInfo.get('title')
                    # house_title = houseInfo('p')[0].contents[1].string.replace('\n       ','')
                    house_t = houseInfo('p')[0].contents[1].string
                    house_title = re.split(r'^\s*|\s*$', house_t)[1]                 #利用正则表达删除字符串的前面和后面空格字符
                    # house_url = 'https://bj.zu.ke.com' + houseInfo.get('href')
                    house_url = 'https://bj.zu.ke.com' + houseInfo('p')[0].contents[1].get('href')
                    if '整租' in house_title:
                        house_loc = house_title.split(' ')[0].replace('整租·', '')
                    elif '独栋' in house_title:
                        house_loc = house_title.split(' ')[1]                         #基于爬取到的房源名称，处理得到房源地址

                    house_location = re.split(r'[一二三四五六七八九十]*店', house_loc)  #删除地址后面的几号点，否则地图上搜不到

                    ## 提取房屋价格
                    house_price = houseInfo('em')[0].contents[0].string.split('-')[0]
                    csv_writer.writerow([key, house_title, house_location[0], house_price, house_url])  # 将数据写入CSV文件
            if page == totalpage:
                break

    csv_file.close()
    print('page=', page)
    print('---crawling finished---')


# 根据获取的房源信息，针对关键数据进行数据可视化操作
def PlotHouseDiagram(fileName):
    df = pd.read_csv(fileName, header=0, delimiter=',', encoding='gb18030',
                     names=['region', 'name', 'position', 'price', 'webAddr'])

    house_price_label = df.groupby('region').price.agg(['mean', 'count'])
    house_price_label.reset_index(inplace=True)
    region_house_label = house_price_label.sort_values('count', ascending=False)
    # print(df.describe())
    r1 = region_house_label['region']
    house_number = region_house_label['count']
    house_mean_price = region_house_label['mean']
    # house_mean_price = []
    for i in range(len(house_mean_price)):
        house_mean_price[i] = format(house_mean_price[i], '.3f')
    len_test = 10
    ###  单独画图
    line = (
             Line()
             .add_xaxis(list(r1[:len_test]))
             .add_yaxis("北京不同区域", list(house_mean_price[:len_test]))
             .set_series_opts(label_opts=opts.LabelOpts(interval=1))
             .set_global_opts(title_opts=opts.TitleOpts(title="北京不同区域租房的房租均价"),
                              yaxis_opts=opts.AxisOpts(
                                  axislabel_opts=opts.LabelOpts(formatter="{value}元/月")))
    )
    line.render("line_stack_v2.1.html")

    bar = (
        Bar()
        .add_xaxis(list(r1[:len_test]))
        .add_yaxis("北京不同区域",list(house_number[:len_test]))
        # .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
        .set_global_opts(title_opts=opts.TitleOpts(title="北京不同区域租房的房屋数量"),
                         yaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(formatter="{value}套")),)
    )
    bar.render("bar_stack_v2.1.html")

    ### 将bar和line画在一起
    bar = (
        Bar()
        .add_xaxis(xaxis_data=list(r1[:len_test]))
        .add_yaxis("北京不同区域租房的房屋数量", list(house_number[:len_test]))
        .extend_axis(yaxis=opts.AxisOpts(
            axislabel_opts=opts.LabelOpts(formatter="{value}元/月")))

        # .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
        .set_global_opts(title_opts=opts.TitleOpts(title="不同区域数量和均价分布图"),
                         yaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(formatter="{value}套")), )
    )

    line = Line().add_xaxis(list(r1[:len_test])).add_yaxis("北京不同区域租房的房租均价", list(house_mean_price[:len_test]), yaxis_index=1)
    bar.overlap(line)
    bar.render("bar_line_stack_v2.1.html")

def main():

    ###（1）初始化
    print("begin crawl!")
    url = "https://bj.zu.ke.com/zufang"             #  租房网站




    # parser = argparse.ArgumentParser()  # 解析命令行参数，读取参数文件.ini
    # # parser.add_argument('params_file',
    # #                     help='Please input params_file(xxx.ini).')
    # parser.add_argument('house_param',default='不限')
    # args = parser.parse_args()
    # region_param = args.house_param
    # print(region_param)


    # config = ConfigParser.ConfigParser()  # 读取配置文件的包，括号“[ ]”内包含的为section。
    # config.read(args.params_file)
    # region_param = dict(config.items('house_region'))


    uList = []
    ### （2）获取北京市不同区域名称和其拼音形成的字典信息
    InforDict = get_houseArea(uList, url)



   ### （3）指定北京某个区域爬取该区域房屋信息
    region_param = '大兴'                            #默认为大兴区域
    getHouseInfo(InforDict,  region_param)

   ### （4）按照区域顺序爬取北京城区所有房源信息
    saveFileName = "rentV2.1_All_houseInfo.csv"
    getAllHouseInfo(InforDict, saveFileName)

   ### （5）采用pyecharts，实现房源数据相关参数的可视化
    PlotHouseDiagram(saveFileName)


if __name__ == '__main__':
    main()