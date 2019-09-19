import requests,json,random,rsa
import Comm
from pprint import pprint
import urllib.parse
class api():
    def __init__(self,username,password):
        self.username = username
        self.password = password
        self.conn = requests.session()

    def login(self):
        conn=self.conn
        mobileKey=int(random.random()*10000000000)
        width=282
        height=130
        url="https://web.stocke.com.cn/servlet/SlidingBlockImage?r=%d&mobileKey=%d&width=%d&height=%d"%(mobileKey,mobileKey,width,height)
        headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-Hans-CN,zh-Hans;q=0.5",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko",
            "Referer": "https://web.stocke.com.cn/deskProduct/views/login.html",
            'X-Requested-With': 'XMLHttpRequest',
            "Connection": "keep-alive",
            "Host": "web.stocke.com.cn",
        }
        conn.cookies['ip']='192.168.137.1'
        conn.cookies['mac']='00155d022001_'
        conn.cookies['hardInfo']='ST9750420AS(W60SQ4RB)'
        conn.cookies['cpuId']='BFCBFBFF000206A70000000000000000'
        conn.cookies['hostName']='DESKTOP-K9D3HRB'
        response = conn.get(url=url, headers=headers)
        logResult = json.loads(response.text)
        x_axis=logResult['x_axis']
        url="https://web.stocke.com.cn/servlet/json"
        postdata={'funcNo':'1000000','op_station':'0%7C192.168.137.1%7C00155d022001%7CST9750420AS(W60SQ4RB)%7CBFCBFBFF000206A70000000000000000%7C%20%7CDESKTOP-K9D3HRB%7C192.168.137.1%7C1.0.6'}
        response = conn.post(url=url,data=postdata, headers=headers)
        logResult = json.loads(response.text)
        if logResult['error_no']=='0':
            publicExponent=logResult['results'][0]['publicExponent']
            modulus=logResult['results'][0]['modulus']
            print({'x_axis':x_axis,'publicExponent':publicExponent,'modulus':modulus})
        pw=Comm.rsaEncrypt(self.password.encode('utf-8'),modulus,publicExponent)

        conn.cookies['modulus']=modulus
        conn.cookies['publicExponent']=publicExponent
        url='https://web.stocke.com.cn/servlet/json'
        postdata={
            'funcNo':300100,
            'entrust_way':6,
            'branch_no':'',
            'input_type':0,
            'input_content':self.username,
            'op_station':'0%257C192.168.137.1%257C00155d022001%257CST9750420AS(W60SQ4RB)%257CBFCBFBFF000206A70000000000000000%257C%2520%257CDESKTOP-K9D3HRB%257C192.168.137.1%257C1.0.6',
            'password':'encrypt_rsa%3A'+pw,
            'content_type':'',
            'auth_type':'',
            'auth_source':'',
            'auth_key':'',
            'auth_bind_station':'0%257C%2520%257C00155d022001_%257CST9750420AS(W60SQ4RB)%257C%2520%257Cpc%257C%2520%257Cpc%257Cwt',
            'op_source':0,
            'ticket':x_axis,
            'mobileKey':mobileKey,
            'ticketFlag':0,
        }
        response = conn.post(url=url,data=postdata, headers=headers)
        logResult = json.loads(response.text)
        pprint(logResult)

        url='https://web.stocke.com.cn/servlet/json'
        postdata={
            'funcsb':urllib.parse.quote(Comm.aesEncrypt('B49A86FA425D439','301504*'+'1320011172')),
            'funcNo':"301504",
            'fund_account':'1320011172',
            'entrust_way':'6',
            'branch_no':'25',
            'cust_code':'1320011172',
            'password':'',
            'op_station':'0%257C192.168.137.1%257C00155d022001%257CST9750420AS(W60SQ4RB)%257CBFCBFBFF000206A70000000000000000%257C%2520%257CDESKTOP-K9D3HRB%257C192.168.137.1%257C1.0.6',
            'sessionid':'',
            'money_type':'',
            'op_source':'',
        }
        response = conn.post(url=url,data=postdata, headers=headers)
        logResult = json.loads(response.text)
        pprint(logResult)