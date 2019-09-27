import requests,json,random,rsa,re,os
import Comm
from const import *
import urllib.parse
import pickle
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
        self.conn.cookies['ip']=IP
        self.conn.cookies['mac']=MAC+'_'
        self.conn.cookies['hardInfo']=HARD_INFO
        self.conn.cookies['cpuId']=CPUID
        self.conn.cookies['hostName']=HOST_NAME
        self.__logInfo={}

        self.__get_configuration()

    '''登陆(300100)'''
    '''
    return:
        {'dsName': ['results'],
         'error_info': '',
         'error_no': '0',
         'results': [{'asset_prop': '0',
           'branch_no': '25',
           'client_name': '***',
           'client_rights': 'Cqt',
           'cust_code': '1320011***',
           'exchange_type': '2',
           'fund_account': '1320011***',
           'fundidtype': '',
           'holder_kind': '0',
           'holder_rights': '',
           'holder_status': '0',
           'jsessionid': 'abcOpfAMhRNXXd0YMPX1w',
           'last_login_time': '2019-09-27 173110',
           'main_flag': '1',
           'risk_flag': '1',
           'risk_level': '4',
           'seat_no': '',
           'secuidtype': '',
           'session_id': '',
           'stock_account': 'A467162***'},
          {'asset_prop': '0',
           'branch_no': '25',
           'client_name': '***',
           'client_rights': 'Cqt',
           'cust_code': '1320011***',
           'exchange_type': '0',
           'fund_account': '1320011***',
           'fundidtype': '',
           'holder_kind': '0',
           'holder_rights': 'j',
           'holder_status': '0',
           'last_login_time': '2019-09-27 173110',
           'main_flag': '1',
           'risk_flag': '1',
           'risk_level': '4',
           'seat_no': '',
           'secuidtype': '',
           'session_id': '',
           'stock_account': '0104977***'}]}

    '''
    def login(self):
        if self.load_objInfo():
            balance=self.get_balance()
            if balance['error_no']=='0':
                print('从%s之前登陆状态登陆'%(self.username))
                return self.__logInfo
            print(self.username+'的历史登陆状态已经失效,重新登陆')

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
        self.__logInfo=logResult
        if logResult['error_no']=='0':
            self.save_objInfo()
        return logResult

    '''退出(3001001)'''
    def logout(self):
        funcNo='3001001'
        sj=servlet_json(self.conn)
        sj.postdata={
        'funcNo':funcNo,
        'fund_account':self.username,
        'entrust_way':self.__entrust_way,
        'branch_no':self.__logInfo['results'][0]['branch_no'],
        'cust_code':self.username,
        'password':'',
        'op_station':OP_STATION,
        'sessionid':'',
        }
        return sj.post()

    '''获取行情服务器时间(29999)'''
    '''
    return:
        {'dsName': ['results'],
         'error_info': '',
         'error_no': '0',
         'results': [[37878, '20190927', '20190927153245', '20190927153740', '0']]}
    '''
    def get_HqState(self):
        funcNo='29999'
        sj=servlet_json(self.conn)
        sj.postdata={
            'funcNo':funcNo,
            'version':1,
        }
        logResult=sj.post()
        return logResult

    '''股东查询(301512)'''
    '''
    return:
        {'dsName': ['results'],
         'error_info': '调用成功',
         'error_no': '0',
         'results': [{'exchange_type': '2',
           'exchange_type_name': '上海A股',
           'holder_kind': '0',
           'holder_rights': '',
           'holder_status': '0',
           'main_flag': '1',
           'stock_account': 'A467162***'},
          {'exchange_type': '0',
           'exchange_type_name': '深圳A股',
           'holder_kind': '0',
           'holder_rights': 'j',
           'holder_status': '0',
           'main_flag': '1',
           'stock_account': '0104977***'}]}
    '''
    def get_Stockholder(self):
        funcNo='301512'
        sj=servlet_json(self.conn)
        sj.postdata={
            'funcNo':funcNo,
            'fund_account':self.username,
            'entrust_way':self.__entrust_way,
            'branch_no':self.__logInfo['results'][0]['branch_no'],
            'cust_code':self.username,
            'password':'',
            'op_station':OP_STATION,
            'sessionid':'',
        }
        return sj.post()

    '''获取开通转帐银行账号(300200)'''
    '''
    获取开通转帐银行账号(300200)
    return:
        {'dsName': ['results'],
         'error_info': '调用成功',
         'error_no': '0',
         'results': [{'bank_account': '8888093001697***',
           'bank_code': '4',
           'bank_name': '建行存管',
           'bkaccount_status': '0',
           'fund_account': '1320011***',
           'money_type': '0'}]}
    '''
    def get_TransferBanks(self):
        funcNo='300200'
        sj=servlet_json(self.conn)
        sj.postdata={
        'funcsb':urllib.parse.quote(Comm.aesEncrypt(self.__aes_key,funcNo+'*'+self.username)),
        'funcNo':funcNo,
        'fund_account':self.username,
        'entrust_way':self.__entrust_way,
        'branch_no':self.__logInfo['results'][0]['branch_no'],
        'cust_code':self.username,
        'password':'',
        'op_station':OP_STATION,
        'sessionid':'',
        'money_type':'',
        'op_source':'',
        }
        return sj.post()

    '''获取资金账户信息(301504)'''
    '''
    return:
        {'dsName': ['results'],
         'error_info': '调用成功',
         'error_no': '0',
         'results': [{'assert_val': '5001.69',
           'current_balance': '5001.69',
           'daily_income_balance': '0.00',
           'enable_balance': '5001.69',
           'fetch_balance': '5001.69',
           'frozen_balance': '0.00',
           'fund_account': '',
           'fund_val': '',
           'market_val': '0.00',
           'money_type': '0',
           'money_type_name': '人民币',
           'total_income_balance': '0.00'}]}
    '''
    def get_balance(self):
        funcNo='301504'
        sj=servlet_json(self.conn)
        sj.postdata={
            'funcsb':urllib.parse.quote(Comm.aesEncrypt(self.__aes_key,funcNo+'*'+self.username),safe=""),
            'funcNo':funcNo,
            'fund_account':self.username,
            'entrust_way':self.__entrust_way,
            'branch_no':self.__logInfo['results'][0]['branch_no'],
            'cust_code':self.username,
            'password':'',
            'op_station':OP_STATION,
            'sessionid':'',
            'money_type':'',
            'op_source':'',
        }
        return sj.post()

    '''证券持仓查询(301503)'''
    '''
    return:
      尚未有成交
    '''
    def get_Positions(self):
        funcNo='301503'
        sj=servlet_json(self.conn)
        sj.postdata={
            'funcsb':urllib.parse.quote(Comm.aesEncrypt(self.__aes_key,funcNo+'*'+self.username),safe=""),
            'funcNo':funcNo,
            'fund_account':self.username,
            'entrust_way':self.__entrust_way,
            'branch_no':self.__logInfo['results'][0]['branch_no'],
            'cust_code':self.username,
            'password':'',
            'op_station':OP_STATION,
            'sessionid':'',
            'money_type':'',
            'op_source':'',
        }
        return sj.post()

    '''获取客户基本信息(300102)'''
    '''
    return:
        {'dsName': ['results'],
         'error_info': '调用成功',
         'error_no': '0',
         'results': [{'address': '******************',
           'client_name': '***',
           'e_mail': ' ',
           'education': '',
           'fax': ' ',
           'full_name': '***',
           'id_address': '*****************',
           'id_begindate': '20140313',
           'id_enddate': '20340313',
           'id_kind': '0',
           'id_no': '*********************',
           'mail_name': ' ',
           'mobile': '1**********',
           'occtype': '',
           'open_date': '20140926',
           'organ_name': '个人',
           'organ_prop': '0',
           'phonecode': '1*********',
           'sex': '0',
           'zipcode': '******'}]}

    '''
    def get_ClientInfo(self):
        funcNo='300102'
        sj=servlet_json(self.conn)
        sj.postdata={
        'funcNo':funcNo,
        'fund_account':self.username,
        'entrust_way':self.__entrust_way,
        'branch_no':self.__logInfo['results'][0]['branch_no'],
        'cust_code':self.username,
        'password':'',
        'op_station':OP_STATION,
        'sessionid':'',
       }
        return sj.post()

    '''股票信息联动(301514) '''
    '''
    in:
       stock_code 股票代码 必填
       entrust_bs 交易方向 必填 【0：买入 |  1：卖出】
       entrust_price 交易价格 可选(如不填为最新价格)
    
    return:
        {'dsName': ['results'],
         'error_info': '调用成功',
         'error_no': '0',
         'results': [{'buy_unit': '100',
           'delist_flag': '0',
           'down_limit': '19.700000',
           'enable_balance': '',
           'exchange_type': '2',
           'full_rate': '',
           'interest': '',
           'point': '2',
           'price': '5.00',
           'price_step': '10',
           'stock_account': 'A467162***',
           'stock_code': '600118',
           'stock_max_amount': '900',
           'stock_name': '中国卫星',
           'stock_type': '0',
           'store_unit': '1',
           'up_limit': '24.080000',
           'zdfx': '',
           'zdfx_txt': ''}]}
    
    '''
    def get_StockInfo(self,stock_code,entrust_bs='',entrust_price=''):
        funcNo='301514'
        sj=servlet_json(self.conn)
        sj.postdata={
        'funcNo':funcNo,
        'fund_account':self.username,
        'entrust_way':self.__entrust_way,
        'branch_no':self.__logInfo['results'][0]['branch_no'],
        'cust_code':self.username,
        'password':'',
        'op_station':OP_STATION,
        'sessionid':'',
        'stock_code':stock_code,
        'entrust_bs':entrust_bs,
        'entrust_price':entrust_price,
        'op_source':'0',
        }
        return sj.post()

    '''获取指定证券代码的标准行情(1000003)'''
    '''
    in:
       stockcode:股票代码 必填
       count: 最新分笔成交明细数目，默认为10
    return:
          {'dealList': [{'deal': 17, 'flag': 0, 'minite': '14:56', 'price': 21.92},
          {'deal': 3, 'flag': 0, 'minite': '14:56', 'price': 21.93},
          {'deal': 11, 'flag': 1, 'minite': '14:56', 'price': 21.92},
          {'deal': 19, 'flag': 0, 'minite': '14:56', 'price': 21.93},
          {'deal': 1, 'flag': 1, 'minite': '14:56', 'price': 21.92},
          {'deal': 3, 'flag': 0, 'minite': '14:56', 'price': 21.93},
          {'deal': 10, 'flag': 0, 'minite': '14:56', 'price': 21.93},
          {'deal': 6, 'flag': 0, 'minite': '14:56', 'price': 21.93},
          {'deal': 10, 'flag': 0, 'minite': '14:57', 'price': 21.93},
          {'deal': 522, 'flag': 1, 'minite': '15:00', 'price': 21.92}],
         'dsName': ['stockHq', 'dealList', 'stockInfo'],
         'error_info': '调用成功!',
         'error_no': '0',
         'stockHq': [{'buy_price1': 21.92,
           'buy_price2': 21.91,
           'buy_price3': 21.9,
           'buy_price4': 21.89,
           'buy_price5': 21.88,
           'buy_vol1': 548.0,
           'buy_vol2': 188.0,
           'buy_vol3': 153.0,
           'buy_vol4': 137.0,
           'buy_vol5': 904.0,
           'date': 20190927,
           'minite': 239,
           'sell_price1': 21.93,
           'sell_price2': 21.94,
           'sell_price3': 21.95,
           'sell_price4': 21.96,
           'sell_price5': 21.97,
           'sell_vol1': 321.0,
           'sell_vol2': 55.0,
           'sell_vol3': 1268.0,
           'sell_vol4': 23.0,
           'sell_vol5': 142.0,
           'stock_code': '600118',
           'stock_name': '中国卫星'}],
         'stockInfo': [{'amount': 119927816.0,
           'argprice': 21.9757,
           'buy': 21.92,
           'code': '600118',
           'dt_price': 19.701,
           'flux': 0.0137,
           'high': 22.15,
           'hsl': 0.0046,
           'inside': 30332.0,
           'isStop': '2',
           'low': 21.85,
           'ltsz': 25920161792.0,
           'market': 'SH',
           'mgjz': 4.66,
           'name': '中国卫星',
           'now': 21.92,
           'open': 21.85,
           'outside': 24241.0,
           'pgr': 68.4408,
           'pyname': 'ZGWX',
           'sell': 21.93,
           'sjl': 4.7039,
           'stock_type': 9,
           'stop_flag': '2',
           'thedeal': 522.0,
           'up': 0.03,
           'upperacent': 0.13999999999999999,
           'volrate': 0.669,
           'volume': 54572.0,
           'wb': 0.0324,
           'wc': 121.0,
           'yesterday': 21.89,
           'zsz': 25920159744.0,
           'zt_price': 24.079}]}

    
    '''
    def get_StandardMarket(self,stockcode,count=10):
        funcNo='1000003'
        qInfo=self.get_StockInterceptor(stockcode)
        if qInfo['error_no'] != '0':
            return {'error_no':'-1','error_info':'请核对输入的股票代码','result':[]}
        if len(qInfo['results'])==0:
            return {'error_no':'-1','error_info':'未找到股票信息','result':[]}
        if len(qInfo['results'])>1:
            return {'error_no':'-1','error_info':'查询股票信息不唯一','result':[]}
        market=qInfo['results'][0]['market']
        sj=servlet_json(self.conn)
        sj.postdata={
        'funcNo':funcNo,
        'market':market,
        'stockcode': stockcode,
        'count':count
        }
        return sj.post()

    '''股票查询(1000004)'''
    '''
    in:
       stockcode 股票代码 必填
    return:
         {'dsName': ['results'],
           'error_info': '调用成功!',
           'error_no': '0',
           'results': [{'market': 'SH',
           'pyjc': 'ZGWX',
           'stock_code': '600118',
           'stock_name': '中国卫星',
           'stock_type': 9}]}
       
    '''
    def get_StockInterceptor(self,stockcode):
        funcNo='1000004'
        sj=servlet_json(self.conn)
        sj.postdata={
        'funcNo':funcNo,
        'type':urllib.parse.quote('0:1:2:3:4:5:6:8:9:10:11:12:13:14:16:17:18:19:20:21:22:23:24:25:26:27:30:64:65:66'),
        'q': stockcode,
        'count':5,
        'op_station':OP_STATION
        }
        return sj.post()

    '''普通委托(301501)'''
    '''
    in:
       code: 股票代码 必填
       bs :交易方向 必填【0：买入 | 1：卖出】
       price：交易价格 必填
       amount：交易数量 必填
    return :
        {'dsName': ['results'],
         'error_info': '委托已提交，合同号是4263',
         'error_no': '0',
         'results': [{'batch_no': '4263', 'entrust_no': '4263', 'report_no': '4263'}]}
    '''
    def Entrust(self,code,bs,price,amount):
        StockInterceptor=self.get_StockInterceptor(code)
        if len(StockInterceptor['results'])!=1:
            return {"error_no":"-1","results":[],"error_info":"输入的股票代码有误"}
        exchange_type=StockInterceptor['results'][0]['market']
        stockInfo=self.get_StockInfo(code,bs,price)
        if stockInfo['error_no']!='0':
            return stockInfo
        if float(price)>float(stockInfo['results'][0]['up_limit']) or float(price)<float(stockInfo['results'][0]['down_limit']):
            return {"error_no":"-1","results":[],"error_info":"委托价格在涨跌停范围之外"}
        if float(stockInfo['results'][0]['stock_max_amount'])<float(amount):
            return {"error_no":"-1","results":[],"error_info":"委托数量%d超过最大限额%s"%(amount,stockInfo['results'][0]['stock_max_amount'])}
        price=stockInfo['results'][0]['price']
        stock_account=stockInfo['results'][0]['stock_account']

        funcNo='301501'
        value='*'.join([funcNo,self.username,'A467162210',price,str(amount),code])
        sj=servlet_json(self.conn)
        sj.postdata={
            'funcNo':funcNo,
            'funcsb':urllib.parse.quote(Comm.aesEncrypt(self.__aes_key,value),safe=""),
            'entrust_way':self.__entrust_way,
            'branch_no':'',
            'fund_account':self.username,
            'cust_code':self.username,
            'password':'',
            'op_station':OP_STATION,
            'sessionid':'',
            'entrust_bs':bs,
            'exchange_type':exchange_type,
            'stock_account':stock_account,
            'stock_code':code,
            'entrust_price':price,
            'entrust_amount':amount,
            'batch_no':','
        }
        return sj.post()

    '''撤单(301502)'''
    '''
    in:
        entrust_no: 委托编号
    return:
        {'dsName': ['results'],
         'error_info': '撤单委托成功，合同号是:4263',
         'error_no': '0',
         'results': [{'entrust_no': '4263'}]}
    '''
    def Cancel(self,entrust_no):
        funcNo='301502'
        sj=servlet_json(self.conn)
        sj.postdata={
            'funcNo':funcNo,
            'main_site':'',
            'Mac':'',
            'gd_base64':'',
            'entrust_way':self.__entrust_way,
            'branch_no':self.__logInfo['results'][0]['branch_no'],
            'fund_account':self.username,
            'cust_code':self.username,
            'password':'',
            'op_station':OP_STATION,
            'sessionid':'',
            'entrust_no':entrust_no,
            'batch_flag':'',
            'exchange_type':'',
            'op_source':'',
        }
        return sj.post()

    '''获取当日委托(301508)'''
    '''
    return:
        {'dsName': ['results'],
         'error_info': '调用成功',
         'error_no': '0',
         'results': [{'business_amount': '0',
           'business_balance': '0.0',
           'business_price': '0.000000',
           'cancel_amount': '100',
           'cancel_flag': '1',
           'entrust_amount': '100',
           'entrust_bs': '0',
           'entrust_date': '2019-09-26',
           'entrust_name': '委托买入',
           'entrust_no': '1',
           'entrust_price': '5.100000',
           'entrust_state': '7',
           'entrust_state_name': '已撤',
           'entrust_time': '22:43:31',
           'entrust_type': '0',
           'entrust_type_name': '买卖',
           'exchange_type': '2',
           'exchange_type_name': '上海A股',
           'report_no': '1',
           'stock_account': 'A467162210',
           'stock_code': '601398',
           'stock_name': '工商银行'},
          {'business_amount': '0',
           'business_balance': '0.0',
           'business_price': '0.000000',
           'cancel_amount': '100',
           'cancel_flag': '1',
           'entrust_amount': '100',
           'entrust_bs': '0',
           'entrust_date': '2019-09-27',
           'entrust_name': '委托买入',
           'entrust_no': '4263',
           'entrust_price': '5.010000',
           'entrust_state': '7',
           'entrust_state_name': '已撤',
           'entrust_time': '12:57:39',
           'entrust_type': '0',
           'entrust_type_name': '买卖',
           'exchange_type': '2',
           'exchange_type_name': '上海A股',
           'report_no': '4263',
           'stock_account': 'A467162210',
           'stock_code': '601398',
           'stock_name': '工商银行'}]}

    '''
    def get_TodayEntrust(self):
        funcNo='301508'
        sj=servlet_json(self.conn)
        sj.postdata={
            'funcNo':funcNo,
            'entrust_way':self.__entrust_way,
            'branch_no':self.__logInfo['results'][0]['branch_no'],
            'fund_account':self.username,
            'cust_code':self.username,
            'password':'',
            'op_station':OP_STATION,
            'sessionid':'',
            'exchange_type':'',
            'stock_account':'',
            'stock_code':'',
            'entrust_bs':'',
            'op_source':''
        }
        return sj.post()

    '''获取当日成交(301509)'''
    '''
    return:
       尚未有成交
    '''
    def get_TodayTrade(self):
        funcNo='301509'
        sj=servlet_json(self.conn)
        sj.postdata={
            'funcNo':funcNo,
            'entrust_way':self.__entrust_way,
            'branch_no':self.__logInfo['results'][0]['branch_no'],
            'fund_account':self.username,
            'cust_code':self.username,
            'password':'',
            'op_station':OP_STATION,
            'sessionid':'',
            'exchange_type':'',
            'stock_account':'',
            'stock_code':'',
            'entrust_bs':'',
            'op_source':''
        }
        return sj.post()

    '''获取可撤单委托(301515)'''
    '''
    return:
       同当日委托
    '''
    def get_CanCancel(self):
        funcNo='301515'
        sj=servlet_json(self.conn)
        sj.postdata={
            'funcNo':funcNo,
            'entrust_way':self.__entrust_way,
            'branch_no':self.__logInfo['results'][0]['branch_no'],
            'fund_account':self.username,
            'cust_code':self.username,
            'password':'',
            'op_station':OP_STATION,
            'sessionid':'',
            'exchange_type':'',
            'op_source':''
        }
        return sj.post()

    '''获取历史委托(301510)'''
    '''
    in:
        begin_time:起始时间  必填 格式：yyyy-mm-dd 
        end_time   结束时间  必填 格式：yyyy-mm-dd
    return:
        同当日委托格式
    '''
    def get_HistoryEntrust(self,begin_time,end_time):
        funcNo='301510'
        sj=servlet_json(self.conn)
        sj.postdata={
            'funcNo':funcNo,
            'entrust_way':self.__entrust_way,
            'branch_no':self.__logInfo['results'][0]['branch_no'],
            'fund_account':self.username,
            'cust_code':self.username,
            'password':'',
            'op_station':OP_STATION,
            'sessionid':'',
            'exchange_type':'',
            'stock_account':'',
            'stock_code':'',
            'begin_time':begin_time,
            'end_time':end_time,
            'entrust_bs':'',
            'op_source':''
        }
        return sj.post()

    '''获取历史成交(301511)'''
    '''
     in:
        begin_time:起始时间  必填 格式：yyyy-mm-dd 
        end_time   结束时间  必填 格式：yyyy-mm-dd
     return:
        同当日成交格式   
     '''
    def get_HistoryTrade(self,begin_time,end_time):
        funcNo='301511'
        sj=servlet_json(self.conn)
        sj.postdata={
            'funcNo':funcNo,
            'entrust_way':self.__entrust_way,
            'branch_no':self.__logInfo['results'][0]['branch_no'],
            'fund_account':self.username,
            'cust_code':self.username,
            'password':'',
            'op_station':OP_STATION,
            'sessionid':'',
            'exchange_type':'',
            'stock_account':'',
            'stock_code':'',
            'begin_time':begin_time,
            'end_time':end_time,
            'entrust_bs':'',
            'op_source':''
        }
        return sj.post()



    '''====================状态保存及加载========================'''

    '''保存客户登陆信息'''
    def save_objInfo(self,objFile_dir='custLoginInfo'):
        objFile=objFile_dir+'/'+self.username+'.login'
        if not os.path.exists(objFile_dir):
            os.mkdir(objFile_dir)
        with open(objFile, "wb") as f:
            pickle.dump(self, f)
        return True

    '''加载客户登陆信息'''
    def load_objInfo(self,objFile_dir='custLoginInfo'):
        objFile=objFile_dir+'/'+self.username+'.login'
        if not os.path.exists(objFile):
            print('没有%s的历史login信息'%(self.username))
            return False
        with open(objFile, "rb") as f:
            oldObj= pickle.load(f)
            self.__dict__.update(oldObj.__dict__)
        return True


    '''====================私有成员函数========================'''

    '''登陆前获取相关全局参数信息'''
    def __get_configuration(self):
        url="https://web.stocke.com.cn/configuration.js?v=1.0.6-1568549474216"
        response=self.conn.get(url)
        self.__aes_key=re.findall('"my":"(.*?)"', response.text, re.M | re.I | re.S)[0]
        self.__entrust_way=re.findall('"entrust_way":"(.*?)"', response.text, re.M | re.I | re.S)[0]

    '''获取登陆所用图片移动模块位置信息'''
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

    ''' 获取登陆所用RSA的公钥信息(1000000)'''
    def __get_rsa_para(self):
        sj=servlet_json(self.conn)
        sj.postdata={'funcNo':'1000000','op_station':OP_STATION}
        logResult=sj.post()
        if logResult['error_no']!='0':
            return False,logResult['error_info']
        return True,logResult['results'][0]




'''
/servlet/json 功能接口类
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