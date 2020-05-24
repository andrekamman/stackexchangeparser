from lxml import etree
from datetime import datetime, timedelta
import csv, os

batches = False
header = ['Id', 'Reputation', 'CreationDate', 'DisplayName', 'EmailHash', 'LastAccessDate', 'WebsiteUrl', 'Location', 'Age', 'AboutMe', 'Views', 'UpVotes', 'DownVotes']
xmlfilename = "c:\\workdir\\stackexchange\\stackoverflow.com-Users\\Users.xml"
csvfiledatepart = '01-01-2020 00:00:00'
csvfiledate = datetime.strptime(csvfiledatepart, '%d-%m-%Y %H:%M:%S')
csvrecordtype = 'Users'
filecounter = 1

if (batches):
    csvfilename = "c:\\workdir\\stackexchange\\batches\\{csvfiledate}{csvrecordtype}\\{csvrecordtype}_{csvfilenumber:05d}.csv".format(csvfiledate=csvfiledate.strftime('%Y%m%d%H%M'), csvrecordtype=csvrecordtype, csvfilenumber=filecounter)
    dirname = "c:\\workdir\\stackexchange\\batches\\{csvfiledate}{csvrecordtype}".format(csvfiledate=csvfiledate.strftime('%Y%m%d%H%M'), csvrecordtype=csvrecordtype)
    os.mkdir(dirname)
else:
    csvfilename = "c:\\workdir\\stackexchange\\{csvrecordtype}.csv".format(csvrecordtype=csvrecordtype)

f = open(csvfilename, 'w', newline='', encoding="utf-8")
w = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
w.writerow(header)

context = etree.iterparse(xmlfilename, events=('end',), tag='row')
rowcounter = 0

for event, element in context:
    rowcounter += 1
    if (rowcounter % 1000000 == 0):
        print(rowcounter)

    if 'Id' not in element.attrib:
        Id = ''
    else: 
        Id = element.attrib['Id']

    if 'Reputation' not in element.attrib:
        Reputation = ''
    else: 
        Reputation = element.attrib['Reputation']

    if 'CreationDate' not in element.attrib:
        CreationDate = ''
    else: 
        CreationDate = element.attrib['CreationDate']
    
    if 'DisplayName' not in element.attrib:
        DisplayName = ''
    else:
        DisplayName = element.attrib['DisplayName']

    if 'EmailHash' not in element.attrib:
        EmailHash = ''
    else: 
        EmailHash = element.attrib['EmailHash']

    if 'LastAccessDate' not in element.attrib:
        LastAccessDate = ''
    else: 
        LastAccessDate = element.attrib['LastAccessDate']

    if 'WebsiteUrl' not in element.attrib:
        WebsiteUrl = ''
    else: 
        WebsiteUrl = element.attrib['WebsiteUrl']

    if 'Location' not in element.attrib:
        Location = ''
    else: 
        Location = element.attrib['Location']

    if 'Age' not in element.attrib:
        Age = ''
    else: 
        Age = element.attrib['Age']

    if 'AboutMe' not in element.attrib:
        AboutMe = ''
    else: 
        AboutMe = element.attrib['AboutMe']

    if 'Views' not in element.attrib:
        Views = ''
    else: 
        Views = element.attrib['Views']

    if 'UpVotes' not in element.attrib:
        UpVotes = ''
    else: 
        UpVotes = element.attrib['UpVotes']

    if 'DownVotes' not in element.attrib:
        DownVotes = ''
    else: 
        DownVotes = element.attrib['DownVotes']

    AboutMe = AboutMe.replace("\r\n","&#xd;&#xa;").replace("\r","&#xD;").replace("\n", "&#xA;")

    row = [Id, Reputation, CreationDate, DisplayName, EmailHash, LastAccessDate, WebsiteUrl, Location, Age, AboutMe, Views, UpVotes, DownVotes]
    w.writerow(row)
    element.clear()

    if (batches):
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