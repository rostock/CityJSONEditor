"""Main module of the CityJSON Blender addon"""

import json
import random
import time

import bpy
from bpy.props import BoolProperty, EnumProperty, StringProperty
from bpy.types import Operator
from bpy_extras.io_utils import ExportHelper, ImportHelper

from .core.material import BasicMaterialFactory
from .core.utils import (assign_properties, clean_buffer, clean_list,
                         coord_translate_axis_origin, original_coordinates)

bl_info = {
    "name": "Import CityJSON files",
    "author": "Konstantinos Mastorakis",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "File > Import > CityJSON (.json)",
    "description": "Visualize 3D City Models encoded in CityJSON format",
    "warning": "",
    "wiki_url": "",
    "category": "Import-Export",
}

material_factory = BasicMaterialFactory()

def write_cityjson(context, filepath):
    #Will write all scene data in CityJSON format"
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump("No problem", f, ensure_ascii=False, indent=4)
    
    return {'FINISHED'}

def get_geometry_name(objid, geom, index):
    """Returns the name of the provided geometry"""
    if 'lod' in geom:
        return "{index}: [LoD{lod}] {name}".format(name=objid, lod=geom['lod'], index=index)
    else:
        return "{index}: [GeometryInstance] {name}".format(name=objid, index=index)

def create_empty_object(name):
    """Returns an empty blender object"""

    new_object = bpy.data.objects.new(name, None)

    return new_object

def create_mesh_object(name, vertices, faces, materials=[], material_indices=[]):
    """Returns a mesh blender object"""

    mesh_data = None

    if faces:
        mesh_data = bpy.data.meshes.new(name)

        for material in materials:
            mesh_data.materials.append(material)

        indices = [i for face in faces for i in face]

        mesh_data.vertices.add(len(vertices))
        mesh_data.loops.add(len(indices))
        mesh_data.polygons.add(len(faces))

        coords = [c for v in vertices for c in v]

        loop_totals = [len(face) for face in faces]
        loop_starts = []
        i = 0
        for face in faces:
            loop_starts.append(i)
            i += len(face)

        mesh_data.vertices.foreach_set("co", coords)
        mesh_data.loops.foreach_set("vertex_index", indices)
        mesh_data.polygons.foreach_set("loop_start", loop_starts)
        mesh_data.polygons.foreach_set("loop_total", loop_totals)
        if len(material_indices) == len(faces):
            mesh_data.polygons.foreach_set("material_index", material_indices)
        elif len(material_indices) > len(faces):
            print("Object {name} has {num_faces} faces but {num_surfaces} semantic surfaces!"
                  .format(name=name,
                          num_faces=len(faces),
                          num_surfaces=len(material_indices)))

        mesh_data.update()

    new_object = bpy.data.objects.new(name, mesh_data)

    return new_object

def parse_geometry(data, vertices, theid, index):
    #Parsing the boundary data of every geometry
    bound=list()                

    geom = data['CityObjects'][theid]['geometry'][index]

    #Checking how nested the geometry is i.e what kind of 3D geometry it contains
    if((geom['type']=='MultiSurface') or (geom['type'] == 'CompositeSurface')):
        for face in geom['boundaries']:
            # This if - else statement ignores all the holes if any in any geometry
            if len(face)>0:
                bound.append(tuple(face[0]))
        
    elif (geom['type']=='Solid'):
        for shell in geom['boundaries']:
            for face in shell:
                if (len(face)>0):
                    bound.append(tuple(face[0]))
                                                    
    elif (geom['type']=='MultiSolid'):
        for solid in geom['boundaries']:
            for shell in solid:
                for face in shell:
                    if (len(face)>0):
                        bound.append(tuple(face[0]))
    
    temp_vertices, temp_bound = clean_buffer(vertices, bound)

    #Assigning semantics to every face of every geometry
    mats = []
    values = []  
    if 'semantics' in geom:
        values = geom['semantics']['values']
        
        for surface in geom['semantics']['surfaces']:
            mats.append(material_factory.get_material(surface))
                       
        values = clean_list(values)
        
    geom_obj = create_mesh_object(get_geometry_name(theid, geom, index), temp_vertices, temp_bound, mats, values)

    return geom_obj

