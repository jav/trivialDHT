
import SocketServer
import hashlib # For keys
import random
import message 
import sys
import string
import socket

### Global vars (later to be class members)

peerList = dict()
dataList = dict()

class DHTNode:
    m_key = ""
    m_nearestKey = ""
    m_peerList = dict()
    m_address = ""
    m_port = 0

    def __init__(self):
        self.mkKey()

    def mkKey(self):
        sha = hashlib.sha1()
        sha.update( str(random.random()) )
        self.m_key = sha.hexdigest()

    def getKey(self):
        return self.m_key

    def getAddress(self):
        return self.m_addres

    def setAddress(self, address):
        self.m_addres = address

    def getPort(self):
        return self.m_port

    def setPort(self, port):
        self.m_port = port

    def doAddNode(self, nodeAddress, nodePort):
        print "doAddNode():", "nodeAddress:", nodeAddress, "nodePort", str(nodePort)
        msg = message.Message()
        msg.setType(2)
        msg.setMessage( self.m_address + ":" + str(self.m_port) + " " + self.m_key )
        
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((nodeAddress, nodePort))
        s.send(msg.toString())
        s.close()

    def onAddNode(self, msg, sock):
        msgAddress = msg.getMessage().partition(" ")[0]
        msgId = msg.getMessage().partition(" ")[2]
        print "addNode() : ", msgId, msgAddress
        # If key already exists, just update the post and exit
        if msgId in self.m_peerList.keys() :
            self.m_peerList[msgId] = msgAddress
            return

        #Add new key
        self.m_peerList[msgId] = msgAddress

        ## Find nearest previous neighbor
        pos = 0
        nearestKey = ""

        print "My key:", self.m_key
        for key in sorted(self.m_peerList.iterkeys()):
            print "key: ",key
            if key < self.m_key and key > nearestKey :
                print "new nearestKey: ", nearestKey
                nearestKey = key

        if( "" == nearestKey):
            nearestKey = msgId

        print "Result:"
        print "My Key:", self.m_key
        print "Nearest Key:", nearestKey
        print "PeerList:" , self.m_peerList


    def doQueryForNodes(self, nodeAddress, nodePort):
        print "doQueryForNodes():", "nodeAddress:", nodeAddress, "nodePort", str(nodePort)
        msg = message.Message()
        msg.setType(2)
        msg.setMessage(self.m_key)
        
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((nodeAddress, nodePort))
        s.send(msg.toString())
        s.close()
            

    def onQueryForNodes(self, msg, sock ):
        sock.send("You asked for nodes?")
        
    
#Not yet implemented!
    def addData(self, msg):
        sha = haslib.sha1()
        sha.update( msg.getMessage() )
        ## Check that sha is in range
        if self.m_nearestKey < sha.hexdigest() and sha.hexdigest() <= self.m_key :
            ## Add the data
            print "add data"
            print "answer OK"

        else:
            print "divert to next node"
            print "answer with correct node address"
        ## find the dictionary 


class MyRequestHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        print "Connected:", self.client_address


        recvMsg = ""
        recvMsg = self.request.recv(1024).strip()
        while "" != recvMsg :

            

            if len(recvMsg) <= 0:
                print "Empty message (broken?)"
                break

            print "From:", self.client_address," msg:", recvMsg
            sys.stdout.flush()

            msg = message.Message()
            msg.parseMsg( recvMsg )

            if( 1 == msg.getType() ):
                node.onAddNode( msg, self.request )
            
            if( 10 == msg.getType() ):
                node.addData( msg, self.request )

            recvMsg = self.request.recv(1024).strip()        



### MAIN()

node = DHTNode()
node.setAddress(sys.argv[1])
node.setPort( int(sys.argv[2]) )

print "My ID:", node.getKey()

## BOOTSTRAP
# if defined
if len(sys.argv) == 5:
    # add known node to list
    # query list for new nodes
    node.doAddNode(sys.argv[3], int(sys.argv[4]) )
    node.doQueryForNodes( sys.argv[3], int(sys.argv[4]) )

## ORDINARY OPERATION

myServer = SocketServer.TCPServer(('', int( sys.argv[2] ) ),
                MyRequestHandler)

myServer.serve_forever()
