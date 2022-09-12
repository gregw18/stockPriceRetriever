"""
File to test argument parsing
V0.04, May 16, 2020, GAW
"""

from . import addSrcToPath

from progArgs import Action, PriceProvider, ProgArgs
import pytest


defltFile = "defltFile.xls"
defltTab = "defltTab"
testFile = "goodFile.xls"
testTab = "goodTab"
defltProvider = PriceProvider.yahoo


@pytest.mark.unit
def test_noArgs_retrieveDefaults():
    # If pass no arguments, retrieve using defaults.
    args = ["spr.py"]
    myArgs = ProgArgs()
    myArgs.parse_args(args, defltFile, defltTab)
    assert myArgs.action == Action.retrieve
    assert myArgs.srcFile == defltFile
    assert myArgs.srcTab == defltTab
    assert myArgs.priceProvider == defltProvider


def test_help():
    args = ["spr.py", "-h"]
    myArgs = ProgArgs()
    myArgs.parse_args(args, defltFile, defltTab)
    assert myArgs.action == Action.help


def test_lookup():
    args = ["spr.py", "-l", "AAPL"]
    myArgs = ProgArgs()
    myArgs.parse_args(args, defltFile, defltTab)
    assert myArgs.action == Action.lookup
    assert myArgs.symbol == "AAPL"


def test_graph():
    args = ["spr.py", "-g", "test.txt"]
    myArgs = ProgArgs()
    myArgs.parse_args(args, defltFile, defltTab)
    assert myArgs.action == Action.graph
    assert myArgs.srcFile == "test.txt"
    assert myArgs.display is True


def test_retrieveWithFile():
    args = ["spr.py", "-f", testFile]
    myArgs = ProgArgs()
    myArgs.parse_args(args, defltFile, defltTab)
    assert myArgs.action == Action.retrieve
    assert myArgs.srcFile == testFile
    assert myArgs.srcTab == defltTab
    assert myArgs.priceProvider == defltProvider


def test_retrieveWithFileArg():
    args = ["spr.py", testFile]
    myArgs = ProgArgs()
    myArgs.parse_args(args, defltFile, defltTab)
    assert myArgs.action == Action.retrieve
    assert myArgs.srcFile == testFile
    assert myArgs.srcTab == defltTab
    assert myArgs.priceProvider == defltProvider


def test_retrieveWithFileAndProvider():
    args = ["spr.py", "-f", testFile, "-p", "yahoo"]
    myArgs = ProgArgs()
    myArgs.parse_args(args, defltFile, defltTab)
    assert myArgs.action == Action.retrieve
    assert myArgs.srcFile == testFile
    assert myArgs.srcTab == defltTab
    assert myArgs.priceProvider == PriceProvider.yahoo


def test_retrieveWithFileAndDefltProvider():
    args = ["spr.py", "-f", testFile, "-p", "alpha"]
    myArgs = ProgArgs()
    myArgs.parse_args(args, defltFile, defltTab)
    assert myArgs.action == Action.retrieve
    assert myArgs.srcFile == testFile
    assert myArgs.srcTab == defltTab
    assert myArgs.priceProvider == PriceProvider.alphavest


def test_retrieveWithProvider():
    args = ["spr.py", "-p", "yahoo"]
    myArgs = ProgArgs()
    myArgs.parse_args(args, defltFile, defltTab)
    assert myArgs.action == Action.retrieve
    assert myArgs.srcFile == defltFile
    assert myArgs.srcTab == defltTab
    assert myArgs.priceProvider == PriceProvider.yahoo


def test_noDisplay():
    args = ["spr.py", "-n"]
    myArgs = ProgArgs()
    myArgs.parse_args(args, defltFile, defltTab)
    assert myArgs.display is False
