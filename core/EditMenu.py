import bpy
from .FeatureTypes import FeatureTypes
from .CityMaterial import CityMaterial

class VIEW3D_MT_cityedit_mesh_context_submenu(bpy.types.Menu):
    bl_label = 'SurfaceTypes'
    bl_idname = 'VIEW3D_MT_cityedit_mesh_context_submenu'
    
    def draw(self, context):
        print("building edit menu")
        layout = self.layout
        obj = context.selected_objects            
        
        try:
            constructionType = getattr(obj[0], "CBOconstruction")
            features = FeatureTypes()
            layout.label(text=constructionType)  
            for surface in features.getAllElementsOfFeatureType(constructionType):
                layout.operator(SetSurfaceOperator.bl_idname, text=surface).surfaceType = surface
        except:
            layout.label(text="set construction type in object mode or select object in object mode")  
        
class VIEW3D_MT_cityedit_mesh_context_menu(bpy.types.Menu):
    bl_label = ''
    # Leave empty for compatibility.
    def draw(self, context):
        pass

class SetSurfaceOperator(bpy.types.Operator):
    bl_idname = "wm.set_surface"
    bl_label = "SetSurfaceOperator"
    surfaceType: bpy.props.StringProperty(
        name = 'surfaceType',
        default = ''
    )
    def execute(self, context):
        obj = context.object
        print("Klick:" + obj.CBOconstruction)
        if obj.type == 'MESH':
            mesh = obj.data # Assumed that obj.type == 'MESH'
            obj.update_from_editmode() # Loads edit-mode data into object data
            selected_polygons = [p for p in mesh.polygons if p.select]
            for face in selected_polygons:
                mat = CityMaterial(name=self.surfaceType)
                mat.addMaterialToObj(obj)
                mat.addMaterialToFace(obj)
                mat.addCustomStringProperty('CBMtype', self.surfaceType)
                ft = FeatureTypes()
                color = ft.getRGBColor(obj.CBOconstruction, self.surfaceType)
                print (color)
                #mat.setColor(color)
                #mat.addDefinedColo
      
        return {'FINISHED'}
