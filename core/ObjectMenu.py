import bpy
from .CityObject import CityObject
from .FeatureTypes import FeatureTypes

class VIEW3D_MT_cityobject_lod_submenu(bpy.types.Menu):
    bl_label = 'LevelOfDetail'
    bl_idname = 'VIEW3D_MT_cityobject_lod_submenu'
    def draw(self, context):
        layout = self.layout
        layout.label(text="LevelOfDetail")
        layout.operator(SetLODOperator.bl_idname, text="1").CJEOlod = 1
        layout.operator(SetLODOperator.bl_idname, text="2").CJEOlod = 2
        layout.operator(SetLODOperator.bl_idname, text="3").CJEOlod = 3
        layout.operator(SetLODOperator.bl_idname, text="4").CJEOlod = 4
        layout.operator(SetLODOperator.bl_idname, text="5").CJEOlod = 5

class VIEW3D_MT_cityobject_type_submenu(bpy.types.Menu):
    bl_label = 'Type'
    bl_idname = 'type'
    def draw(self, context):
        layout = self.layout
        layout.label(text="Type")
        # bei den folgenden Operatoren muss ein Weg gefunden werden 
        layout.operator(SetTypeOperator.bl_idname, text="CompositeSurface").CJEOtype = "CompositeSurface"

class VIEW3D_MT_cityobject_construction_submenu(bpy.types.Menu):
    bl_label = 'Construction'
    bl_idname = 'construction'
    def draw(self, context):

        layout = self.layout
        layout.label(text="Construction")

        ft = FeatureTypes()
        list = ft.getAllFeatures()
        
        for feature in list:
            layout.operator(SetConstructionOperator.bl_idname, text=feature).CJEOconstruction = feature

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
    bl_idname = "wm.set_cjeolod"
    bl_label = "SetLODOperator"
    CJEOlod: bpy.props.IntProperty(
        name = 'CJEOlod',
        default=2,
        min=1,
        max=5,
        description="LevelOfDetail"
    )

    def execute(self, context):
        obj = CityObject(bpy.context.active_object)
        obj.setCustomProperty('CJEOlod',self.CJEOlod)
        return {'FINISHED'} 

class SetTypeOperator(bpy.types.Operator):
    bl_idname = "wm.set_cjeotype"
    bl_label = "SetTypeOperator"
    CJEOtype: bpy.props.StringProperty(
        name = 'CJEOtype',
        default= 'CompositeSurface',
    )

    def execute(self, context):
        obj = CityObject(bpy.context.active_object)
        #    obj.addCustomStringProperty('CBOtype',self.type)
        obj.setCustomProperty('CJEOtype',self.CJEOtype)
        return {'FINISHED'} 

class SetConstructionOperator(bpy.types.Operator):
    bl_idname = "wm.set_cjeoconstruction"
    bl_label = "SetConstructionOperator"
    CJEOconstruction: bpy.props.StringProperty(
        name = 'CJEOconstruction',
        default= 'Building',
    )

    def execute(self, context):
        obj = CityObject(bpy.context.active_object)
    #    obj.addCustomStringProperty('CBOconstruction',self.construction)
        obj.setCustomProperty('CJEOconstruction',self.CJEOconstruction)
        return {'FINISHED'} 