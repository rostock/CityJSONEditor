import bpy
import json

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)

#Open CityJSON file
with open('/home/konstantinos/Thesis/cityjson_datasets/vienna.json') as json_file: 
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
            #bpy.data.objects[name].select_set(True)
            #Assigning attributes to orphan objects
            if 'attributes' in data['CityObjects'][theid]:
                for attribute in data['CityObjects'][theid]['attributes']:
                        obj[attribute]=data['CityObjects'][theid]['attributes'][attribute]
        
        
    #bpy.ops.object.light_add(type='SUN', location=(91231.52200000001, 435866.023, 55.085))
    #bpy.ops.object.camera_add(enter_editmode=False, align='VIEW', location=(91531.52200000001, 435866.023, 15.085), rotation=(0.814687, 0.008346, 1.16357))

