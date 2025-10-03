-- Seed script for TicketsystemInstallations used by ShoWare System Setup integration tests
IF OBJECT_ID('dbo.TicketsystemInstallations', 'U') IS NOT NULL
  DROP TABLE dbo.TicketsystemInstallations;

CREATE TABLE dbo.TicketsystemInstallations (
  Id INT IDENTITY(1,1) PRIMARY KEY,
  Name NVARCHAR(255) NOT NULL,
  DatabaseName NVARCHAR(255) NOT NULL,
  GeminiProjectID INT NOT NULL,
  DirPathDev NVARCHAR(512) NULL,
  DevSystemSetup DATETIME NOT NULL,
  DeploymentCountry INT NOT NULL,
  LIVE BIT NOT NULL
);

-- Insert a production-ready row (matches query conditions)
INSERT INTO dbo.TicketsystemInstallations (Name, DatabaseName, GeminiProjectID, DirPathDev, DevSystemSetup, DeploymentCountry, LIVE)
VALUES
('Ripleys Christmas Spectacular','ripleyschristmasspectacular',1979,'qa-ripleyschristmasspectacular.showare.net', DATEADD(day, -1, GETDATE()), 2, 0),
('Sample Dev Only','sampledb',0,'qa-sample.showare.net', DATEADD(day, -200, GETDATE()), 2, 0);

GO
