#!/bin/bash
set -eo pipefail
rm -rf package
pip install --target package/python -r code/requirements.txt
