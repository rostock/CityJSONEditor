import json
import bpy
from .CityObject import ExportCityObject

class ExportProcess:
    
    def __init__(self, filepath):
        self.filepath = filepath
        self.jsonExport = None

    def createJSONStruct(self):
        emptyJSON = {
            "type": "CityJSON",
            "version": "1.0",
            "CityObjects": {},
            "transform":{
                "scale":[
                    0.001, 
                    0.001,
                    0.001
                    ],
                "translate":[]
            },
            "vertices": None,
            "appearance":{
                "textures":[],
                "vertices-texture":[]
            },
            "metadata": {}
        }
        self.jsonExport = emptyJSON
    
    def getMetadata(self):
        self.jsonExport["metadata"] = bpy.context.scene.world['CRS']

    def getTransform(self):
        self.jsonExport["transform"]["translate"].append(bpy.context.scene.world['X_Origin'])
        self.jsonExport["transform"]["translate"].append(bpy.context.scene.world['Y_Origin'])
        self.jsonExport["transform"]["translate"].append(bpy.context.scene.world['Z_Origin'])

    def createCityObject(self):
        vertexArray = []
        blendObjects = bpy.data.objects
        for object in blendObjects:
            cityobj = ExportCityObject(object)
            cityobj.execute()
            for i in cityobj.vertices:
                vertexArray.append(i)
        self.jsonExport['vertices'] = vertexArray     

    def getTextures(self):
        allTextures = bpy.data.textures.data.images
        for texture in allTextures:
            imageType = texture.file_format
            if imageType == 'TARGA':
                pass
            else:
                basename = texture.name
                imageName = "appearance/" + basename
                textureJSON = {
                    "type": imageType,
                    "image": imageName,
                    "wrapMode":"wrap",
                    "textureType":"specific",
                    "borderColor":[
                    0.0,
                    0.0,
                    0.0,
                    1.0
                    ]
                }
                self.jsonExport['appearance']['textures'].append(textureJSON)

    def getVerticesTexture(self):
        meshes = bpy.data.meshes
        for mesh in meshes:
            uvLayers = mesh.uv_layers
            for uvLayer in uvLayers:
                UVs = uvLayer.data
                for uv in UVs:
                    uvParameters = uv.uv


    def execute(self):
        self.createJSONStruct()
        self.getMetadata()
        self.getTransform()
        self.createCityObject()
        self.getTextures()
        print(self.jsonExport)