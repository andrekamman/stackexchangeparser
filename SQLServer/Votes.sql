Create Table Votes(
   Id int NOT NULL,
   PostId int NOT NULL,
   VoteTypeId tinyint NOT NULL,
   UserId int NULL,
   CreationDate datetime NULL,
   BountyAmount int NULL,
)
