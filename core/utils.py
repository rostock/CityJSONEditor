"""Blender CityJSON plugin utils module

This modules provides utitily methods for the importing/exporting
processing of CityJSON files
"""

import bpy,idprop

########## Importer functions ##########

def remove_scene_objects():
    """Clears the scenes of any objects and removes world's custom properties 
    and collections"""
    #Delete world custom properties
    if bpy.context.scene.world.keys():
        for custom_property in bpy.context.scene.world.keys():
            del bpy.context.scene.world[custom_property]
    # Deleting previous objects every time a new CityJSON file is imported
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    # Deleting previously existing collections
    for collection in bpy.data.collections:
        bpy.data.collections.remove(collection)

def clean_list(values):
    """Creates a list of non list in case lists nested in lists exist"""

    while isinstance(values[0], list):
        values = values[0]

    return values

def assign_properties(obj, props, prefix=[]):
    """Assigns the custom properties to obj based on the props"""

    for prop, value in props.items():

        if prop in ["geometry", "children", "parents"]:
            continue

        if isinstance(value, dict):
            obj = assign_properties(obj, value, prefix + [prop])

        else:
            obj[".".join(prefix + [prop])] = value

    return obj

def coord_translate_axis_origin(vertices):
    """Translates the vertices to the origin (0, 0, 0)"""
    #Finding minimum value of x,y,z
    minx = min(i[0] for i in vertices)
    miny = min(i[1] for i in vertices)
    minz = min(i[2] for i in vertices)

    #Calculating new coordinates
    translated_x = [i[0]-minx for i in vertices]
    translated_y = [i[1]-miny for i in vertices]
    translated_z = [i[2]-minz for i in vertices]

    return (tuple(zip(translated_x, translated_y, translated_z)),
            minx,
            miny,
            minz)

def original_coordinates(vertices, minx, miny, minz):
    """Translates the vertices from origin to original"""
    #Calculating original coordinates
    original_x = [i[0]+minx for i in vertices]
    original_y = [i[1]+miny for i in vertices]
    original_z = [i[2]+minz for i in vertices]

    return tuple(zip(original_x, original_y, original_z))

def clean_buffer(vertices, bounds):
    """Cleans the vertices index from unused vertices3"""

    new_bounds = list()
    new_vertices = list()
    i = 0
    for bound in bounds:
        new_bound = list()

        for vertex_id in bound:
            new_vertices.append(vertices[vertex_id])
            new_bound.append(i)
            i = i + 1

        new_bounds.append(tuple(new_bound))

    return new_vertices, new_bounds

########## Exporter functions ##########

def store_semantics (minimal_json,city_object,index,original_objects_name,face):
    """Stores the semantics from the objects materials"""
    if city_object.data.materials:
        # minimal_json["CityObjects"][original_objects_name]['geometry'][index].update({'semantics':{}})
        minimal_json["CityObjects"][original_objects_name]["geometry"][index]['semantics'].setdefault('values',[[]])
        minimal_json["CityObjects"][original_objects_name]["geometry"][index]['semantics']['values'][0].append(face.index)
        surface_semantic = city_object.data.materials[face.material_index].values()
        minimal_json["CityObjects"][original_objects_name]["geometry"][index]['semantics'].setdefault('surfaces',[]).append({'type':surface_semantic[0]})

    return None

