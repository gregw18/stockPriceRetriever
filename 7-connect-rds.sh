#!/bin/bash
set -eo pipefail

identifier=$(<dbidentifier.txt)

endpoint=$(aws rds describe-db-instances \
    --db-instance-identifier $identifier \
    --query 'DBInstances[*].[Endpoint.Address]' \
    --output text)

mysql -h $endpoint -u stockDbRoot -p