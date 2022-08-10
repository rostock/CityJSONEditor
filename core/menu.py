import bpy

class VIEW3D_MT_edit_mesh_context_submenu(bpy.types.Menu):
    bl_label = 'SurfaceTypes'
    bl_idname = 'VIEW3D_MT_edit_mesh_context_submenu'

    def draw(self, context):
        layout = self.layout
        layout.label(text="Building")
        # bei den folgenden Operatoren muss ein Weg gefunden werden 
        layout.operator(SetSurfaceOperator.bl_idname, text="GroundSurface")
        layout.operator(SetSurfaceOperator.bl_idname, text="WallSurface")
        layout.operator(SetSurfaceOperator.bl_idname, text="RoofSurface")

class VIEW3D_MT_edit_mesh_context_menu(bpy.types.Menu):
    bl_label = ''

    # Leave empty for compatibility.
    def draw(self, context):
        pass

class SetSurfaceOperator(bpy.types.Operator):
    bl_idname = "wm.set_surface"
    bl_label = "Minimal Operator"
    
    def execute(self, context):
        print("Hier soll die Unterscheidung zwischen den Types getroffen werden und entsprechend die Materialfunction aufgerufen werden")
        print(self.text)
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
        layout.menu(VIEW3D_MT_edit_mesh_context_submenu.bl_idname, text="set SurfaceType3")

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