def bbox(objects):

    """Calculates the bounding box of the objects given"""
    #Initialization 
    obj = objects[0]
    bbox = obj.bound_box
    xmax = bbox[0][0]
    ymax = bbox[0][1]
    zmax = bbox[0][2]
    xmin = xmax
    ymin = ymax
    zmin = zmax
    world_max_extent = [xmax, ymax, zmax]
    world_min_extent = [xmin, ymin, zmin]

    #Calculating bbox of the whole scene
    for obj in objects:
        bbox = obj.bound_box

        xmax = bbox[0][0]
        ymax = bbox[0][1]
        zmax = bbox[0][2]

        xmin = xmax
        ymin = ymax
        zmin = zmax
    
        for i in range(len(bbox)):
            if bbox[i][0] > xmax:
                xmax = bbox[i][0]
            if bbox[i][0] < xmin:
                xmin = bbox[i][0]
                
            if bbox[i][1] > ymax:
                ymax = bbox[i][1]
            if bbox[i][1] < ymin:
                ymin = bbox[i][1]
                
            if bbox[i][2] > zmax:
                zmax = bbox[i][2]
            if bbox[i][2] < zmin:
                zmin = bbox[i][2]
            
        object_max_extent = [xmax, ymax, zmax]
        object_min_extent = [xmin, ymin, zmin]
        
        if object_max_extent[0]>world_max_extent[0]:
            world_max_extent[0]=object_max_extent[0]
        if object_max_extent[1]>world_max_extent[1]:
            world_max_extent[1]=object_max_extent[1]
        if object_max_extent[2]>world_max_extent[2]:
            world_max_extent[2]=object_max_extent[2]
        if object_min_extent[0]<world_min_extent[0]:
            world_min_extent[0]=object_min_extent[0]
        if object_min_extent[1]<world_min_extent[1]:
            world_min_extent[1]=object_min_extent[1]
        if object_min_extent[2]<world_min_extent[2]:
            world_min_extent[2]=object_min_extent[2]
    
    #Translating back to original
    world_min_extent[0]-=bpy.context.scene.world["Axis_Origin_X_translation"]
    world_min_extent[1]-=bpy.context.scene.world["Axis_Origin_Y_translation"]
    world_min_extent[2]-=bpy.context.scene.world["Axis_Origin_Z_translation"]

    world_max_extent[0]-=bpy.context.scene.world["Axis_Origin_X_translation"]
    world_max_extent[1]-=bpy.context.scene.world["Axis_Origin_Y_translation"]
    world_max_extent[2]-=bpy.context.scene.world["Axis_Origin_Z_translation"]

    return world_min_extent,world_max_extent

def write_vertices_to_CityJSON(city_object,minimal_json,vertices,progress_max):
    """ Writing vertices to minimal_json after translation to the original position. """
    # Initialize progress status
    progress = 0
    for vert in vertices:
        coord = city_object.matrix_world @ vert
        if 'transformed' in bpy.context.scene.world:
            #First translate back to the original CRS coordinates 
            x,y,z = coord[0]-bpy.context.scene.world["Axis_Origin_X_translation"],coord[1]\
                    -bpy.context.scene.world["Axis_Origin_Y_translation"],coord[2]\
                    -bpy.context.scene.world["Axis_Origin_Z_translation"]
            #Second transform the original CRS coordinates based on the transform parameters of the original CityJSON file
            x = round((x - bpy.context.scene.world['transform.X_translate'])/ bpy.context.scene.world['transform.X_scale'])
            y = round((y - bpy.context.scene.world['transform.Y_translate'])/ bpy.context.scene.world['transform.Y_scale'])
            z = round((z - bpy.context.scene.world['transform.Z_translate'])/ bpy.context.scene.world['transform.Z_scale'])
            minimal_json['vertices'].append([x,y,z])
            progress +=1
            print("Appending vertices into CityJSON: {percent}% completed".format(percent=round(progress * 100 / progress_max, 1)),end="\r")
        else:
            minimal_json['vertices'].append([coord[0]-bpy.context.scene.world["Axis_Origin_X_translation"],\
                                             coord[1]-bpy.context.scene.world["Axis_Origin_Y_translation"],\
                                             coord[2]-bpy.context.scene.world["Axis_Origin_Z_translation"]])
            progress +=1
            print("Appending vertices into CityJSON: {percent}% completed".format(percent=round(progress * 100 / progress_max, 1)),end="\r")
    
    return None

