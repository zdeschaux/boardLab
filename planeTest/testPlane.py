# Pragun Maharaj, September 2, 2013
# This guy just test the plane.py file

from plane import Plane
import numpy.random as random

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

