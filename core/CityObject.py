from multiprocessing import context
import bpy


class CityObject:
    
    def __init__(self,obj):
        self.blenderObj = obj
    
    def addCustomProperty(self, customLabel):
        setattr(bpy.types.Object, customLabel, getattr(CityObjectProps,customLabel)) # diese Funktion entspricht der generischen Umsetzung von bpy.types.Object.CJEOconsturction = bpy.props.StringProperty(name = 'CJEOconstruction', default= 'Building')
        
    def setCustomProperty(self, customLabel, value):
        if not value == None:
            setattr(self.blenderObj, customLabel, value)
            #bpy.data.screens['Layout'].areas
                
        else:
            #setattr(self.obj, customLabel, value)
            pass
            

    def printAttr(self, name):
        print(dir(self.blenderObj))
        #print(getattr(self.blenderObj,name))

    def listAllAttr(self):
        for name, prop in self.blenderObj.rna_type.properties.items():
            print("Name: {}, Value: {}, Type:{}".format(name, prop, type(prop)))

    def checkAttrExists(self, attrKey):
        return hasattr(self.blenderObj, attrKey)

class CityObjectProps(bpy.types.PropertyGroup):
    CJEOconstruction = bpy.props.StringProperty(name = 'CJEOconstruction', default= 'Building')
    CJEOtype = bpy.props.StringProperty(name = 'CJEOtype', default= 'CompositeSurface')
    CJEOlod = bpy.props.IntProperty(name="CJEOlod", default=2, min=1, max=5, description="LevelOfDetail")
    CJEOsublod = bpy.props.IntProperty(name="CJEOsublod", default=0, min=0, max=9, description="Subversion of LOD")            
