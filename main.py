#!/usr/bin/env python3

import sys

from AnimateCompression import *

def main():
	filepath = sys.argv[1]
	makeQuadtreeAnimation(filepath, border = False, reverse=True)


if __name__ == "__main__":
	main()