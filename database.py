# -*- coding = utf-8 -*-
# @TIME : 2021/4/13 10:29
# @Author : Eric Ma
# @File : database.py
# @Software : PyCharm

import sqlite3


# 存储商标信息
def saveTmData(dataList):
    for item in dataList:
        connComList = []
        for comInfo in item['connList']:
            connComList.append({'name': comInfo['comName'], 'link': comInfo['comLink']})

        # 添加数据到数据库，如果当前数据存在则不做操作
        sql = '''
        insert or ignore into trademark_info (regNo, tmName, tmPic, tmClassNo, tmClassText, status, appCom, appDate, connComList) 
        values ("{}","{}","{}","{}","{}","{}","{}","{}","{}")
        '''.format(item['regNo'], item['tmName'], item['tmPic'], item['tmClass'], item['intCls'], item['status'],
                   item['applicantCn'], item['appDate'], str(connComList))

        conn = sqlite3.connect('Company_Info.db')
        cursor = conn.cursor()
        cursor.execute(sql)
        # print('商标名称:{}, 注册号:{}  存储完成'.format(item['tmName'], item['regNo']))
        conn.commit()
        conn.close()


# 存储专利信息
def savePatentData(dataList):
    for item in dataList:
        connComList = []
        for comInfo in item['connList']:
            connComList.append({'name': comInfo['comName'], 'link': comInfo['comLink']})

        # 添加数据到数据库，如果当前数据存在则不做操作
        sql = '''
        insert or ignore into patent_info (patentNo, patentName, appNo, appTime, appComList, appPublishNo, appPublishTime, connComList, 
                                            latestLegalStatus, abstracts, agency, imgUrl) 
        values ("{}","{}","{}","{}",'{}',"{}","{}","{}","{}","{}","{}","{}")
        '''.format(item['patentNum'], item['patentName'], item['appnumber'], item['applicationTime'],
                   item['applicantName'], item['applicationPublishNum'],
                   item['applicationPublishTime'], str(connComList), item['lprs'], item['abstracts'], item['agency'],
                   item['imgUrl'])

        conn = sqlite3.connect('Company_Info.db')
        cursor = conn.cursor()
        cursor.execute(sql)
        # print('专利名称:{}, 申请号:{}  存储完成'.format(item['patentName'], item['appnumber']))
        conn.commit()
        conn.close()


# 存储软件著作权信息
def saveSCData(dataList):
    for item in dataList:
        connComList = []
        for comInfo in item['connList']:
            connComList.append({'name': comInfo['comName'], 'link': comInfo['comLink']})

        # 添加数据到数据库，如果当前数据存在则不做操作
        sql = '''
        insert or ignore into soft_copyright (regNo, fullName, simpleName, regTime, catNo, appCom, publishTime, version, connComList) 
        values ("{}","{}","{}","{}","{}","{}","{}","{}","{}")
        '''.format(item['regnum'], item['fullname'], item['simplename'], item['regtime'], item['catnum'],
                   item['authorNationality'],
                   item['publishtime'], item['version'], str(connComList))

        conn = sqlite3.connect('Company_Info.db')
        cursor = conn.cursor()
        cursor.execute(sql)
        # print('软件名称:{}, 登记号:{}  存储完成'.format(item['fullname'], item['regnum']))
        conn.commit()
        conn.close()


# 存储网站备案信息
def saveWRData(dataList):
    for item in dataList:
        connComList = []
        for comInfo in item['connList']:
            connComList.append({'name': comInfo['comName'], 'link': comInfo['comLink']})

        # 添加数据到数据库，如果当前数据存在则不做操作
        sql = '''
        insert or ignore into website_records (id, icpId, liscense, webName, website, domain, examineDate, appComId, appComName, appComType, connComList, status) 
        values ("{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}")
        '''.format(item['id'], item['icpId'], item['liscense'], item['webName'], item['webSite'], item['ym'],
                   item['examineDate'], item['companyId'], item['companyName'], item['companyType'], str(connComList),
                   item['status'])

        conn = sqlite3.connect('Company_Info.db')
        cursor = conn.cursor()
        cursor.execute(sql)
        # print('软件名称:{}, 登记号:{}  存储完成'.format(item['fullname'], item['regnum']))
        conn.commit()
        conn.close()


