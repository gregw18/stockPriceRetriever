#!/bin/bash
set -eo pipefail
if [ $# == 0 ]
then
	echo "Please provide path to spreadsheet to upload"
else
	cp $1 src/code/Portfolio.xls
	ARTIFACT_BUCKET=$(cat src/code/bucket-name.txt)
	aws cloudformation package --template-file template.yml --s3-bucket $ARTIFACT_BUCKET --output-template-file out.yml
	aws cloudformation deploy --template-file out.yml --stack-name stock-price-retriever --capabilities CAPABILITY_NAMED_IAM \
	 --parameter-overrides file://src/code/dbparams.json
fi
