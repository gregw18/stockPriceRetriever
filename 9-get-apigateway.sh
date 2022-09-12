url=$(aws apigateway get-rest-apis \
    --query 'items[0].[id]' \
    --output text)
# Write endpoint to file for code to use.
echo https://$url.execute-api.us-east-1.amazonaws.com/Prod/data > api_url.txt
