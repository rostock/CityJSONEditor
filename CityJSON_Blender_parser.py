bl_info = {
    "name": "Import CityJSON files",
    "author": "Konstantinos Mastorakis",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "File > Import > CityJSON (.json)",
    "description": "Visualize 3D City Models encoded in CityJSON format",
    "warning": "",
    "wiki_url": "",
    "category": "Import-Export",
}


import bpy
import json


def read_some_data(context, filepath, use_some_setting):
    print("Importing CityJSON file...")
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=True)
    #Open CityJSON file
    with open(filepath) as json_file:
        data = json.load(json_file)
        vertices=list()    
        #Checking if coordinates need to be transformed and transforming if necessary 
        if 'transform' not in data:
            for vertex in data['vertices']:
                vertices.append(tuple(vertex))
        else:
            trans_param = data['transform']
            #Transforming coords to actual real world coords
            for vertex in data['vertices']:
                x=vertex[0]*trans_param['scale'][0]+trans_param['translate'][0]
                y=vertex[1]*trans_param['scale'][1]+trans_param['translate'][1]
                z=vertex[2]*trans_param['scale'][2]+trans_param['translate'][2]
                vertices.append((x,y,z))
        #Parsing the boundary data of every object
        for theid in data['CityObjects']:
            # If a parent is found all children are parsed and visualized. 
            if 'children' in data['CityObjects'][theid]:
                #Storing parent's id
                parents_name = theid
                children_id = data['CityObjects'][theid]['children']
                for child in children_id:
                    for geom in data['CityObjects'][child]['geometry']:
                        bound=list()
                        #Checking how nested the geometry is i.e what kind of 3D geometry it contains
                        if((geom['type']=='MultiSurface') or (geom['type'] == 'CompositeSurface')):
                            for face in geom['boundaries']:
                                for verts in face:
                                    bound.append(tuple(verts))
                        elif (geom['type']=='Solid'):
                            for shell in geom['boundaries']:
                                for face in shell:
                                    for verts in face:
                                        bound.append(tuple(verts))                                    
                        elif (geom['type']=='MultiSolid'):
                            for solid in geom['boundaries']:
                                for shell in solid:
                                    for face in shell:
                                        for verts in face:
                                            bound.append(tuple(verts))
                    #Visualization part
                    mesh_data = bpy.data.meshes.new("mesh")
                    mesh_data.from_pydata(vertices, [], bound)
                    mesh_data.update()
                    obj = bpy.data.objects.new(child, mesh_data)
                    scene = bpy.context.scene
                    scene.collection.objects.link(obj)
                    #bpy.data.objects[child].select_set(True)
                    #Assigning attributes to chilren objects
                    if 'attributes' in data['CityObjects'][child]: 
                        for attribute in data['CityObjects'][child]['attributes']:
                            obj[attribute]=data['CityObjects'][child]['attributes'][attribute]        
                #Creating empty meshes of the parents to join all the children    
                mesh_data = bpy.data.meshes.new("empty")
                obj = bpy.data.objects.new(parents_name, mesh_data)
                scene = bpy.context.scene
                scene.collection.objects.link(obj)
                #bpy.data.objects[parents_name].select_set(True)
                #Assigning attributes to parent objects
                if 'attributes' in data['CityObjects'][theid]:
                    for attribute in data['CityObjects'][theid]['attributes']:
                            obj[attribute]=data['CityObjects'][theid]['attributes'][attribute]
                #Creating parent-child relationship
                objects = bpy.data.objects
                parent_obj = objects[parents_name]
                for child in children_id:
                    child_obj = objects[child]
                    child_obj.parent = parent_obj
            #Otherwise it searches for "orphan buildings" that have no parents and are not parents as well                                
            elif (('children' not in data['CityObjects'][theid]) and ('parents' not in data['CityObjects'][theid])):
                name = theid            
                for geom in data['CityObjects'][theid]['geometry']:
                    bound=list()
                    #Checking how nested the geometry is i.e what kind of 3D geometry it contains
                    if((geom['type']=='MultiSurface') or (geom['type'] == 'CompositeSurface')):
                        for face in geom['boundaries']:
                            for verts in face:
                                bound.append(tuple(verts))
                    elif (geom['type']=='Solid'):
                        for shell in geom['boundaries']:
                            for face in shell:
                                for verts in face:
                                    bound.append(tuple(verts))
                    elif (geom['type']=='MultiSolid'):
                        for solid in geom['boundaries']:
                            for shell in solid:
                                for face in shell:
                                    for verts in face:
                                        bound.append(tuple(verts))
                #Visualization part
                mesh_data = bpy.data.meshes.new("cube_mesh_data")
                mesh_data.from_pydata(vertices, [], bound)
                mesh_data.update()
                obj = bpy.data.objects.new(name, mesh_data)
                scene = bpy.context.scene
                scene.collection.objects.link(obj)
                #Assigning attributes to orphan objects
                if 'attributes' in data['CityObjects'][theid]:
                    for attribute in data['CityObjects'][theid]['attributes']:
                            obj[attribute]=data['CityObjects'][theid]['attributes'][attribute]
        print("CityJSON file successfully imported.")
    return {'FINISHED'}
# ImportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator


class ImportCityJSON(Operator, ImportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "import_test.some_data"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Import Some Data"

    # ImportHelper mixin class uses this
    filename_ext = ".json"

    filter_glob: StringProperty(
        default="*.json",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    use_setting: BoolProperty(
        name="Example Boolean",
        description="Example Tooltip",
        default=True,
    )

    type: EnumProperty(
        name="Example Enum",
        description="Choose between two items",
        items=(
            ('OPT_A', "First Option", "Description one"),
            ('OPT_B', "Second Option", "Description two"),
        ),
        default='OPT_A',
    )

    def execute(self, context):
        return read_some_data(context, self.filepath, self.use_setting)


# Only needed if you want to add into a dynamic menu
def menu_func_import(self, context):
    self.layout.operator(ImportCityJSON.bl_idname, text="CityJSON (.json)")


def register():
    bpy.utils.register_class(ImportCityJSON)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


def unregister():
    bpy.utils.unregister_class(ImportCityJSON)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)

if __name__ == "__main__":
    register()
    bpy.ops.import_test.some_data('INVOKE_DEFAULT')
