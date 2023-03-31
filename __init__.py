# Addon Metadata
bl_info = {
    "name": "CityJSONEditor",
    "author": "Konstantinos Mastorakis, Tim Balschmiter, Hagen Schoenkaese",
    "version": (2, 0, 0),
    "blender": (3, 4, 0),
    "location": "File > Import > CityJSON (.json) || File > Export > CityJSON (.json)",
    "description": "Visualize, edit and export 3D structures encoded in CityJSON format",
    "warning": "",
    "wiki_url": "",
    "category": "Import-Export",
}

import bpy
from .core.ImportOperator import ImportCityJSON
from .core.ExportOperator import ExportCityJSON


classes = (
    # Import Operator
    ImportCityJSON,
    # Export Operator
    ExportCityJSON,
)

def menu_func_import(self, context):
    """Defines the menu item for CityJSON export"""
    self.layout.operator(ImportCityJSON.bl_idname, text="CityJSON (.json)")

def menu_func_export(self, context):
    """Defines the menu item for CityJSON import"""
    self.layout.operator(ExportCityJSON.bl_idname, text="CityJSON (.json)")


def register():
    """Registers the classes and functions of the addon"""
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)
    
    
def unregister():
    """Unregisters the classes and functions of the addon"""
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)

    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()