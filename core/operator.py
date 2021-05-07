import bpy

class UP3DATECityjsonfy(bpy.types.Operator):
    bl_idname = "cityjson.cityjsonfy"
    bl_label = "Convert to cityjson"
    bl_context = "scene"

    def execute(self, context):
        scene = bpy.context.scene
        props = scene.cityjsonfy_properties

        # define properties
        LOD_fullversion = props.LOD
        if props.LOD_version != 0:
            LOD_fullversion = round(props.LOD + (props.LOD_version / 10), 1)

        # loop through selected objects
        for geom_obj in bpy.context.selected_objects:
            cityjson_id = geom_obj.name
            geom_location = geom_obj.location

            # create empty
            cityjson_object = bpy.data.objects.new("empty", None)
            scene.collection.objects.link(cityjson_object)
            cityjson_object.location = geom_location

            # set names and attributes
            geom_obj.name = f"{props.LOD}: [LOD{LOD_fullversion}] {cityjson_id}"
            geom_obj["type"] = props.geometry_type
            geom_obj["lod"] = props.LOD
            cityjson_object.name = cityjson_id
            cityjson_object["type"] = props.feature_type

        return {"FINISHED"}