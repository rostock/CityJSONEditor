import bpy
import pprint
import idprop

class VIEW3D_MT_edit_mesh_context_submenu(bpy.types.Menu):
    bl_label = 'SurfaceTypes'
    bl_idname = 'VIEW3D_MT_edit_mesh_context_submenu'

    def draw(self, context):
        layout = self.layout
        layout.label(text="Building")
        # bei den folgenden Operatoren muss ein Weg gefunden werden 
        #layout.operator(SetSurfaceOperator.bl_idname, text="GroundS").surfaceType = "GroundSurface"
        layout.operator(SetSurfaceOperator.bl_idname, text="GroundSurface").surfaceType = 'GroundSurface'
        layout.operator(SetSurfaceOperator.bl_idname, text="WallSurface").surfaceType = 'WallSurface'
        layout.operator(SetSurfaceOperator.bl_idname, text="RoofSurface").surfaceType = 'RoofSurface'

class VIEW3D_MT_edit_mesh_context_menu(bpy.types.Menu):
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
        print(self.surfaceType)
        obj = bpy.context.object
        if obj.type == 'MESH':
            mesh = obj.data # Assumed that obj.type == 'MESH'
            obj.update_from_editmode() # Loads edit-mode data into object data
            selected_polygons = [p for p in mesh.polygons if p.select]
            for face in selected_polygons:
                print ("Huhu")
                #print (face.id)
                #für jede Fläche sollen nun die entsprechenden Materialien und CustomProperties angelegt werden
        return {'FINISHED'}

classes = (
    SetSurfaceOperator,
    VIEW3D_MT_edit_mesh_context_submenu    
    )

def menu_func(self, context):
    is_vert_mode, is_edge_mode, is_face_mode = context.tool_settings.mesh_select_mode
    if is_face_mode:
        layout = self.layout
        layout.separator()
        layout.label(text="CityJSON Options")
        layout.menu(VIEW3D_MT_edit_mesh_context_submenu.bl_idname, text="set SurfaceType")

def register():
    print("Register")
    for cls in classes:
        bpy.utils.register_class(cls)
    
def unregister():
    bpy.utils.unregister_module(__name__)
        
if __name__ == '__main__':
    register()
    # Register menu only if it doesn't already exist.
    rcmenu = getattr(bpy.types, "VIEW3D_MT_edit_mesh_context_menu", None)
    if rcmenu is None:
        bpy.utils.register_class(VIEW3D_MT_edit_mesh_context_menu)
        rcmenu = VIEW3D_MT_edit_mesh_context_menu

    # Retrieve a python list for inserting draw functions.
    draw_funcs = rcmenu._dyn_ui_initialize()
    draw_funcs.append(menu_func)