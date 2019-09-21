from Crypto.Cipher import AES
import rsa
import binascii,base64,os,pickle
import random

'''
获取n位的随机数
'''
def getRandom(n):
    return int(random.random()*10**n)

'''
RSA加密
'''
def rsaEncrypt(bitInfo,n,e):
    rsa.PublicKey.n=int(n, 16)
    rsa.PublicKey.e=int(str(e), 16)
    p=rsa.encrypt(bitInfo,rsa.PublicKey)
    return binascii.b2a_hex(p).decode()

'''
AES加密
'''
def aesEncrypt(key,value):
    key=key+"d"
    aes=AES.new(key.encode(), AES.MODE_ECB)
    vLen=len(value)
    add = 16 - (vLen % 16)
    return base64.b64encode(aes.encrypt(value+chr(add)*add)).decode()


'''
保存客户登陆信息
'''
def save_loginInfo(cookiesDict,cookiesFile_dir='custLoginInfo',cookiesFile_name='temp'):
    cookiesFile=cookiesFile_dir+'/'+cookiesFile_name+'.login'
    if not os.path.exists(cookiesFile_dir):
        os.mkdir(cookiesFile_dir)
    with open(cookiesFile, "wb") as f:
        pickle.dump(cookiesDict, f)
    return True

'''
加载客户登陆信息
'''
def load_loginInfo(cookiesFile_dir='custLoginInfo',cookiesFile_name='temp'):
    cookiesFile=cookiesFile_dir+'/'+cookiesFile_name+'.login'
    if not os.path.exists(cookiesFile):
        print('没有%s的login信息'%(cookiesFile_name))
        return False
    with open(cookiesFile, "rb") as f:
        return pickle.load(f)