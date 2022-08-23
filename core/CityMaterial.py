import bpy

class CityMaterial:

    material_colors = {
        "WallSurface": (0.8, 0.8, 0.8, 1),
        "RoofSurface": (0.9, 0.057, 0.086, 1),
        "GroundSurface": (0.507, 0.233, 0.036, 1)
    }

    def __init__(self,name):
        self.material = self.createMaterial(name)
        self.name = self.material.name #hier benötigen wir den richtigen Namen, also inklusive *.ooX

    def createMaterial(self, name):
        return bpy.data.materials.new(name=name)
    
    def addCustomPropertie(self, customLabel, value):
        obj = self.material
        if customLabel not in obj:
            obj[customLabel] = value

        # get or create the UI object for the property
        ui = obj.id_properties_ui(customLabel)
        ui.update(description = "scripted Property, do not change")
        ui.update(default = value)

    def setColor(self, diffuseColor):
        self.material.diffuse_color = (diffuseColor)
        
    def addMaterialToObj(self, obj):
        obj.data.materials.append(self.material)

    def addMaterialToFace(self, obj):
        obj.active_material_index = self.getIndex(obj)
        bpy.ops.object.material_slot_assign()
        

    def setTexture():
        pass

    def getIndex(self, obj):
        return obj.material_slots.find(self.name)
            
