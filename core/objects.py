"""Module to manipulate objects in Blender regarding CityJSON"""

from asyncio.windows_events import NULL
import json
from posixpath import basename
import time
import sys
import bpy
import idprop
import os
import shutil

from pathlib import Path
from inspect import getmembers
from pprint import pprint
from datetime import datetime

from .material import (BasicMaterialFactory, ReuseMaterialFactory,
                       CityObjectTypeMaterialFactory)
from .utils import (assign_properties, clean_buffer, clean_list,
                    coord_translate_axis_origin, coord_translate_by_offset, remove_all_materials,
                    remove_scene_objects, get_geometry_name, create_empty_object,
                    create_mesh_object, get_collection, write_vertices_to_CityJSON,
                    remove_vertex_duplicates, export_transformation_parameters,
                    export_metadata, export_parent_child, export_attributes,
                    store_semantic_surfaces, link_face_semantic_surface, common_setup)    
from .CityMaterial import (CityMaterial)              

class CityJSONParser:
    """Class that parses a CityJSON file to Blender"""

    def __init__(self, filepath, material_type, reuse_materials=True, clear_scene=True):
        self.filepath = filepath
        self.clear_scene = clear_scene

        self.data = {}
        self.vertices = []

        if material_type == 'SURFACES':
            if reuse_materials:
                self.material_factory = ReuseMaterialFactory()
            else:
                self.material_factory = BasicMaterialFactory()
        else:
            self.material_factory = CityObjectTypeMaterialFactory()

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
            #Creating transform properties
            bpy.context.scene.world['transformed'] = True
            bpy.context.scene.world['transform.X_scale'] = trans_param['scale'][0]
            bpy.context.scene.world['transform.Y_scale'] = trans_param['scale'][1]
            bpy.context.scene.world['transform.Z_scale'] = trans_param['scale'][2]

            bpy.context.scene.world['transform.X_translate'] = trans_param['translate'][0]
            bpy.context.scene.world['transform.Y_translate'] = trans_param['translate'][1]
            bpy.context.scene.world['transform.Z_translate'] = trans_param['translate'][2]

        
        if 'Axis_Origin_X_translation' in bpy.context.scene.world:
            offx = -bpy.context.scene.world['Axis_Origin_X_translation']
            offy = -bpy.context.scene.world['Axis_Origin_Y_translation']
            offz = -bpy.context.scene.world['Axis_Origin_Z_translation']
            translation = coord_translate_by_offset(vertices, offx, offy, offz)
        else:
            translation = coord_translate_axis_origin(vertices)

            bpy.context.scene.world['Axis_Origin_X_translation']=-translation[1]
            bpy.context.scene.world['Axis_Origin_Y_translation']=-translation[2]
            bpy.context.scene.world['Axis_Origin_Z_translation']=-translation[3]

        # Updating vertices with new translated vertices
        self.vertices = translation[0]

    def parse_geometry(self, theid, obj, geom, index, data, filepath):
        """Returns a mesh object for the provided geometry"""
        bound = []

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

        """
        mats, values = self.material_factory.get_materials(cityobject=obj,
                                                           geometry=geom)
        """

        # Array of all materials
        mats = []
        # Array of the material indices
        values = []

        #appearances = []
        #textureValues = []

        #""" 
        ##### Material only #####

        if 'semantics' in geom:
            values = geom['semantics']['values']
            for surface in geom['semantics']['surfaces']:
                # create new material
                new_material = CityMaterial(surface['type'])
                # set color of material
                new_material.setColor(surface['type'])
                # set custom property "type"
                new_material.addCustomStringProperty("type",surface['type'])
                mats.append(new_material.material)  

        """     
        for material in bpy.data.materials:
            material_type = material.CityJSONType
            print(material_type)
            pass
        """
        
        ##### with optional texture #####
        """
        if 'semantics' in geom:
            values = geom['semantics']['values']
            texture_index = 0
            for surface in geom['semantics']['surfaces']:
                # create new material
                new_material = CityMaterial(surface['type'])

                if 'texture' in geom:
                    #set texture of material
                    new_material.setTexture(data, texture_index, filepath)
                    texture_index += 1
                else:
                    # set color of material
                    new_material.setColor(surface['type'])
                # set custom property "type"
                new_material.addCustomProperty("type",surface['type'])
                mats.append(new_material.material)  

        """


        ###############

        geom_obj = create_mesh_object(get_geometry_name(theid, geom, index),
                                      temp_vertices,
                                      temp_bound,
                                      mats,
                                      values)

        if 'lod' in geom:
            geom_obj['lod'] = geom['lod']

        geom_obj['type'] = geom['type']

        return geom_obj

    def execute(self):
        """Execute the import process"""

        if self.clear_scene:
            common_setup()
            remove_all_materials()
            remove_scene_objects()
            
            
        print("\nImporting CityJSON file...")

        self.load_data()

        self.prepare_vertices()

        #Storing the reference system
        if 'metadata' in self.data:
                    
            if 'referenceSystem' in self.data['metadata']:
                bpy.context.scene.world['CRS'] = self.data['metadata']['referenceSystem']
            
        new_objects = []
        cityobjs = {}

        progress_max = len(self.data['CityObjects'])
        progress = 0
        start_import = time.time()

        # Creating empty meshes for every CityObjects and linking its
        # geometries as children-meshes
        for objid, obj in self.data['CityObjects'].items():
            cityobject = create_empty_object(objid)
            cityobject = assign_properties(cityobject,
                                           obj)
            new_objects.append(cityobject)
            cityobjs[objid] = cityobject

            for i, geom in enumerate(obj['geometry']):
                data = self.data
                geom_obj = self.parse_geometry(objid, obj, geom, i, data, self.filepath)
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
        print ("\nBuilding hierarchy...")
        for objid, obj in self.data['CityObjects'].items():
            if 'parents' in obj:
                parent_id = obj['parents'][0]
                cityobjs[objid].parent = cityobjs[parent_id]

            progress += 1
            print("Building hierarchy: {percent}% completed"
                  .format(percent=round(progress * 100 / progress_max, 1)),
                  end="\r")
        end_hier = time.time()

        start_link = time.time()

        # Link everything to the scene
        print ("\nLinking objects to the scene...")
        collection = bpy.context.scene.collection
        for new_object in new_objects:
            if 'lod' in new_object:
                get_collection("LoD{}".format(new_object['lod'])).objects.link(new_object)
            else:
                collection.objects.link(new_object)
        
        end_link = time.time()
        #Console output
        print("Total importing time: ", round(end_import-start_import, 2), "s")
        print("Building hierarchy: ", round(end_hier-start_hier, 2), "s")
        print("Linking: ", round(end_link-start_link, 2), "s")
        print("Done!")
        timestamp = datetime.now()
        print("\n[" +timestamp.strftime("%d/%b/%Y @ %H:%M:%S")+ "]", "CityJSON file successfully imported from '"+str(self.filepath)+"'.")

        return {'FINISHED'}

