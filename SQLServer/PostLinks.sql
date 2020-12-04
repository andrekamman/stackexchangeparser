Create Table PostLinks(
   Id int NOT NULL,
   CreationDate datetime NOT NULL,
   PostId int NOT NULL,
   RelatedPostId int NOT NULL,
   LinkTypeId tinyint NOT NULL,
)
