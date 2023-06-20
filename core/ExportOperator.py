from bpy.props import BoolProperty, EnumProperty, StringProperty, IntProperty
from bpy.types import Operator
from bpy_extras.io_utils import ExportHelper
from .ExportProcess import ExportProcess

# Import Operator
class ExportCityJSON(Operator, ExportHelper):

    "Export scene as a CityJSON file"
    bl_idname = "cityjson.export_file"
    bl_label = "Export CityJSON"

    # ExportHelper mixin class uses this
    filename_ext = ".json"

    filter_glob: StringProperty(
        default="*.json",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    # List of Operator properties
    texture_setting: BoolProperty(
        name="Export Textures",
        description="Choose if textures present in blender should be exported to the CityJSON file",
        default=True,
    )

    def execute(self, context):
        CityJSONExport = ExportProcess(self.filepath, self.texture_setting)
        return CityJSONExport.execute()