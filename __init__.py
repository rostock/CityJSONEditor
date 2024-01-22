# Addon Metadata
bl_info = {
    "name": "CityJSONEditor",
    "author": "Konstantinos Mastorakis, Tim Balschmiter, Hagen Schoenkaese",
    "version": (2, 1, 0),
    "blender": (3, 5, 1),
    "location": "File > Import > CityJSON (.json) || File > Export > CityJSON (.json)",
    "description": "Visualize, edit and export 3D structures encoded in CityJSON format",
    "warning": "",
    "wiki_url": "",
    "category": "Import-Export",
}

import bpy
from .core.ImportOperator import ImportCityJSON
from .core.ExportOperator import ExportCityJSON
from .core import EditMenu, ObjectMenu




classes = (
    # Import Operator
    ImportCityJSON,
    # Export Operator
    ExportCityJSON,
    # EditMode Menu
    EditMenu.SetSurfaceOperator,
    EditMenu.VIEW3D_MT_cityedit_mesh_context_submenu,
    EditMenu.CalculateSemanticsOperator,
    # ObjectMode Menu
    ObjectMenu.SetConstructionOperator,
    ObjectMenu.VIEW3D_MT_cityobject_construction_submenu,
    ObjectMenu.SetAttributes,

)

def menu_func_import(self, context):
    """Defines the menu item for CityJSON import"""
    self.layout.operator(ImportCityJSON.bl_idname, text="CityJSON (.json)")

def menu_func_export(self, context):
    """Defines the menu item for CityJSON export"""
    self.layout.operator(ExportCityJSON.bl_idname, text="CityJSON (.json)")

def objectmenu_func(self, context):
    """create context menu in object mode"""
    layout = self.layout
    layout.separator()
    layout.label(text="CityJSON Options")
    layout.operator(ObjectMenu.SetAttributes.bl_idname, text="set initial attributes")
    layout.menu(ObjectMenu.VIEW3D_MT_cityobject_construction_submenu.bl_idname, text="set Construction")

def editmenu_func(self, context):
    """create context menu in edit mode"""
    is_vert_mode, is_edge_mode, is_face_mode = context.tool_settings.mesh_select_mode
    if is_face_mode:
        layout = self.layout
        layout.separator()
        layout.label(text="CityJSON Options")
        layout.menu(EditMenu.VIEW3D_MT_cityedit_mesh_context_submenu.bl_idname, text="set SurfaceType")
        layout.operator(EditMenu.CalculateSemanticsOperator.bl_idname, text="calculateSemantics")




def register():
    """Registers the classes and functions of the addon"""
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

    # add menu to object mode context menu
    bpy.types.VIEW3D_MT_object.append(objectmenu_func)
    bpy.types.VIEW3D_MT_object_context_menu.append(objectmenu_func)
    # add menu to edit mode context menu
    bpy.types.VIEW3D_MT_edit_mesh_context_menu.append(editmenu_func)
    
    
def unregister():
    """Unregisters the classes and functions of the addon"""
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)

    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()