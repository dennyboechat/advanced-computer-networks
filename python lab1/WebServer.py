#import socket module
from socket import *
import sys # In order to terminate the program

serverSocket = socket(AF_INET, SOCK_STREAM)
#Prepare a sever socket
#Fill in start
serverPort = 6789
# Allow restarting right away without "Address already in use"
serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
serverSocket.bind(('', serverPort))
serverSocket.listen(1)
#Fill in end

while True:
    #Establish the connection
    print('Ready to serve...')
    connectionSocket, addr = serverSocket.accept()
    # Don't wait forever on a connection that never sends a request
    connectionSocket.settimeout(2)
    try:
        message = connectionSocket.recv(1024).decode()
        # Read the rest of the request; closing with unread data sends a reset and the browser drops the page
        while message and "\r\n\r\n" not in message:
            chunk = connectionSocket.recv(1024).decode()
            if not chunk:
                break
            message += chunk
        # Browsers may open a connection and send nothing; skip it instead of crashing
        if not message:
            connectionSocket.close()
            continue
        filename = message.split()[1]
        f = open(filename[1:])
        outputdata = f.read()
        f.close()
        #Send one HTTP header line into socket
        connectionSocket.send("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n".encode())
        #Send the content of the requested file to the client
        for i in range(0, len(outputdata)):
            connectionSocket.send(outputdata[i].encode())
        connectionSocket.send("\r\n".encode())
        connectionSocket.close()
    except timeout:
        # Idle connection: drop it and go back to waiting
        connectionSocket.close()
    except IOError:
        #Send response message for file not found
        connectionSocket.send("HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\n".encode())
        connectionSocket.send("<html><body><h1>404 Not Found</h1></body></html>\r\n".encode())
        #Close client socket
        connectionSocket.close()

serverSocket.close()
sys.exit()#Terminate the program after sending the corresponding data
