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
import config
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.by import By
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options

Keywords = config.Keywords3
Journals = config.Journals

def get_papers(pages, Ts, wf):
    docs = range(1,11)
    for page in [pages]:
        for doc in docs:
            try:
                params = {'product': 'UA',
                          'search_mode': 'AdvancedSearch',
                          'qid': '1',
                          'SID': '6BEGcONYvx9UwsFqcjJ',
                          'page': page,
                          'doc': doc+10*page}
                headers = {'Connection': 'keep-alive',
                           'Cache-Control': 'max-age=0',
                           'Upgrade-Insecure-Requests': '1',
                           'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36',
                           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                           'Sec-Fetch-Site': 'same-origin',
                           'Sec-Fetch-Mode': 'navigate',
                           'Sec-Fetch-User': '?1',
                           'Sec-Fetch-Dest': 'document',
                           # 'Referer': 'https://vpns.jlu.edu.cn/http/77726476706e69737468656265737421f1e7518f69276d52710e82a297422f30a0c6fa320a29ae/summary.do?product=UA&doc=1&qid=1&SID=5DBpNAh2XO1RiRuktE5&search_mode=AdvancedSearch&update_back2search_link_param=yes',
                           'Accept-Language': 'zh-CN,zh;q=0.9',
						   # 这里得Cookies需要修改成自己登录后的Cookies
                           'Cookie': 'remember_token=cGomHwzZHlXaNRRaojffCTmArGaQSybzZmZmgbwMRHwdDFZcsgQLPPfyvXWGGoWX; wengine_vpn_ticket=b96dc49f3eda90d9; refresh=0'}
				# 因为是从我学校的vpn登录的，所以这里需要改成自己的能够登录的网站
                url = 'https://vpns.jlu.edu.cn/http/77726476706e69737468656265737421f1e7518f69276d52710e82a297422f30a0c6fa320a29ae/full_record.do'
                htm1 = requests.get(url, headers=headers, params=params, verify=False)
                soup = BeautifulSoup(htm1.text, 'html.parser')
                title = soup.find('div', attrs={'class':'title'}).text
                if title not in Ts:  # 已经爬取过的文章跳过
                    abstract = soup.find('div', text='摘要').find_next().text
                    keywords = soup.find('div', text='关键词').find_next().text
                    journal = soup.find('span', attrs={'class':'hitHilite'}).text
                    print(page, doc, title, sep='    ')
                    wf.write("<Inner>".join([title, abstract, keywords, journal]).replace('\n','')+'\n')
            except:
                traceback.print_exc()
                time.sleep(3)
                continue


# def get_cookies(search_command):    # 根据高级检索的结果动态获取Cookies
#     chrome_opt = Options()      # 创建参数设置对象.
#     # chrome_opt.add_argument('--headless')   # 无界面化.
#     # chrome_opt.add_argument('--disable-gpu')    # 配合上面的无界面化.
#     chrome_opt.add_argument('--window-size=1366,768')   # 设置窗口大小, 窗口大小会有影响.
#     # 创建Chrome对象并传入设置信息.
#     driver = webdriver.Chrome(chrome_options=chrome_opt, executable_path='D:/program/chromedriver.exe')
#     driver.get('https://vpns.jlu.edu.cn/http/77726476706e69737468656265737421a2a713d27669301e2c5dc7fe/plus/link_view.aspx?id=166')     # get方式访问简书.
#     driver.find_element_by_id('user_name').send_keys(config.username)
#     driver.find_element_by_name('password').send_keys(config.password)
#     driver.find_element_by_class_name('el-button-login').click()
#     # 登录完毕
#     WebDriverWait(driver, 100).until(
#         EC.presence_of_element_located((By.XPATH, '/html/body/div[9]/div/ul/li[3]/a')))
#     driver.find_element_by_xpath('/html/body/div[9]/div/ul/li[3]/a').click()
#     WebDriverWait(driver, 100).until(
#         EC.presence_of_element_located((By.XPATH, '/html/body/form[1]/div[1]/table/tbody/tr/td[1]/div[2]/textarea')))
#     driver.find_element_by_xpath('/html/body/form[1]/div[1]/table/tbody/tr/td[1]/div[2]/textarea').send_keys(search_command)
#     driver.find_element_by_xpath('/html/body/form[1]/div[1]/table/tbody/tr/td[1]/div[2]/div[1]/table/tbody/tr/td[1]/span[1]/button').click()
#     # 等待检索结果出现
#     WebDriverWait(driver, 100).until(
#             EC.presence_of_element_located((By.XPATH, '/html/body/div[13]/form/table/tbody/tr[3]/td[2]/div/a')))
#     a = driver.find_element_by_xpath('/html/body/div[13]/form/table/tbody/tr[3]/td[2]/div/a')
#     paper_number = a.text    # 返回论文的检索结果数量
#     a.click()
#     print(driver.get_log('browser'))
#     print(driver.get_log('driver'))
#     print(driver.get_log('client'))
#     print(driver.get_log('server'))
#     # driver.quit()  # 使用完, 记得关闭浏览器, 不然chromedriver.exe进程为一直在内存中.
#     time.sleep(100000)
#     return paper_number

def check_titles():    # 判断当前爬取的论文是否已经存在，存在则跳过
    Ts = []
    files = os.listdir('Results')
    for file in files:
        with open('Results/'+file, 'r', encoding='utf-8') as rf:
            Ts.extend([line.strip().split('<Inner>')[0] for line in rf.readlines()])
    print('已经爬取：', len(Ts))
    return Ts


def generate_command(id):
    Ks,Js = [],[]
    Ks = ' OR '.join(['TS='+K for K in Keywords[1:]])
    Ks = '('+Ks+')'
    for J in Journals:
        J = "SO="+J
        Js.append(J)
    commands = []
    for J in Js:
        commands.append(Ks+' AND '+J)
    print(commands[id])  #

def generate_command2(TS = 'neoliberal globalization'):
    Command = 'TS = '+TS + 'AND'
    Js = []
    for J in Journals:
        J = "SO="+J
        Js.append(J)
    print(' OR '.join(Js))


if __name__ == '__main__':
    id = 7
    Ts = check_titles()
    threads = []    # 存放多线程
    all_pages = int(2933/10) + 1
    wf = open('Results/{}.txt'.format('journal'+str(id+1)), 'a', encoding='utf-8')
    for i in range(100, all_pages):
        threads.append(threading.Thread(target=get_papers, args=(i,Ts,wf)))
    num = 0
    while num <= len(threads):
        if threading.activeCount() <= 6:   # 最大线程数小于6
            threads[num].start()
            num += 1
        else:
            time.sleep(10)    # 否则我休眠十秒去执行线程