def cityjson_parser(context, filepath):
    print("Importing CityJSON file...")
    #Deleting previous objects every time a new CityJSON file is imported
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=True)
            
    #Read CityJSON file
    with open(filepath) as json_file:
        data = json.load(json_file)
        vertices=list() 
           
        #Checking if coordinates need to be transformed and transforming if necessary 
        if 'transform' not in data:
            for vertex in data['vertices']:
                vertices.append(tuple(vertex))
        else:
            trans_param = data['transform']
            #Transforming coords to actual real world coords
            for vertex in data['vertices']:
                x=vertex[0]*trans_param['scale'][0]+trans_param['translate'][0]
                y=vertex[1]*trans_param['scale'][1]+trans_param['translate'][1]
                z=vertex[2]*trans_param['scale'][2]+trans_param['translate'][2]
                vertices.append((x,y,z))
        
        #Translating coordinates to the axis origin
        translation = coord_translate_axis_origin(vertices)
        
        #Updating vertices with new translated vertices
        vertices = translation[0]

        new_objects = []
        cityobjs = {}
                
        progress_max = len(data['CityObjects'])        
        progress = 0
        start_render = time.time()
        #Creating empty meshes for every CityObjects and linking its geometries as children-meshes
        for theid in data['CityObjects']:
            cityobject = create_empty_object(theid)
            cityobject = assign_properties(cityobject, data["CityObjects"][theid])
            new_objects.append(cityobject)
            cityobjs[theid] = cityobject
                        
            for i in range(len(data['CityObjects'][theid]['geometry'])):
                geom_obj = parse_geometry(data,vertices,theid,i)
                geom_obj.parent = cityobject
                new_objects.append(geom_obj)
            progress+=1
            
            print ("Rendering: " + str(round(progress*100/progress_max, 1))+"% completed", end="\r")    
        end_render = time.time()
                
        progress = 0
        start_hier = time.time()
        
        # Link everything to the scene
        collection = bpy.context.scene.collection
        for new_object in new_objects:
            collection.objects.link(new_object)

        #Assigning child building parts to parent buildings   
        for theid in data['CityObjects']:
            if 'parents' in data['CityObjects'][theid]:
                cityobjs[theid].parent = cityobjs[data['CityObjects'][theid]['parents'][0]]
            progress+=1
            print ("Building Hierarchy " + str(round(progress*100/progress_max, 1))+"% completed",end="\r")
        end_hier= time.time()
        
        #Console output
        print ("\n")
        print("CityJSON file successfully imported!\n")
        print ("Total Rendering Time: ", round(end_render-start_render,2),"s")
        print ("Building Hierarchy: ", round(end_hier-start_hier,2),"s")
        
    return {'FINISHED'}

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

    def execute(self, context):
        return cityjson_parser(context, self.filepath) #self.use_setting)

class ExportCityJSON(Operator, ExportHelper):
    "Export scene as a CityJSON file"
    bl_idname = "cityjson.export_file"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Export CityJSON"

    # ExportHelper mixin class uses this
    filename_ext = ".json"

    filter_glob: StringProperty(
        default="*.json",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    def execute(self, context):
        return write_cityjson(context, self.filepath)

def menu_func_export(self, context):
    self.layout.operator(ExportCityJSON.bl_idname, text="CityJSON (.json)")

def menu_func_import(self, context):
    self.layout.operator(ImportCityJSON.bl_idname, text="CityJSON (.json)")
    
def register():
    bpy.utils.register_class(ImportCityJSON)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    
    bpy.utils.register_class(ExportCityJSON)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

def unregister():
    bpy.utils.unregister_class(ImportCityJSON)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    
    bpy.utils.unregister_class(ExportCityJSON)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)

if __name__ == "__main__":
    register()
