import requests,json,random,rsa,re
import Comm
from const import *
from pprint import pprint
import urllib.parse

'''
ZSZQ接口类
'''
class api():

    def __init__(self,username,password):
        self.conn = requests.session()
        self.username = username
        self.__password = password
        self.__mobileKey=Comm.getRandom(10)
        self.__aes_key='' # 可以从网页获取
        self.__entrust_way=''
        self.__branch_no=''
        self.conn.cookies['ip']=IP
        self.conn.cookies['mac']=MAC+'_'
        self.conn.cookies['hardInfo']=HARD_INFO
        self.conn.cookies['cpuId']=CPUID
        self.conn.cookies['hostName']=HOST_NAME

        self.__get_configuration()

    '''
    登陆
    '''
    def login(self):
        conn=self.conn
        x_axis=self.__get_mv_pic_pos()
        isT,result=self.__get_rsa_para()
        if not isT:
            return False,result
        e=result['publicExponent']
        n=result['modulus']
        pw=Comm.rsaEncrypt(self.__password.encode('utf-8'),n,e)

        conn.cookies['modulus']=n
        conn.cookies['publicExponent']=e

        sj=servlet_json(conn)
        sj.postdata={
            'funcNo':300100,
            'entrust_way':self.__entrust_way,
            'branch_no':'',
            'input_type':0,
            'input_content':self.username,
            'op_station':OP_STATION,
            'password':'encrypt_rsa%3A'+pw,
            'content_type':'',
            'auth_type':'',
            'auth_source':'',
            'auth_key':'',
            'auth_bind_station':'0%257C%2520%257C00155d022001_%257CST9750420AS(W60SQ4RB)%257C%2520%257Cpc%257C%2520%257Cpc%257Cwt',
            'op_source':0,
            'ticket':x_axis,
            'mobileKey':self.__mobileKey,
            'ticketFlag':0,
        }
        logResult=sj.post()
        if logResult['error_no']!='0':
            return False,logResult['error_info']

        return True,logResult['results']

    '''
    获取资金账户信息
    '''
    def get_balance(self):
        funcNo='301504'
        sj=servlet_json(self.conn)
        sj.postdata={
            'funcsb':urllib.parse.quote(Comm.aesEncrypt(self.__aes_key,funcNo+'*'+self.username)),
            'funcNo':funcNo,
            'fund_account':self.username,
            'entrust_way':self.__entrust_way,
            'branch_no':'25',
            'cust_code':self.username,
            'password':'',
            'op_station':OP_STATION,
            'sessionid':'',
            'money_type':'',
            'op_source':'',
        }
        logResult=sj.post()
        if logResult['error_no']!='0':
            return False,logResult['error_info']
        return True,logResult['results'][0]

    '''
    登陆前获取相关全局参数信息
    '''
    def __get_configuration(self):
        url="https://web.stocke.com.cn/configuration.js?v=1.0.6-1568549474216"
        response=self.conn.get(url)
        self.__aes_key=re.findall('"my":"(.*?)"', response.text, re.M | re.I | re.S)[0]
        self.__entrust_way=re.findall('"entrust_way":"(.*?)"', response.text, re.M | re.I | re.S)[0]

    '''
    获取登陆所用图片移动模块位置信息
    '''
    def __get_mv_pic_pos(self):
        mobileKey=self.__mobileKey
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

        response = self.conn.get(url=url, headers=headers)
        logResult = json.loads(response.text)
        if 'x_axis' in logResult:
           return logResult['x_axis']
        return False

    '''
    获取登陆所用RSA的公钥信息
    '''
    def __get_rsa_para(self):
        sj=servlet_json(self.conn)
        sj.postdata={'funcNo':'1000000','op_station':OP_STATION}
        logResult=sj.post()
        if logResult['error_no']!='0':
            return False,logResult['error_info']
        return True,logResult['results'][0]


'''
/servlet/json 接口类
'''
class servlet_json():

    def __init__(self,conn):
        self.conn=conn
        self.url="https://web.stocke.com.cn/servlet/json"
        self.headers={
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-Hans-CN,zh-Hans;q=0.5",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko",
            "Referer": "https://web.stocke.com.cn/deskProduct/views/login.html",
            'X-Requested-With': 'XMLHttpRequest',
            "Connection": "keep-alive",
            "Host": "web.stocke.com.cn",
        }
        self.postdata={}

    def post(self):
        response=self.conn.post(url=self.url,data=self.postdata,headers=self.headers)
        return json.loads(response.text)