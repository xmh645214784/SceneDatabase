import direct.directbase.DirectStart
from panda3d.core import *
from direct.showbase.DirectObject import DirectObject
from direct.task import Task
from direct.actor.Actor import Actor
#for Pandai
from panda3d.ai import *
 
# Globals
speed = 6.75
 
class World(DirectObject):
 
    def __init__(self):
        base.disableMouse()
        base.cam.setPosHpr(0,0,55,0,-90,0)
 
        self.loadModels()
        self.setAI()
 
    def loadModels(self):
        # Seeker
        ralphStartPos = Vec3(0, 0, 0)
        self.wanderer = Actor("models/panda",
                                 {"run":"../../../../Panda3D-1.9.4-x64/models/panda-walk.egg.pz"})                                
        self.wanderer.reparentTo(render)
        self.wanderer.setScale(0.5)
        self.wanderer.setPos(ralphStartPos)
 
    def setAI(self):
        #Creating AI World
        self.AIworld = AIWorld(render)
 
        self.AIchar = AICharacter("wanderer",self.wanderer, 100, 0.05, 5)
        self.AIworld.addAiChar(self.AIchar)
        self.AIbehaviors = self.AIchar.getAiBehaviors()
 
        self.AIbehaviors.wander(5, 3, 10, 1.0)
        self.wanderer.loop("run")
 
        #AI World update        
        taskMgr.add(self.AIUpdate,"AIUpdate")
 
    #to update the AIWorld    
    def AIUpdate(self,task):
        self.AIworld.update()            
        return Task.cont
 
w = World()
run()