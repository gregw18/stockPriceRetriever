"""
v0.04, May 16, 2020
Parse provided arguments, store in class for use.
"""

import getopt

from sprEnums import Action, PriceProvider


class ProgArgs:
    """
    Class to parse and store arguments provided to program
    """
    def __init__(self):
        self.action = Action.retrieve
        self.srcFile = ""
        self.srcTab = ""
        self.priceProvider = PriceProvider.yahoo
        self.symbol = ""
        self.display = True

    def display_args(self):
        """
        Print out provided arguments.
        """
        print("action=", self.action)
        print("srcFile=", self.srcFile)
        print("srcTab=", self.srcTab)
        print("priceProvider=", self.priceProvider)
        print("symbol=", self.symbol)
        print("display=", self.display)

    def parse_args(self, argv, defltFile, defltTab):
        """
        Pass in all args - function will strip off argument 1, the name of the python program.
        """
        self.srcFile = defltFile
        self.srcTab = defltTab
        self.symbol = ""
        self.display = True

        try:
            opts, args = getopt.getopt(argv[1:], "hnl:g:f:p:", [])
        except getopt.GetoptError:
            self.action = Action.help
            return

        print("opts=", opts)
        print("args=", args)

        # If received one argument, assume that it is the name of the file containing symbols to
        # retrieve prices for. Will be overridden if another option specifying a source file is
        # given.
        for arg in args:
            self.srcFile = arg

        if len(opts) > 0:
            if opts[0][0] == "-h":
                self.action = Action.help
            elif opts[0][0] == "-l":
                self.action = Action.lookup
                self.symbol = opts[0][1]
            else:
                for opt, arg in opts:
                    print("opt=", opt, ", arg=", arg)
                    if opt == "-g":
                        self.action = Action.graph
                        self.srcFile = arg
                    elif opt == "-f":
                        self.action = Action.retrieve
                        self.srcFile = arg
                    elif opt == "-n":
                        self.display = False
                    elif opt == "-p":
                        if arg == "yahoo":
                            self.priceProvider = PriceProvider.yahoo
                        elif arg == "alpha":
                            self.priceProvider = PriceProvider.alphavest
                        else:
                            print("Unrecognized price provider ", arg, ", using AlphaVest.")
                    else:
                        print("Unrecognized option: ", opt, ", ", arg)

        self.display_args()
