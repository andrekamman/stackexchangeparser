Create Table Comments(
   Id int NOT NULL,
   PostId int NOT NULL,
   Score int NOT NULL,
   Text nvarchar(1200) NOT NULL,
   CreationDate datetime NOT NULL,
   UserDisplayName nvarchar(80) NULL,
   UserId int NULL,
   ContentLicense varchar(12) NOT NULL,
)
