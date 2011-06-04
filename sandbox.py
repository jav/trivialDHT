import circularlist
import random

cirlst = circularlist.CircularList()


for i in range(1,10):
    key = int( random.random()*1000 )
    val = key+1
    cirlst.add(key,val)
    print "added:", val


print ""
print cirlst.toString()


myKey = 500

print "next key is:", cirlst.getNextKey(500)
print "next value is:", cirlst.get(cirlst.getNextKey(500))

print "prev key is:", cirlst.getPrevKey(500)
print "prev value is:", cirlst.get(cirlst.getPrevKey(500))
