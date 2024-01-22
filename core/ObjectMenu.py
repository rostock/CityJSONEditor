import bpy
from .FeatureTypes import FeatureTypes

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
    cityJSONType: bpy.props.StringProperty(
        name = 'cityJSONType',
        default= 'Building',
    )

    def execute(self, context):
        obj = bpy.context.active_object
        obj['cityJSONType'] = self.cityJSONType
        #obj.setCustomProperty('cityJSONType',self.cityJSONType)
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

            
           