# 评估四项数据，得分存入数据库
def evaData(comNameList: list):
    print('开始进行模块评估...')
    dataList = []
    conn = sqlite3.connect('Company_Info.db')
    cursor = conn.cursor()
    for comName in comNameList:
        print('开始评估 {} 数据...'.format(comName))
        tmScore = getTmScore(comName)
        patentScore = getPatentScore(comName)
        scScore = getSCScore(comName)
        wrScore = getWRScore(comName)

        dataList.append({'comName': comName, 'tmScore': tmScore, 'patentScore': patentScore,
                         'scScore': scScore, 'wrScore': wrScore})
        sql = 'select * from company_score where comName="{}"'.format(comName)
        res = cursor.execute(sql)
        if len(res.fetchall()) == 0:
            sql = '''
                    insert into company_score (comName, tmScore, patentScore, scScore, wrScore) 
                    values ("{}",{},{},{},{})
                    '''.format(comName, tmScore, patentScore, scScore, wrScore)
        else:
            sql = '''
                update company_score set tmScore={}, patentScore={}, scScore={}, wrScore={}
                where comName="{}"
            '''.format(tmScore, patentScore, scScore, wrScore, comName)
        cursor.execute(sql)
        conn.commit()
        print('{} 数据评估完成！'.format(comName))

    conn.close()
    print('模块评估结束.')


# 获取数据表中全部企业列表
def getAllCom():
    sql = '''
    select distinct appCom from trademark_info
    '''
    conn = sqlite3.connect('Company_Info.db')
    cursor = conn.cursor()
    res = cursor.execute(sql)
    comList = []
    for row in res:
        comList.append(row[0])
    conn.close()

    return comList


# 评估商标信息得分
def getTmScore(comName):
    scoreDict = {'未公开': 1, '申请收文': 2, '等待注册证发文': 1, '等待驳回复审': 1, '打印驳回通知': 1, '等待打印注册证': 1, '变更商标': -2,
                 '异议复审': 1, '商标转让': -10, '商标异议申请': 1, '打印注册证': 2, '连续三年停止使用注册商标': -8, '撤销连续三年停止使用注册商标': 2,
                 '商标续展': 3, '等待实质审查': 1}
    totalScore = 0
    sql = '''
        select regNo, status from trademark_info where appCom="{}"
    '''.format(comName)
    conn = sqlite3.connect('Company_Info.db')
    cursor = conn.cursor()
    res = cursor.execute(sql)
    for row in res:
        totalScore += scoreDict[row[1]]
    conn.close()

    return totalScore


# 评估专利信息得分
def getPatentScore(comName):
    scoreDict = {'实质审查的生效': 2, '公开': 3, '授权': 5, '专利申请权、专利权的转移专利权的转移': -1, '专利权的终止(未缴年费专利权终止)': -5,
                 '专利权人的姓名或者名称、地址的变更': -1, '实质审查': 2, '': 0}
    totalScore = 0
    sql = '''
            select patentNo, latestLegalStatus from patent_info where connComList like '%{}%'
        '''.format(comName)
    conn = sqlite3.connect('Company_Info.db')
    cursor = conn.cursor()
    res = cursor.execute(sql)
    for row in res:
        totalScore += scoreDict[row[1]]
    conn.close()

    return totalScore


# 评估软件著作得分
def getSCScore(comName):
    sql = '''
                select regNo from soft_copyright where connComList like '%{}%'
            '''.format(comName)
    conn = sqlite3.connect('Company_Info.db')
    cursor = conn.cursor()
    res = cursor.execute(sql)
    totalScore = len(res.fetchall())
    conn.close()

    return totalScore


# 评估网站备案得分
def getWRScore(comName):
    sql = '''
                    select id from website_records where connComList like '%{}%'
                '''.format(comName)
    conn = sqlite3.connect('Company_Info.db')
    cursor = conn.cursor()
    res = cursor.execute(sql)
    totalScore = len(res.fetchall())
    conn.close()

    return totalScore


# 将企业模块评分标准化
def standScore():
    conn = sqlite3.connect('Company_Info.db')
    cursor = conn.cursor()
    sql = '''
        SELECT MAX(tmScore), MAX(patentScore), MAX(scScore), MAX(wrScore) FROM company_score
    '''
    res = cursor.execute(sql).fetchall()[0]

    # 各模块TOP1的企业得分
    maxTmScore = res[0]
    maxPatentScore = res[1]
    maxSCScore = res[2]
    maxWRScore = res[3]

    sql = '''
        UPDATE company_score SET tmScore = tmScore/{}.0, patentScore = patentScore/{}.0, scScore = scScore/{}.0, wrScore = wrScore/{}.0
    '''.format(maxTmScore, maxPatentScore, maxSCScore, maxWRScore)
    cursor.execute(sql)

    conn.commit()
    conn.close()
    print('模块评分标准化完成!')
