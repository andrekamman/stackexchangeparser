BULK INSERT dbo.Badges
FROM 'D:\output\coffee.stackexchange.com\Badges.csv'
WITH
(
	FORMAT = 'CSV',
	CODEPAGE = '65001',
	FIELDTERMINATOR = ',',
	BATCHSIZE = 100000,
	FIRSTROW = 2
)

BULK INSERT dbo.Comments
FROM 'D:\output\coffee.stackexchange.com\Comments.csv'
WITH
(
	FORMAT = 'CSV',
	CODEPAGE = '65001',
	FIELDTERMINATOR = ',',
	BATCHSIZE = 1000000,
	FIRSTROW = 2
)

BULK INSERT dbo.PostHistory
FROM 'D:\output\coffee.stackexchange.com\PostHistory.csv'
WITH
(
	FORMAT = 'CSV',
	CODEPAGE = '65001',
	FIELDTERMINATOR = ',',
	BATCHSIZE = 100000,
	FIRSTROW = 2
)

BULK INSERT dbo.PostHistoryTypes
FROM 'D:\output\coffee.stackexchange.com\PostHistoryTypes.csv'
WITH
(
	FORMAT = 'CSV',
	CODEPAGE = '65001',
	FIELDTERMINATOR = ',',
	BATCHSIZE = 1000000,
	FIRSTROW = 2
)
BULK INSERT dbo.PostLinks
FROM 'D:\output\coffee.stackexchange.com\PostLinks.csv'
WITH
(
	FORMAT = 'CSV',
	CODEPAGE = '65001',
	FIELDTERMINATOR = ',',
	BATCHSIZE = 100000,
	FIRSTROW = 2
)

BULK INSERT dbo.Posts
FROM 'D:\output\coffee.stackexchange.com\Posts.csv'
WITH
(
	FORMAT = 'CSV',
	CODEPAGE = '65001',
	FIELDTERMINATOR = ',',
	BATCHSIZE = 1000000,
	FIRSTROW = 2
)

BULK INSERT dbo.PostTypes
FROM 'D:\output\coffee.stackexchange.com\PostTypes.csv'
WITH
(
	FORMAT = 'CSV',
	CODEPAGE = '65001',
	FIELDTERMINATOR = ',',
	BATCHSIZE = 100000,
	FIRSTROW = 2
)

BULK INSERT dbo.Tags
FROM 'D:\output\coffee.stackexchange.com\Tags.csv'
WITH
(
	FORMAT = 'CSV',
	CODEPAGE = '65001',
	FIELDTERMINATOR = ',',
	BATCHSIZE = 1000000,
	FIRSTROW = 2
)

BULK INSERT dbo.Users
FROM 'D:\output\coffee.stackexchange.com\Users.csv'
WITH
(
	FORMAT = 'CSV',
	CODEPAGE = '65001',
	FIELDTERMINATOR = ',',
	BATCHSIZE = 100000,
	FIRSTROW = 2
)

BULK INSERT dbo.Votes
FROM 'D:\output\coffee.stackexchange.com\Votes.csv'
WITH
(
	FORMAT = 'CSV',
	CODEPAGE = '65001',
	FIELDTERMINATOR = ',',
	BATCHSIZE = 1000000,
	FIRSTROW = 2
)

BULK INSERT dbo.VoteTypes
FROM 'D:\output\coffee.stackexchange.com\VoteTypes.csv'
WITH
(
	FORMAT = 'CSV',
	CODEPAGE = '65001',
	FIELDTERMINATOR = ',',
	BATCHSIZE = 100000,
	FIRSTROW = 2
)


