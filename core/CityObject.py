import bpy
import numpy
from .Mesh import Mesh
from.Material import Material

class ImportCityObject:

    def __init__(self, object, vertices, objID, textureSetting, rawObjectData, filepath):
        # entire data of the object
        self.object = object
        # the object's mesh
        self.mesh = []
        # list of all vertices
        self.vertices = vertices
        # name/id of the object
        self.objectID = objID
        # Import-setting which lets the user choose if textures present in the CityJSON should be imported
        # True - import textures
        # False - do not import textures
        self.textureSetting = textureSetting
        # materials of the object which encode the objects face semantics
        self.materials = []
        # type of the given object e.g. "Building" or "Bridge" etc.
        self.objectType = self.object['type']
        # entire Data of the file
        self.rawObjectData = rawObjectData
        # File to be imported
        self.filepath = filepath

    def createMesh(self, object, vertices, oid):
        # create the objects mesh and store the data
        mesh = Mesh(object,vertices,oid)
        self.mesh = mesh.execute()

    def createObject(self, mesh):
        # create a new object with the stored mesh
        newObj = bpy.data.objects.new(self.objectID, mesh)
        # create a custom property of the object to save its type
        newObj['cityJSONType'] = self.objectType
        # get the collection with the title "Collection"
        collection = bpy.data.collections.get("Collection")
        # add the new object to the collection
        collection.objects.link(newObj)
        return newObj

    def createMaterials(self, newObject):
        for geom in self.object['geometry']:
            if geom['type'] == 'Solid':
                # surfaceIndex --> the index in the "values"-array, which is the index of the surface
                # surfaceValue --> the value of the surface, wich is a link to an entry in the "surfaces"-array
                for surfaceIndex, surfaceValue in enumerate(geom['semantics']['values'][0]):
                    material = Material(geom['semantics']['surfaces'][surfaceValue]['type'], newObject, self.objectID, self.textureSetting, self.objectType, surfaceIndex, surfaceValue, self.rawObjectData, self.filepath, geom )
                    material.execute()
                    # add a created material to the array of all of the objects materials
                    self.materials.append(material) 
    
    def uvMapping(self, object, data, geom):

        # list of all themes used in the object
        themeNames = list(geom['texture'].keys())
        # name of the first theme, as this is the default for now
        themeName = themeNames[0]

        # uv coordinates from json file
        uv_coords = data['appearance']['vertices-texture']
        # all data from the json file
        mesh_data = object.data
        # create a new uv layer
        # this uv-unwraps all faces even if they don't have a texture (is irrelevent though)
        uv_layer = mesh_data.uv_layers.new()
        # set the new uv layer as the active layer
        mesh_data.uv_layers.active = uv_layer

        # iterate through faces
        for face_index, face in enumerate(geom['texture'][themeName]['values'][0]):
            # if the face has a texture (texture reference is not none)
            if face != [[None]]:
                # get the polygon/face from the newly created mesh
                poly = mesh_data.polygons[face_index]
                # iterate through the mesh-loops of the polygon/face
                for vert_idx, loop_idx in enumerate(poly.loop_indices):
                    # get the index of the uv that belongs to the vertex of the face
                    # this is mapped using the values in the geom['texture'][theme_name]['values'], where the value at index 0 is the
                    # index of the cooresponding texture-appearance, which means that the index of the vertex has to be increased by 1
                    texture_map_value = face[0][vert_idx+1]
                    # set UVs of the uv-layer using the texture_map_value as index for the list in the json data
                    uv_layer.data[loop_idx].uv = (uv_coords[texture_map_value][0],uv_coords[texture_map_value][1])
            
            # if there is no texture --> do nothing  
            else:
                pass


    def execute(self):
        self.createMesh(self.object, self.vertices, self.objectID)
        newObject = self.createObject(self.mesh)
        self.createMaterials(newObject)
        try:
            # UV Mapping of the textures
            self.uvMapping(newObject, self.rawObjectData, self.object['geometry'][0])
        except:
            print("UV Mapping was not possible because the CityJSON file does not contain appearances!")

