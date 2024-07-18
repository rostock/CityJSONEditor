import json
import bpy
import os
import shutil
from .CityObject import ExportCityObject

class ExportProcess:
    
    def __init__(self, filepath, textureSetting):
        self.filepath = filepath
        self.jsonExport = None
        # True - export textures
        # False - do not export textures
        self.textureSetting = textureSetting
        self.textureReferenceList = []

    def createJSONStruct(self):
        if self.textureSetting: 
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
        else: 
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
                "metadata": {}
            }
        self.jsonExport = emptyJSON
    
    def getMetadata(self):
        self.jsonExport["metadata"].update({"referenceSystem" : str(bpy.context.scene.world['CRS'])})

    def getTransform(self):
        self.jsonExport["transform"]["translate"].append(bpy.context.scene.world['X_Origin'])
        self.jsonExport["transform"]["translate"].append(bpy.context.scene.world['Y_Origin'])
        self.jsonExport["transform"]["translate"].append(bpy.context.scene.world['Z_Origin'])

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
                self.textureReferenceList.append(basename)
                self.exportTextures(texture)

    def getVerticesTexture(self):
        meshes = bpy.data.meshes
       
        for mesh in meshes:
            uv_layer = mesh.uv_layers[0].data
            for polyIndex, poly  in enumerate(mesh.polygons):
                semantic = poly.material_index
                loopTotal = poly.loop_total
                if len(mesh.materials[semantic].node_tree.nodes) > 2:
                    for loop_index in range(poly.loop_start, poly.loop_start + loopTotal):
                        uv = uv_layer[loop_index].uv
                        u = uv[0]
                        v = uv[1]
                        vertices_textureJSON = [round(u,7),
                                                round(v,7)]
                        self.jsonExport['appearance']['vertices-texture'].append(vertices_textureJSON)
                else: 
                    pass

    def createCityObject(self):
        vertexArray = []
        blendObjects = bpy.data.objects
        lastVertexIndex = 0
        for object in blendObjects:
            print("Create Export-Object: "+object.name)
            cityobj = ExportCityObject(object, lastVertexIndex, self.jsonExport, self.textureSetting, self.textureReferenceList)
            cityobj.execute()
            for vertex in cityobj.vertices:
                vertex[0] = round(vertex[0]/0.001)
                vertex[1] = round(vertex[1]/0.001)
                vertex[2] = round(vertex[2]/0.001)
                vertexArray.append(vertex)
            self.jsonExport["CityObjects"].update(cityobj.json)
            lastVertexIndex = cityobj.lastVertexIndex + 1
            print("lastVertexIndex "+str(lastVertexIndex))
        self.jsonExport['vertices'] = vertexArray

    def exportTextures(self, texture):
        fileSourceInfos = texture.filepath.split('\\')
        fileSourceName = fileSourceInfos[ len(fileSourceInfos) - 1 ]
        folderSource = texture.filepath.replace(fileSourceInfos[ len(fileSourceInfos) - 1 ],"")
        
        fileInfosTarget =self.filepath.split('\\')
        folderTarget =self.filepath.replace(fileInfosTarget[ len(fileInfosTarget) - 1 ],"")
        
        src_path = folderSource.replace("//","") + fileSourceName
        dst_path = folderTarget + r"appearance\\" + fileSourceName
        
        # create parent path for appearance
        path = os.path.join(folderTarget, 'appearance')
        if not os.path.exists(path):
            os.mkdir(path)
        shutil.copy((r'%s' %src_path), (r'%s' %dst_path))
    
    def writeData(self):
        with open(self.filepath, 'w', encoding='utf-8') as f:
            filecontent = json.dumps(self.jsonExport)
            f.write(filecontent)

    def execute(self):
        print('##########################')
        print('### STARTING EXPORT... ###')
        print('##########################')

        self.createJSONStruct()
        self.getMetadata()
        self.getTransform()
        if self.textureSetting: 
            self.getTextures()
            self.getVerticesTexture()
        self.createCityObject()
        self.writeData()

        print('########################')
        print('### EXPORT FINISHED! ###')
        print('########################')
        return {'FINISHED'}