class CityJSONExporter:

    def __init__ (self, filepath, check_for_duplicates=True, precision=3):
        self.filepath = filepath
        self.check_for_duplicates = check_for_duplicates
        self.precision = precision
    
    def initialize_dictionary(self):
        empty_json = {
            "type": "CityJSON",
            "version": "1.0",
            # "extensions": {},
            "metadata": {},
            "CityObjects": {},
            "vertices": [],
            "appearance": {
                    "textures": [],
                    "vertices-texture": []
                }
            }
        return empty_json

    def get_custom_properties(self,city_object,init_json,CityObject_id):
        """Creates the required structure according to CityJSON and writes all the object's custom properties (aka attributes)"""
        init_json["CityObjects"].setdefault(CityObject_id,{})
        init_json["CityObjects"][CityObject_id].setdefault('geometry',[])
        cp=city_object.items()
        for prop in cp:
            # When a new empty object is added by user, Blender assigns some built in properties at the first index of the property list. 
            # With this it is bypassed and continues to the actual properties of the object                
            if prop[0]=="_RNA_UI":
                continue  
            # Upon import into Blender the for every level deeper an attribute is nested the more a "." is used in the string between the 2 attributes' names
            # So to store it back to the original form the concatenated string must be split. 
            # Split is the list containing the original attributes names.
            split = prop[0].split(".") 
            # Check if the attribute is IDPropertyArray and convert to python list type because JSON encoder cannot handle type IDPropertyArray.
            if isinstance(prop[1],idprop.types.IDPropertyArray):
                attribute=prop[1].to_list()
            else:
                attribute=prop[1]
            export_attributes(split,init_json,CityObject_id,attribute)

    def create_mesh_structure(self,city_object,objid,init_json):
        "Prepares the structure within the empty mesh for storing the geometries, stored the lod and accesses the vertices and faces of the geometry within Blender"
        #Create geometry key within the empty object for storing the LoD(s) 
        CityObject_id = objid.split(' ')[2]
        init_json["CityObjects"].setdefault(CityObject_id,{})
        init_json["CityObjects"][CityObject_id].setdefault('geometry',[])
        #Check if the user has assigned the custom properties 'lod' and 'type' correctly 
        if ('lod' in city_object.keys() and (type(city_object['lod']) == float or type(city_object['lod'])==int) ):
            if ('type' in city_object.keys() and (city_object['type'] == "MultiSurface" or city_object['type'] == "CompositeSurface" or city_object['type'] == "Solid")):
                #Check if object has materials (in Blender) i.e semantics in real life and if yes create the extra keys (within_geometry) to store it.
                #Otherwise just create the rest of the tags
                if city_object.data.materials:
                    themeName = 'unnamed'
                    if 'theme' in bpy.context.scene.world:
                        themeName =  bpy.context.scene.world["theme"]
                    #init_json["CityObjects"][CityObject_id]['geometry'].append({'type':city_object['type'],'boundaries':[],'semantics':{'surfaces': [], 'values': [[]]},'texture':{},'lod':city_object['lod']})  ##Auskommentiert von Tim
                    init_json["CityObjects"][CityObject_id]['geometry'].append({'type':city_object['type'],'boundaries':[],'semantics':{'surfaces': [], 'values': []},'texture':{themeName:{'values':[]}},'lod':city_object['lod']})
                else:
                    init_json["CityObjects"][CityObject_id]['geometry'].append({'type':city_object['type'],'boundaries':[],'lod':city_object['lod']})
            else:
                print ("You either forgot to add `type` as a custom property of the geometry, ", name, ", or 'type' is not `MultiSurface`,`CompositeSurface` or `Solid`")
                sys.exit(None)
        else:
            print ("You either forgot to add `lod` as a custom property of the geometry, ", name, ", or 'lod' is not a number")
            sys.exit(None)
            
        #Accessing object's vertices 
        object_verts = city_object.data.vertices
        #Accessing object's faces
        object_faces = city_object.data.polygons

        return CityObject_id,object_verts,object_faces

    ##### Texture Export ####
    def create_appearance_item(self, basename):
        imageType = "PNG"
        imageName = "appearance/" + basename
        texture = {
            "type": imageType,
            "image": imageName,
            "wrapMode":"clamp",
            "textureType":"unknown",
            "borderColor":[
               0.0,
               0.0,
               0.0,
               1.0
            ]
        }
        return texture

    def create_texture_vertex(self, uv):
        print (uv.to_tuple())
        return uv.to_tuple()
    #########################

    def export_geometry_and_semantics(self,city_object,init_json,CityObject_id,object_faces,object_verts,
                                      vertices,cj_next_index):        
        #Index in the geometry list that the new geometry needs to be stored.
        index = len(init_json["CityObjects"][CityObject_id]['geometry'])-1

        # Index of the vertices for the uv coordinates in the future CityJSON file
        uv_index = 0

        # Create semantic surfaces
        semantic_surfaces = store_semantic_surfaces(init_json, city_object, index, CityObject_id)
        if city_object['type'] == 'MultiSurface' or city_object['type'] == 'CompositeSurface':
            
            ##### Texture Export ####  
            
            # Build Appearance 
            # list of all the materials with a texture
            materials_with_texture = []
            # index of the materials
            material_index = 0 
            for material_slot in city_object.material_slots:
                # Only try to build an appearance if there actually is a texture used in this material
                # which can be checked by the existence of more than 2 nodes
                if (len(material_slot.material.node_tree.nodes))>2:
                    image_basename = material_slot.material.node_tree.nodes[2].image.name
                    init_json['appearance']['textures'].append(self.create_appearance_item(image_basename))
                    # add index of the material with a texture to the list of such materials
                    materials_with_texture.append(material_index)
                # increase the material index
                material_index += 1
            #########################

            # Browsing through faces and their vertices of every object.
            for face in object_faces:
                init_json["CityObjects"][CityObject_id]["geometry"][index]["boundaries"].append([[]])
                
                ##### Texture Export ####
                # Building JSON-Sructure for UV-Mapping
                init_json["CityObjects"][CityObject_id]["geometry"][index]["texture"]["unnamed"]["values"].append([[]])

                # ID of the material of the currently processed face
                face_material = face.material_index

                # Write the index of the appearance in texture>unnamed>values
                # Face has a texture
                if face_material in materials_with_texture:
                    
                    # get the future index of the appearance (Texture) as it will be in the CityJSON file
                    future_material_index = materials_with_texture.index(face_material)
                    # Appending the ID of the corresponding appearance as first parameter (mapping material/texture to face UV-Coordinates)
                    init_json["CityObjects"][CityObject_id]["geometry"][index]["texture"]["unnamed"]["values"][face.index][0].append(future_material_index)

                # Face does not have a texture
                else:
                    # if there is no texture for this face append null-value instead
                    init_json["CityObjects"][CityObject_id]["geometry"][index]["texture"]["unnamed"]["values"][face.index][0].append(None)

                # Vertex Loop 
                for i in range(len(object_faces[face.index].vertices)):
                    original_index = object_faces[face.index].vertices[i]
                    get_vertex = object_verts[original_index]

                    #Write vertex to init_json at this point so the mesh_object.world_matrix (aka transformation matrix) is always the
                    #correct one. With the previous way it would take the last object's transformation matrix and would potentially lead to wrong final
                    #coordinate to be exported.
                    write_vertices_to_CityJSON(city_object,get_vertex.co,init_json)
                    vertices.append(get_vertex.co)
                    
                    # Store Boundaries
                    init_json["CityObjects"][CityObject_id]["geometry"][index]["boundaries"][face.index][0].append(cj_next_index)

                    ##### Texture Export ####
                    # If the face of the vertex loop has a texture --> get the texture mapping parameters
                    if face_material in materials_with_texture:
                        # UV layer of the city_object, only the layer with index = 0 is used (beacause in our data there is only one)
                        uv_layer = city_object.data.uv_layers[0].data   
                        # Store UV - Coordinates
                        init_json['appearance']['vertices-texture'].append(self.create_texture_vertex(uv_layer[cj_next_index].uv))
                        # Store UV - Mapping (UV Coordinates to Faces)
                        init_json["CityObjects"][CityObject_id]["geometry"][index]["texture"]["unnamed"]["values"][face.index][0].append(uv_index)
                        # increase the uv_index, which represents the uv-point index in the appearance of the CityJSON
                        uv_index += 1
                #########################
                    
                    cj_next_index += 1
                

                # In case the object has semantics they are accordingly stored as well
                link_face_semantic_surface(init_json, city_object, index, CityObject_id, semantic_surfaces, face)


        if city_object['type'] == 'Solid':

            init_json["CityObjects"][CityObject_id]["geometry"][index]["boundaries"].append([])
            for face in object_faces:
                init_json["CityObjects"][CityObject_id]["geometry"][index]["boundaries"][0].append([[]])
                
                for i in range(len(object_faces[face.index].vertices)):
                    original_index = object_faces[face.index].vertices[i]
                    get_vertex = object_verts[original_index]
                    if get_vertex.co in vertices:
                        vert_index = vertices.index(get_vertex.co)
                        init_json["CityObjects"][CityObject_id]["geometry"][index]["boundaries"][0][face.index][0].append(vert_index)
                    else:
                        write_vertices_to_CityJSON(city_object,get_vertex.co,init_json)
                        vertices.append(get_vertex.co)
                        init_json["CityObjects"][CityObject_id]["geometry"][index]["boundaries"][0][face.index][0].append(cj_next_index)
                        cj_next_index += 1
                # In case the object has semantics they are accordingly stored as well
                link_face_semantic_surface(init_json, city_object, index, CityObject_id, semantic_surfaces, face)
        return cj_next_index

    def execute(self):
        start=time.time()
        print("\nExporting Blender scene into CityJSON file...")
        #Create the initial structure of the cityjson dictionary
        init_json = self.initialize_dictionary()

        # switch to Object-Mode (does nothing if already in Object-Mode)
        # requirement for some of the later functions to work properly
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # Variables to keep up with the exporting progress. Used to print percentage in the terminal.
        progress_max = len(bpy.data.objects)
        # Initialize progress status
        progress = 0
        # Variable to store the next free index that a vertex should be saved in the cityjson file. Avoiding saving duplicates.
        cj_next_index = 0
        # Create a list of vertices to store the global vertices of all objects
        verts = list()

        for city_object in bpy.data.objects:
            #Get object's name
            objid = city_object.name
            #Empty objects have all the attributes so their properties are accessed to extract this information
            if city_object.type=='EMPTY':
                #Get all the custom properties of the object
                self.get_custom_properties(city_object,init_json,objid)                       
            #If the object is MESH means that is an actual geometry contained in the CityJSON file
            if city_object.type =='MESH':
                """ Export geometries with their semantics into CityJSON
                    Geometry type is checked for every object, because the structure that the geometry has to be stored in the cityjson is different depending on the geometry type 
                    In case the object has semantics they are accordingly stored as well using the 'store_semantics' function
                    Case of multisolid hasn't been taken under consideration!!
                """
                #Creating the structure for storing the geometries and get the initial ID of the CityObject its vertices and its faces
                CityObject_id,object_verts,object_faces = self.create_mesh_structure(city_object,objid,init_json)

                #Exporting geometry and semantics. CityJSON vertices_index is returned so it can be re-fed into the function at the correct point.
                cj_next_index = self.export_geometry_and_semantics(city_object,init_json,CityObject_id,object_faces,
                                object_verts,verts,cj_next_index)
            
            progress += 1
            print("Appending geometries, vertices, semantics, attributes: {percent}% completed".format(percent=round(progress * 100 / progress_max, 1)),end="\r")

        if self.check_for_duplicates:
            remove_vertex_duplicates(init_json, self.precision)
        export_parent_child(init_json)
        export_transformation_parameters(init_json)
        export_metadata(init_json)

        print ("Writing to CityJSON file...")
        #Writing CityJSON file
        with open(self.filepath, 'w', encoding='utf-8') as f:
            basePathInfos = bpy.data.filepath.split('\\')
            baseFolder = bpy.data.filepath.replace(basePathInfos[ len(basePathInfos) - 1 ],"")
            
            json.dump(init_json, f, ensure_ascii=False)
            for image in bpy.data.images:
                if image.filepath:
                    fileSourceInfos = image.filepath.split('\\')
                    fileSourceName = fileSourceInfos[ len(fileSourceInfos) - 1 ]
                    folderSource = image.filepath.replace(fileSourceInfos[ len(fileSourceInfos) - 1 ],"")
                    
                    fileInfosTarget =self.filepath.split('\\')
                    folderTarget =self.filepath.replace(fileInfosTarget[ len(fileInfosTarget) - 1 ],"")
                
                    src_path = baseFolder + folderSource.replace("//","") + fileSourceName
                    dst_path = folderTarget + r"appearance\\" + fileSourceName
                    
                    # create parent path for appearance
                    path = os.path.join(folderTarget, 'appearance')
                    if not os.path.exists(path):
                        os.mkdir(path)
                    shutil.copy((r'%s' %src_path), (r'%s' %dst_path))
        
        end=time.time()
        timestamp = datetime.now()
        print("\n[" +timestamp.strftime("%d/%b/%Y @ %H:%M:%S")+ "]", "Blender scene successfully exported to CityJSON at '"+str(self.filepath)+"'.")
        # print("\nBlender scene successfully exported to CityJSON at '"+str(self.filepath)+"'.")
        print("\nTotal exporting time: ", round(end-start, 2), "s")
        
        return{'FINISHED'}       