def export_transformation_parameters(minimal_json):

    if 'transformed' in bpy.context.scene.world:
        print ("\nExporting transform parameters...")
        minimal_json.update({'transform':{}})
        minimal_json['transform'].update({'scale':[]})
        minimal_json['transform'].update({'translate':[]})

        minimal_json['transform']['scale'].append(bpy.context.scene.world['transform.X_scale'])
        minimal_json['transform']['scale'].append(bpy.context.scene.world['transform.Y_scale'])
        minimal_json['transform']['scale'].append(bpy.context.scene.world['transform.Z_scale'])

        minimal_json['transform']['translate'].append(bpy.context.scene.world['transform.X_translate'])
        minimal_json['transform']['translate'].append(bpy.context.scene.world['transform.Y_translate'])
        minimal_json['transform']['translate'].append(bpy.context.scene.world['transform.Z_translate'])
    
    return None

def export_metadata(minimal_json):
    print ("Exporting metadata...")
    #Check if model's reference system exists
    if 'CRS' in bpy.context.scene.world:
        minimal_json['metadata'].update({'referenceSystem':bpy.context.scene.world["CRS"]})
    minimal_json['metadata'].update({'geographicalExtent':[]})
    # Calculation of the bounding box of the whole area to get the geographic extents
    minim,maxim = bbox(bpy.data.objects)

    #Updating the metadata tag
    print ("Appending geographical extent...")
    for extent_coord in minim:
        minimal_json['metadata']['geographicalExtent'].append(extent_coord) 
    for extent_coord in maxim:
        minimal_json['metadata']['geographicalExtent'].append(round(extent_coord,3)) 

    return None

def export_parent_child(minimal_json):
    """ Store parents/children tags into CityJSON file
        Going again through the loop because there is the case that the object whose tag is attempted to be updated
        is not yet created if this code is run iin the above loop.
        TODO this can be done more efficiently. To be improved..."""
    print("\nSaving parents-children relations...")
    for city_object in bpy.data.objects:
        #Parent and child relationships are stored in the empty objects carrying also all the attributes
        if city_object.parent and city_object.type =="EMPTY":
            parents_id = city_object.parent.name
            #Create children node/tag below the parent's ID and assign to it the children's name
            minimal_json["CityObjects"][parents_id].setdefault('children',[])
            minimal_json["CityObjects"][parents_id]['children'].append(city_object.name)
            #Create the "parents" tag below the children's ID and assign to it the parent's name
            minimal_json["CityObjects"][city_object.name].update({'parents':[]})
            minimal_json["CityObjects"][city_object.name]['parents'].append(parents_id)

    return None

def export_attributes(split,minimal_json,name,attribute):
    """ Storing the attributes back to the dictionary. 
        The following code works only up to 3 levels of nested attributes
        TODO Future suggestion: Make a function out of this that works for any level of nested attributes."""       
    if len(split)==3:
        if not (split[0] in  minimal_json["CityObjects"][name]):
            minimal_json["CityObjects"][name].update({split[0]:{}})
        if not (split[1] in  minimal_json["CityObjects"][name][split[0]]):    
            minimal_json["CityObjects"][name][split[0]].update({split[1]:{}})
        if not (split[2] in  minimal_json["CityObjects"][name][split[0]][split[1]]):   
            minimal_json["CityObjects"][name][split[0]][split[1]].update({split[2]:attribute})
    elif len(split)==2:
        if not (split[0] in  minimal_json["CityObjects"][name]):
            minimal_json["CityObjects"][name].update({split[0]:{}})
        if not (split[1] in  minimal_json["CityObjects"][name][split[0]]):
            minimal_json["CityObjects"][name][split[0]].update({split[1]:attribute})
    elif len(split)==1:
        if not (split[0] in  minimal_json["CityObjects"][name]):
            minimal_json["CityObjects"][name].update({split[0]:attribute})

    return None
