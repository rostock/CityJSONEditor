import bpy
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
    def __init__(self, object):
        self.object = object
        self.vertices = []

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
        

    def execute(self):
        self.getVertices()