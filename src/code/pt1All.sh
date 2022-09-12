#!/bin/bash
# Run pytest for all tests.
# Can pass in additional parameters, such as -rP to print full results for passing tests.
# Can run pytest --markers to get list of markers used.

pytest $1 ../../tests/