import socket
import hashlib
import random
import message
import sys

HOST = sys.argv[1]
PORT = int(sys.argv[2])
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sha = hashlib.sha1()
sha.update( str(random.random() ) )
myId = sha.hexdigest()

msg = message.Message()
msg.setType(1)


msg.setMessage("127.0.0.1:8998 " + myId)

s.connect((HOST, PORT))
print "Sending: ", msg.toString()
s.send(msg.toString())

