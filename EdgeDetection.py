def kernelPass(image, kernel):
	return image.filter(ImageFilter.Kernel((3, 3),
		kernel, 1, 0))


def filterEdges(pixel):
	return 255*(pixel > 120)


def findEdges(filepath, brighteningFactor, threshold = 120):
	im = Image.open(filepath).copy()

	im = kernelPass(im, default_kernels["gausBlur"])
	im = kernelPass(im, default_kernels["edges"][2])

	im = im.filter(ImageFilter.MedianFilter())

	im = im.crop((1, 1, im.size[0]-2, im.size[1]-2))

	im = ImageEnhance.Brightness(im).enhance(brighteningFactor)

	edgesImage = im.convert(mode="L")

	edgesImage = edgesImage.point(filterEdges)

	pixels = edgesImage.load()
	
	points = []

	for i in range(im.size[0]):
		for j in range(im.size[1]):
			if pixels[i, j] > threshold:
				points.append((i, j))

	edgesImage.show()

	return im.size, points