from lxml import etree
from datetime import datetime, timedelta
import csv, os

header = ['Id', 'PostHistoryTypeId', 'PostId', 'RevisionGUID', 'CreationDate', 'UserId', 'UserDisplayName', 'Comment', 'Text', 'CloseReasonId']
xmlfilename = "c:\\workdir\\stackexchange\\stackoverflow.com-PostHistory\\PostHistory.xml"
csvfiledatepart = '01-01-2020 00:00:00'
csvfiledate = datetime.strptime(csvfiledatepart, '%d-%m-%Y %H:%M:%S')
csvrecordtype = 'PostHistory'
filecounter = 1
csvfilename = "c:\\workdir\\stackexchange\\batches\\{csvfiledate}{csvrecordtype}\\{csvrecordtype}_{csvfilenumber:05d}.csv".format(csvfiledate=csvfiledate.strftime('%Y%m%d%H%M'), csvrecordtype=csvrecordtype, csvfilenumber=filecounter)
dirname = "c:\\workdir\\stackexchange\\batches\\{csvfiledate}{csvrecordtype}".format(csvfiledate=csvfiledate.strftime('%Y%m%d%H%M'), csvrecordtype=csvrecordtype)
os.mkdir(dirname)

f = open(csvfilename, 'w', newline='', encoding="utf-8")
w = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
w.writerow(header)

context = etree.iterparse(xmlfilename, events=('end',), tag='row')
rowcounter = 0

for event, element in context:
    rowcounter += 1
    if (rowcounter % 1000000 == 0):
        print(rowcounter)

    if 'UserId' not in element.attrib:
        userId = ''
    else: 
        UserId = element.attrib['UserId']

    if 'UserDisplayName' not in element.attrib:
        UserDisplayName = ''
    else: 
        UserDisplayName = element.attrib['UserDisplayName']

    if 'Comment' not in element.attrib:
        Comment = ''
    else: 
        Comment = element.attrib['Comment']
    
    if 'Text' not in element.attrib:
        Text = ''
    else:
        Text = element.attrib['Text']

    if 'CloseReasonId' not in element.attrib:
        CloseReasonId = ''
    else: 
        CloseReasonId = element.attrib['CloseReasonId']

    Comment = Comment.replace("\r\n","&#xD;&#xA;").replace("\r","&#xD;").replace("\n", "&#xA;")
    Text = Text.replace("\r\n","&#xd;&#xa;").replace("\r","&#xD;").replace("\n", "&#xA;")

    row = [element.attrib['Id'], element.attrib['PostHistoryTypeId'], element.attrib['PostId'], element.attrib['RevisionGUID'], element.attrib['CreationDate'], UserId, UserDisplayName, Comment, Text , CloseReasonId]
    w.writerow(row)
    element.clear()

    if (rowcounter % 10000 == 0):
            f.close()
            filecounter += 1
            if (filecounter % 200 == 0):
                csvfiledate = csvfiledate + timedelta(hours=1)
                dirname = "c:\\workdir\\stackexchange\\batches\\{csvfiledate}{csvrecordtype}".format(csvfiledate=csvfiledate.strftime('%Y%m%d%H%M'), csvrecordtype=csvrecordtype)
                os.mkdir(dirname)

            csvfilename = "c:\\workdir\\stackexchange\\batches\\{csvfiledate}{csvrecordtype}\\{csvrecordtype}_{csvfilenumber:05d}.csv".format(csvfiledate=csvfiledate.strftime('%Y%m%d%H%M'), csvrecordtype=csvrecordtype, csvfilenumber=filecounter)
            f = open(csvfilename, 'w', newline='', encoding="utf-8")
            w = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
            w.writerow(header)

    while element.getprevious() is not None:
        del element.getparent() [0]

f.close()