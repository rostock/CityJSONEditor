import bpy 
import bmesh
from .FeatureTypes import (FeatureTypes)

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
        # create the material with a fitting name
        material = bpy.data.materials.new(name=str(self.objectID)+"_"+str(self.type))
        # create the custom parameter of the objects type
        material['CJEOtype'] = self.type
        # add the material to the current object
        self.currentObject.data.materials.append(material)
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
            
            #print("image texture: "+str(image_path_raw)+" was used!")
        
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

    # Methods for use in edit-mode context menu

    def addMaterialToFace(self, index, faceIndex):
        #materialSlot = bpy.context.object.material_slots.find(str(self.objectID)+"_"+str(self.type))
        #bpy.ops.object.mode_set(mode='OBJECT')
        #bpy.context.object.data.polygons[faceIndex].select = True
        me = bpy.context.object.data
        bm = bmesh.from_edit_mesh(me)
        bm.faces.ensure_lookup_table()
        bm.faces[faceIndex].select = True
        bmesh.update_edit_mesh(me)
        #bpy.ops.object.mode_set(mode='EDIT')
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