import bpy

class VIEW3D_MT_edit_mesh_context_menu(bpy.types.Menu):
    bl_label = ''

    # Leave empty for compatibility.
    def draw(self, context):
        pass


def menu_func(self, context):
    is_vert_mode, is_edge_mode, is_face_mode = context.tool_settings.mesh_select_mode
    if is_face_mode:
        layout = self.layout
        layout.separator()
        layout.label(text="CityJSON Options")
        #layout.operator('mesh.flip_normals', text = 'Flip Normals')
        layout.operator(HelloWorldOperator.bl_idname, text="Hello World Operator")
        #layout.operator(HelloWorldOperator.bl, text="Hello World Operator")
    
    
#def printHuhu(self):
#    print("HUHU")

#def createMaterial(self, context):
#    return 0

#def addSurfaceType(self, context):
#    return 0


if __name__ == '__main__':
    # Register menu only if it doesn't already exist.
    rcmenu = getattr(bpy.types, "VIEW3D_MT_edit_mesh_context_menu", None)
    if rcmenu is None:
        bpy.utils.register_class(VIEW3D_MT_edit_mesh_context_menu)
        rcmenu = VIEW3D_MT_edit_mesh_context_menu

    # Retrieve a python list for inserting draw functions.
    draw_funcs = rcmenu._dyn_ui_initialize()
    draw_funcs.append(menu_func)







class HelloWorldOperator(bpy.types.Operator):
    bl_idname = "wm.hello_world"
    bl_label = "Minimal Operator"

    def execute(self, context):
        print("Hello World")
        return {'FINISHED'}


# Only needed if you want to add into a dynamic menu.
#def menu_func(self, context):
#    self.layout.operator(HelloWorldOperator.bl_idname, text="Hello World Operator")


# Register and add to the view menu (required to also use F3 search "Hello World Operator" for quick access).
bpy.utils.register_class(HelloWorldOperator)
bpy.types.VIEW3D_MT_view.append(menu_func)

# Test call to the newly defined operator.
bpy.ops.wm.hello_world()