url=$(aws amplify list-apps \
    --query 'apps[0].[defaultDomain]' \
    --output text)
# Write endpoint to file for code to use.
echo https://dev.$url > src/code/websiteurl.txt
