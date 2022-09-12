#!/bin/bash
set -eo pipefail

aws cloudformation describe-stack-events --stack-name stock-price-retriever