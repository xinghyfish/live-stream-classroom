import socket

HOST = '0.0.0.0'
PORT = 3434

# AD_INET: IPv4, SOCK_DGRAM: UDP
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((HOST, PORT))

while True:
    data, address = s.recvfrom(1024)
    print("Received: %s from %s" % (str(data), str(address)))
