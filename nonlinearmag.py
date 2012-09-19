import skimage.transform
import scipy.spatial, scipy.optimize
from PIL import Image
from skimage import data
import numpy as np
import csv

def RescaleEdge(edges, pta, ptb, dists, scale):
	for i in range(len(edges)):
		if pta == edges[i][0] and ptb == edges[i][1]:
			dists[i] *= scale
		if pta == edges[i][1] and ptb == edges[i][0]:
			dists[i] *= scale

def EvalFunc(pos, dists, edges, centTarget):
	pos = np.array(pos)
	x = pos[::2]
	y = pos[1::2]
	pts = zip(x,y)
	err = []

	#Edge errors
	for edge, targetDist in zip(edges, dists):
		dist = np.linalg.norm(np.array(pts[edge[0]]-np.array(pts[edge[1]])))	
		err.append(abs(dist - targetDist))

	#Dist from centeroid
	cent = np.array([x.mean(), y.mean()])
	dist = np.linalg.norm(cent - centTarget)
	err.append(dist)

	tot = np.abs(err).sum()
	print "Fit cost:",tot
	return err

if __name__ == "__main__":
	#Load source image
	srcIm = data.lena()

	#Define control points for warp
	srcCloudFi = csv.reader(open('tess.csv'))
	vertices = []
	srcCloud = []
	scalings = []
	for li in srcCloudFi:
		if len(li)==0: continue
		if li[0] == "tri":
			vertices.append(map(int, li[1:4]))
			scalings.append(float(li[4]))
		if li[0] == "pt":
			srcCloud.append(map(float, li[1:3]))

	#List edges
	edges = []
	for tri in vertices:
		if (tri[0],tri[1]) not in edges and (tri[1],tri[0]) not in edges:
			edges.append((tri[0],tri[1]))
		if (tri[1],tri[2]) not in edges and (tri[2],tri[1]) not in edges:
			edges.append((tri[1],tri[2]))
		if (tri[2],tri[0]) not in edges and (tri[0],tri[2]) not in edges:
			edges.append((tri[2],tri[0]))

	#Calculate lengths
	dists = []
	for edge in edges:
		dist = np.linalg.norm(np.array(srcCloud[edge[0]]-np.array(srcCloud[edge[1]])))
		dists.append(dist)

	#Rescale edges based on weights
	for tri, scaling in zip(vertices, scalings):
		
		RescaleEdge(edges, tri[0], tri[1], dists, scaling)
		RescaleEdge(edges, tri[1], tri[2], dists, scaling)
		RescaleEdge(edges, tri[2], tri[0], dists, scaling)

	#Find centroid
	cent = (np.array([pt[0] for pt in srcCloud]).mean(), np.array([pt[1] for pt in srcCloud]).mean())

	#Find new positions
	posVar = []
	for pt in srcCloud:
		posVar.extend(pt)
	sol = scipy.optimize.leastsq(EvalFunc, posVar, (dists, edges, cent))

	movedPtsX = np.array(sol)[0][::2]
	movedPtsY = np.array(sol)[0][1::2]
	dstCloud = zip(movedPtsX, movedPtsY)

	#Perform transform
	piecewiseAffine = skimage.transform.PiecewiseAffineTransform()
	piecewiseAffine.estimate(np.array(dstCloud), np.array(srcCloud))
	dstArr = skimage.transform.warp(srcIm, piecewiseAffine)
	
	#Visualise result
	dstArr = np.array(dstArr * 255., dtype=np.uint8)
	print dstArr.min(), dstArr.max()
	if dstArr.shape[2] == 1:
		dstArr = dstArr.reshape((dstArr.shape[0],dstArr.shape[1]))
	dstIm = Image.fromarray(dstArr)
	dstIm.show()

