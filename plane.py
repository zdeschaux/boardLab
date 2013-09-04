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
        z = (-1)*(1/self.C)*((self.A*x)+(self.B*y) + (self.D))
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
            x = float(i)
            y = float(i)
            z = self.z(x,y)
            a.append([x,y,z])

            x = float(i)
            y = 0
            z = self.z(x,y)
            a.append([x,y,z])
            
            x = 0
            y = float(i)
            z = self.z(x,y)
            a.append([x,y,z])
        return a

    def normVector(self):
        if self.lsNormalVector:
            return self.lsNormalVector
        return [self.A,self.B,self.C]
    
    def planePoint(self):
        if self.lsPoint:
            return self.lsPoint
        #here, do some intelligent stuff to return a sensible value of a point, right now do nothing

    def parameterize(self):
        p0 = np.array([self.planePoint()])

        # Here's how we'll parametereize, we'll take three vectors [1,0,0],[0,1,0],[0,0,1], we'll add all three to p0. 
        # Take orthographic projections of all three resulting points on the plane. And choose the point with the longest pi-p0 vector
        vs = [np.array([[0.0,0.0,1.0]]), np.array([[0.0,1.0,0.0]]), np.array([[1.0,0.0,0.0]])]
        ps = [p0 + v for v in vs]
    
        projectedPs = [self.projectPoint(p) for p in ps]
        projectedVs = [p - p0 for p in projectedPs]
        normVs = np.array([linalg.norm(v) for v in projectedVs])
        longestProjectionVectorIndex = normVs.argmax()

        # Here! We have the first basis vector in the plane
        vect1 = projectedVs[longestProjectionVectorIndex]
        # Just for one measure of goodness, lets normalize the vector
        vect1 = vect1/linalg.norm(vect1)
        vect2 = np.cross(vect1,self.normVector())
        vect2 = vect2/linalg.norm(vect2)

        self.origin = p0
        self.basisVector1 = np.array(vect1)
        self.basisVector2 = np.array(vect2)
        tmpNormVector = np.array(self.normVector())

        self.basisVector1.shape = (3,1)
        self.basisVector2.shape = (3,1)
        tmpNormVector.shape  = (3,1)
        tmpNormVector = tmpNormVector/linalg.norm(tmpNormVector)

        # This matrix, say A, when multiplied with say x.
        # Ax = y. Then y is the XYZ representation of the point x specified in the plane co-ordinate system
        self.planeRepresentationToSensor = np.hstack([self.basisVector1,self.basisVector2,tmpNormVector])
        self.sensorRepresentationToPlane = linalg.inv(self.planeRepresentationToSensor)
        

    def planeRepresentationForSensorPoint(self,p):
        # For points inside the plane it gives the plane representation for the point
        # For points outside the plane it gives the plane representation for the projection of the point on the plane
        p = np.array(p)
        pDash = p - self.origin
        pDash.shape = (3,1)
        q = np.dot(self.sensorRepresentationToPlane,pDash)
        q.shape = (3,)
        return [q[0],q[1]]

    def sensorRepresentationForPlanePoint(self,p):
        p = np.array([p[0],p[1],0.0])
        p.shape = (3,1)
        q = np.dot(self.planeRepresentationToSensor,p)
        q.shape = (3,)
        qDash = q + self.origin
        qDash.shape = (3,)
        return [qDash[0],qDash[1],qDash[2]]

    def projectPoint(self,p):
        if type(p) == list:
            p = np.array([p])
        origin = np.array([self.planePoint()])
        Vp_origin = p - origin
        nVect = np.array(self.normVector())

        Vp_origin.shape = (3,1)
        nVect.shape = (1,3)
        dist = np.dot(nVect,Vp_origin)[0,0]

        projectedPoint = p - dist*nVect
        projectedPoint.shape = (3,)

        print 'checking projection'
        print projectedPoint[2],self.z(projectedPoint[0],projectedPoint[1]), p[0,2], self.z(p[0,0],p[0,1])

        return [projectedPoint[0],projectedPoint[1],projectedPoint[2]]


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
        # Of which, N is going to be the eigenvector, corresponding to the smallest eigenvalue. How cute!

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
        minEigVector = minEigVector/linalg.norm(minEigVector)
        #Now, we calculate the simple form of the plane
        A = minEigVector[0]
        B = minEigVector[1]
        C = minEigVector[2]

        #We reshpae the minEigVector so that numpy knows that it is actually a vertical vector
        minEigVector.shape = (3,1)
        aVector = np.array([[a,b,c]])
        dotP = np.dot(aVector,minEigVector)
#        print dotP
        D = (-1)*( dotP[0,0] )

        #And now, we dish out the newly found plane!!
        fitPlane = Plane(A,B,C,D)
        fitPlane.lsPoint = [a,b,c]
        fitPlane.lsNormalVector = [A,B,C]

        return fitPlane

    @classmethod
    def findRotationTranslationScaleForPointClouds(self,pcloudA,pcloudB):
        # Returns the rotation matrix and scaling to be applied TO a point in the reference frame of B, to find its representation in A
        # In other words, the inv(RotationMatrix) and inv(Scale) were applied to points in A to get points of B
        # Find the centroid for both parties of the pointCloud
        centroidA = np.array([0.0,0.0])
        centroidB = np.array([0.0,0.0])
        pointCloudSize = len(pcloudA)
        for i in range(pointCloudSize):
            pointA = pcloudA[i]
            pointB = pcloudB[i]
            a = np.array(pointA)/pointCloudSize # This is the location of the via on the PCB
            b = np.array(pointB)/pointCloudSize # This is the location of the via from the sensor
            centroidA += a
            centroidB += b

        #print 'Centroid A',centroidA
        #print 'Centroid B',centroidB

        # Move both pointClouds to their centroids respectively
        # Also build the X,Y matrices to multiple and get the covariance matrix at the same time

        Avectors = np.zeros((2,pointCloudSize))
        Bvectors = np.zeros((2,pointCloudSize))

        translatedPCloudA = []
        translatedPCloudB = []
        for i in range(pointCloudSize):
            pointA = pcloudA[i]
            pointB = pcloudB[i]
            newA = pointA - centroidA
            newB = pointB - centroidB
            translatedPCloudA.append(newA)
            translatedPCloudB.append(newB)

        # timeToCalculate the scaling
        normA = []
        normB = []
        scaleAB = []
        for i in range(pointCloudSize):
            a = linalg.norm(translatedPCloudA[i])
            b = linalg.norm(translatedPCloudB[i])
            normA.append(a)
            normB.append(b)
            scaleAB.append(a/b)
        
        scaleAB = np.mean(scaleAB)
        
        #scale the B vectors to make them equilength with A vectors
        # Build the covariance matrix

        for i in range(pointCloudSize):
            pointA = translatedPCloudA[i]
            pointB = translatedPCloudB[i]
            Avectors[:,i] = pointA
            Bvectors[:,i] = pointB*scaleAB
            
        #S = np.dot(Avectors,np.transpose(Bvectors))
        S = np.dot(Bvectors,np.transpose(Avectors))
        U,s,V = linalg.svd(S)
        R = np.dot(V,np.transpose(U))

        print 'Scale AB',scaleAB
        print 'Centroid A',centroidA
        print 'Centroid B',centroidB
        print 'Rotation Matrix',R

        return R, centroidA, centroidB, scaleAB

