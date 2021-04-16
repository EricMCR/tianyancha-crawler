# -*- coding = utf-8 -*-
# @TIME : 2021/4/13 10:24
# @Author : Eric Ma
# @File : main.py
# @Software : PyCharm

import urllib.request as request
from urllib.parse import quote
import string
from bs4 import BeautifulSoup
import json
import math
from database import *


# 提取公司名称对应的数据
def getData(companyNameList: list):
    for companyName in companyNameList:
        # 提取商标信息
        print('{} 商标信息 开始提取...'.format(companyName))
        tmDataList = getTmData(companyName)
        # 存储商标数据到数据库
        saveTmData(tmDataList)
        print('{} 商标信息 提取完成!'.format(companyName))

        # 提取专利信息
        print('{} 专利信息 开始提取...'.format(companyName))
        patentDataList = getPatentData(companyName)
        # 存储专利数据到数据库
        savePatentData(patentDataList)
        print('{} 专利信息 提取完成!'.format(companyName))

        # 提取软件著作权信息
        print('{} 软件著作权信息 开始提取...'.format(companyName))
        scDataList = getSCData(companyName)
        # 存储软件著作权数据到数据库
        saveSCData(scDataList)
        print('{} 软件著作权信息 提取完成!'.format(companyName))

        # 提取网站备案信息
        print('{} 网站备案信息 开始提取...'.format(companyName))
        wrDataList = getWRData(companyName)
        # 存储软件著作权数据到数据库
        saveWRData(wrDataList)
        print('{} 网站备案信息 提取完成!'.format(companyName))

        print('**************************************')


# 获取总页数
def getTotalPage(url):
    response = askURL(url)
    bs = BeautifulSoup(response, "html.parser")

    # 获取总页数
    totalPage = math.ceil(int(bs.select('div.result-tips span em:first-child')[0].string) / 10)
    # 非会员只能查看最多10页信息
    totalPage = 10 if totalPage > 10 else totalPage

    return totalPage


# 获取商标信息
def getTmData(companyName):
    tmDataList = []
    # url 中 t401:商标信息, t402:专利信息, t403:软件著作权, t404:网站备案
    searchUrl = 'https://www.tianyancha.com/search/t401?key=' + companyName

    totalPage = getTotalPage(searchUrl)

    for page in range(1, totalPage + 1):
        searchUrl = 'https://www.tianyancha.com/search/t401/p{}?key={}'.format(page, companyName)
        response = askURL(searchUrl)
        bs = BeautifulSoup(response, "html.parser")

        tagList = bs.find_all('script', class_='dataInfo')
        for item in tagList:
            jsonObj = json.loads(item.string)

            # 关联企业列表提取
            connList = []
            for item2 in jsonObj['connList']:
                comTag = BeautifulSoup(item2, "html.parser")
                connList.append({'comName': comTag.string, 'comLink': comTag.a['href']})
            jsonObj['connList'] = connList

            tmDataList.append(jsonObj)

    return tmDataList


# 获取专利信息
def getPatentData(companyName):
    patentDataList = []
    # url 中 t401:商标信息, t402:专利信息, t403:软件著作权, t404:网站备案
    searchUrl = 'https://www.tianyancha.com/search/t402?key=' + companyName

    totalPage = getTotalPage(searchUrl)

    for page in range(1, totalPage + 1):
        searchUrl = 'https://www.tianyancha.com/search/t402/p{}?key={}'.format(page, companyName)
        response = askURL(searchUrl)
        bs = BeautifulSoup(response, "html.parser")

        tagList = bs.find_all('script', class_='dataInfo')
        for item in tagList:
            jsonObj = json.loads(item.string)

            # 关联企业列表提取
            connList = []
            for item2 in jsonObj['connList']:
                comTag = BeautifulSoup(item2, "html.parser")
                connList.append({'comName': comTag.string, 'comLink': comTag.a['href']})
            jsonObj['connList'] = connList

            try:
                jsonObj['agency']
            except KeyError:
                jsonObj['agency'] = ''

            try:
                jsonObj['imgUrl']
            except KeyError:
                jsonObj['imgUrl'] = ''

            try:
                jsonObj['lprs']
            except KeyError:
                jsonObj['lprs'] = ''

            patentDataList.append(jsonObj)

    return patentDataList


# 获取软件著作权信息
def getSCData(companyName):
    scDataList = []
    # url 中 t401:商标信息, t402:专利信息, t403:软件著作权, t404:网站备案
    searchUrl = 'https://www.tianyancha.com/search/t403?key=' + companyName

    totalPage = getTotalPage(searchUrl)

    for page in range(1, totalPage + 1):
        searchUrl = 'https://www.tianyancha.com/search/t403/p{}?key={}'.format(page, companyName)
        response = askURL(searchUrl)
        bs = BeautifulSoup(response, "html.parser")

        tagList = bs.find_all('script', class_='dataInfo')
        for item in tagList:
            jsonObj = json.loads(item.string)

            # 关联企业列表提取
            connList = []
            for item2 in jsonObj['connList']:
                comTag = BeautifulSoup(item2, "html.parser")
                connList.append({'comName': comTag.string, 'comLink': comTag.a['href']})
            jsonObj['connList'] = connList

            scDataList.append(jsonObj)

    return scDataList


# 获取网站备案信息
def getWRData(companyName):
    wrDataList = []
    # url 中 t401:商标信息, t402:专利信息, t403:软件著作权, t404:网站备案
    searchUrl = 'https://www.tianyancha.com/search/t404?key=' + companyName

    totalPage = getTotalPage(searchUrl)

    for page in range(1, totalPage + 1):
        searchUrl = 'https://www.tianyancha.com/search/t404/p{}?key={}'.format(page, companyName)
        response = askURL(searchUrl)
        bs = BeautifulSoup(response, "html.parser")

        tagList = bs.find_all('div', class_='search_result_type')
        for item in tagList:
            jsonObj = json.loads(item.find('script', class_='dataInfo').string)

            # 关联企业列表提取
            connList = []
            for item2 in jsonObj['connList']:
                comTag = BeautifulSoup(item2, "html.parser")
                connList.append({'comName': comTag.string, 'comLink': comTag.a['href']})
            jsonObj['connList'] = connList

            # 状态信息提取
            jsonObj['status'] = item.select('div.row_3 div.item-right.item-fix span')[0].string

            wrDataList.append(jsonObj)

    return wrDataList


# 发送请求获取响应
def askURL(url):
    # 解决url中的中文编码问题
    url = quote(url, safe=string.printable)

    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36"
    }
    req = request.Request(url, headers=header)
    response = request.urlopen(req)

    return response.read()


if __name__ == '__main__':
    # 由于未收到题目中的企业名称附表，使用下方列表模拟
    comList = ['云南白药集团股份有限公司', '北京字节跳动网络技术有限公司', '腾讯科技（深圳）有限公司']
    # 提取天眼查数据到数据库
    getData(comList)
    # 按模块评估数据并存入数据库
    evaData(comList)
    # 将评估数据标准化
    standScore()
