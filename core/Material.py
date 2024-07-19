import bpy 
import bmesh
from .FeatureTypes import (FeatureTypes)
import time

class Material:

    def __init__(self, type, newObject, objectID, textureSetting, objectType, surfaceIndex, surfaceValue, rawObjectData, filepath, geometry):
        # surface type eg. RoofSurface or WallSurface etc.
        self.type = type
        # data of the current object
        self.currentObject = newObject
        # ID of the current object
        self.objectID = objectID
        # Import-setting which lets the user choose if textures present in the CityJSON should be imported
        # True - import textures
        # False - do not import textures
        self.textureSetting = textureSetting
        # type of the given object e.g. "Building" or "Bridge"
        self.objectType = objectType
        # container for the created material in Blender
        self.material = None
        # the index in the "values"-array, which is the index of the surface
        self.surfaceIndex = surfaceIndex
        # the value of the surface, wich is a link to an entry in the "surfaces"-array
        self.surfaceValue = surfaceValue
        # File to be imported
        self.filepath = filepath
        # appearance section of the CityJSON file
        try:
            self.appearances = rawObjectData["appearance"]
        except:
            pass
        # geometry property of the current object
        self.geometry = geometry

    def createMaterial(self):
        
        """
        # add a new slot for the material in the current object
        # THE NEXT LINE IS THE PERFORMANCE KILLER!
        bpy.ops.object.material_slot_add()        
         # create the material with a fitting name
        material = bpy.data.materials.new(name=str(self.objectID)+"_"+str(self.type))
        # create the custom parameter of the objects type
        material['CJEOtype'] = self.type
        # add the material to the material slot created above        
        bpy.context.object.active_material = material
        self.material = material
        """

        object = bpy.context.object
        # add a new slot for the material in the current object
        object.data.materials.append(None)
        # get the material slots of the object
        material_slots = object.material_slots
        # get the index of the last material slot
        last_material_index = len(material_slots) - 1
        # set material slot as active
        object.active_material_index = last_material_index
        # create the material with a fitting name
        material = bpy.data.materials.new(name=str(self.objectID)+"_"+str(self.type))
        # create the custom parameter of the objects type
        material['CJEOtype'] = self.type
        # add the material to the material slot created above 
        object.active_material = material
        self.material = material
        
    def setTexture(self):
        
        # list of all themes used in the object
        themeNames = list(self.geometry['texture'].keys())
        # name of the first theme, as this is the default for now
        themeName = themeNames[0]
        # stacked array of texture references
        textureEncoding = self.geometry['texture'][themeName]['values'][0][self.surfaceIndex]
        # bare array of texture references
        textureIndex = textureEncoding[0][0]
    
        # setup image
        # check if the current surface has a texture assigned
        if textureIndex != None:
            # extraction of the path without the name of the json
            basepath_without_basename = self.filepath.rsplit("\\",1)[0]
            # image name and relative path
            image_path_raw = self.appearances['textures'][textureIndex]['image']
            image_path_with_backslash = image_path_raw.replace("/","\\")
            # construction of absolute image path 
            image_path = str(basepath_without_basename)+"\\"+ str(image_path_with_backslash)
            #print("image_path: "+ str(image_path))
            # loading of image
            image  = bpy.data.images.load(str(image_path))
            # check, if data has been loaded into the variable
            
            # print(str(image.has_data))

            #use nodes
            self.material.use_nodes = True

            # setup node tree
            # set node to PBSDF
            principled_BSDF = self.material.node_tree.nodes.get('Principled BSDF')
            # create a new texture-node
            texture_node = self.material.node_tree.nodes.new('ShaderNodeTexImage')
            # assign the texture image to the texture-node
            texture_node.image = image
            # link the texture-node to the PBSDF-node
            self.material.node_tree.links.new(texture_node.outputs[0], principled_BSDF.inputs[0])
        
        else: 
            self.setColor()

    def setColor(self):
        ft = FeatureTypes()
        # get the color preset based on the Object-Type and Surface-Type
        rgb = ft.getRGBColor(self.objectType, self.type)
        
        # setup the material to use nodes
        self.material.use_nodes = True

        # get node which has the color setting
        principled_BSDF = self.material.node_tree.nodes.get('Principled BSDF')
        # set the color
        principled_BSDF.inputs['Base Color'].default_value = (rgb[0], rgb[1], rgb[2], 1)

    def assignMaterials(self, surfaceIndex, surfaceValue):
        # assign:
        # the object of ID: "objectID"
        # surface/polygon of index: "surfaceIndex"
        # the objects material of index: "surfaceValue"
        bpy.data.meshes[self.objectID].polygons[surfaceIndex].material_index = surfaceValue   

    # Methods for use in edit-mode context menu and face-normal based calculation

    def addMaterialToFace(self, index, faceIndex):
        me = bpy.context.object.data
        bm = bmesh.from_edit_mesh(me)
        bm.faces.ensure_lookup_table()
        bm.faces[faceIndex].select = True
        bmesh.update_edit_mesh(me)
        bpy.context.object.active_material_index = index
        bpy.ops.object.material_slot_assign()
        bpy.ops.mesh.select_all(action='DESELECT')

    def execute(self):
        self.createMaterial()
        # use the corresponding function for the objects appearance according to the presence of a texture
        if self.textureSetting is True:
            self.setTexture()
        else:
            self.setColor()
        # assign the materials to the individual faces
        self.assignMaterials(self.surfaceIndex, self.surfaceValue)
        