class ExportCityObject:
    def __init__(self, object, lastVertexIndex, jsonExport, textureSetting, textureReferenceList):
        self.object = object
        self.vertices = []
        self.objID = self.object.name
        self.objType = self.object['cityJSONType']
        self.maxValue = ""
        self.offsetArray = [bpy.context.scene.world['X_Origin'],bpy.context.scene.world['Y_Origin'],bpy.context.scene.world['Z_Origin']]
        self.objGeoExtent = []
        self.json = {}
        self.geometry = []
        self.lastVertexIndex = lastVertexIndex
        self.semanticValues = []
        self.scalefactor = 0.001
        self.jsonExport = jsonExport
        self.textureValues = []
        self.textureSetting = textureSetting
        self.counter = 0
        self.textureReferenceList = textureReferenceList


    def getVertices(self):
        vertexArray = []
        vertices = self.object.data.vertices
        for vertex in vertices:
            vertexCoordinates = vertex.co
            vertexJSON = []
            vertexJSON.append(vertexCoordinates[0])
            vertexJSON.append(vertexCoordinates[1])
            vertexJSON.append(vertexCoordinates[2])
            vertexArray.append(vertexJSON)
        self.vertices = vertexArray

    def getObjectExtend(self):
        objGeoExtend = []
        vertices = numpy.asarray(self.vertices)
        maxValue = vertices.max(axis=0, keepdims=True)[0]
        maxValue = maxValue+self.offsetArray
        minValue = vertices.min(axis=0, keepdims=True)[0]
        minValue = minValue+self.offsetArray
        for i in minValue:
            objGeoExtend.append(round(i,3))
        for i in maxValue:
            objGeoExtend.append(round(i,3))
        self.objGeoExtent = objGeoExtend

    def getBoundaries(self):
        # get the mesh by name
        mesh = bpy.data.meshes[self.objID]
        boundaries = []
        # iterate through polygons
        for poly in mesh.polygons:
            loop = []
            # iterate through loops inside polygons
            for loop_index in poly.loop_indices:
                vertexIndex = mesh.loops[loop_index].vertex_index
                vertexValue = []
                vertexValue.append(mesh.vertices[vertexIndex].co[0])
                vertexValue.append(mesh.vertices[vertexIndex].co[1])
                vertexValue.append(mesh.vertices[vertexIndex].co[2])
                exportIndex = self.vertices.index(vertexValue)
                loop.append(exportIndex+self.lastVertexIndex)
            boundaries.append([loop])
        maxVertex = max(max([max(i) for i in boundaries]))
        self.lastVertexIndex = maxVertex
        self.geometry = [{
            "type": "Solid",
            "boundaries" : [boundaries]
        }]

    def getSemantics(self):
        mesh = bpy.data.meshes[self.objID]
        self.semanticValues = []
        self.semanticSurfaces =[]
        # iterate through polygons
        for polyIndex, poly  in enumerate(mesh.polygons):
            # semantic: material of the surface which is also contains the semantic information regarding the surface type
            semantic = poly.material_index
            self.semanticValues.append(semantic)
            semanticSurface = mesh.materials[semantic]['CJEOtype']
            self.semanticSurfaces.append({"type": semanticSurface})
            if self.textureSetting:
                # extract uv mapping
                self.getTextureMapping(mesh, poly, semantic, polyIndex)
    
    def getTextureMapping(self, mesh, poly, semantic, polyIndex):
        #check if face has texture
        if len(mesh.materials[semantic].node_tree.nodes) > 2:
            print(str(polyIndex) + " has texture!")
            #face_material = semantic - self.counter

            # index of texture in appearances section of CityJSON
            # name of the image of the material
            faceMaterial = mesh.materials[semantic].node_tree.nodes['Image Texture'].image.name
            textureIndex =  self.textureReferenceList.index(faceMaterial)

            # number of loops in the polygon (is equal to vertices)
            loopTotal = poly.loop_total
            uv_layer = mesh.uv_layers[0].data
            uvList = self.jsonExport['appearance']['vertices-texture']
            #self.textureValues.append([[face_material]])
            self.textureValues.append([[textureIndex]])

            for loop_index in range(poly.loop_start, poly.loop_start + loopTotal):
                uv = uv_layer[loop_index].uv
                u = uv[0]
                v = uv[1]
                vertices_textureJSON = [round(u,7),
                                        round(v,7)]
                uv_index = uvList.index(vertices_textureJSON)
                self.textureValues[polyIndex][0].append(uv_index) 
        else:
            print(str(polyIndex) + " does NOT have texture!")
            self.textureValues.append([[None]])
            self.counter =+ 1

    def createJSON(self):
        self.json = {self.objID : {"geographicalExtent" : self.objGeoExtent}}
        self.json[self.objID].update({"type": self.objType})
        self.geometry[0].update({"semantics" : {"values" : [self.semanticValues],"surfaces" : self.semanticSurfaces}})
        if self.textureSetting: 
            self.geometry[0].update({"texture" : {"default" : { "values" : [self.textureValues] }}})
        self.json[self.objID].update({"geometry" : self.geometry})
        
    def execute(self):
        self.getVertices()
        self.getObjectExtend()
        self.getBoundaries()
        self.getSemantics()
        self.createJSON()
        