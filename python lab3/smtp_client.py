from socket import *

msg = "\r\n This is a test MR Bradley!"
endmsg = "\r\n.\r\n"

# Sender and recipient (change these to real addresses)
fromAddress = "dennyboechat@hotmail.com"
toAddress = "test@test.com"

# Choose a mail server (e.g. Google mail server) and call it mailserver
# Fill in start
# Use a (host, port) tuple. For local testing, run MailHog:
#   brew install mailhog && mailhog
# MailHog accepts SMTP on port 1025; view received mail at http://localhost:8025
# Public servers such as ("smtp.gmail.com", 587) require STARTTLS + authentication,
# which this plain-socket client does not implement.
mailserver = ("localhost", 1025)
# Fill in end

# Create socket called clientSocket and establish a TCP connection with mailserver
# Fill in start
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect(mailserver)
# Fill in end

recv = clientSocket.recv(1024).decode()
print(recv)
if recv[:3] != '220':
    print('220 reply not received from server.')

# Send HELO command and print server response.
heloCommand = 'HELO\r\n'
clientSocket.send(heloCommand.encode())
recv1 = clientSocket.recv(1024).decode()
print(recv1)
if recv1[:3] != '250':
    print('250 reply not received from server.')

# Send MAIL FROM command and print server response.
# Fill in start
mailFromCommand = 'MAIL FROM:<' + fromAddress + '>\r\n'
clientSocket.send(mailFromCommand.encode())
recv2 = clientSocket.recv(1024).decode()
print(recv2)
if recv2[:3] != '250':
    print('250 reply not received from server.')
# Fill in end

# Send RCPT TO command and print server response.
# Fill in start
rcptToCommand = 'RCPT TO:<' + toAddress + '>\r\n'
clientSocket.send(rcptToCommand.encode())
recv3 = clientSocket.recv(1024).decode()
print(recv3)
if recv3[:3] not in ('250', '251'):
    print('250 reply not received from server.')
# Fill in end

# Send DATA command and print server response.
# Fill in start
dataCommand = 'DATA\r\n'
clientSocket.send(dataCommand.encode())
recv4 = clientSocket.recv(1024).decode()
print(recv4)
if recv4[:3] != '354':
    print('354 reply not received from server.')
# Fill in end

# Send message data.
# Fill in start
headers = ('From: ' + fromAddress + '\r\n'
           'To: ' + toAddress + '\r\n'
           'Subject: SMTP Lab Test\r\n')
clientSocket.send((headers + msg).encode())
# Fill in end

# Message ends with a single period.
# Fill in start
clientSocket.send(endmsg.encode())
recv5 = clientSocket.recv(1024).decode()
print(recv5)
if recv5[:3] != '250':
    print('250 reply not received from server.')
# Fill in end

# Send QUIT command and get server response.
# Fill in start
quitCommand = 'QUIT\r\n'
clientSocket.send(quitCommand.encode())
recv6 = clientSocket.recv(1024).decode()
print(recv6)
if recv6[:3] != '221':
    print('221 reply not received from server.')
clientSocket.close()
# Fill in end
