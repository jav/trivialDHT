import socket
import sys
import message

HOST = sys.argv[1]
PORT = sys.argv[2]

msg = message.Message()
msg.setType(10)
msg.setMessage(" ".join(sys.argv[3:] ))

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, int(PORT)) )
s.send(msg.toString() )

reply = message.Message()
data = s.recv(1024)
reply.parseMsg( data )

print "Reply was:", reply.toString()

while 12 == reply.getType():
    s.close()
    print "getMessage():", reply.getMessage()
    print "print getMessage().partition():", reply.getMessage().partition(" ")
    (addr, sep, key) = reply.getMessage().partition(" ")
    (HOST, sep, PORT) = addr.partition(":")
    
    msg = message.Message()
    msg.setType(10)
    msg.setMessage(" ".join(sys.argv[3:] ))

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, int(PORT)) )
    s.send(msg.toString() )
    
    data = s.recv(1024)
    reply.parseMsg( data )
    print "Reply was:", reply.toString()
    

s.close()
print 'Received', data
