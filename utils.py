import hashlib

def getMD5sum(file):
    md5sum = hashlib.md5()
    inputFile = open(file, "rb")
    content = inputFile.read()
    md5sum.update(content)
    return md5sum.hexdigest()

def getSHA1sum(file):
    sha1sum = hashlib.sha1()
    inputFile = open(file, "rb")
    content = inputFile.read()
    sha1sum.update(content)
    return sha1sum.hexdigest()

def createCoupleTuple(mylist):
    i = 0
    myCouples = []
    while i < (len(mylist)-1):
        item1 = mylist[i]
        item2 = mylist[i+1]
        myCouples.append((item1, item2))
        i+=2
    return myCouples

def fromTuplesToOneList(tuple1, tuple2):
    oneList = list(tuple1)
    for item in tuple2: oneList.append(item)
    return oneList