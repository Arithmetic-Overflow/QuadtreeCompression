#!/usr/bin/env python3

from PIL import Image, ImageFilter, ImageEnhance
from random import shuffle, random
import sys

from ImageQuadtree import ImageQuadtree

def compressToQuadtree(filepath, border = False, reverse = False):
	im = Image.open(filepath).copy()
	print("image size:", im.size)

	qtree = ImageQuadtree(im)
	qtree.decomposeImage()

	return qtree


def makeQuadtreeAnimation(filepath, border = False, reverse = False):
	qtree = compressToQuadtree(filepath, border=border, reverse=reverse)

	print("image size:", qtree.im.size)
	print("done decomposing image")

	qtree.reconstructImage(border, reverse)

	print("done reconstructing image")


def main():
	filepath = sys.argv[1]
	makeQuadtreeAnimation(filepath, border = False, reverse=True)


if __name__ == "__main__":
	main()