from socket import *
import sys
import os

if len(sys.argv) <= 1:
    print('Usage : "python ProxyServer.py server_ip"\n[server_ip : It is the IP Address Of Proxy Server')
    sys.exit(2)

CACHE_DIR = "cache"


def cache_path(name):
    # Flatten the URL into a single safe filename inside the cache folder,
    # so paths like "www.example.com/img/logo.png" don't need sub-directories.
    safe = name.replace("/", "_").replace("?", "_").replace(":", "_")
    return os.path.join(CACHE_DIR, safe or "_")


# Create a server socket, bind it to a port and start listening
tcpSerSock = socket(AF_INET, SOCK_STREAM)
# Fill in start.
serverPort = 8888
tcpSerSock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
tcpSerSock.bind((sys.argv[1], serverPort))
tcpSerSock.listen(5)
os.makedirs(CACHE_DIR, exist_ok=True)
# Fill in end.

while 1:
    # Start receiving data from the client
    print('Ready to serve...')
    tcpCliSock, addr = tcpSerSock.accept()
    print('Received a connection from:', addr)
    message = tcpCliSock.recv(4096).decode('utf-8', errors='ignore')  # Fill in start. # Fill in end.
    print(message)

    # Browsers sometimes open a connection and send nothing; skip those
    if len(message.split()) < 2:
        tcpCliSock.close()
        continue

    # Extract the filename from the given message
    print(message.split()[1])
    url = message.split()[1]
    # When the browser is configured to use the proxy, it sends the full URL
    # ("GET http://www.example.com/x HTTP/1.1"); normalise it to "/www.example.com/x"
    if url.startswith("http://"):
        url = "/" + url[len("http://"):]
    filename = url.partition("/")[2]
    print(filename)
    fileExist = "false"
    filetouse = "/" + filename
    print(filetouse)

    try:
        # Check whether the file exists in the cache
        # (binary mode so images and other non-text objects work)
        f = open(cache_path(filetouse[1:]), "rb")
        outputdata = f.read()
        f.close()
        fileExist = "true"
        # ProxyServer finds a cache hit and generates a response message.
        # The cached file holds the origin server's complete response
        # (status line + headers + body), so it is sent back as-is; this keeps
        # the correct Content-Type for images, CSS, etc.
        # Fill in start.
        tcpCliSock.sendall(outputdata)
        # Fill in end.
        print('Read from cache')

    # Error handling for file not found in cache
    except IOError:
        if fileExist == "false":
            # Create a socket on the proxyserver
            c = socket(AF_INET, SOCK_STREAM)  # Fill in start. # Fill in end.
            hostn = filename.partition("/")[0]
            path = "/" + filename.partition("/")[2]
            print(hostn)
            try:
                # Connect to the socket to port 80
                # Fill in start.
                c.connect((hostn, 80))
                # Fill in end.

                # Create a temporary file on this socket and ask port 80
                # for the file requested by the client
                fileobj = c.makefile('rwb', 0)
                fileobj.write(("GET " + path + " HTTP/1.0\r\n"
                               "Host: " + hostn + "\r\n"
                               "Connection: close\r\n\r\n").encode())

                # Read the response into buffer
                # Fill in start.
                buffer = fileobj.read()
                # Fill in end.

                # Create a new file in the cache for the requested file.
                # Also send the response in the buffer to client socket
                # and the corresponding file in the cache
                tmpFile = open(cache_path(filename), "wb")
                # Fill in start.
                tmpFile.write(buffer)
                tmpFile.close()
                tcpCliSock.sendall(buffer)
                fileobj.close()
                c.close()
                # Fill in end.
            except Exception as e:
                print("Illegal request:", e)
                tcpCliSock.sendall(b"HTTP/1.0 404 Not Found\r\n"
                                   b"Content-Type: text/html\r\n\r\n"
                                   b"<html><body><h1>404 Not Found</h1></body></html>\r\n")
        else:
            # HTTP response message for file not found
            # Fill in start.
            tcpCliSock.sendall(b"HTTP/1.0 404 Not Found\r\n"
                               b"Content-Type: text/html\r\n\r\n"
                               b"<html><body><h1>404 Not Found</h1></body></html>\r\n")
            # Fill in end.

    # Close the client socket
    tcpCliSock.close()

# Close the server socket
# Fill in start.
tcpSerSock.close()
# Fill in end.
