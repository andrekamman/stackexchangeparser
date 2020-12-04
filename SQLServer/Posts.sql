Create Table Posts(
   Id int NOT NULL,
   PostTypeId tinyint NOT NULL,
   AcceptedAnswerId int NULL,
   CreationDate datetime NOT NULL,
   Score int NOT NULL,
   ViewCount int NULL,
   Body nvarchar(max) NULL,
   OwnerUserId int NULL,
   LastActivityDate datetime NULL,
   Title nvarchar(500) NULL,
   Tags nvarchar(500) NULL,
   AnswerCount int NULL,
   CommentCount int NULL,
   FavoriteCount int NULL,
   ContentLicense varchar(12)
)


