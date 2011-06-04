import random
import copy

class CircularList:
    m_list = list()
    m_dict = dict()

    def size(self):
        return len(self.m_list)

    def get(self, key ):
        return self.m_dict[ key ]

    def add(self, key, val):
        if key in self.m_dict:
            return -1
        self.m_list.append(key)
        self.m_list.sort() # Sort on insert
        self.m_dict[key] = val
        return 1

    def remove(self, key):
        if key not in self.m_dict:
            return -1
        del self.m_dict[key]
        self.m_list.remove(key)
        return 1

    def getVal(self, key):
        return self.m_dict[key]

    def getNextKey(self, key):
        if 0 == self.size():
            return -1

        # for each, do arr-key - key, smallest but > 0 is next.
        nextKey = ""
        for item in self.m_list :
            if item > key :
                nextKey = item
                break;

        if "" == nextKey :  # Rotate/overflow?
            nextKey = self.m_list[0]

        return self.m_list[ self.m_list.index(nextKey) ]

    def getNextVal(self, key):
        return self.m_dict[ self.getNextKey(key) ]

    def getPrevKey(self, key):
        if 0 == self.size():
            return 0

        # for each, do arr-key - key, smallest but > 0 is next.
        nextKey = ""
        for item in reversed( self.m_list ) :
            if item < key :
                nextKey = item
                break;

        if "" == nextKey :  # Rotate/overflow?
            nextKey = self.m_list[0]

        return self.m_list[ self.m_list.index(nextKey) ]

    def getPrevVal(self, key):
        return self.m_dict[ self.getPrevKey(key) ]

    def toString(self):
        retStr = "{"
        for item in self.m_list:
            retStr += "("+str(item)+":"
            retStr += str(self.m_dict[item])+")"
        retStr += "}"
        return retStr

    def getRandomKeys(self, count):
        if 0 == len(self.m_list):
            return []
        count = min(count, len(self.m_list) )

        randList = copy.deepcopy(self.m_list)
        random.shuffle(randList)
        return randList[0:count]
