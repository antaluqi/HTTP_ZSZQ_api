from Crypto.Cipher import AES
import rsa
import binascii,base64,os,pickle
import random

'''
获取n位的随机整数
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

