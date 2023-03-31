import bpy

class Mesh:

    def __init__(self, object, vertices, oid):
        # entire data of the object
        self.object = object
        # list of all vertices
        self.vertices = vertices
        # list which describes the faces mapped to the vertex indices
        self.vertexMaps = []
        # name/id of the object
        self.name = oid
        

    def extractVertexMapping(self):
        # create and store a list of the vertex mapping (faces)
        for geom in self.object['geometry']:
            if geom['type'] == 'Solid':
                for shell in geom['boundaries']:
                    for face in shell:
                        for side in face:
                            if side:
                                self.vertexMaps.append(side)
    
    def createBlenderMesh(self):
        # vertices used for defining blender meshes
        vertices = []
        # edges defined by vertex indices (not required if faces are made)
        edges = []
        # faces defindes by vertex indides
        faces = []

        vertices = self.vertices
        faces = self.vertexMaps

        # creating a new mesh with the name of the object
        newMesh = bpy.data.meshes.new(self.name)
        # build the mesh from vertices and faces (edges not required)
        newMesh.from_pydata(vertices, edges, faces)
        # return the mesh so it can be handed over to the object  
        return newMesh    
        

    def execute(self):
        self.extractVertexMapping()
        mesh = self.createBlenderMesh()
        return mesh