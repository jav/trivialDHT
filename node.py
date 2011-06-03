
import SocketServer
import hashlib 
import random
import message 
import sys
import string
import socket
import copy 
import threading
import time 
import signal

class DHTNode:
    m_key = ""
    m_prevKey = ""
    m_nextKey = ""
    m_peerList = dict()
    m_address = ""
    m_port = 0
    m_data = dict()

    def __init__(self):
        self.mkKey()

    def mkKey(self):
        sha = hashlib.sha1()
        sha.update( str(random.random()) )
        self.m_key = sha.hexdigest()
        #self.m_key = str(7190000000000000000000000000000000000000)

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

    def doAddNode(self, destAddress, destPort, nodeAddress, nodePort, nodeKey):
        print "doAddNode():", "destAddress:", destAddress, "destPort", str(destPort), "nodeAddress:", nodeAddress, "nodePort", nodePort
        msg = message.Message()
        msg.setType(1)
        msg.setMessage( nodeAddress + ":" + str(nodePort) + " " + nodeKey )
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((destAddress, destPort))
        s.send(msg.toString())
        s.close()

    def onAddNode(self, msg, sock):
        msgAddress = msg.getMessage().partition(" ")[0]
        msgId = msg.getMessage().partition(" ")[2]

        print "onAddNode() : ", msgId, msgAddress

        # If key already exists, just update the post and exit
        if msgId in self.m_peerList.keys() :
            self.m_peerList[msgId] = msgAddress
            return

        #Add new key
        self.m_peerList[msgId] = msgAddress

        ## Find nearest previous neighbor
        pos = 0
        prevKey = ""

        print "onAddNode(): My key:", self.m_key

        keyList = sorted(self.m_peerList.iterkeys())
        for key in keyList:
            print "onAddNode(): key: ",key
            if key < self.m_key and key > prevKey :
                print "onAddNode(): new prevKey: ", prevKey
                prevKey = key

        # If prevKey is null ("") then pick the highest one in peerList
        # Makes the "list" circular
        if "" == prevKey and 0 < len( keyList ) :
                prevKey = keyList[-1]
                print "onAddNode(): new prevKey: ", prevKey

        print "onAddNode(): Result:"
        print "onAddNode(): My Key:", self.m_key
        print "onAddNode(): Nearest Key:", prevKey
        print "onAddNode(): PeerList:" , self.m_peerList

        (dAddr, s, dPort) = msgAddress.partition(":")
        print "onAddNode(): doAddNode(",dAddr, dPort, self.getAddress(), str(self.getPort()),self.getKey(), ")"
        self.doAddNode(dAddr, int(dPort), self.getAddress(), self.getPort(), self.getKey())

    def doQueryForNodes(self, nodeAddress, nodePort):
        print "doQueryForNodes():", "nodeAddress:", nodeAddress, "nodePort", str(nodePort)
        msg = message.Message()
        msg.setType(2)
        msg.setMessage( self.getAddress() + ":" + str(self.getPort()) + " " + self.m_key )
    
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((nodeAddress, nodePort))
        try:
            s.send(msg.toString())
        except Exception:
            pass
        s.close()
        print "doQueryForNodes(): done!"


    def onQueryForNodes(self, msg, sock ):
        print "onQueryForNodes(): ",msg.getMessage()
        if 0 == len(self.m_peerList):
            return

        (remoteAddr, s, remoteKey) = msg.getMessage().partition(" ")
        (remoteIp, s, remotePort) = remoteAddr.partition(":")

        # Pick three random nodes
        redNodeList = copy.deepcopy(self.m_peerList)
        del redNodeList[remoteKey]
        print "onQueryForNodes(): redNodeList:", redNodeList
        for i in range (0 , min(3, len(redNodeList ) ) ):
            if 0 < len( redNodeList ) :
                print "Random choice from listsize:", len(redNodeList)
                print redNodeList
                keyToSend = random.choice( redNodeList.keys() )
                print keyToSend
                (pAddr, s, pPort) = redNodeList[keyToSend].partition(":")
                (dAddr, s, dPort) = self.m_peerList[remoteKey].partition(":")

                del redNodeList[keyToSend]
                self.doAddNode(remoteIp, int(remotePort), pAddr, int(pPort), keyToSend )

#Not yet implemented!
    def onAddData(self, msg, sock):
        sha = hashlib.sha1()
        sha.update( msg.getMessage() )
        ## Check that sha is in range
        print "hash for:", msg.getMessage(), "was:", sha.hexdigest()
        print self.m_peerList
        print "My id:", self.m_key

        ## TODO: Fix "circular" list! This won't work if I have the lowest key!
        if self.m_prevKey < sha.hexdigest() and sha.hexdigest() <= self.m_key :
            ## Add the data
            print "add data"
            print "answer OK"
            this.m_data[sha.hexdigest()] = msg.getMessage()
            okMsg = Message()
            okMsg.setType(11)
            okMsg.setMessage("OK")
            sock.send(okMsg.toString())
            
        else:
            print "divert to next node"
            print "answer with correct node address"

            # Find a better node and save as "peer"

            divMsg = Message()
            divMsg.setType(12)
            divMsg.setMessage(peerAddr)
            sock.send(divMsg.toString())
            



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
                print "onAddNode!"
                node.onAddNode( msg, self.request )
            if( 2 == msg.getType() ):
                print "onQueryForNodes!"
                node.onQueryForNodes( msg, self.request )
            if( 10 == msg.getType() ):
                print "onAddData!"
                node.onAddData( msg, self.request )

            print "" 

            recvMsg = self.request.recv(1024).strip()        


class ThreadClass(threading.Thread):
    def run(self):
        print "listen on '', " + sys.argv[2]
        myServer = SocketServer.TCPServer(('', int( sys.argv[2] ) ),
                                          MyRequestHandler)
        
        myServer.serve_forever()
        

def signal_handler(signal, frame):
        print 'You pressed Ctrl+C!'
        sys.exit(0)            

### Global var
node = DHTNode()

### MAIN()
def main(args):

    signal.signal(signal.SIGINT, signal_handler)

    node.setAddress(args[1])
    node.setPort( int(args[2]) )

    print "My ID:", node.getKey()

    ### ORDINARY OPERATION
    # start "main" thread
    t = ThreadClass()
    t.start()

    ## BOOTSTRAP
    # if defined
    if len(args) == 5:
        time.sleep(2)
        # register with known node
        # query list for new nodes
        node.doAddNode(args[3], int(args[4]), args[1], int(args[2]), node.getKey() )
        node.doQueryForNodes(args[3], int(args[4]) )


if __name__ == '__main__':
  main(sys.argv)
