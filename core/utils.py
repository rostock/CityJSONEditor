"""Blender CityJSON plugin utils module

This modules provides utitily methods for the importing/exporting
processing of CityJSON files
"""

import bpy

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
