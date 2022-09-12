#!/bin/bash
# Run pytest for all tests except those that require moto library.
# Can pass in additional parameters, such as -rP to print full results for passing tests.
# Can run pytest --markers to get list of markers used.

pytest $1 --ignore=../../tests/test_fileManagement.py \
            --ignore=../../tests/test_notification.py \
            ../../tests/