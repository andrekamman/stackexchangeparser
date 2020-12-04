Create Table Badges(
   Id int NOT NULL,
   UserId int NOT NULL,
   Name nvarchar(100) NOT NULL,
   Date datetime NOT NULL,
   Class tinyint NOT NULL,
   TagBased bit NOT NULL,
)
