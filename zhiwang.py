import requests
import re
from bs4 import BeautifulSoup
import pandas as pd
import os
from ctypes import cdll
import threading
import traceback
import tqdm   # 进度条
import time
import json
import pickle
import pymysql
import re

journal_list = ['管理世界', '中国农村经济', '科学学与科学技术管理', '预测', '农业经济问题', '中国工业经济',
'金融研究', '科研管理', '科学学研究', '研究与发展管理', '管理工程学报', '管理评论', '中国软科学',
'工业工程与管理', '数量经济技术经济研究', '管理科学学报', '中国管理科学', '南开管理评论', '系统工程',
'中国人口·资源与环境', '运筹与管理', '系统工程理论与实践', '管理科学', '管理学报', '数理统计与管理',
'系统管理学报', '公共管理学报', '系统工程学报', '会计研究']

journal_code = ["GLSJ","ZNJJ","KXXG","YUCE","NJWT","GGYY","JRYJ","KYGL","KXYJ","YJYF","GLGU","ZWGD","ZGRK","GYGC",
"SLJY","JCYJ","ZGGK","LKGP","GCXT","ZGRZ","YCGL","XTLL","JCJJ","GLXB","SLTJ","XTGL","GGGL","XTGC","KJYJ"]

keywords = [
'数字创新',
'数字平台',
'数字基础设施',
'数字生态系统',
'商业模式创新',
'数字功能可见性',
'数字创业',
'数字经济',
'数字创业生态系统',
'数字转型',
'数字化',
'数字化决策',
'共享决策',
'数字证据',
'数字取证',
'决策知识共享',
'数字商业生态系统',
'数字转型战略',
'数字商业网络',
'数据驱动的决策支持',
'数字化战略',
'数字产品',
'数字化产品创新',
'数字化过程创新',
'数字化营销',
'数字化技术',
'数字化资产',
'数字化新创企业',
'数字化金融',
'金融科技',
'数字化革命',
'数字化商业模式',
'数字化创业过程',
'平台战略',
'数字创业者',
'数字化机会',
'数字创新理论',
'价值共创',
'组织柔性',
'虚拟团队',
'数字能力',
'自生长性',
'数字化逻辑',
'数字多边平台',
'数字化赋能',
'数字化动态能力',
'数字化初创企业'
]

header={'Connection':'Keep-Alive',
                 'Accept':'text/html,*/*',
                 'User-Agent':'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.66 Safari/537.36',
        'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
        # 'Referer':'http://navi.cnki.net/KNavi/JournalDetail?pcode=CJFD&pykm=GLSJ',
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'
        # 'Cookie': 'Ecp_ClientId=2200210174601303834; RsPerPage=20; cnkiUserKey=814a1a67-effa-b5af-9db6-3b38894d2622; Ecp_IpLoginFail=200602125.223.253.2; ASP.NET_SessionId=qudz13gpalld1xpiq2antz3w; SID_kns=123105; SID_klogin=125143; SID_crrs=125132; KNS_SortType=; _pk_ref=%5B%22%22%2C%22%22%2C1591103026%2C%22https%3A%2F%2Fwww.cnki.net%2F%22%5D; _pk_ses=*; SID_krsnew=125134; SID_kns_new=kns123117'
        }
params = {
    'pcode': 'CJFD',
    'baseId': 'GLSJ',   # 需要根据期刊修改
    'where': '%28SU%25%27%7B0%7D%27%29',   # 不要修改
    'searchText': '创业研究',   # 根据检索关键词修改
    'condition':'',
    'orderby': 'RT',
    'ordertype': 'DESC',
    'scope':'',
    'pageIndex': 0,   # 在遍历的时候修改,0表示第一页
    'pageSize': 50   #
}

def get_search_page_link():
    with open('./数字创业/links.txt', 'a', encoding='utf-8') as wf:
        for journal in journal_code:
            print(journal)
            for keyword in keywords:
                print(keyword)
                params['baseId'] = journal
                params['searchText'] = keyword
                path = 'http://navi.cnki.net/knavi/JournalDetail/GetArticleDataXsltByInternalSearch'
                htm1 = requests.get(path, headers=header, params=params)
                soup = BeautifulSoup(htm1.text, 'html.parser')
                links = soup.find_all('td', attrs={'class':'name'})
                for link in links:
                    href = link.find('a')
                    if href:
                        href = href['href']
                        wf.write(href.strip()+'\n')
                        wf.flush()
                        print(href.strip())
# get_search_page_link()

# 通过连接获取数据

def get_papers():
    files = []
    file = open('./数字创业/papers.txt', 'w', encoding='utf-8')
    with open('./数字创业/links.txt', 'r', encoding='utf-8') as rf:
        for line in rf.readlines():
            name = re.findall('&fileName=.+?&', line.strip())[0]
            url = 'https://kns.cnki.net/kcms/detail/detail.aspx?dbcode=CJFD' + name[:-1]
            if url not in files:
                files.append(url)
        print(len(files), files)
        for url in files:
            htm1 = requests.get(url)
            soup = BeautifulSoup(htm1.text, 'html.parser')
            title = soup.find('title').text.strip()
            abstract = soup.find('span', attrs={'id':'ChDivSummary'})
            if abstract is None:
                abstract = ''
            else:
                abstract = abstract.text.strip()
            keyword = soup.find('p', attrs={'class':'keywords'})
            ks = []
            if keyword is not None:
                keyword = keyword.find_all('a')
                for each in keyword:
                    ks.append(each.text.strip())
                ks = ''.join(ks).replace('\n', '')
            else:
                ks = ""   # 没有关键词
            print(title, url, ks)
            file.write('<Inner>'.join([title,abstract,ks,url])+'\n')
            file.flush()
            # time.sleep(0.1)
    file.close()
get_papers()