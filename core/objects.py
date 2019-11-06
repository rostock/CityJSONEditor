"""Module to manipulate objects in Blender regarding CityJSON"""

import json
import time

import bpy

from .material import BasicMaterialFactory, ReuseMaterialFactory
from .utils import (assign_properties, clean_buffer, clean_list,
                    coord_translate_axis_origin, remove_scene_objects)


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

class CityJSONParser:
    """Class that parses a CityJSON file to Blender"""

    def __init__(self, filepath, reuse_materials=True, clear_scene=True):
        self.filepath = filepath
        self.clear_scene = clear_scene

        self.data = {}
        self.vertices = []

        if reuse_materials:
            self.material_factory = ReuseMaterialFactory()
        else:
            self.material_factory = BasicMaterialFactory()

    def load_data(self):
        """Loads the CityJSON data from the file"""

        with open(self.filepath) as json_file:
            self.data = json.load(json_file)

    def prepare_vertices(self):
        """Prepares the vertices by applying any required transformations"""

        vertices = []

        # Checking if coordinates need to be transformed and
        # transforming if necessary
        if 'transform' not in self.data:
            for vertex in self.data['vertices']:
                vertices.append(tuple(vertex))
        else:
            trans_param = self.data['transform']
            # Transforming coords to actual real world coords
            for vertex in self.data['vertices']:
                x = vertex[0]*trans_param['scale'][0] \
                    + trans_param['translate'][0]
                y = vertex[1]*trans_param['scale'][1] \
                    + trans_param['translate'][1]
                z = vertex[2]*trans_param['scale'][2] \
                    + trans_param['translate'][2]

                vertices.append((x, y, z))

        # Translating coordinates to the axis origin
        translation = coord_translate_axis_origin(vertices)

        # Updating vertices with new translated vertices
        self.vertices = translation[0]

    def parse_geometry(self, theid, index):
        """Returns a mesh object for the provided geometry"""
        bound = []

        geom = self.data['CityObjects'][theid]['geometry'][index]

        # Checking how nested the geometry is i.e what kind of 3D
        # geometry it contains
        if (geom['type'] == 'MultiSurface'
                or geom['type'] == 'CompositeSurface'):
            for face in geom['boundaries']:
                if face:
                    bound.append(tuple(face[0]))
        elif geom['type'] == 'Solid':
            for shell in geom['boundaries']:
                for face in shell:
                    if face:
                        bound.append(tuple(face[0]))
        elif geom['type'] == 'MultiSolid':
            for solid in geom['boundaries']:
                for shell in solid:
                    for face in shell:
                        if face:
                            bound.append(tuple(face[0]))

        temp_vertices, temp_bound = clean_buffer(self.vertices, bound)

        #Assigning semantics to every face of every geometry
        mats = []
        values = []
        if 'semantics' in geom:
            values = geom['semantics']['values']

            for surface in geom['semantics']['surfaces']:
                mats.append(self.material_factory.get_material(surface))

            values = clean_list(values)

        geom_obj = create_mesh_object(get_geometry_name(theid, geom, index),
                                      temp_vertices,
                                      temp_bound,
                                      mats,
                                      values)

        return geom_obj

    def execute(self):
        """Execute the import process"""

        if self.clear_scene:
            remove_scene_objects()

        print("Importing CityJSON file...")

        self.load_data()

        self.prepare_vertices()

        new_objects = []
        cityobjs = {}

        progress_max = len(self.data['CityObjects'])
        progress = 0
        start_import = time.time()

        # Creating empty meshes for every CityObjects and linking its
        # geometries as children-meshes
        for theid in self.data['CityObjects']:
            cityobject = create_empty_object(theid)
            cityobject = assign_properties(cityobject,
                                           self.data["CityObjects"][theid])
            new_objects.append(cityobject)
            cityobjs[theid] = cityobject

            for i, _ in enumerate(self.data['CityObjects'][theid]['geometry']):
                geom_obj = self.parse_geometry(theid, i)
                geom_obj.parent = cityobject
                new_objects.append(geom_obj)

            progress += 1
            print("Importing: {percent}% completed"
                  .format(percent=round(progress * 100 / progress_max, 1)),
                  end="\r")
        end_import = time.time()

        progress = 0
        start_hier = time.time()

        #Assigning child building parts to parent buildings
        for objid in self.data['CityObjects']:
            if 'parents' in self.data['CityObjects'][objid]:
                parent_id = self.data['CityObjects'][objid]['parents'][0]
                cityobjs[objid].parent = cityobjs[parent_id]

            progress += 1
            print("Building hierarchy: {percent}% completed"
                  .format(percent=round(progress * 100 / progress_max, 1)),
                  end="\r")
        end_hier = time.time()

        start_link = time.time()

        # Link everything to the scene
        collection = bpy.context.scene.collection
        for new_object in new_objects:
            collection.objects.link(new_object)
        
        end_link = time.time()

        #Console output
        print("\n")
        print("CityJSON file successfully imported!\n")
        print("Total Importing Time: ", round(end_import-start_import, 2), "s")
        print("Building Hierarchy: ", round(end_hier-start_hier, 2), "s")
        print("Linking: ", round(end_link-start_link, 2), "s")

        return {'FINISHED'}
