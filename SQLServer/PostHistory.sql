Create Table PostHistory(
   Id int NOT NULL,
   PostHistoryTypeId tinyint NOT NULL,
   PostId int NOT NULL,
   RevisionGUID uniqueidentifier NOT NULL,
   CreationDate datetime NOT NULL,
   UserId int NULL,
   UserDisplayName nvarchar(80) NULL,
   Comment nvarchar(800) NULL,
   Text nvarchar(max) NULL,
   ContentLicense varchar(12) NULL,
)
