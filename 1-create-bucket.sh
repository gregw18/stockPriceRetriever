#!/bin/bash
BUCKET_NAME=stock-price-retriever
echo $BUCKET_NAME > src/code/bucket-name.txt
aws s3 mb s3://$BUCKET_NAME
