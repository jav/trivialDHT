import zmq
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
import circularlist

# TODO: Optimize so that self cannot occur in reply on queryForNodes (in circular list?)
# TODO: Dont keep the key as a hexdigest (string)

class DHTNode(threading.Thread, SocketServer.BaseRequestHandler):
    m_key = ""
    m_keyList = circularlist.CircularList()
    m_address = ""
    m_port = 0
    m_data = dict()
    m_zmqctx = 0;
    m_sock = 0;
    
    def __init__(self, address, port):
        super(DHTNode, self).__init__()
        self.m_zmqctx = zmq.Context()
        self.mkKey()
        self.setAddress(address)
        self.setPort(port)
        self.m_keyList.add(self.m_key, self.m_address+":"+str(self.m_port) )

    def run(self):
        print "run()"
        address = self.getAddress()
        port = str(self.getPort())
        print "listen on '', " + address + ":" + port
        self.m_sock = self.m_zmqctx.socket(zmq.REP)
        self.m_sock.bind ("tcp://"+ address + ":" + port )

        while( 1 ) :
            print "while(1)"
            message = self.m_sock.recv()
            print "Received request: ", message
            time.sleep(2)
            

    def mkKey(self):
        if "" == self.m_key:
            sha = hashlib.sha1()
            sha.update( str(random.random()) )
            self.m_key = sha.hexdigest()
            #self.m_key = "940000000714f13a9fb6603676867c3f81c73bcf" #line kept for debugging

    def getKey(self):
        return self.m_key

    def getAddress(self):
        return self.m_address

    def setAddress(self, address):
        self.m_address = address
 
    def getPort(self):
        return self.m_port

    def setPort(self, port):
        self.m_port = port
 
    def doAddNode(self, destAddress, destPort, nodeAddress, nodePort, nodeKey):
        if not self.isAlive(): return false
        
        print "doAddNode():", "destAddress:", destAddress, "destPort", str(destPort), "nodeAddress:", nodeAddress, "nodePort", nodePort
        msg = message.Message()
        msg.setType(1)
        msg.setMessage( nodeAddress + ":" + str(nodePort) + " " + nodeKey )
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((destAddress, destPort))
        s.send(msg.toString())
        s.close()

    def onAddNode(self, msg, sock):
        if not self.isAlive(): return false
        
        msgAddress = msg.getMessage().partition(" ")[0]
        msgId = msg.getMessage().partition(" ")[2]

        print "onAddNode() : ", msgId, msgAddress

        # If key already exists, just update the post and exit

        if -1 == self.m_keyList.add(msgId, msgAddress):
            return

        print "onAddNode(): PeerList:" , self.m_keyList.toString()

        (dAddr, s, dPort) = msgAddress.partition(":")
        print "onAddNode(): doAddNode(",dAddr, dPort, self.getAddress(), str(self.getPort()),self.getKey(), ")"
        self.doAddNode(dAddr, int(dPort), self.getAddress(), self.getPort(), self.getKey())

    def doQueryForNodes(self, nodeAddress, nodePort):
        if not self.isAlive(): return false
        
        print "doQueryForNodes():", "nodeAddress:", nodeAddress, "nodePort", str(nodePort)
        msg = message.Message()
        msg.setType(2)
        msg.setMessage( self.getAddress() + ":" + str(self.getPort()) + " " + self.m_key )
    
        s = self.m_zmqctx.socket(zmq.REQ)
        s.connect("tcp://" + nodeAddress +":" + str( nodePort ) )
        try:
            s.send(msg.toString())
        except Exception:
            pass
        s.close()
        print "doQueryForNodes(): done!"


    def onQueryForNodes(self, msg, sock ):
        if not self.isAlive(): return false
        
        print "onQueryForNodes(): ",msg.getMessage()
        if 0 == self.m_keyList.size():
            return

        # Who did the query
        (remoteAddr, s, remoteKey) = msg.getMessage().partition(" ")
        (remoteIp, s, remotePort) = remoteAddr.partition(":")

        # Pick three random nodes
        for keyToSend in self.m_keyList.getRandomKeys(3):
            print keyToSend
            (pAddr, s, pPort) = self.m_keyList[keyToSend].partition(":")
            (dAddr, s, dPort) = self.m_keyList[remoteKey].partition(":")
            print  self.m_keyList[keyToSend]
            print self.m_keyList.toString()
            print "doAddNode(", remoteIp, remotePort, pAddr, pPort, keyToSend, ")"
            self.doAddNode(remoteIp, int(remotePort), pAddr, int(pPort), keyToSend )

    #TODO: Add case for when I think I should have the data, but don't
    def onAddData(self, msg, sock):
        if not self.isAlive(): return false
                
        sha = hashlib.sha1()
        sha.update( msg.getMessage() )
        key = sha.hexdigest()

        print "hash for:", msg.getMessage(), "was:", key
        print self.m_keyList.toString()
        print "My id:", self.m_key

        
        if self.isKeyInRange(key):
            ## Add the data
            print "answer OK"
            ## TODO: Chache eviction scheme here.
            self.m_data[sha.hexdigest()] = msg.getMessage()
            okMsg = message.Message()
            okMsg.setType(11)
            okMsg.setMessage("OK")
            sock.send(okMsg.toString())
            
        else:
            print "divert to next node"
            print "answer with correct node address"

            # Find a better node and save as "peer"
            nextPeer = self.m_keyList.getPrevVal(key) + " "+  self.m_keyList.getPrevKey(key)
            print "Going to answer", nextPeer
            divMsg = message.Message()
            divMsg.setType(12)
            divMsg.setMessage( nextPeer )

            print "divertReply:", divMsg.toString()
            #divMsg.setMessage(peerAddr)
            sock.send(divMsg.toString())

    def onGetData(self, msg, sock):
        if not self.isAlive(): return false
        
        print "onGetData(", msg.getType(), msg.getMessage(), ")"
        key = msg.getMessage()

        print self.m_data

        if key in self.m_data:
            print "I should have that data..."
            msg = message.Message()
            msg.setType(21)
            msg.setMessage( self.m_data[key] )
            sock.send( msg.toString() )
            
        else:
            print "Some one else should have that data..."
            print "msgKey:", key
            print "mykey:", self.m_key
            print "keyList:", self.m_keyList.toString()
            msg = message.Message()
            msg.setType(22)
            suggestedNodeKey = self.m_keyList.getPrevKey(key)
            suggestedNodeAddr = self.m_keyList.get(suggestedNodeKey)
            print "msg.setMessage( "+suggestedNodeAddr+" "+suggestedNodeKey+" )"
            msg.setMessage( suggestedNodeAddr+" "+suggestedNodeKey  )
            sock.send( msg.toString() )

    
    def isKeyInRange(self, key):
        if not self.isAlive(): return false
        
        print "isKeyInRange(",key,")"
        print self.m_keyList.toString()

        if 1 >= self.m_keyList.size():
            return 1
        prevKey = self.m_keyList.getPrevKey(self.m_key)
        if(prevKey < self.m_key):
            if prevKey < key and key <= self.m_key:
                return 1
            else: return 0
        else:
            if prevKey > key or key <= self.m_key:
                return 1
            else: return 0
            

    def handle(self):
        if not self.isAlive(): return false
        
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
                self.onAddNode( msg, self.request )
            if( 2 == msg.getType() ):
                print "onQueryForNodes!"
                self.onQueryForNodes( msg, self.request )
            if( 10 == msg.getType() ):
                print "onAddData!"
                self.onAddData( msg, self.request )
            if( 11 == msg.getType() ):
                print "Data was added (ignored message)"
            if( 12 == msg.getType() ):
                print "dataDiverted (ignored message)"
            if( 20 == msg.getType() ):
                print "onGetData!"
                self.onGetData( msg, self.request )

            print "" 

            recvMsg = self.request.recv(1024).strip()        


def signal_handler(signal, frame):
        print 'You pressed Ctrl+C!'
        sys.exit(0)            

### Global var


### MAIN()
# args: 1: myIP, 2: myPort, 3: knownIP, 4: knownPort
def main(args):
    signal.signal(signal.SIGINT, signal_handler)

    node = DHTNode(args[1],  int(args[2]) )

    print "My ID:", node.getKey()

    ### ORDINARY OPERATION
    # start the DHT Node thread
    node.start()

    ## BOOTSTRAP
    # if defined
    if len(args) == 5:
        time.sleep(2)
        # register with known node
        # query list for new nodes
        node.doAddNode(args[3], int(args[4]), args[1], int(args[2]), node.getKey() )
        node.doQueryForNodes(args[3], int(args[4]) )

    node.join()

if __name__ == '__main__':
  main(sys.argv)
