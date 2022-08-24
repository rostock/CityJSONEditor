import bpy

class CityObject:
    
    def __init__(self,obj):
        self.obj = obj
    
    def addCustomPropertie(self, customLabel, value):
        obj = self.obj
        #if customLabel not in obj:
        obj[customLabel] = value

        # get or create the UI object for the property
        ui = obj.id_properties_ui(customLabel)
        ui.update(description = "scripted Property, do not change")
        ui.update(default = value)
    
    def printAttr(self, name):
        print(getattr(self.obj,name))