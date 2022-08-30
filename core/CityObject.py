import bpy

class CityObject:
    
    def __init__(self,obj):
        self.obj = obj
    
    def addCustomPropertie(self, customLabel, value):

        #bpy.types.Object.foo = bpy.props.IntProperty(default=4)
        obj = self.obj
        #if customLabel not in obj:
        obj[customLabel] = value

        bpy.types.Object.footer = bpy.props.IntProperty(default=4)
        obj = self.obj
        #if customLabel not in obj:
        obj[customLabel] = value
        #print(obj[customLabel])

        # get or create the UI object for the property
        ui = obj.id_properties_ui(customLabel)
        ui.update(description = "scripted Property, do not change")
        ui.update(default = value)
    
    def printAttr(self, name):
        print(getattr(self.obj,name))
        print(getattr(self.obj,name))

    def listAllAttr(self):
        for name, prop in self.obj.rna_type.properties.items():
            print("Name: {}, Value: {}, Type:{}".format(name, prop, type(prop)))

