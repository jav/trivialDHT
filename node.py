
import SocketServer
import hashlib # For keys
import random
import message 
import sys
import string


### Global vars (later to be class members)

peerList = dict()
dataList = dict()

class DHTNode:
    m_key = ""
    m_nearestKey = ""
    def __init__(self):
        sha = hashlib.sha1()
        sha.update( str(random.random()) )
        self.m_key = sha.hexdigest()

    def getKey(self):
        return self.m_key

    def addNode(self, msg):
        print "addNode() : ", msg.getId(), msg.getAddress()
        #Add new key
        peerList[msg.getId()] = msg.getAddress() 

        ## Find nearest previous neighbor
        pos = 0
        nearestKey = ""

        print "My key:", myKey
        for key in sorted(peerList.iterkeys()):
            print "key: ",key
            if key < myKey and key > nearestKey :
                print "new nearestKey: ", nearestKey
                nearestKey = key

        if( "" == nearestKey):
            nearestKey = msg.getId()

        print "Result:"
        print "My Key:", myKey
        print "Nearest Key:", nearestKey

        print "PeerList:" , peerList

        ## Compute responsibility interval
        # print "Sorted PeerList:",  peerList.sort()

    
#Not yet implemented!
    def addData(self, msg):
        sha = haslib.sha1()
        sha.update( msg.getMessage() )
        ## Check that sha is in range
        if self.m_nearestKey < sha.hexdigest() and sha.hexdigest() <= self.m_key :
            ## Add the data
            print "add data"
            print "answer OK"

        else
            print "divert to next node"
            print "answer with correct node address"
        ## find the dictionary 


class MyRequestHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        print "Connected:", self.client_address

        while "" != self.request.recv(1024).strip() :

            recvMsg = self.request.recv(1024).strip()
            print "From:", self.client_address," msg:", recvMsg
            sys.stdout.flush()

            msg = message.Message()
            msg.parseMsg( recvMsg )

            if( 1 == msg.getType() ):
                node.addNode( msg )
            
            if( 10 == msg.getType() ):
                node.addData( msg )

        


### MAIN()



node = DHTNode()

print "My ID:", node.getKey()

myServer = SocketServer.TCPServer(('', int( sys.argv[1] ) ),
                MyRequestHandler)

myServer.serve_forever()
