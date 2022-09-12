#!/bin/bash
set -eo pipefail

# Retrieving parameters from json file.
# First line retrieves everything after : in line containing target text.
# Second removes first and last two character from results of first.
jsonfile=src/code/dbparams.json
ru=$(grep -A0 '"DbUsername"' $jsonfile | sed -n -e 's/^.*: //p')
rootuser=${ru:1:-2}

pass=$(grep -A0 '"DbPassword"' $jsonfile | sed -n -e 's/^.*: //p')
rootpasswd=${pass:1:-2}

us=$(grep -A0 '"DbUserSR"' $jsonfile | sed -n -e 's/^.*: //p')
dbuser=${us:1:-2}

# Only removing last character, rather than last two, as this is last item in json
#file, and so doesn't have trailing comma.
db=$(grep -A0 '"DbName"' $jsonfile | sed -n -e 's/^.*: //p')
dbname=${db:1:-1}

dbidentifier=$(<dbidentifier.txt)

endpoint=$(aws rds describe-db-instances \
    --db-instance-identifier $dbidentifier \
    --query 'DBInstances[*].[Endpoint.Address]' \
    --output text)

# Write endpoint to file for code to use.
echo $endpoint > src/code/dbendpoint.txt


#Command to test that have correct parameters.
#mysql -h ${endpoint} -u${rootuser} -p${rootpasswd} -e "SELECT VERSION()"

#Various troubleshooting commands
#mysql -h ${endpoint} -u${rootuser} -p${rootpasswd} -e "SHOW DATABASES"
#mysql -h ${endpoint} -u${rootuser} -p${rootpasswd} -e "USE ${dbname}"
#mysql -h ${endpoint} -u${rootuser} -p${rootpasswd} -e "SELECT host, user from mysql.user"
#mysql -h ${endpoint} -u${rootuser} -p${rootpasswd} -e "SHOW GRANTS FOR ${dbuser}@localhost"

mysql -h ${endpoint} -u${rootuser} -p${rootpasswd} -e "CREATE DATABASE IF NOT EXISTS ${dbname}"
mysql -h ${endpoint} -u${rootuser} -p${rootpasswd} -e "CREATE USER IF NOT EXISTS ${dbuser}@'%' IDENTIFIED WITH AWSAuthenticationPlugin AS 'RDS' REQUIRE SSL"
mysql -h ${endpoint} -u${rootuser} -p${rootpasswd} -e "GRANT ALTER, CREATE, DELETE, DROP, INDEX, INSERT, SELECT, UPDATE ON ${dbname}.* TO ${dbuser}"
