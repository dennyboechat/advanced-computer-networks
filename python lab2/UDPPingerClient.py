# UDPPingerClient.py
import time
from socket import *

clientSocket = socket(AF_INET, SOCK_DGRAM)
# Wait up to 1 second for a reply
clientSocket.settimeout(1)

for i in range(1, 11):
    sendTime = time.time()
    message = 'Ping ' + str(i) + ' ' + time.ctime(sendTime)
    clientSocket.sendto(message.encode(), ('localhost', 12000))
    try:
        response, address = clientSocket.recvfrom(1024)
        rtt = time.time() - sendTime
        print(response.decode())
        print('RTT:', rtt, 'seconds')
    except timeout:
        print('Request timed out')

clientSocket.close()
