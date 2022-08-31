import bpy

class CityMaterial:

    def __init__(self,name):
        self.material = self.createMaterial(name)
        self.name = self.material.name #hier benötigen wir den richtigen Namen, also inklusive *.ooX

    def createMaterial(self, name):
        return bpy.data.materials.new(name=name)
    
    """
    def addCustomProperty(self, customLabel, value):
        obj = self.material
        if customLabel not in obj:
            obj[customLabel] = value
            bpy.types.Material.type = bpy.props.StringProperty(name=customLabel, default="default value")
            # bpy.data.materials[1].CityJSONType = "huhu"
            self.material.type = value
    
    """
    def addCustomStringProperty(self, customLabel, value):
        if not hasattr(self.material, customLabel):
            setattr(bpy.types.Material, customLabel, bpy.props.StringProperty(name=customLabel, default="blabla"))
        setattr(self.material, customLabel, value)
            

    def setColor(self, rgb):
        self.material.diffuse_color = (rgb[0], rgb[1], rgb[2], 1)
    
    """
    # set color of the material
    def setColor(self,surface_type):
        # switch material to use nodes
        self.material.use_nodes = True

        # get node which has the color setting
        principled_BSDF = self.material.node_tree.nodes.get('Principled BSDF')

        # if the surface type is in the list --> set material color accordingly
        if surface_type in self.material_colors:
            principled_BSDF.inputs['Base Color'].default_value = self.material_colors[surface_type]
    """
        

    def addMaterialToObj(self, obj):
        obj.data.materials.append(self.material)

    def addMaterialToFace(self, obj):
        obj.active_material_index = self.getIndex(obj)
        bpy.ops.object.material_slot_assign()      

    def setTexture(self, data, texture_index, filepath):

        # setup image

        # path of the imported file (json)
        basepath = filepath
        # extraction of the path without the name of the json
        basepath_without_basename = basepath.rsplit("\\",1)[0]
        # appearance section of the CityJSON file
        appearances = data["appearance"]
        # image name and relative path
        image_path_raw = appearances['textures'][texture_index]['image']
        image_path_with_backslash = image_path_raw.replace("/","\\")
        # construction of absolute image path 
        image_path = str(basepath_without_basename)+"\\"+ str(image_path_with_backslash)
        print("image_path: "+ str(image_path))
        # loading of image
        image  = bpy.data.images.load(str(image_path))
        # check, if data has been loaded into the variable
        print(str(image.has_data))
        
        
        self.use_nodes = True

        # setup node tree

        material_output = self.node_tree.nodes.get('Material Output')
        principled_BSDF = self.node_tree.nodes.get('Principled BSDF')

        texture_node = self.node_tree.nodes.new('ShaderNodeTexImage')
        texture_node.image = image

        self.node_tree.links.new(texture_node.outputs[0], principled_BSDF.inputs[0]) 

        

    def uvMapping(self,uv_parameters):
        pass

    def getIndex(self, obj):
        return obj.material_slots.find(self.name)
            
