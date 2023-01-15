"""
Hack to let test modules find src modules that they are testing.
Would love to know of a better approach.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../src/code")
