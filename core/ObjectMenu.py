import bpy
from .FeatureTypes import FeatureTypes
from .Material import Material
import math

class SetAttributes(bpy.types.Operator):
    bl_idname = "wm.set_attributes"
    bl_label = "SetAttributes"

    def execute(self,context):
        obj = bpy.context.active_object
        obj['cityJSONType'] = "Building"
        obj['LOD'] = 2 
        return {'FINISHED'} 

class SetConstructionOperator(bpy.types.Operator):
    bl_idname = "wm.set_cityjsontype"
    bl_label = "SetCityJSONType"
    cityJSONType:     bpy.props.StringProperty(name='cityJSONType',default='Building',)

    def execute(self, context):
        obj = bpy.context.active_object
        obj['cityJSONType'] = self.cityJSONType
        return {'FINISHED'} 
    

class VIEW3D_MT_cityobject_construction_submenu(bpy.types.Menu):
    bl_label = 'Construction'
    bl_idname = 'VIEW3D_MT_cityobject_construction_submenu'
    def draw(self, context):

        layout = self.layout
        layout.label(text="Construction")

        ft = FeatureTypes()
        list = ft.getAllFeatures()
        
        for feature in list:
            layout.operator(SetConstructionOperator.bl_idname, text=feature).cityJSONType = feature

class CalculateSemanticsOperator(bpy.types.Operator):
    bl_idname = "wm.calc_semantics"
    bl_label = "CalculateSemantics"

    def execute(self, context):

        # if initial attributes are not already set, do so now
        try: 
            obj = bpy.context.active_object
            type = obj['cityJSONType']
                        
        except:
            obj['cityJSONType'] = "Building"
            obj['LOD'] = 2 
        
        def materialCreator(surfaceType,matSlot,faceIndex):
            mat = Material(type=surfaceType, newObject=obj, objectID=obj.id_data.name, textureSetting=False, objectType=obj['cityJSONType'], surfaceIndex=None, surfaceValue=None, filepath=None, rawObjectData=None, geometry=None)
            mat.createMaterial()
            mat.setColor()
            mat.addMaterialToFace(matSlot,faceIndex)
            del mat

        def materialCleaner():
            bpy.ops.object.mode_set(mode='OBJECT')
            for face in obj.data.polygons:
                matIndex = face.material_index
                bpy.context.object.active_material_index = matIndex
                bpy.ops.object.material_slot_remove()
            bpy.ops.object.mode_set(mode='EDIT')   
            bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=False, do_recursive=True)

        obj = context.object

        materialCleaner()
        matSlot = 0
        for faceIndex, face in enumerate(obj.data.polygons):
            if math.isclose(face.normal[2] ,-1.0):
                surfaceType = "GroundSurface"
                materialCreator(surfaceType,matSlot,faceIndex)
                matSlot+=1
            elif math.isclose(face.normal[2],0,abs_tol=1e-3) or ((face.normal[2] < 0) and (math.isclose(face.normal[2],-1.0) == False)):
                surfaceType = "WallSurface"
                materialCreator(surfaceType,matSlot,faceIndex)
                matSlot+=1
            else:
                surfaceType = "RoofSurface"
                materialCreator(surfaceType,matSlot,faceIndex)
                matSlot+=1
        
        return {'FINISHED'}

            
           


