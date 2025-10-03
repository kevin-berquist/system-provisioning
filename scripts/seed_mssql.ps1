param(
    [string]$ContainerName = 'system-provisioning_mssql_1',
    [string]$SqlFile = 'sql\seed_ticketsysteminstallations.sql',
    [string]$SaPassword = 'Your_strong@Passw0rd'
)

if (-not (Test-Path $SqlFile)) {
    Write-Error "SQL file not found: $SqlFile"
    exit 1
}

Write-Output ('Copying {0} into container {1}:/tmp/seed.sql' -f $SqlFile, $ContainerName)
docker cp $SqlFile "${ContainerName}:/tmp/seed.sql"

Write-Output ('Running seed via sqlcmd inside container {0}' -f $ContainerName)
docker exec -i $ContainerName /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P $SaPassword -i /tmp/seed.sql
