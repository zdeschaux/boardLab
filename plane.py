# Pragun Maharaj, September 2, 2013
# This file uses the recipie described in the hyperplane fitting section (4) of the  
# document http://www.geometrictools.com/Documentation/LeastSquaresFitting.pdf. 
# To compute a 3D plane for a set of points

import numpy as np
import numpy.linalg as linalg
import numpy.random as random

class Plane(object):
    def __init__(self,A,B,C,D):
        # Here we mean, a plane of the form Ax +By +Cz +D = 0
        self.A = float(A)
        self.B = float(B)
        self.C = float(C)
        self.D = float(D)

    def z(self,x,y):
        z = (-1)*(1/self.C)*((self.A*x)+(self.B*y)+(self.D))
        return z

    def randomPoints(self,numberOfPoints):
        a = []
        for i in range(numberOfPoints):
            x = 10*random.randn()
            y = 10*random.randn()
            z = self.z(x,y)
            a.append([x,y,z])
        return a

    def gridPoints(self,numberOfPoints):
        a = []
        for i in range(numberOfPoints):
            x = i
            y = i
            z = self.z(x,y)
            a.append([x,y,z])

            x = i
            y = 0
            z = self.z(x,y)
            a.append([x,y,z])
            
            x = 0
            y = i
            z = self.z(x,y)
            a.append([x,y,z])
        return a

    def __repr__(self):
        return 'Plane: %fx + %fy + %fz + %f = 0\n'%(self.A,self.B,self.C,self.D)

    @classmethod
    def leastSquaresFit(cls,listOfPoints):
        # I excpect a simple list of points of the form [ [x,y,z],[x,y,z],[x,y,z],...]
        # where x,y,z are vanilla python floats
        
        # The equation of the plane is found out as
        # N.(X-A) = 0
        # where N is the normal vector, and A is a point on the plane
        
        # Finding out A is trivial, its the mean of all the points
        A = [0.0,0.0,0.0]
        sumOfCoordinates = [0.0,0.0,0.0]
        
        # Just add all the points first
        for p in listOfPoints:
            sumOfCoordinates[0] += p[0]
            sumOfCoordinates[1] += p[1]
            sumOfCoordinates[2] += p[2]
        
        # Divide with the number of points to get the mean
        # Here! We have A!, now lets make things a little more explicit
        [a,b,c] = [sumOfCoordinates[j]/len(listOfPoints) for j in [0,1,2]] 

        # Now, lets calculate N
        # Butt, first we need to calculate M(A), the mother matrix of N.
        # Of which, N is going to be the eigenvector, corresponding to the smalles eigenvalue. How cute!

        MA = np.zeros([3,3])
        # Now we start filling up MA
        for p in listOfPoints:
            x = p[0]
            y = p[1]
            z = p[2]
            MA[0,0] += (x-a)*(x-a)
            MA[0,1] += (x-a)*(y-b)
            MA[0,2] += (x-a)*(z-c)
            MA[1,1] += (y-b)*(y-b)
            MA[1,2] += (y-b)*(z-c)
            MA[2,2] += (z-c)*(z-c)

        #Now after all, all well behaved mother matrices are symmetric
        MA[1,0] = MA[0,1]
        MA[2,0] = MA[0,2]
        MA[2,1] = MA[1,2]
        #Mother matrix ready!!!

        #Calculate the eigenvalues and eigenvectors of the mother matrix
        eigvalues, eigenvectors = linalg.eig(MA)
        minEigValueIndex = np.argmin(eigvalues)
        #This right here is the normal vector for the plane!
        minEigVector = eigenvectors[:,minEigValueIndex]
        
        #Now, we calculate the simple form of the plane
        A = minEigVector[0]
        B = minEigVector[1]
        C = minEigVector[2]

        #We reshpae the minEigVector so that numpy knows that it is actually a vertical vector
        minEigVector.shape = (3,1)
        aVector = np.array([[a,b,c]])
        D = (-1)*( np.dot(aVector,minEigVector)[0,0] )

        #And now, we dish out the newly found plane!!
        return Plane(A,B,C,D)

