import matplotlib.pyplot as plt

def plotPng(filename):
    fig = plt.figure(figsize=(4,2), dpi=100)
    axes = fig.add_axes([0.1, 0.1, 0.8, 0.8])
    axes.plot([1,2,3,4])
    fig.savefig('s.png')

