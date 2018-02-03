import sys
import numpy as np
from panda3d.bullet import *
from panda3d.core import Point3
def obj2TriangleMesh(filename,matrix):
    print "Obj->Mesh:"+filename
    mesh = BulletTriangleMesh()
    vetexArray=[]
    # dummy
    vetexArray.append(Point3(0,0,0))
    with open(filename,"r") as file:
        for line in file.readlines():
            if line.startswith('v '):
                values=line.split()
                vec=np.array([float(values[1]),float(values[2]),float(values[3]),1])
                vec=np.dot(matrix,vec)
                vetexArray.append(Point3(vec[0],vec[1],vec[2]))
            elif line.startswith('f'):
                values=line.split()
                if(values[1].find("/")!=-1):
                    values=map(lambda x:x[0:x.find("/")] ,values)
                mesh.add_triangle(vetexArray[int(values[1])] , vetexArray[int(values[2])] , vetexArray[int(values[3])])

    return mesh
def obj2ConvexHull(filename,matrix):
    print "Obj->ConvexHull:"+filename
    mesh = BulletConvexHullShape()
    with open(filename,"r") as file:
        for line in file.readlines():
            if line.startswith('v '):
                values=line.split()
                vec=np.array([float(values[1]),float(values[2]),float(values[3]),1])
                vec=np.dot(matrix,vec)
                mesh.add_point(Point3(vec[0],vec[1],vec[2]))
    return mesh
