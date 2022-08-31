import bpy

class CityObject:
    
    def __init__(self,obj):
        self.obj = obj
    
    def addCustomStringProperty(self, customLabel, value):
        if not hasattr(self.obj, customLabel):
            setattr(bpy.types.Object, customLabel, bpy.props.StringProperty(name=customLabel, default="blabla"))
        setattr(self.obj, customLabel, value)

    def addCustomIntegerProperty(self, customLabel, value):
        if not hasattr(self.obj, customLabel):
            setattr(bpy.types.Object, customLabel, bpy.props.IntProperty(name=customLabel, default=2))
        setattr(self.obj, customLabel, value)

    def printAttr(self, name):
        print(getattr(self.obj,name))

    def listAllAttr(self):
        for name, prop in self.obj.rna_type.properties.items():
            print("Name: {}, Value: {}, Type:{}".format(name, prop, type(prop)))
