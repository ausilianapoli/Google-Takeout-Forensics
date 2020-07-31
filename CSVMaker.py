import pandas as pd
import time
from datetime import datetime
import os

class CSVMaker():
    def __init__(self):
        pass

    def createPlacesCSV(self, data, filename):
        with open(filename, 'w') as f:
            f.write("startTS,endTS,startTime,endTime,lat,long,confidence")
            f.write("\n")
            for d in data:
                keysList = list(d.keys())
                for key in d.keys():
                    if key == "address": continue
                    f.write("%s"%d[key])
                    if str(key) != keysList[-1]: f.write(",")
                f.write("\n")
            f.close()

    def createComparisonsCSV(self, data, filename):
        with open(filename, "w") as f:
            f.write("startTS,endTS,starTS,endTS,lat,long,lat,long,distance,address")
            f.write("\n")
            for d in data:
                for i in range(len(d)):
                    f.write("%s"%d[i])
                    if i != (len(d)-1): f.write(",")
                f.write("\n")
            f.close()

    def createQueryTimestampCSV(self, queryInput, queryOutput, inputFile, filename):
        with open(filename, "a") as f:
            f.write("input-file,datetime-query,lat,long,startTS,startTime,endTS,endTime,confidence")
            f.write("\n")
            f.write(inputFile + ",")
            f.write(str(queryInput)+",")
            #f.write(queryOutput["address"] + ",")
            f.write(str(queryOutput["lat"]) + ",")
            f.write(str(queryOutput["long"]) + ",")
            f.write(str(queryOutput["startTS"]) + ",")
            f.write(str(queryOutput["startTime"]) + ",")
            f.write(str(queryOutput["endTS"]) + ",")
            f.write(str(queryOutput["endTime"]) + ",")
            f.write(str(queryOutput["confidence"]))
            f.write("\n")
            f.close()
    