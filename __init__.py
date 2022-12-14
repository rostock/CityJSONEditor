"""Main module of the CityJSON Blender addon"""

import json
from multiprocessing.sharedctypes import Value
import time
import bpy

from bpy.props import BoolProperty, EnumProperty, StringProperty, IntProperty
from bpy.types import Operator
from bpy_extras.io_utils import ExportHelper, ImportHelper

from .core.objects import CityJSONParser, CityJSONExporter
from .core import ui, prop, operator, EditMenu, ObjectMenu, CityObject

bl_info = {
    "name": "CityJSONEditor",
    "author": "Konstantinos Mastorakis, Tim Balschmiter, Hagen Schoenkaese",
    "version": (1, 0, 1),
    "blender": (3, 2, 2),
    "location": "File > Import > CityJSON (.json) || File > Export > CityJSON (.json)",
    "description": "Visualize, edit and export 3D structures encoded in CityJSON format",
    "warning": "",
    "wiki_url": "",
    "category": "Import-Export",
}

class ImportCityJSON(Operator, ImportHelper):
    "Load a CityJSON file"
    bl_idname = "cityjson.import_file"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Import CityJSON"

    # ImportHelper mixin class uses this
    filename_ext = ".json"

    filter_glob: StringProperty(
        default="*.json",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )
    
    """
    material_type: EnumProperty(
        name="Materials' type",
        items=(('SURFACES', "Surfaces",
                "Creates materials based on semantic surface types"),
               ('CITY_OBJECTS', "City Objects",
                "Creates materials based on the type of city object")),
        description=(
            "Create materials based on city object or semantic"
            " surfaces"
        )
    )

    reuse_materials: BoolProperty(
        name="Reuse materials",
        description="Use common materials according to surface type",
        default=True
    )

    clean_scene: BoolProperty(
        name="Clean scene",
        description="Remove existing objects from the scene before importing",
        default=True
    )"""

    def execute(self, context):
        """Executes the import process"""

        """parser = CityJSONParser(self.filepath,
                                material_type=self.material_type,
                                reuse_materials=self.reuse_materials,
                                clear_scene=self.clean_scene)"""

        parser = CityJSONParser(self.filepath)

        return parser.execute()

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

    check_for_duplicates: BoolProperty(
        name="Remove vertex duplicates",
        default=True,
    )

    precision: IntProperty(
        name="Precision",
        default=5,
        description="Decimals to check for vertex duplicates",
        min=0,
        max=12,
    )
    def execute(self, context):
        
        exporter = CityJSONExporter(self.filepath,
                                    check_for_duplicates=self.check_for_duplicates,
                                    precision=self.precision)
        return exporter.execute()

class SetAttributes(bpy.types.Operator):
    bl_idname = "wm.set_attributes"
    bl_label = "SetAttributes"

    def execute(self,context):
        print('settng Attributes...')
        obj = CityObject.CityObject(bpy.context.active_object)
        for attr in CityObject.CityObjectProps.__dict__.keys():
            print(attr)
            # initialize attributes
            if attr.startswith('CJEO') and not obj.checkAttrExists(attr):
                obj.addCustomProperty(attr)

            # set attribute-values of selected Object (default values) so they show up in UI
            if attr.startswith('CJEO'):
                value = getattr(bpy.context.active_object, attr)
                obj.setCustomProperty(attr, value)

        print('finished setting attributes...')
        return {'FINISHED'} 

class GetLOD(bpy.types.Operator):
    bl_idname = "wm.get_lod"
    bl_label = "getlod"
    def execute(self, context):
        obj = CityObject.CityObject(context.active_object)
        obj.printAttr('CJEOtype')


classes = (
    ImportCityJSON,
    ExportCityJSON,
    prop.UP3DATE_CityjsonfyProperties,
    CityObject.CityObjectProps,
    operator.UP3DATECityjsonfy,
    ui.UP3DATE_PT_gui,
    EditMenu.SetSurfaceOperator,
    EditMenu.VIEW3D_MT_cityedit_mesh_context_menu,
    EditMenu.VIEW3D_MT_cityedit_mesh_context_submenu,
    ObjectMenu.SetLODOperator,
    ObjectMenu.VIEW3D_MT_cityobject_lod_menu,
    ObjectMenu.VIEW3D_MT_cityobject_lod_submenu,
    ObjectMenu.SetTypeOperator,
    ObjectMenu.VIEW3D_MT_cityobject_type_menu,
    ObjectMenu.VIEW3D_MT_cityobject_type_submenu,
    ObjectMenu.SetConstructionOperator,
    ObjectMenu.VIEW3D_MT_cityobject_construction_menu,
    ObjectMenu.VIEW3D_MT_cityobject_construction_submenu,
    SetAttributes,
    GetLOD
)

def menu_func_export(self, context):
    """Defines the menu item for CityJSON import"""
    self.layout.operator(ExportCityJSON.bl_idname, text="CityJSON (.json)")

def menu_func_import(self, context):
    """Defines the menu item for CityJSON export"""
    self.layout.operator(ImportCityJSON.bl_idname, text="CityJSON (.json)")

# create submenu in edit mode
def editmenu_func(self, context):
    is_vert_mode, is_edge_mode, is_face_mode = context.tool_settings.mesh_select_mode
    if is_face_mode:
        layout = self.layout
        layout.separator()
        layout.label(text="CityJSON Options")
        layout.menu(EditMenu.VIEW3D_MT_cityedit_mesh_context_submenu.bl_idname, text="set SurfaceType")

def objectmenu_func(self, context):
    layout = self.layout
    layout.separator()
    layout.label(text="CityJSON Options")
    layout.operator(SetAttributes.bl_idname, text="set initial attributes")
    # layout.operator(GetLOD.bl_idname, text="get LOD")
    layout.menu(ObjectMenu.VIEW3D_MT_cityobject_lod_submenu.bl_idname, text="set LOD")
    layout.menu(ObjectMenu.VIEW3D_MT_cityobject_type_submenu.bl_idname, text="set Type")
    layout.menu(ObjectMenu.VIEW3D_MT_cityobject_construction_submenu.bl_idname, text="set Construction")

def register():
    """Registers the classes and functions of the addon"""
    print("Function: register()")
    for cls in classes:
        bpy.utils.register_class(cls)
    # bpy.types.Scene.cityjsonfy_properties = bpy.props.PointerProperty(type=prop.UP3DATE_CityjsonfyProperties)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)
    # add menu to edit mod
    bpy.types.VIEW3D_MT_edit_mesh_faces.append(editmenu_func)
    bpy.types.VIEW3D_MT_edit_mesh_context_menu.append(editmenu_func)
    # add menu to object mod
    bpy.types.VIEW3D_MT_object.append(objectmenu_func)
    bpy.types.VIEW3D_MT_object_context_menu.append(objectmenu_func)

    # bpy.types.Material.my_settings = bpy.props.PointerProperty(type=MaterialProps)
    # bpy.types.Object.my_settings = bpy.props.PointerProperty(type=MaterialProps)
    # print(bpy.types.Object.my_settings)

    
def unregister():
    """Unregisters the classes and functions of the addon"""
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)

    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.cityjsonfy_properties

if __name__ == "__main__":
    register()