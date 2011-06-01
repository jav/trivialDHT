import string
import re 

class Message:

    def parseMsg(self, msg_string):
        self.raw_message = msg_string
        pattern = re.compile("([0-9]+) (.*)")
        split = pattern.match(self.raw_message)
        self.type = int( split.group(1) )
        self.message = split.group(2)
        
    def setType(self, type):
        self.type = type
        return self.type

    def getType(self):
        return self.type

    def getTypeAsString(self):
        if 1 == self.getType():
            return "newNode"
        else:
            return "unknown type"
        
    def getAddress(self):
        if 1 == self.getType():
            (address, sep, id) = self.message.partition(" ")
            return address
        else:
            return ""

    def getId(self):
        if 1 == self.getType():
            (address, sep, id) = self.message.partition(" ")
            return id
        else:
            return ""

    def setMessage(self, message):
        self.message = message
        return self.message

    def getMessage(self):
        return self.message

    def toString(self):
        return str(self.getType()) + " " + self.getMessage()
