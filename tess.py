
import scipy.spatial
import csv

if __name__ == "__main__":

	#Define control points for warp
	srcCloudFi = csv.reader(open('input.csv'))
	srcCloud = []
	for pt in srcCloudFi:
		if len(pt)>0: srcCloud.append(map(float,pt))

	tess = scipy.spatial.Delaunay(srcCloud)

	#Save tesselation to file
	fi = open("tess.csv","wt")
	for tri in tess.vertices:
		fi.write("tri,{0},{1},{2},1.".format(*tri)+"\n")
	for pt in tess.points:
		fi.write("pt,{0},{1},,\n".format(*pt))
	fi.close()

