import json
from datetime import datetime
import os
import time
from math import sin, cos, sqrt, atan2, radians
import numpy as np
import sys

class SegmentParser():
    def __init__(self):
        pass

    def distance_GPS(self, lat1,lon1,lat2,lon2, R = 6357000.0):

        lat1 = radians(lat1)
        lon1 = radians(lon1)
        lat2 = radians(lat2)
        lon2 = radians(lon2)

        dlon = lon2 - lon1
        dlat = lat2 - lat1

        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        return R * c

    def parsePlaceHistory(self, filename, minDuration):
        try:
            data = json.load(open(filename,'r'))
        except json.JSONDecodeError:
            sys.exit("ERROR You must pass JSON file")

        places = []
        try:
            for to in data["timelineObjects"]:
                for key in to:
                    if key == "placeVisit":
                        place = dict()
                        place["startTS"] = int(to[key]["duration"]["startTimestampMs"])
                        place["endTS"] = int(to[key]["duration"]["endTimestampMs"])
                        place["startTime"] = datetime.fromtimestamp((int(float(to[key]["duration"]["startTimestampMs"])/1000)))
                        place["endTime"] = datetime.fromtimestamp((int(float(to[key]["duration"]["endTimestampMs"])/1000)))
                        place["lat"] = float(to[key]["location"]["latitudeE7"])/10000000
                        place["long"] = float(to[key]["location"]["longitudeE7"])/10000000
                        try:
                            place["address"] = to[key]["location"]["address"].replace('\n',' ')
                        except KeyError:
                            try:
                                place["address"] = to[key]["location"]["name"].replace('\n',' ')
                            except KeyError:
                                place["address"] = 'NULL'
                        place["confidence"] = to[key]["visitConfidence"]


                        # Selecting only places with duration at least minDuration in seconds
                        duration = place["endTS"] - place["startTS"]
                        if ((duration/1000) >= minDuration):
                            places.append(place)
        except KeyError:
            sys.exit("ERROR You must pass google takeout monthly JSON")

        return places

    def compareVisits(self, placesDict, maxDistance):
        meetings = []
        filenamesList = list(placesDict.keys())  
        masterPlaces = placesDict[filenamesList[0]]
        for i in range(len(masterPlaces)):
            oneBitEncoding = np.zeros(len(filenamesList)-1)
            startTSMaster = masterPlaces[i]["startTS"]
            endTSMaster = masterPlaces[i]["endTS"]
            tmpMeetings = []
            for places in placesDict.keys():
                if places == filenamesList[0]: continue
                slavePlaces = placesDict[places]
                for j in range(len(slavePlaces)):
                    startTSSlave = slavePlaces[j]["startTS"]
                    endTSSlave = slavePlaces[j]["endTS"]
                    if ((startTSSlave >= startTSMaster and startTSSlave <= endTSMaster) or (startTSSlave <= startTSMaster and startTSMaster <= endTSSlave)):
                        distance = self.distance_GPS(masterPlaces[i]["lat"], masterPlaces[i]["long"], slavePlaces[j]["lat"], slavePlaces[j]["long"])
                        if distance <= maxDistance:
                            #print("i ", i)
                            #print("j ", j)
                            oneBitEncoding[filenamesList.index(places)-1] = 1
                            tmpMeetings.append([startTSMaster, endTSMaster, startTSSlave, endTSSlave, masterPlaces[i]["lat"], masterPlaces[i]["long"], slavePlaces[j]["lat"], slavePlaces[j]["long"], distance, masterPlaces[i]["address"]])
            if np.all(oneBitEncoding):
                for meet in tmpMeetings: meetings.append(meet)
        return meetings

    def queryDatetime(self, filename, queryDate):
        timestamp = datetime.timestamp(queryDate)
        data = json.load(open(filename,'r'))
        place = dict()
        
        for to in data["timelineObjects"]:
            for key in to:
                if key == "placeVisit":
                    startTS = int(to[key]["duration"]["startTimestampMs"])//1000
                    endTS = int(to[key]["duration"]["endTimestampMs"])//1000
                    if int(timestamp) >= int(startTS) and int(timestamp) <= int(endTS):
                        place["startTS"] = startTS
                        place["endTS"] = endTS
                        place["startTime"] = datetime.fromtimestamp(startTS)
                        place["endTime"] = datetime.fromtimestamp(endTS)
                        place["lat"] = float(to[key]["location"]["latitudeE7"])/10000000
                        place["long"] = float(to[key]["location"]["longitudeE7"])/10000000
                        try:
                            place["address"] = to[key]["location"]["address"].replace('\n',' ')
                        except KeyError:
                            try:
                                place["address"] = to[key]["location"]["name"].replace('\n',' ')
                            except KeyError:
                                place["address"] = 'NULL'
                        place["confidence"] = to[key]["visitConfidence"]
                        break

        return place

    
    def queryPlaces(self, filename, queryCoord, maxDistance, timestamps = None):
        if timestamps is not None:
            startTS = datetime.timestamp(timestamps[0])
            endTS = datetime.timestamp(timestamps[1])
        latitude = queryCoord[0]
        longitude = queryCoord[1]

        data = json.load(open(filename,'r'))
        
        for to in data["timelineObjects"]:
            for key in to:
                if key == "placeVisit":
                    latFile = float(to[key]["location"]["latitudeE7"])/10000000
                    longFile = float(to[key]["location"]["longitudeE7"])/10000000
                    distance = self.distance_GPS(float(latitude), float(longitude), latFile, longFile)
                    if distance <= maxDistance:
                        if timestamps is None: return True
                        else:
                            startFile = int(to[key]["duration"]["startTimestampMs"])//1000
                            endFile = int(to[key]["duration"]["endTimestampMs"])//1000
                            if (startTS >= startFile and startTS <= endFile) and (endTS >= startFile and endTS <= endFile): return True
        return False
