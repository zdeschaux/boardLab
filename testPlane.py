# Pragun Maharaj, September 2, 2013
# This guy just test the plane.py file

import sys, json
from plane import Plane
import numpy.random as random
import numpy as np

def str(a):
    return ' '.join([b.__str__() for b in a])

#First we just create a simple plane 
inputPlane = Plane(1.0,1.0,1.0,1.0)
print 'Input : %s'%(inputPlane,)

print 'Grid points on the plane'
samplePoints = inputPlane.gridPoints(20)
for i in samplePoints:
    print str(i)


print '\nAdding some noise to the points'
noisySamples = []
for p in samplePoints:
    a = [(0.5*random.randn())+j for j in p]
    noisySamples.append(a)

print '\nHere are some noisy sample points.'
for p in noisySamples:
    print str(p)

outputPlane = Plane.leastSquaresFit(noisySamples)
print '\n%s'%(outputPlane,)


print '\nGrid points on the plane'
samplePoints = outputPlane.gridPoints(20)
for i in samplePoints:
    print str(i)

print '\nParameterizing...'
outputPlane.parameterize()
print outputPlane
print outputPlane.planePoint()

print '\nChecking parameterization'
planePoints = []

print '\nParameterizing sample points'
for i in samplePoints:
    q = outputPlane.planeRepresentationForSensorPoint(i)
    planePoints.append(q)
    #print str(q)


if True:
    print '\nDe-parameterizng sample points'
    for i in range(len(planePoints)):
        q = outputPlane.sensorRepresentationForPlanePoint(planePoints[i])
        if True:
            print ''
            print str(samplePoints[i])
            print str(planePoints[i])
        print str(q)



print '\nChecking rotation, translation, scaling estimation'
p = [[1.0,1.0], [10.0,10.0], [10.0,1.0]]
pT = [1.0,10.0]
scale = 1.5

rotationAngle = 60.0
rotAng = (rotationAngle/180)*np.pi
rotmat = np.array([ [np.cos(rotAng),-np.sin(rotAng)],[np.sin(rotAng),np.cos(rotAng)]])
print rotmat

print '\n Rotating points'
rp = [np.dot(rotmat,i) for i in p]
rpT = np.dot(rotmat,pT)*scale

#adding noise to these points
pcloudA = []
pcloudB = []
numPoints = 5

for i in range(numPoints):
    for j in range(len(p)):
        pcloudA.append(np.array(p[j]))
        d = rp[j] + np.array([0.1*random.randn(),0.3*random.randn()])
        d *= scale
        pcloudB.append(d)
    

Plane.findRotationTranslationScaleForPointClouds(pcloudA,pcloudB)

#This uses the pointcloud data in the file
print 'Now running pointCLoud alignment on real data...'
f = open('pointcloud.dat')
g = f.readlines()[0]
h = json.loads(g)
A = h['A']
B = h['B']

for i in B:
    i[1] = -i[1]

Plane.findRotationTranslationScaleForPointClouds(A,B)

