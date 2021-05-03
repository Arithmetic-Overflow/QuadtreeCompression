def pathEdges(qtree, startingPoint, numPoints):
	p0 = startingPoint

	for i in range(numPoints-1):
		minDist = inf
		closestPoint = None

		for p in qtree.nearbyPoints(x, y):
			newDist = distance.euclidean(p0, p)

			if newDist < minDist:
				minDist = newDist
				closestPoint = p

		p0 = closestPoint