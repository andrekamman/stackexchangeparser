from lxml import etree
from pathlib import Path
from datetime import datetime
import os, csv, logging, argparse

parser = argparse.ArgumentParser()
parser.add_argument("inputfolder", help="Location of the StackExchange files or subfolders")
parser.add_argument("outputfolder", help="Export destination folder where subfolders will be created")
parser.add_argument("-m", "--meta", help="Also export the meta files", action="store_true")
parser.add_argument("-p", "--progressindicatorvalue", help="Shows nr of rows imported for larger files", type=int, default=1000000)
args = parser.parse_args()

start_time = datetime.now() 

tables = {
    "Badges": ["UserId","Name","Date"],
    "Comments": ["Id","PostId","Score","Text","CreationDate","UserId"],
    "Posts": ["Id","PostTypeId","ParentId","AccepedAnswerId","CreationDate","Score","ViewCount","Body","OwnerUserId","LastEditorUserId","LastEditorDisplayName","LastEditDate","LastActivityDate","CommunityOwnedDate","ClosedDate","Title","Tags","AnswerCount","CommentCount","FavoriteCount"],
    "PostHistory": ["Id","PostHistoryTypeId","PostId","RevisionGUID","CreationDate","UserId","UserDisplayName","Comment","Text","CloseReasonId"],
    "PostLinks": ["Id","CreationDate","PostId","RelatedPostId","PostLinkTypeId"],
    "Tags": ["Id","TagName","Count","ExcerptPostId","WikiPostId"],
    "Users": ["Id","Reputation","CreationDate","DisplayName","EmailHash","LastAccessDate","WebsiteUrl","Location","Age","AboutMe","View","UpVotes","DownVotes"],
    "Votes": ["Id","PostId","VoteTypeId","CreationDate","UserId","BountyAmount"]
}

dircounter = 0
stackexchangefiles = ["{table}.xml".format(table=table) for table in tables]

inputdir = args.inputfolder
outputdir = args.outputfolder

def fast_scandir(dirname):
    subfolders = [f.path for f in os.scandir(dirname) if f.is_dir()]
    for dirname in list(subfolders):
        subfolders.extend(fast_scandir(dirname))
    return subfolders

def has_validfiles(dirname, validfiles):
    _has_validfiles = False
    files = [f.name for f in os.scandir(dirname) if not f.is_dir()]
    for file in files:
        if file in validfiles:
            _has_validfiles = True
            break
    return _has_validfiles

def write_csv_from_xml(sourcefilename, table, columns, destinationfilename):
    rowcounter = 0
    logging.info("Exporting:  %s - %s.csv", os.path.basename(subfolder), table)
    f = open(destinationfilename, 'w', newline='', encoding="utf-8")
    w = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
    w.writerow(columns)
    context = etree.iterparse(sourcefilename, events=('end',), tag='row')
    for event, element in context:
        rowcounter += 1
        if (rowcounter % args.progressindicatorvalue == 0):
            logging.info("            Exported %s rows for %s in %s", rowcounter, table, os.path.basename(subfolder))
        row=[element.attrib[column].replace("\r\n","&#xD;&#xA;").replace("\r","&#xD;").replace("\n", "&#xA;") if column in element.attrib else '' for column in columns]
        w.writerow(row)
        while element.getprevious() is not None:
            del element.getparent() [0]
    f.close()

format = "%(asctime)s: %(message)s"
logging.basicConfig(format=format, level=logging.INFO,
                    datefmt="%H:%M:%S")

subfolders = fast_scandir(inputdir)  

logging.info("Input  directory: %s", inputdir)
logging.info("Output directory: %s", outputdir)

if args.meta: 
    logging.info("Including meta")
else:
    logging.info("Skipping meta")

for subfolder in subfolders:
    if not args.meta:
        if ".meta." in os.path.basename(subfolder):
            continue
    if has_validfiles(subfolder, stackexchangefiles):
        
        if not os.path.isdir("{outputdir}\\{subfolder}".format(outputdir=outputdir, subfolder=os.path.basename(subfolder))):
            os.mkdir("{outputdir}\\{subfolder}".format(outputdir=outputdir, subfolder=os.path.basename(subfolder)))
            dircounter += 1
            for file in stackexchangefiles:
                if os.path.isfile("{subfolder}\\{file}".format(subfolder=subfolder, file=file)):
                    write_csv_from_xml("{inputdir}\\{subfolder}\\{sourcefile}".format(inputdir=inputdir, subfolder=os.path.basename(subfolder), sourcefile=file), Path(file).stem, tables[Path(file).stem], "{destinationfolder}\\{subfolder}\\{tablename}.csv".format(destinationfolder=outputdir, subfolder=os.path.basename(subfolder), tablename=Path(file).stem))

elapsed_time = datetime.now() - start_time
logging.info("Finished processing, exported to %s new directories in %s", dircounter, elapsed_time)

