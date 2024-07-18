import json
import bpy
from .CityObject import ImportCityObject, ExportCityObject
import time

class ImportProcess:

    def __init__(self, filepath, textureSetting):
        # File to be imported
        self.filepath = filepath
        # Content of imported file
        self.data = []
        # Vertices of imported files geometry for further use in blenders objects
        self.vertices = []
        # Translation parameters / world origin
        self.worldOrigin = []
        # Scale parameters
        self.scaleParam = []
        # Import-setting which lets the user choose if textures present in the CityJSON should be imported
        # True - import textures
        # False - do not import textures
        self.textureSetting = textureSetting
        # vertices before scaling
        self.unScaledVertices = []

    def load_data(self):
        # load contents of file 
        with open(self.filepath) as json_file:
            self.data = json.load(json_file)

    def getTransformationParameters(self):

        try: 
            # check if the transform property exists
            transformProperty = self.data['transform']

        except:
            # if it does not exist, create it
            print('The files does not have the transform property, therefore it will now be created and applied to all vertices!')
            # calc trsanlate matrix
            bboxXmin = self.data['metadata']['geographicalExtent'][0]
            bboxYmin = self.data['metadata']['geographicalExtent'][1]
            bboxZmin = min([self.data['metadata']['geographicalExtent'][2], self.data['metadata']['geographicalExtent'][5]])
            translate = [bboxXmin, bboxYmin, bboxZmin]
            self.worldOrigin = translate 
            # scale factor is 1 since the values are in meters (with decimals)
            scale = [1, 1, 1]
            self.scaleParam = scale
            
            # apply transform values to all vertices
            for vertex in self.data['vertices']:
                x = vertex[0]-bboxXmin
                y = vertex[1]-bboxYmin
                z = vertex[2]-bboxZmin
                self.unScaledVertices.append([x,y,z])


        else:
            # if it exists, use it
            print('The file has the transform property!')
            # extract coordinates of CityJSON world origin / real world offset parameters
            for param in self.data['transform']['translate']:
                self.worldOrigin.append(param)
            # extract scale factor for coordinate values of vertices
            for param in self.data['transform']['scale']:
                self.scaleParam.append(param)
            # no need for processing of the vertices so they are just send along "as is "
            for vertex in self.data['vertices']:
                x = vertex[0]
                y = vertex[1]
                z = vertex[2]
                self.unScaledVertices.append([x,y,z])           
            

    def scaleVertexCoordinates(self):
        # apply scale factor to vertices
        for vertex in self.unScaledVertices:
            x = round(vertex[0]*self.scaleParam[0],3)
            y = round(vertex[1]*self.scaleParam[1],3)
            z = round(vertex[2]*self.scaleParam[2],3)
            self.vertices.append([x,y,z])

    def checkImport(self):
        # checks if this is the first imported CityJSON file
        # if the custom property "X_Origin" exists there has already been an import
        try: 
            test = bpy.context.scene.world['X_Origin']    
        except: 
            print('This is the first file!')
            return True
        else: 
            print('This is NOT the first file!')
            # load the x-origin set in the project
            establishedX = bpy.context.scene.world['X_Origin']
            # load the x-origin of the import file
            currentX = self.worldOrigin[0]
            # calculate the difference
            deltaX = currentX - establishedX
            # apply the difference to all coordinates
            for vertex in self.vertices:
                vertex[0] = vertex[0] + deltaX
            
            # load the y-origin set in the project
            establishedY = bpy.context.scene.world['Y_Origin']
            # load the y-origin of the import file
            currentY = self.worldOrigin[1]
            # calculate the difference
            deltaY = currentY - establishedY
            # apply the difference to all coordinates
            for vertex in self.vertices:
                vertex[1] = vertex[1] + deltaY

            # load the z-origin set in the project
            establishedZ = bpy.context.scene.world['Z_Origin']
            # load the z-origin of the import file
            currentZ = self.worldOrigin[2]
            # calculate the difference
            deltaZ = currentZ - establishedZ
            # apply the difference to all coordinates
            for vertex in self.vertices:
                vertex[2] = vertex[2] + deltaZ
            return False

    def createWorldProperties(self):
        bpy.context.scene.world['CRS'] = self.data['metadata']['referenceSystem']
        bpy.context.scene.world['X_Origin'] = self.worldOrigin[0]
        bpy.context.scene.world['Y_Origin'] = self.worldOrigin[1]
        bpy.context.scene.world['Z_Origin'] = self.worldOrigin[2]
        print("World parameters have been set!")

    def createCityObjects(self):
        # create the CityObjects with coresponding meshesS
        cityobjects = self.data['CityObjects'] #variable is a dict
        for objID, object in cityobjects.items():
            print('Creating object: '+ objID)
            cityobj = ImportCityObject(object, self.vertices, objID, self.textureSetting, self.data, self.filepath)
            cityobj.execute()
        print('All CityObjects have been created!')

    def execute(self):
        time_start = time.time()
        bpy.ops.wm.console_toggle()
        print('##########################')
        print('### STARTING IMPORT... ###')
        print('##########################')
        
        # clean up unused objects
        bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=False, do_recursive=True)

        self.load_data()
        self.getTransformationParameters()
        self.scaleVertexCoordinates()
        status = self.checkImport()
        # only set the world parameters if the file is the first CityJSON file to be imported
        if status is True:
            self.createWorldProperties()                         
        self.createCityObjects()

        print('########################')
        print('### IMPORT FINISHED! ###')
        print('########################')
        print("Time needed: %.4f sec" % (time.time() - time_start))
        return {'FINISHED'}