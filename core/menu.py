import bpy

class VIEW3D_MT_edit_mesh_context_submenu(bpy.types.Menu):
    bl_label = 'SurfaceTypes'
    bl_idname = 'VIEW3D_MT_edit_mesh_context_submenu'
    print("VIEW3D_MT_edit_mesh_context_submenu")
    def draw(self, context):
        layout = self.layout
        layout.label(text="Building")
        # bei den folgenden Operatoren muss ein Weg gefunden werden 
        layout.operator(SetSurfaceOperator.bl_idname, text="GroundSurface").surfaceType = 'GroundSurface'
        layout.operator(SetSurfaceOperator.bl_idname, text="WallSurface").surfaceType = 'WallSurface'
        layout.operator(SetSurfaceOperator.bl_idname, text="RoofSurface").surfaceType = 'RoofSurface'

class VIEW3D_MT_edit_mesh_context_menu(bpy.types.Menu):
    bl_label = ''
    print("VIEW3D_MT_edit_mesh_context_menu")
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