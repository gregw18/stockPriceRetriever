url=$(aws rds describe-db-instances \
    --query 'DBInstances[0].[DBInstanceIdentifier]' \
    --output text)
# Write endpoint to file for code to use.
echo https://dev.$url > dbidentifier.txt
