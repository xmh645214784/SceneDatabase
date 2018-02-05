import sys
import direct.directbase.DirectStart

from direct.showbase.DirectObject import DirectObject
from direct.showbase.InputStateGlobal import inputState


from direct.showbase.ShowBase import ShowBase, LVecBase3

from panda3d.core import AmbientLight
from panda3d.core import DirectionalLight
from panda3d.core import Vec3
from panda3d.core import Vec4
from panda3d.core import Point3
from panda3d.core import TransformState
from panda3d.core import BitMask32

from panda3d.bullet import *
from panda3d.bullet import BulletWorld
from panda3d.bullet import BulletPlaneShape
from panda3d.bullet import BulletBoxShape
from panda3d.bullet import BulletRigidBodyNode
from panda3d.bullet import BulletDebugNode

from parseObj import obj2TriangleMesh, obj2ConvexHull
from parseXml import parseXml_RetPathAndMatrixPair, parseXml_RetPathAndMatrixPair_Wall


class Game(DirectObject):

  def __init__(self):
    DirectObject.__init__(self)
    base.setBackgroundColor(0.1, 0.1, 0.8, 1)
    base.setFrameRateMeter(True)

    base.cam.setPos(0, -20, 4)
    base.cam.lookAt(0, 0, 0)

    # Light
    alight = AmbientLight('ambientLight')
    alight.setColor(Vec4(0.5, 0.5, 0.5, 1))
    alightNP = render.attachNewNode(alight)

    dlight = DirectionalLight('directionalLight')
    dlight.setDirection(Vec3(1, 1, -1))
    dlight.setColor(Vec4(0.7, 0.7, 0.7, 1))
    dlightNP = render.attachNewNode(dlight)

    render.clearLight()
    render.setLight(alightNP)
    render.setLight(dlightNP)

    # Input
    self.accept('escape', self.doExit)
    self.accept('r', self.doReset)
    self.accept('f1', self.toggleWireframe)
    self.accept('f2', self.toggleTexture)
    self.accept('f3', self.toggleDebug)

    inputState.watchWithModifiers('forward', 'w')
    inputState.watchWithModifiers('left', 'a')
    inputState.watchWithModifiers('reverse', 's')
    inputState.watchWithModifiers('right', 'd')
    inputState.watchWithModifiers('turnLeft', 'q')
    inputState.watchWithModifiers('turnRight', 'e')

    # Task
    taskMgr.add(self.update, 'updateWorld')
    # Array for storing all the object
    self.index=0
    self.allTheThingsNP=[]
    # Physics
    self.setup()

  # _____HANDLER_____

  def doExit(self):
    self.cleanup()
    sys.exit(1)

  def doReset(self):
    self.cleanup()
    self.setup()

  def toggleWireframe(self):
    self.toggleWireframe()

  def toggleTexture(self):
    self.toggleTexture()

  def toggleDebug(self):
    if self.debugNP.isHidden():
      self.debugNP.show()
    else:
      self.debugNP.hide()

  # ____TASK___

  def processInput(self, dt):
    force = Vec3(0, 0, 0)
    torque = Vec3(0, 0, 0)

    if inputState.isSet('forward'): force.setY( 1.0)
    if inputState.isSet('reverse'): force.setY(-1.0)
    if inputState.isSet('left'):    force.setX(-1.0)
    if inputState.isSet('right'):   force.setX( 1.0)
    if inputState.isSet('turnLeft'):  torque.setZ( 1.0)
    if inputState.isSet('turnRight'): torque.setZ(-1.0)

    force *= 30.0
    torque *= 10.0

    force = render.getRelativeVector(self.allTheThingsNP[0], force)
    torque = render.getRelativeVector(self.allTheThingsNP[0], torque)

    self.allTheThingsNP[0].node().setActive(True)
    self.allTheThingsNP[0].node().applyCentralForce(force)
    self.allTheThingsNP[0].node().applyTorque(torque)



  def update(self, task):
    dt = globalClock.getDt()
    #self.processInput(dt)
    self.world.doPhysics(dt, 3, 1.0/180.0)
    return task.cont

  def cleanup(self):
    self.world.removeRigidBody(self.groundNP.node())
    for each in self.allTheThingsNP:
        self.world.removeRigidBody(each.node())
    self.world = None

    self.debugNP = None
    self.groundNP = None
    self.allTheThingsNP=[]

    self.worldNP.removeNode()

  def setup(self):
    self.worldNP = render.attachNewNode('World')

    # World
    self.debugNP = self.worldNP.attachNewNode(BulletDebugNode('Debug'))
    self.debugNP.show()
    self.debugNP.node().showWireframe(True)
    self.debugNP.node().showConstraints(True)
    self.debugNP.node().showBoundingBoxes(False)
    self.debugNP.node().showNormals(True)

    #self.debugNP.showTightBounds()
    #self.debugNP.showBounds()

    self.world = BulletWorld()
    self.world.setGravity(Vec3(0, 0, -9.81))
    self.world.setDebugNode(self.debugNP.node())

    # Ground (static)
    shape = BulletPlaneShape(Vec3(0, 0, 1), 1)
    self.groundNP = self.worldNP.attachNewNode(BulletRigidBodyNode('Ground'))
    self.groundNP.node().addShape(shape)
    self.groundNP.setPos(0, 0, -10)
    self.groundNP.setCollideMask(BitMask32.allOn())

    self.world.attachRigidBody(self.groundNP.node())

    # add all the thing
    temp_for_debug=0
    for each in parseXml_RetPathAndMatrixPair("t.xml"):
        if(temp_for_debug in [0,1]):
            self.addOneThing(each[0],each[1])
        temp_for_debug=temp_for_debug+1;

    # add all walls
    temp_for_debug=0
    for each in parseXml_RetPathAndMatrixPair_Wall("t.xml"):
        if(temp_for_debug in [0,1,2,3,4]):
            self.addOneWall(each)
        temp_for_debug=temp_for_debug+1;

  def addOneThing(self,objPath,matrix):
      # shape = BulletTriangleMeshShape(obj2TriangleMesh(objPath,matrix), dynamic=True)
      shape=obj2ConvexHull(objPath,matrix)
      # shape=obj2ConvexHull(objPath,matrix)
      tempNP = self.worldNP.attachNewNode(BulletRigidBodyNode('thing' + str(self.index)))
      self.index=self.index+1
      tempNP.node().setMass(1.0)
      tempNP.node().addShape(shape)
      tempNP.setPos(0, 0, 0)
      tempNP.node().setInertia(LVecBase3(0,0,-100000))
      tempNP.setCollideMask(BitMask32.allOn())
      self.world.attachRigidBody(tempNP.node())
      self.allTheThingsNP.append(tempNP)

  def addOneWall(self,matrix):
      import numpy as np
      # Calculates the values of two vertices (1,1,1),(-1,-1,-1) after the matrix transformation.
      vec1=np.array([1,1,1,1])
      vec1=np.dot(matrix,vec1)
      vec2=np.array([-1,-1,-1,1])
      vec2=np.dot(matrix,vec2)    
      # The full extents of the box will be twice the half extents, Two vertices (1,1,1),(-1,-1,-1) can determine box pos and vec.
      shape = BulletBoxShape(Vec3((vec1[0]-vec2[0])/2, (vec1[1]-vec2[1])/2, (vec1[2]-vec2[2])/2))
      tempNP = self.worldNP.attachNewNode(BulletRigidBodyNode('wall' + str(self.index)))
      self.index=self.index+1
      # tempNP.node().setMass(1.0)
      tempNP.node().addShape(shape)
      tempNP.setPos((vec1[0]+vec2[0])/2, (vec1[1]+vec2[1])/2, (vec1[2]+vec2[2])/2) 
      # tempNP.node().setInertia(LVecBase3(0,0,-100000))
      tempNP.setCollideMask(BitMask32.allOn())
      self.world.attachRigidBody(tempNP.node())
      self.allTheThingsNP.append(tempNP)  
  
game = Game()
base.run()

