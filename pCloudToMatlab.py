import json

a = open('pointcloud.dat','r')
b = a.readlines()[0]
c = json.loads(b)

m = open('pcA.dat','w')
n = open('pcB.dat','w')

def str(p):
    q = ''
    for i in p:
        q += i.__str__()+' '
    q += '\n'
    return q

for i in c['A']:
    m.write(str(i))

m.close()

for i in c['B']:
    n.write(str(i))

n.close()
