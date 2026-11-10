from socket import *
import os
import sys
import struct
import time
import select
import binascii

ICMP_ECHO_REQUEST = 8
ICMP_ECHO_REPLY = 0


def checksum(string):
    # Works on bytes (Python 3): indexing bytes already gives ints
    csum = 0
    countTo = (len(string) // 2) * 2
    count = 0
    while count < countTo:
        thisVal = string[count + 1] * 256 + string[count]
        csum = csum + thisVal
        csum = csum & 0xffffffff
        count = count + 2
    if countTo < len(string):
        csum = csum + string[len(string) - 1]
        csum = csum & 0xffffffff
    csum = (csum >> 16) + (csum & 0xffff)
    csum = csum + (csum >> 16)
    answer = ~csum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer


def receiveOnePing(mySocket, ID, timeout, destAddr):
    timeLeft = timeout
    while 1:
        startedSelect = time.time()
        whatReady = select.select([mySocket], [], [], timeLeft)
        howLongInSelect = (time.time() - startedSelect)
        if whatReady[0] == []:  # Timeout
            return "Request timed out."
        timeReceived = time.time()
        recPacket, addr = mySocket.recvfrom(1024)

        #Fill in start
        # Fetch the ICMP header from the IP packet.
        # The IP header comes first; its length is in the low 4 bits of byte 0 (in 32-bit words).
        if (recPacket[0] >> 4) == 4:
            ipHeaderLen = (recPacket[0] & 0x0F) * 4
            ttl = recPacket[8]
        else:  # no IP header (Linux unprivileged ICMP socket)
            ipHeaderLen = 0
            ttl = None

        icmpHeader = recPacket[ipHeaderLen:ipHeaderLen + 8]
        icmpType, code, recChecksum, packetID, sequence = struct.unpack("bbHHh", icmpHeader)

        # Only accept echo replies meant for us (ignore e.g. our own request echoed on localhost)
        if icmpType == ICMP_ECHO_REPLY and (packetID == ID or ipHeaderLen == 0):
            bytesInDouble = struct.calcsize("d")
            timeSent = struct.unpack("d", recPacket[ipHeaderLen + 8:ipHeaderLen + 8 + bytesInDouble])[0]
            rtt = (timeReceived - timeSent) * 1000
            return "Reply from %s: bytes=%d seq=%d TTL=%s checksum=0x%04x time=%.3f ms" % (
                addr[0], len(recPacket) - ipHeaderLen, sequence, ttl, recChecksum, rtt)
        #Fill in end

        timeLeft = timeLeft - howLongInSelect
        if timeLeft <= 0:
            return "Request timed out."


def sendOnePing(mySocket, destAddr, ID):
    # Header is type (8), code (8), checksum (16), id (16), sequence (16)
    myChecksum = 0
    # Make a dummy header with a 0 checksum
    # struct -- Interpret strings as packed binary data
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    data = struct.pack("d", time.time())
    # Calculate the checksum on the data and the dummy header.
    myChecksum = checksum(header + data)
    # Get the right checksum, and put in the header
    if sys.platform == 'darwin':
        # Convert 16-bit integers from host to network byte order
        myChecksum = htons(myChecksum) & 0xffff
    else:
        myChecksum = htons(myChecksum)
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    packet = header + data
    mySocket.sendto(packet, (destAddr, 1))  # AF_INET address must be tuple, not str
    # Both LISTS and TUPLES consist of a number of objects
    # which can be referenced by their position number within the object.


def doOnePing(destAddr, timeout):
    icmp = getprotobyname("icmp")
    # SOCK_RAW is a powerful socket type. For more details: http://sock-raw.org/papers/sock_raw
    try:
        mySocket = socket(AF_INET, SOCK_RAW, icmp)
    except PermissionError:
        # Without root, fall back to the unprivileged ICMP socket (macOS / Linux)
        mySocket = socket(AF_INET, SOCK_DGRAM, icmp)
    myID = os.getpid() & 0xFFFF  # Return the current process id
    sendOnePing(mySocket, destAddr, myID)
    delay = receiveOnePing(mySocket, myID, timeout, destAddr)
    mySocket.close()
    return delay


def ping(host, timeout=1, count=None):
    # timeout=1 means: If one second goes by without a reply from the server,
    # the client assumes that either the client's ping or the server's pong is lost
    dest = gethostbyname(host)
    print("Pinging " + dest + " using Python:")
    print("")
    # Send ping requests to a server separated by approximately one second
    sent = 0
    delay = None
    try:
        while count is None or sent < count:
            delay = doOnePing(dest, timeout)
            print(delay)
            sent += 1
            time.sleep(1)  # one second
    except KeyboardInterrupt:
        print("\nStopped.")
    return delay


if __name__ == "__main__":
    # Usage: sudo python3 icmp_pinger.py [host] [count]
    host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    count = int(sys.argv[2]) if len(sys.argv) > 2 else None
    ping(host, count=count)
