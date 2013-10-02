import matplotlib.pyplot as plt

def plotPng(filename,values,testData=None):
    fig = plt.figure(figsize=(4,2), dpi=100)
    axes = fig.add_axes([0.1, 0.1, 0.8, 0.8])

    xValues = range(len(values))
    if testData is not None:
        axes.plot(testData['time'],testData['voltage'],'r')
        xValues = testData['time'][:len(values)]
    axes.plot(xValues,values,'b-*')

    fig.savefig('s.png')

