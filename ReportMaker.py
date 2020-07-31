from mdutils.mdutils import MdUtils as mdu
import time
from datetime import datetime
import os

class ReportMaker():

    def __init__(self, filename):
        self.startTime = time.time()
        self.filename = filename#+str(int(self.startTime))
        self.mdFile = mdu(file_name = filename, title = "GEO Forensics Report")

    def save(self):
        self.endTime = time.time()
        date = str(datetime.fromtimestamp(self.endTime))
        self.mdFile.write("  \n")
        self.mdFile.write("Saved at: ", bold_italics_code = 'bi')
        self.mdFile.write(date)
        self.mdFile.create_md_file()
        cmdConversion = "pandoc " + self.filename + ".md --pdf-engine=xelatex -o " + self.filename + ".pdf" 
        os.system(cmdConversion)

    def makeHeader(self, username):
        '''
        Write header with timestamp, username
        '''
        self.mdFile.write("Author: ", bold_italics_code = 'bi')
        self.mdFile.write(username.upper())
        self.mdFile.write("  \n")
        date = str(datetime.fromtimestamp(self.startTime))
        self.mdFile.write("Date: ", bold_italics_code = 'bi')
        self.mdFile.write(date)
        self.mdFile.write("  \n")

    def makeUploadSection(self):
        self.mdFile.new_header(level = 3, title = "Uploads Section")
        self.mdFile.new_paragraph("This section contains the list of uploaded takeouts  \n", bold_italics_code = "i")

    def insertUpload(self, filename):
        date = str(datetime.fromtimestamp(time.time()))
        self.mdFile.write("File ")
        self.mdFile.write(filename, bold_italics_code = "c")
        self.mdFile.write(" at date ")
        self.mdFile.write(date, bold_italics_code = "i")
        self.mdFile.write("  \n")

    def makePlacesSection(self):
        self.mdFile.new_header(level = 3, title = "Places Section")
        self.mdFile.new_paragraph("This section contains the table of places visited.", bold_italics_code = "i")
        self.mdFile.write("  \n")
    
    def insertPlaces(self, places, filename, minDuration):
        self.mdFile.new_header(level = 4, title = filename)
        self.mdFile.write("  \nFor the file ")
        self.mdFile.write(filename, bold_italics_code = "c")
        self.mdFile.write(" ")
        self.mdFile.write(str(len(places)), bold_italics_code = "b")
        self.mdFile.write(" places with duration at least ")
        self.mdFile.write(str(minDuration), bold_italics_code = "b")
        self.mdFile.write(" seconds have been found at date ")
        date = str(datetime.fromtimestamp(time.time()))
        self.mdFile.write(date, bold_italics_code = "i")
        self.mdFile.write(".  \n")
        tableContent = ["Start Time", "End Time", "Latitude", "Longitude", "Address", "Confidence"]
        for i in range(len(places)):
            startTime = str(datetime.fromtimestamp(places[i]["startTS"]//1000))
            endTime = str(datetime.fromtimestamp(places[i]["endTS"]//1000))
            tableContent.extend([startTime, endTime, str(places[i]["lat"]), str(places[i]["long"]), places[i]["address"], str(places[i]["confidence"])])
        self.mdFile.new_line()
        self.mdFile.new_table(columns = 6, rows = len(places)+1, text = tableContent, text_align = "center")

    def makeComparisonSection(self):
        self.mdFile.new_header(level = 3, title = "Comparisons Section")
        self.mdFile.new_paragraph("This section contains all comparison between uploaded files.  \n", bold_italics_code = "i")

    def insertMeeting(self, data, filenames):
        self.mdFile.write("  \n")
        self.mdFile.write("The input files ")
        for i in range(len(filenames)):
            self.mdFile.write(filenames[i], bold_italics_code = "c")
            if i == (len(filenames)-1): self.mdFile.write(" ")
            else: self.mdFile.write(", ")
        self.mdFile.write(" have been compared; there are ")
        self.mdFile.write(str(len(data)//(len(filenames)-1)), bold_italics_code = "i")
        self.mdFile.write(" meetings.  \n")
        masterFilename = filenames[0]
        for i in range(0, len(data), len(filenames)-1):
            address = data[i][9]
            self.mdFile.write(address, bold_italics_code = "bi")
            self.mdFile.write(":  \n\t")
            self.mdFile.write("Input file ")
            self.mdFile.write(masterFilename, bold_italics_code = "c")
            self.mdFile.write(":  \n")
            listInfo = ["Start Time " + str(datetime.fromtimestamp(data[i][0]//1000)), "End Time " + str(datetime.fromtimestamp(data[i][1]//1000)), "Latitude " + str(data[i][4]), "Longitude " + str(data[i][5]), "Distance " + str(data[i][8]) + " meters"]
            self.mdFile.new_list(listInfo)
            self.mdFile.write("  \n")
            for j in range(i, i + len(filenames) - 1):
                self.mdFile.write("Input file ")
                self.mdFile.write(filenames[j - i + 1], bold_italics_code = "c")
                self.mdFile.write(":  \n")
                listInfo = ["Start Time " + str(datetime.fromtimestamp(data[j][2]//1000)), "End Time " + str(datetime.fromtimestamp(data[j][3]//1000)), "Latitude " + str(data[j][6]), "Longitude " + str(data[j][7]), "Distance " + str(data[j][8]) + " meters"] 
                self.mdFile.new_list(listInfo)
                self.mdFile.write("  \n")
        self.mdFile.write("  \n")

    def makeQueriesTimestampSection(self):
        self.mdFile.new_header(level = 3, title = "Queries section - Timestamp")
        self.mdFile.new_paragraph("This section contains all queries based on timestamp about input files.  \n", bold_italics_code = "i")
        self.mdFile.write("  \n")

    def insertQueryTimestamp(self, filename, queryInput, queryOutput):
        self.mdFile.write("The input file ")
        self.mdFile.write(filename, bold_italics_code = "c")
        self.mdFile.write(" at ")
        self.mdFile.write(str(queryInput), bold_italics_code = "i")
        if queryOutput: 
            self.mdFile.write(" is in ")
            self.mdFile.write(queryOutput["address"], bold_italics_code = "i")
            self.mdFile.write(" (latitude ")
            self.mdFile.write(str(queryOutput["lat"]), bold_italics_code = "i")
            self.mdFile.write(", longitude ")
            self.mdFile.write(str(queryOutput["long"]), bold_italics_code = "i")
            self.mdFile.write(") because it stays in this place from ")
            self.mdFile.write(str(datetime.fromtimestamp(int(queryOutput["startTS"]))), bold_italics_code = "i")
            self.mdFile.write(" to ")
            self.mdFile.write(str(datetime.fromtimestamp(int(queryOutput["endTS"]))), bold_italics_code = "i")
            self.mdFile.write(".  \n")
        else:
            self.mdFile.write(" has no values.  \n")

    def makeQueriesPlacesSection(self):
        self.mdFile.new_header(level = 3, title = "Queries section - Places")
        self.mdFile.new_paragraph("This section contains all queries based on places about input files.  \n", bold_italics_code = "i")
        self.mdFile.write("  \n")

    def insertQueryPlace(self, filename, queryInput, queryOutput, distance):
        self.mdFile.write("Have been ")
        self.mdFile.write(filename, bold_italics_code = "c")
        self.mdFile.write(" registered at the place (")
        self.mdFile.write(str(queryInput[0]), bold_italics_code = "i")
        self.mdFile.write(", ")
        self.mdFile.write(str(queryInput[1]), bold_italics_code = "i")
        self.mdFile.write(") with maximum distance of ")
        self.mdFile.write(str(distance), bold_italics_code = "i")
        self.mdFile.write(" meters ")
        if len(queryInput) == 4:
            self.mdFile.write("from ")
            self.mdFile.write(str(queryInput[2]), bold_italics_code = "i")
            self.mdFile.write(" to ")
            self.mdFile.write(str(queryInput[3]), bold_italics_code = "i")
        self.mdFile.write("? ")
        self.mdFile.write(str(queryOutput), bold_italics_code = "bi")
        self.mdFile.write(".  \n")

    def makeAttachmentsSection(self, attachmentsList):
        self.mdFile.new_header(level = 3, title = "Attachments")
        self.mdFile.new_paragraph("This section contains all attachments created by GeoForensics.  \n", bold_italics_code = "i")
        for att in attachmentsList:
            self.mdFile.write("  \n")
            self.mdFile.write(att[0], bold_italics_code = "c") #filename
            self.mdFile.write(" created at ")
            self.mdFile.write(str(datetime.fromtimestamp(int(att[1]))), bold_italics_code = "i")
            self.mdFile.write(". Checksum:  \n")
            self.mdFile.write("MD5: ", bold_italics_code = "b")
            self.mdFile.write(str(att[2]), bold_italics_code = "c")
            self.mdFile.write("  \n")
            self.mdFile.write("SHA-1:  ", bold_italics_code = "b")
            self.mdFile.write(str(att[3]), bold_italics_code = "c")
            self.mdFile.write("  \n")

    
        