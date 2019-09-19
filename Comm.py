from Crypto.Cipher import AES
import rsa
import binascii,base64
'''
rsa加密
'''
def rsaEncrypt(bitInfo,modulus,publicExponent):
    e = int(str(publicExponent), 16)
    n = int(modulus, 16)
    rsa.PublicKey.n=n
    rsa.PublicKey.e=e
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