from lxml import etree
import csv

header = ['Id','CreationDate','PostId','RelatedPostId','LinktTypeId']
xmlfilename = "c:\\workdir\\stackexchange\\PostLinks.xml"
csvfilename = "c:\\workdir\\stackexchange\\PostLinks.csv"

f = open(csvfilename, 'w', newline='', encoding="utf-8")
w = csv.writer(f, delimiter='·')
w.writerow(header)

context = etree.iterparse(xmlfilename, events=('end',), tag='row')

for event, element in context:
    row = [element.attrib['Id'], element.attrib['CreationDate'], element.attrib['PostId'], element.attrib['RelatedPostId'], element.attrib['LinkTypeId']]
    w.writerow(row)
    element.clear()
    while element.getprevious() is not None:
        del element.getparent() [0]

f.close()