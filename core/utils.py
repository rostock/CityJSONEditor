"""Blender CityJSON plugin utils module

This modules provides utitily methods for the importing/exporting
processing of CityJSON files
"""

import bpy

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