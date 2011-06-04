import circularlist
import random

cirlst = circularlist.CircularList()

print "Test getNextKey(1000) on empty list"
print cirlst.getNextKey(1000)

print "Select 100 random keys:"
randomKeys = cirlst.getRandomKeys(100)
for val in randomKeys:
    print "val:", val

print "Test getNextKey(1000) and then getNextKey(1) on list with only 100 as key"
cirlst.add(100, 101)
print cirlst.getNextKey(1000)
print cirlst.getNextKey(1)

print "Test getPrevKey(1000) and then getPrevKey(1) on list with only 100 as key"
print cirlst.getPrevKey(1000)
print cirlst.getPrevKey(1)

print "Add 10 values, random()*1000"

for i in range(1,10):
    key = int( random.random()*1000 )
    val = key+1
    cirlst.add(key,val)
    print "added:", val


print ""
print cirlst.toString()

print "Set myKey = 500, selecting relative keys:"
myKey = 500

print "next key is:", cirlst.getNextKey(500)
print "next value is:", cirlst.get(cirlst.getNextKey(500))

print "prev key is:", cirlst.getPrevKey(500)
print "prev value is:", cirlst.get(cirlst.getPrevKey(500))

print "Select 100 random keys:"
randomKeys = cirlst.getRandomKeys(100)
for val in randomKeys:
    print "val:", val
