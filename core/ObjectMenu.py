import bpy
from .CityObject import CityObject

class VIEW3D_MT_cityobject_lod_submenu(bpy.types.Menu):
    bl_label = 'LevelOfDetail'
    bl_idname = 'VIEW3D_MT_cityobject_lod_submenu'
    def draw(self, context):
        layout = self.layout
        layout.label(text="LevelOfDetail")
        # bei den folgenden Operatoren muss ein Weg gefunden werden 
        layout.operator(SetLODOperator.bl_idname, text="1").lod = 1
        layout.operator(SetLODOperator.bl_idname, text="2").lod = 2
        layout.operator(SetLODOperator.bl_idname, text="3").lod = 3
        layout.operator(SetLODOperator.bl_idname, text="4").lod = 4
        layout.operator(SetLODOperator.bl_idname, text="5").lod = 5

class VIEW3D_MT_cityobject_type_submenu(bpy.types.Menu):
    bl_label = 'Type'
    bl_idname = 'type'
    def draw(self, context):
        layout = self.layout
        layout.label(text="Type")
        # bei den folgenden Operatoren muss ein Weg gefunden werden 
        layout.operator(SetTypeOperator.bl_idname, text="CompositeSurface").type = "CompositeSurface"

class VIEW3D_MT_cityobject_construction_submenu(bpy.types.Menu):
    bl_label = 'Construction'
    bl_idname = 'construction'
    def draw(self, context):
        layout = self.layout
        layout.label(text="Construction")
        # bei den folgenden Operatoren muss ein Weg gefunden werden 
        layout.operator(SetConstructionOperator.bl_idname, text="Building").construction = "Building"

class VIEW3D_MT_cityobject_construction_menu(bpy.types.Menu):
    bl_label = ''
    # Leave empty for compatibility.
    def draw(self, context):
        pass

class VIEW3D_MT_cityobject_type_menu(bpy.types.Menu):
    bl_label = ''
    # Leave empty for compatibility.
    def draw(self, context):
        pass

class VIEW3D_MT_cityobject_lod_menu(bpy.types.Menu):
    bl_label = ''
    # Leave empty for compatibility.
    def draw(self, context):
        pass

class SetLODOperator(bpy.types.Operator):
    bl_idname = "wm.set_lod"
    bl_label = "SetLODOperator"
    lod: bpy.props.IntProperty(
        name = 'lod',
        default=2,
        min=1,
        max=5,
        description="LevelOfDetail"
    )

    def execute(self, context):
        obj = CityObject(bpy.context.active_object)
        obj.addCustomPropertie('lod',self.lod)
        return {'FINISHED'} 

class SetTypeOperator(bpy.types.Operator):
    bl_idname = "wm.set_type"
    bl_label = "SetTypeOperator"
    type: bpy.props.StringProperty(
        name = 'type',
        default= 'CompositeSurface',
    )

    def execute(self, context):
        obj = CityObject(bpy.context.active_object)
        obj.addCustomPropertie('type',self.type)
        return {'FINISHED'} 

class SetConstructionOperator(bpy.types.Operator):
    bl_idname = "wm.set_construction"
    bl_label = "SetConstructionOperator"
    construction: bpy.props.StringProperty(
        name = 'construction',
        default= 'Building',
    )

    def execute(self, context):
        obj = CityObject(bpy.context.active_object)
        obj.addCustomPropertie('construction',self.construction)
        return {'FINISHED'} 
