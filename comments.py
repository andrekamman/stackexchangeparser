from lxml import etree
import csv

header = ['Id', 'PostId', 'Score', 'Text', 'CreationDate', 'UserId']
xmlfilename = "c:\\workdir\\stackexchange\\stackoverflow.com-Comments\\Comments.xml"
csvfilename = "c:\\workdir\\stackexchange\\Comments.csv"

f = open(csvfilename, 'w', newline='', encoding="utf-8")
w = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
w.writerow(header)

context = etree.iterparse(xmlfilename, events=('end',), tag='row')
rowcounter = 0

for event, element in context:
    rowcounter += 1
    if (rowcounter % 1000000 == 0):
        print(rowcounter)

    if 'PostId' not in element.attrib:
        PostId = ''
    else: 
        PostId = element.attrib['PostId']

    if 'Score' not in element.attrib:
        Score = ''
    else: 
        Score = element.attrib['Score']

    if 'Text' not in element.attrib:
        Text = ''
    else: 
        Text = element.attrib['Text']
    
    if 'UserId' not in element.attrib:
        UserId = ''
    else:
        UserId = element.attrib['UserId']

    Text = Text.replace("\r\n","&#xd;&#xa;").replace("\r","&#xD;").replace("\n", "&#xA;")

    row = [element.attrib['Id'], PostId, Score, Text, element.attrib['CreationDate'], UserId]
    w.writerow(row)
    element.clear()

    #if (rowcounter == 5):
    #        break

    while element.getprevious() is not None:
        del element.getparent() [0]

f.close()