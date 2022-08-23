import bpy

class CityMaterial:

    material_colors = {
        "WallSurface": (0.8, 0.8, 0.8, 1),
        "RoofSurface": (0.9, 0.057, 0.086, 1),
        "GroundSurface": (0.507, 0.233, 0.036, 1)
    }

    def __init__(self,name):
        self.material = self.createMaterial(name)

    def createMaterial(self, name):
        return bpy.data.materials.new(name=name)
    
    def addCustomPropertie(customLabel, value, materialId):
        pass

    def setColor(self, diffuseColor):
        self.material.diffuse_color = (diffuseColor)
        
    def addMaterialToObj(self, obj):
        obj.data.materials.append(self.material)

    def addMaterialToFace(self, face):
        pass

    def addTexture():
        pass

    def getIndex(self):
        print ("index:" + str(self.material.pass_index))
