import  xml.etree.ElementTree as ET

class EagleBrdFile(object):
    def __init__(self,fileName):
        self.tree = ET.parse(fileName)
        self.root = self.tree.getroot()
        self.packages = []
        self.loadPackages()

    def getElementsWithTagName(self,tagName):
        returnArray = []
        for child in self.root.iter(tagName):
            returnArray.append(child)
        return returnArray

    def loadPackages(self):
        a = self.getElementsWithTagName('package')
        self.packages = a
        for i in self.packages:
            print i, i.tag, i.attrib
            layerItems = loadLayer(i,'21')
            for j in layerItems:
                print j.tag, j.attrib


def loadLayer(item,layer):
    returnArray = []
    for j in item:
        if 'layer' in j.attrib and j.attrib['layer'] == layer:
            returnArray.append(j)
    return returnArray

a = EagleBrdFile('uno.brd')
