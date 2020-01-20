# Author: gnsJhenJie (github.com/gnsJhenJie)
# Jan 2020

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

import random

def tnfshnew():
    reply = ''
    url = 'https://www.tnfsh.tn.edu.tw/files/501-1000-1012-1.php?Lang=zh-tw'
    resp = requests.get(url) #取得網頁原始碼
    resp.encoding = 'utf8' #轉編碼，才不會出現亂碼
    soup = BeautifulSoup(resp.text, 'html.parser') #利用BeautifulSoup轉換成該套件格式
    sesoup = soup.find_all('span', 'ptname', limit=5) #尋找訊息，且限制最多5項資料

    for i in range(5):
        reply += str(i+1) + '.'
        reply += sesoup[i].find('a').string.strip('\n').strip('\t').strip(' ') #取得最新訊息文字內容
    reply += '\n取得更多資訊請見一中網站'
    return reply

def absent_query(tnfsh_class, tnfsh_number, day):  #Query single day
    url = 'https://sp.tnfsh.tn.edu.tw/attend/index.php/attend/search?begin='+day+'&end='+day+'&class='+tnfsh_class+'&num='+tnfsh_number
    html = urllib.request.urlopen(url).read()
    count_absent = str(html).count('btn-danger')
    count_late = str(html).count('btn-warning')
    count_leave = str(html).count('btn-info')
    return count_absent, count_late, count_leave

# Flask app should start in global layout
app = Flask(__name__)

@app.route("/", methods=['GET'])
def hello():
    return "Hello World!"

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)
    print("Request:")
    print(json.dumps(req, indent=4))

    res = makeWebhookResult(req)

    res = json.dumps(res, indent=4)
    print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

def makeWebhookResult(req):
    if req.get("queryResult").get("action") == "query_news":
        result = req.get("queryResult")
        parameters = result.get("parameters")
        speech = tnfshnew() + '\n若還想查詢缺席請說「查詢缺席」，結束和南一中小幫手的對話請說「掰掰」'
        print("Response:")
        print(speech)
        #回傳
        return {
            'fulfillmentText':speech
        }
    elif req.get("queryResult").get("action") == "query_absentee":
        message_to_send = ''

        result = req.get("queryResult")
        parameters = result.get("parameters")
        tnfsh_class = str(parameters.get('grade')).replace('一','1') + str(parameters.get('class')).replace('十一','11').replace('十二','12').replace('十三','13').replace('十四','14').replace('十五','15').replace('十六','16').replace('十七','17').replace('十八','18').replace('十九','19').replace('一','1').replace('二','2').replace('三','3').replace('四','4').replace('五','5').replace('六','6').replace('七','7').replace('八','8').replace('九','9').replace('十','10')
        tnfsh_number = str(parameters.get('number'))
        date_today = datetime.now().date().strftime("%Y-%m-%d")
        date_p1 = (datetime.now() + timedelta(days = -1)).strftime("%Y-%m-%d")
        date_p2 = (datetime.now() + timedelta(days = -2)).strftime("%Y-%m-%d")
        #Check today
        count_absent_today, count_late_today, count_leave_today = absent_query(tnfsh_class, tnfsh_number, date_today)
        #Check p1 day
        count_absent_p1, count_late_p1, count_leave_p1 = absent_query(tnfsh_class, tnfsh_number, date_p1)
        #Check p2 day
        count_absent_p2, count_late_p2, count_leave_p2 = absent_query(tnfsh_class, tnfsh_number, date_p2)
        #Deal message_to_send
        message_to_send = ''
        if count_absent_today == 0:
            message_to_send += '查無本日缺席\n'
        else:
            message_to_send += '你今天共缺席'+str(count_absent_today)+'節課\n'
        if count_late_today > 0:
            message_to_send += '你今天共遲到'+str(count_late_today)+'節課\n'
        if count_leave_today > 0:
            message_to_send += '你今天共早退'+str(count_leave_today)+'節課\n'
        if count_absent_p1 == 0:
            message_to_send += '查無昨天缺席\n'
        else:
            message_to_send += '你昨天共缺席'+str(count_absent_p1)+'節課\n'
        if count_late_p1 > 0:
            message_to_send += '你昨天共遲到'+str(count_late_p1)+'節課\n'
        if count_leave_p1 >0:
            message_to_send += '你昨天共早退'+str(count_leave_p1)+'節課\n'
        if count_absent_p2 == 0:
            message_to_send += '查無前天缺席\n'
        else:
            message_to_send += '你前天共缺席'+str(count_absent_p2)+'節課\n'
        if count_late_p2 > 0:
            message_to_send += '你前天共遲到'+str(count_late_p2)+'節課\n'
        if count_leave_p2 > 0:
            message_to_send += '你前天共早退'+str(count_leave_p2)+'節課\n'
        if count_absent_today + count_late_today + count_leave_today + count_absent_p1 + count_late_p1 + count_leave_p1 + count_absent_p2 + count_late_p2 + count_leave_p2 >0 :
            message_to_send += '快去看看哪節課被記吧!'
        message_to_send += '\n想知道南一中首頁訊息請說「查詢最新訊息」,若要離開請跟我說「掰掰」'
            #message_to_send += shorten_url('https://sp.tnfsh.tn.edu.tw/attend/index.php/attend/search?begin='+date_p2+'&end='+date_today+'&class='+tnfsh_class+'&num='+tnfsh_number)
        return {
            'fulfillmentText':message_to_send
        }

if __name__ == "__main__":
    app.run(debug=True,port=80)