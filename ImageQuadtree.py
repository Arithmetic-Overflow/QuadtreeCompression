from PIL import Image, ImageStat
import os, glob

import ffmpeg

class ImageQuadtree:
	DEVIATIONTHRESHOLD = 2
	MAXDEPTH = 12

	def setConstants(DEVIATIONTHRESHOLD, MAXDEPTH):
		"""
		Don't set DEVIATIONTHRESHOLD to less than 1 or MAXDEPTH to more than 26
		"""
		ImageQuadtree.DEVIATIONTHRESHOLD = max(devthreshold, 1)
		ImageQuadtree.MAXDEPTH = min(int(maxdepth), 26)

	def __init__(self, im, rect = None, parent = None, depth = 1):
		self.im = im
		self.w, self.h = self.im.size

		if rect is None:
			self.rect = (0, 0, self.w, self.h)

		else:
			self.rect = rect

		self.depth = depth

		self.avColour, self.error = self.calculateAverageAndError()

		self.parent = parent
		
		self.nw = None
		self.ne = None
		self.sw = None
		self.se = None

	def calculateAverageAndError(self):
		imStat = ImageStat.Stat(self.im)

		av = [int(i) for i in imStat.rms]
		er = 0.3*imStat.stddev[0] + 0.6*imStat.stddev[1] + 0.1*imStat.stddev[2]

		return imStat.rms, er


	def decomposeImage(self):
		if self.error > ImageQuadtree.DEVIATIONTHRESHOLD and self.depth < ImageQuadtree.MAXDEPTH:
			self.createChildren()
			return


	def createChildren(self):
		childw = self.w//2
		childh = self.h//2

		cropCoordinates = {
			"nw" : (0, 0, childw, childh),
			"ne" : (childw, 0, self.w, childh),
			"sw" : (0, childh, childw, self.h),
			"se" : (childw, childh, self.w, self.h)
		}

		x, y = self.rect[:2]

		childRect = {
			"nw" : (x, y, childw, childh),
			"ne" : (x + childw, y, self.w - childw, childh), 
			"sw" : (x, y + childh, childw, self.h - childh),
			"se" : (x + childw, y + childh, self.w - childw, self.h - childh)
		}

		if self.w < 4 or self.h < 4:
			return

		if True:
			self.nw = ImageQuadtree(self.im.crop(cropCoordinates["nw"]), childRect["nw"], self, self.depth + 1)
			self.ne = ImageQuadtree(self.im.crop(cropCoordinates["ne"]), childRect["ne"], self, self.depth + 1)
			self.sw = ImageQuadtree(self.im.crop(cropCoordinates["sw"]), childRect["sw"], self, self.depth + 1)
			self.se = ImageQuadtree(self.im.crop(cropCoordinates["se"]), childRect["se"], self, self.depth + 1)

			self.nw.decomposeImage()
			self.ne.decomposeImage()
			self.sw.decomposeImage()
			self.se.decomposeImage()

	def drawAtDepth(self, depthToDraw, currentDepth = 1):
		if self.nw is None or currentDepth == depthToDraw:
			return self.nw is not None
		
		return True in [
			self.nw.drawAtDepth(depthToDraw, currentDepth+1),
			self.ne.drawAtDepth(depthToDraw, currentDepth+1),
			self.sw.drawAtDepth(depthToDraw, currentDepth+1),
			self.se.drawAtDepth(depthToDraw, currentDepth+1)
		]


	def reconstructImage(self, border = False, reverse = False, animation=True, framerate=6):
		imList = []

		depth = 1
		while(self.drawAtDepth(depth)):
			imList.append(self.createImage(depth, border))

			depth += 1

		imList.append(self.createImage(depth, border))

		originalImage = Image.new("RGB", self.im.size, (255, 255, 255))
		originalImage.paste(self.im)

		print(originalImage)

		imList.append(originalImage)

		if not reverse:
			imList.reverse()

		# replace all previous images with the existing ones
		[os.remove(f) for f in glob.glob('./tmp/framedump/*.jpg')]
		[im.save('./tmp/framedump/{}.jpg'.format((chr(ord('A') + i)))) for i, im in enumerate(imList)]

		if animation:
			imSize = [(i - i%2) for i in self.im.size]
			print(f'output mov dimensions: {tuple(imSize)}')

			# turns images into jpg
			(
				ffmpeg
				.input('./tmp/framedump/*.jpg', pattern_type='glob', framerate=framerate)
				.filter('scale', *imSize)
				.output('./Output/output.mov')
				.run()
			)

		# imList[0].save('./Output/output.mp4', format="mp4", save_all=True, optimize=False, append_images=imList[1:]+[imList[-1] for i in range(2)], duration=300, loop=0)

		# close all images
		[i.close() for i in imList]


	def fillPixels(self, image, targetDepth, currentDepth=1, border=False):
		if self.nw is not None and currentDepth < targetDepth:
			self.nw.fillPixels(image, targetDepth, currentDepth+1, border)
			self.ne.fillPixels(image, targetDepth, currentDepth+1, border)
			self.sw.fillPixels(image, targetDepth, currentDepth+1, border)
			self.se.fillPixels(image, targetDepth, currentDepth+1, border)

			return

		col = tuple([int(i) for i in self.avColour])

		boxSize = [i for i in self.im.size]
		topLeft = self.rect[:2]

		if border:
			boxSize = [i-1 for i in boxSize]
			topLeft = [i+1 for i in topLeft]

			borderBox = Image.new("RGB", self.im.size, color = (0,0,0))

			image.paste(borderBox, box=self.rect[:2])
		
		colourBox = Image.new("RGB", boxSize, color = col)
		image.paste(colourBox, box=topLeft)


	def createImage(self, depth, border = False):
		compressedIm = Image.new("RGB", self.im.size)
		self.fillPixels(compressedIm, depth, border = border)

		return compressedIm