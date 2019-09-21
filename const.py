import socket
import uuid


HOST_NAME=socket.getfqdn(socket.gethostname())  # DESKTOP-K9D3HRB
IP=socket.gethostbyname(HOST_NAME)              # 192.168.137.1
MAC=uuid.UUID(int = uuid.getnode()).hex[-12:]   # 00155d022001
HARD_INFO='ST9750420AS(W60SQ4RB)'
CPUID='BFCBFBFF000206A70000000000000000'
VERSION='1.0.6'



OP_STATION='%7C'.join(['0',IP,MAC,HARD_INFO,CPUID,'%20',HOST_NAME,IP,VERSION,])
