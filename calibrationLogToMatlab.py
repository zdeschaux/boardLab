import json

def str(p):
    q = ''
    for i in p:
        q += i.__str__()+' '
    q += '\n'
    return q

m = open('xyzTipPoints.dat','w')

a = open('calibration.log','r')
b = a.readlines()[0]
c = json.loads(b)

for i in c:
    if len(i['data']) > 0:
        for j in i['data']:
            m.write(str([i['x'],i['y'],0.0]+j[2]))

