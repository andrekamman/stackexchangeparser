from lxml import etree
import csv

header = ['Id', 'PostTypeId', 'ParentID', 'AcceptedAnswerId', 'CreationDate', 'Score', 'ViewCount', 'Body', 'OwnerUserId', 'LastEditorUserId', 'LastEditorDisplayName', 'LastEditDate', 'LastAcitvityDate', 'CommunityOwnedDate', 'ClosedDate' ,'Title', 'Tags', 'AnswerCount', 'CommentCount', 'FavouriteCount']
xmlfilename = "c:\\workdir\\stackexchange\\Posts.xml"
csvfilename = "c:\\workdir\\stackexchange\\Posts.csv"

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

    if (rowcounter == 5):
            break

    while element.getprevious() is not None:
        del element.getparent() [0]

f.close()