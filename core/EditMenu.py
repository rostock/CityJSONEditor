from asyncio.windows_events import NULL
from types import NoneType
import bpy
from .FeatureTypes import FeatureTypes
from .Material import Material

class VIEW3D_MT_cityedit_mesh_context_submenu(bpy.types.Menu):
    bl_label = 'SurfaceTypes'
    bl_idname = 'VIEW3D_MT_cityedit_mesh_context_submenu'
    
    def draw(self, context):
        layout = self.layout
        obj = bpy.context.active_object
        try:
            constructionType = obj["cityJSONType"] 
            features = FeatureTypes()
            layout.label(text=constructionType)  
            for surface in features.getAllElementsOfFeatureType(constructionType):
                layout.operator(SetSurfaceOperator.bl_idname, text=surface).surfaceType = surface
        except:
            layout.label(text="set construction type in object mode or select object in object mode")  

class SetSurfaceOperator(bpy.types.Operator):
    bl_idname = "wm.set_surface"
    bl_label = "SetSurfaceOperator"
    surfaceType: bpy.props.StringProperty(
        name = 'surfaceType',
        default = ''
    )

    #TODO fix individual face material assignment
    #TODO test with cityjson file
    def execute(self, context):
        obj = context.object
        if obj.type == 'MESH':
            mesh = obj.data # Assumed that obj.type == 'MESH'
            obj.update_from_editmode() # Loads edit-mode data into object data
            selected_polygons = [p for p in mesh.polygons if p.select]
            for face in selected_polygons:
                bpy.ops.object.mode_set(mode='OBJECT')
                try:
                    print(face.material_index)
                    bpy.data.materials.remove(bpy.context.object.active_material)
                    #bpy.ops.object.material_slot_remove()
                    
                    """
                    print(face.material_index)
                    matOld = Material(surfaceValue=face.material_index, newObject=obj)
                    matOld.deleteMaterial(obj=obj, matIndex=face.material_index)
                    del matOld
                    """
                except:
                    print("The Face does not have a Material or the Material has already been removed!")
                bpy.ops.object.mode_set(mode='EDIT')
                # create the material as object
                mat = Material(type=self.surfaceType, newObject=obj, objectID=obj.id_data.name, textureSetting=False, objectType=obj['cityJSONType'], surfaceIndex=None, surfaceValue=None, filepath=None, rawObjectData=None, geometry=None)
                mat.createMaterial()
                print("created material: "+ str(mat.objectID)+str(mat.type))                
                # set the color of the material
                mat.setColor()
                # assign the material to the selected face in blender                
                mat.addMaterialToFace()

        bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=False, do_recursive=True)
      
        return {'FINISHED'}
    
class CalculateSemanticsOperator(bpy.types.Operator):
    bl_idname = "wm.calc_semantics"
    bl_label = "CalculateSemantics"

    def execute(self, context):
        
        def materialCreator(surfaceType,matSlot,faceIndex):
            mat = Material(type=surfaceType, newObject=obj, objectID=obj.id_data.name, textureSetting=False, objectType=obj['cityJSONType'], surfaceIndex=None, surfaceValue=None, filepath=None, rawObjectData=None, geometry=None)
            mat.createMaterial()
            mat.setColor()
            mat.addMaterialToFace(matSlot,faceIndex)

        def materialCleaner():
            for face in obj.data.polygons:
                bpy.ops.object.mode_set(mode='OBJECT')
                matIndex = face.material_index
                bpy.context.object.active_material_index = matIndex
                bpy.ops.object.material_slot_remove()
                bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=False, do_recursive=True)

        obj = context.object

        materialCleaner()
        matSlot = 0
        for faceIndex, face in enumerate(obj.data.polygons):
            faceNormal = face.normal
            if faceNormal[2]==-1:
                surfaceType = "GroundSurface"
                materialCreator(surfaceType,matSlot,faceIndex)
                print("Ground")
                matSlot+=1
            elif faceNormal[2]>0:
                surfaceType = "RoofSurface"
                materialCreator(surfaceType,matSlot,faceIndex)
                print("Roof")
                matSlot+=1
            else:
                surfaceType = "WallSurface"
                materialCreator(surfaceType,matSlot,faceIndex)
                print("Wall")
                matSlot+=1

        return {'FINISHED'}

    