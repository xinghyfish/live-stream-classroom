import socket
import datetime

HOST = '0.0.0.0'
PORT = 3434

# AF_INET: use IPv4 address, SOCK_STREAM refers to TCP
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))        # bind IP and port
s.listen(1)                 # listen

while True:
    conn, address = s.accept()
    print('Client %s connected!' % str(address))
    dt = datetime.datetime.now()
    message = "Current time is " + str(dt)
    conn.send(message.encode('utf-8'))
    print("Sent: ", message)
    conn.close()


