import urllib
import json
import os
from datetime import datetime, timedelta, date

from flask import Flask
from flask import request
from flask import make_response

import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import unquote as decode

def tnfshnew():
    reply = ''
    url = 'https://www.tnfsh.tn.edu.tw/files/501-1000-1012-1.php?Lang=zh-tw'
    resp = requests.get(url) #取得網頁原始碼
    resp.encoding = 'utf8' #轉編碼，才不會出現亂碼
    soup = BeautifulSoup(resp.text, 'html.parser') #利用BeautifulSoup轉換成該套件格式
    sesoup = soup.find_all('span', class_='ptname', limit=5) #尋找訊息，且限制最多5項資料
    #print(soup)
    print(sesoup)
    for i in range(5):
        reply += str(i+1) + '.'
        reply += sesoup[i].find('a').string.strip('\n').strip('\t').strip(' ') #取得最新訊息文字內容
        reply += sesoup[i].find('a')['href'].strip('\n').strip('\t').strip(' ') + '\n\n' #取得最新訊息連結
    return reply
print(tnfshnew())