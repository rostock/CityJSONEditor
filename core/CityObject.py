import bpy


class CityObject:
    
    def __init__(self,obj):
        self.obj = obj
    
    def addCustomProperty(self, customLabel):
        setattr(bpy.types.Object, customLabel, getattr(CityObjectProps,customLabel))
        
    def setCustomProperty(self, customLabel, value):
        setattr(self.obj, customLabel, value)

    def printAttr(self, name):
        print(getattr(self.obj,name))

    def listAllAttr(self):
        for name, prop in self.obj.rna_type.properties.items():
            print("Name: {}, Value: {}, Type:{}".format(name, prop, type(prop)))

class CityObjectProps(bpy.types.PropertyGroup):
    CJEOconstruction: bpy.props.StringProperty(name = 'CJEOconstruction',default= 'Building')
    CJEOtype: bpy.props.StringProperty(name = 'CJEOtype', default= 'CompositeSurface')
    CJEOlod: bpy.props.IntProperty(name="CJEOlod", default=2, min=1, max=5, description="LevelOfDetail")
    CJEOsublod: bpy.props.IntProperty(name="CJEOsublod", default=0, min=0, max=9, description="Subversion of LOD")            
