#!/usr/bin/env python3

"""Main."""

import sys
from cpu import *


if __name__ == "__main__":
    print(sys.argv[0])
    cpu = CPU()

    cpu.load()
    cpu.run()
