#!/bin/bash
set -eo pipefail
ARTIFACT_BUCKET=$(cat code/bucket-name.txt)
aws cloudformation package --template-file template.yml --s3-bucket $ARTIFACT_BUCKET --output-template-file out.yml
aws cloudformation deploy --template-file out.yml --stack-name stock-price-retriever --capabilities CAPABILITY_NAMED_IAM
