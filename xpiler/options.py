# Copyright (c) 2017, 2018 Jae-jun Kang
# See the file LICENSE for details.

from __future__ import print_function

import getopt
import sys

DEFAULT_SPEC = "py"

class Options(object):
    def __init__(self):
        self.forced = False
        self.out_dir = None
        self.recursive = False
        self.spec = DEFAULT_SPEC

    def parse(self, argv):
        longopts = ["spec=", "out-dir=", "recursive", "force", "help"]
        try:
            opts, args = getopt.getopt(argv, "s:o:rfh", longopts)
        except  getopt.GetoptError as err:
            print(err, file=sys.stderr)
            Options._usage()
            sys.exit(2)

        for opt, optarg in opts:
            if opt in ("-s", "--spec"):
                self.spec = optarg.lower()
                from main import Main
                if spec not in Main.formatters:
                    print("error: unknown target formatter specified - " + spec,
                        file=sys.stderr)
                    sys.exit(2)
            elif opt in ("-o", "--out-dir"):
                self.out_dir = optarg
            elif opt in ("-r", "--recursive"):
                self.recursive = True
            elif opt in ("-f", "--force"):
                self.forced = True
            elif opt in ("-h", "--help"):
                Options._usage()
                sys.exit(2)

        return args

    @staticmethod
    def _usage():
        print("usage: xpiler (options) [path...]")
        print(" options:")
        print("  -f (--force)       : force all to be re-xpiled")
        print("  -h (--help)        : print this message and quit")
        print("  -o (--out-dir) dir : specifies the output root directory")
        print("  -r (--recursive)   : process subdirectories recursively")
        print("  -s (--spec) spec   : specifies the target formatter")

        from main import Main
        for key, value in Main.formatters.items():
            suffix = " (default)" if key == DEFAULT_SPEC else ""
            line = "{:>20} : {}{}".format(key, value.desc(), suffix)
            print(line)
