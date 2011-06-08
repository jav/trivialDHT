import string
import re 


####
## addNode
## Type: 1
## Msg: node-to-add-IP:node-to-add-port node-to-add-key
##
## queryForNodes
## Type: 2
## Msg: queryers-IP:queryer-port queryer-key
##
## addData 
## Type: 10
## Msg: dataToAdd
##
## dataRecordedOK
## Type: 11
## Msg: empty
##
## dataDiverted
## Type: 12
## Msg: suggested-node-IP:suggested-node-port suggested-node-key
##
## getData
## Type: 20
## Msg: keyToGet
## 
## dataReplyOK
## Type: 21
## 
## dataReplyDivert
## Type: 22
## Msg: suggested-node-IP:suggested-node-prot suggested-node-key

class Message:
    m_rawMessage = ""
    m_type = ""
    m_message = ""
    
    def parseMsg(self, msg_string):
        print "Message::parseMsg() : ", msg_string
        self.m_rawMessage = msg_string
        pattern = re.compile("([0-9]+) (.*)")
        split = pattern.match(self.m_rawMessage)
        self.m_type = int( split.group(1) )
        self.m_message = split.group(2)
        
    def setType(self, type):
        self.m_type = type
        return self.m_type

    def getType(self):
        return self.m_type

    def getTypeAsString(self):
        if 1 == self.getType():
            return "newNode"
        if 2 == self.getType():
            return "queryForNode"
        else:
            return "unknown type"
        

    def setMessage(self, message):
        self.m_message = message
        return self.m_message

    def getMessage(self):
        return self.m_message

    def toString(self):
        return str(self.getType()) + " " + self.getMessage()
