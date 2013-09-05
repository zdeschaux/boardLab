# This file will load hemishpere.raw and process it using the radius and output testQuat.raw, plot it in matlab to see if it makes sense.

from polhemus import Quaternion, Fastrak
import numpy as np

b = open('quatOut.raw','w')

tip = np.array(( (-45.5676,),(-0.15494,),(-13.736,), ))

#a = Fastrak(logFile='hemishpere.raw',serialPort=None,fixedPoints=[tip])
a = Fastrak(logFile='rawlog.raw',serialPort='/dev/ttyUSB0',fixedPoints=[tip])
a.setup(reset=False)
a.setContinuous()

while True:
    p = a.readData()
    # This guy prints the sensor xyz and quaternion
    #to = ' '.join(j.__str__() for j in p[0])+' '+' '.join(j.__str__() for j in p[1])+'\n'

    # This guy prints the quaterion calculated position of the tip
    to = ' '.join(j.__str__() for j in p[2])+'\n'

    print to
    #b.write(to)
