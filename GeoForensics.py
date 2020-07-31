import argparse
import time
import sys
from itertools import combinations
from datetime import datetime
from SegmentParser import SegmentParser
from ReportMaker import ReportMaker
from CSVMaker import CSVMaker
from utils import *


class GeoForensics():
    def __init__(self, filename):
        #parameters
        self.filename = filename
        self.username = "GeoForensics"
        self.takeouts = []
        self.datetime = None
        self.placeCoord = None
        self.placeTS = None
        self.minDuration = 0
        self.maxDistance = 0.0
        self.createCSV = False
        self._1vs1 = False
        self._1vsN = False
        #modules
        self.sp = SegmentParser()
        self.rm = ReportMaker(self.filename)
        self.cm = CSVMaker()
        #outputs
        self.csvAttachments = []
        self.placesDict = dict()
        self.meetings1vs1 = []
        self.meetings1vsN = []
        self.saveCSVTimestamp = False
        self.queryTimestampList = []
        self.queryPlacesList = []


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--username", type = str, default = "GeoForensics", help = "Username of investigation's author")
    parser.add_argument("--filename", type = str, help = "Filename of report")
    parser.add_argument("--takeouts", type = str, nargs = "+", help = "Paths of monthly JSON takeout")
    parser.add_argument("--datetime", type = str, nargs = "*", default = None, help = "Timestamp to check; format YYYY-MM-DD,hh:mm:ss; you can pass a value for each input file, otherwise single value for all input file")
    parser.add_argument("--placeCoord", type = str, nargs = "*", default = None, help = "(Lat, Long) to check; you can pass a value couple for each input file, otherwise one couple for all input file")
    parser.add_argument("--placeTS", type = str, nargs = "*", default = None, help = "Start and End timestamp to check for (Lat, Long); format YYYY-MM-DD,hh:mm:ss; you can pass a value couple for each input file, otherwise one couple for all input file")
    parser.add_argument("--minDuration", type = int, default = 0, help = "Selecting only places with duration at least minDuration in seconds; default 0")
    parser.add_argument("--maxDistance", type = float, default = 0.0, help = "Radius of search for comparing places; it is meters")
    parser.add_argument("--oneVSone", action = 'store_true', help = "If true comparison oneVSone of takeouts will be made")
    parser.add_argument("--oneVSn", action = "store_true", help = "If true comparison oneVSn of takeouts will be made")
    parser.add_argument("--createCSV", action = 'store_true', help = "If true CSV files are created" )

    opt = parser.parse_args()

    #create object 
    gf = GeoForensics(opt.filename)
    gf.username = opt.username
    gf.takeouts = opt.takeouts
    gf.datetime = opt.datetime
    gf.placeCoord = opt.placeCoord
    gf.placeTS = opt.placeTS
    gf.minDuration = opt.minDuration
    gf.maxDistance = opt.maxDistance
    gf.createCSV = opt.createCSV
    gf._1vs1 = opt.oneVSone
    gf._1vsN = opt.oneVSn

    #check&manage datetime
    if gf.datetime is not None:
        if len(gf.datetime) > 1 and len(gf.datetime) != len(gf.takeouts): sys.exit("ERROR in datetime parameter: you can pass a value for each input files or single value fo all input files")
        elif len(gf.datetime) == 1 and len(gf.takeouts) > 1: 
            for i in range(len(gf.takeouts) - 1): gf.datetime.append(gf.datetime[0])
            if len(gf.takeouts) != len(gf.datetime): sys.exit("ERROR takeouts and datetimes mismatch in size")
        gf.datetime = list(map(lambda x: datetime.strptime(x, "%Y-%m-%d,%H:%M:%S"), gf.datetime))

    #check&manage placeCoord and placeTS
    if gf.placeCoord is not None:
        if len(gf.placeCoord) % 2 == 1: sys.exit("ERROR in placeCoord parameter: you must pass couple of values (lat, long)")
        if len(gf.placeCoord) > 2 and (len(gf.placeCoord)-1) != len(gf.takeouts): sys.exit("ERROR in placeCoord parameter: you can pass a value couple for each input files or one couple fo all input files")
        elif len(gf.placeCoord) == 2 and len(gf.takeouts) > 1:
            for i in range(len(gf.takeouts) -1):
                gf.placeCoord.append(gf.placeCoord[0])
                gf.placeCoord.append(gf.placeCoord[1])
        gf.placeCoord = createCoupleTuple(gf.placeCoord)
        if gf.placeTS is not None:
            if len(gf.placeTS) % 2 == 1: sys.exit("ERROR in placeTS parameter: you must pass couple of values (start Timestamp, end Timestamp)")
            if len(gf.placeTS) > 2 and (len(gf.placeTS)-1) != len(gf.takeouts): sys.exit("ERROR in placeTS parameter: you can pass a value couple for each input files or one couple fo all input files")
            elif len(gf.placeTS) == 2 and len(gf.takeouts) > 1:
                for i in range(len(gf.takeouts) -1):
                    gf.placeTS.append(gf.placeTS[0])
                    gf.placeTS.append(gf.placeTS[1])
            gf.placeTS = list(map(lambda x: datetime.strptime(x, "%Y-%m-%d,%H:%M:%S"), gf.placeTS))
            gf.placeTS = createCoupleTuple(gf.placeTS)
    elif gf.placeTS is not None: sys.exit("ERROR in placeTS parameter: you must pass values to placeCoord parameter, too") 

    #create report
    print("Creating report...")
    gf.rm.makeHeader(gf.username)
    
    #create uploads section
    try:
        print("Uploading {} takeouts...".format(len(gf.takeouts)))
        gf.rm.makeUploadSection()
        for to in gf.takeouts:
            gf.rm.insertUpload(to)
    except TypeError:
        sys.exit("ERROR You must pass almost one JSON file")

    #create places section
    print("Extracting places...")
    gf.rm.makePlacesSection()
    placesDict = dict()
    for to in gf.takeouts:
        try:
            places = gf.sp.parsePlaceHistory(to, gf.minDuration)
        except FileNotFoundError:
            sys.exit("ERROR You must pass existing input files")
        filename = to.replace("json", "csv")
        if gf.createCSV: 
            gf.cm.createPlacesCSV(places, filename)
            gf.csvAttachments.append([filename, time.time(), getMD5sum(filename), getSHA1sum(filename)])
        gf.rm.insertPlaces(places, to, gf.minDuration)
        placesDict[to] = places
    gf.placesDict = placesDict

    #create comparisons section
    if len(gf.takeouts) > 1:
        if gf._1vs1 or gf._1vsN:
            print("Making comparisons...")
            gf.rm.makeComparisonSection()
            if gf._1vs1:
                combinationsOfTakeouts = combinations(gf.takeouts, 2)
                for couple in list(combinationsOfTakeouts):
                    print("Examining {}... ".format(couple))
                    tmpDict = dict()
                    tmpDict[couple[0]] = gf.placesDict[couple[0]]
                    tmpDict[couple[1]] = gf.placesDict[couple[1]]
                    meetings = gf.sp.compareVisits(tmpDict, gf.maxDistance)
                    gf.meetings1vs1.append(meetings)
                    gf.rm.insertMeeting(meetings, [couple[0], couple[1]])
                    if gf.createCSV:
                        filenameForCSV = couple[0] + "_VS_" + couple[1] + ".csv"
                        filenameForCSV = filenameForCSV.replace("/", "_")
                        gf.cm.createComparisonsCSV(meetings, filenameForCSV)
                        gf.csvAttachments.append([filenameForCSV, time.time(), getMD5sum(filenameForCSV), getSHA1sum(filenameForCSV)])
            if gf._1vsN:
                gf.meetings1vsN = gf.sp.compareVisits(gf.placesDict, gf.maxDistance)
                gf.rm.insertMeeting(gf.meetings1vsN, gf.takeouts)
                if gf.createCSV:
                    filenameForCSV = ""
                    for i in range(len(gf.takeouts)):
                        filenameForCSV += gf.takeouts[i]
                        if i == (len(gf.takeouts)-1): filenameForCSV += ".csv"
                        else: filenameForCSV += "_VS_"
                    filenameForCSV = filenameForCSV.replace("/", "_")
                    gf.cm.createComparisonsCSV(gf.meetings1vsN, filenameForCSV)
                    gf.csvAttachments.append([filenameForCSV, time.time(), getMD5sum(filenameForCSV), getSHA1sum(filenameForCSV)])
    else: print("It can not compare more takeouts with one uploaded takeout")

    #create queries timestamp sections
    if gf.datetime is not None:
        print("Making timestamp queries...")
        if gf.createCSV: filenameForCSV = gf.rm.filename + "_QueryTimestamp.csv"
        gf.rm.makeQueriesTimestampSection()
        for couple in zip(gf.takeouts, gf.datetime):
            queryTimestamp = gf.sp.queryDatetime(couple[0], couple[1])
            gf.queryTimestampList.append(queryTimestamp)
            gf.rm.insertQueryTimestamp(couple[0], couple[1], queryTimestamp)
            if queryTimestamp and gf.createCSV: 
                gf.cm.createQueryTimestampCSV(couple[1], queryTimestamp, couple[0], filenameForCSV)
                gf.saveCSVTimestamp = True
        if gf.saveCSVTimestamp and gf.createCSV:
            gf.csvAttachments.append([filenameForCSV, time.time(), getMD5sum(filenameForCSV), getSHA1sum(filenameForCSV)])

    #create queries places sections
    if gf.placeCoord is not None:
        print("Making places queries...")
        gf.rm.makeQueriesPlacesSection()
        if gf.placeTS is not None:
            for triple in zip(gf.takeouts, gf.placeCoord, gf.placeTS):
                queryPlaces = gf.sp.queryPlaces(triple[0], triple[1], gf.maxDistance, triple[2])
                gf.queryPlacesList.append(queryPlaces)
                gf.rm.insertQueryPlace(triple[0], fromTuplesToOneList(triple[1], triple[2]), queryPlaces, gf.maxDistance)
        else:
            for couple in zip(gf.takeouts, gf.placeCoord):
                queryPlaces = gf.sp.queryPlaces(couple[0], couple[1], gf.maxDistance)
                gf.rm.insertQueryPlace(couple[0], list(couple[1]), queryPlaces, gf.maxDistance)
                self.queryPlacesList.append(queryPlaces)

    #create attachments section
    if gf.createCSV:
        gf.rm.makeAttachmentsSection(gf.csvAttachments)

    #save report
    print("Saving report...")
    gf.rm.save()

if __name__ == "__main__":
    main()