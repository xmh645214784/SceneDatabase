import xml.dom.minidom
import numpy as np
def parseXml_RetPathAndMatrixPair(xmlPath):
    domtree=xml.dom.minidom.parse(xmlPath)
    collection=domtree.documentElement
    shapes = collection.getElementsByTagName("shape")
    result=[]
    for each in shapes:
        if each.hasAttribute("type") and each.getAttribute("type")=="shapenet":
             path=each.getElementsByTagName("string")[0].getAttribute("value")
             matrix=each.getElementsByTagName("transform")[0].getElementsByTagName("matrix")[0].getAttribute("value")
             matrix=np.array(map(float,matrix.split())).reshape([4,4])
             result.append([path,matrix])
    return result