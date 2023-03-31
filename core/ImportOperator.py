from bpy.props import BoolProperty, EnumProperty, StringProperty, IntProperty
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper
from .ImportProcess import ImportProcess

# Import Operator
class ImportCityJSON(Operator, ImportHelper):

    # Operator Metadata
    bl_idname = "cityjson.import_file"
    bl_label = "Import CityJSON"
    filename_ext = ".json"

    filter_glob: StringProperty(
        default="*.json",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    # List of Operator properties
    texture_setting: BoolProperty(
        name="Import Textures",
        description="Choose if textures present in the CityJSON file should be imported",
        default=True,
    )
    
    # Operator Main Method (Import-Process)
    def execute(self, context):
        importAndParse = ImportProcess(self.filepath, self.texture_setting)
        return importAndParse.execute()