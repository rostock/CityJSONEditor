"""Module to manipulate materials in Blender regarding CityJSON

This module provides a set of factory classes to create materials
based on the semantics of the CityJSON file.
"""

import bpy
from .utils import assign_properties

material_colors = {
    "WallSurface": (0.8, 0.8, 0.8, 1),
    "RoofSurface": (0.9, 0.057, 0.086, 1),
    "GroundSurface": (0.507, 0.233, 0.036, 1)
}

class BasicMaterialFactory:
    """A factory that creates a simple mateirla for every city object"""

    def create_material(self, surface):
        """Returns a new material based on the semantic surface of the object"""
        mat = bpy.data.materials.new(name=surface['type'])

        assign_properties(mat, surface)

        #Assign color based on surface type
        if surface['type'] in material_colors:
            mat.diffuse_color = material_colors[surface["type"]]
        else:
            mat.diffuse_color = (0, 0, 0, 1)

        return mat

    def check_material(self, material, surface):
        """Checks if the material can represent the provided surface"""

        if not material.name.startswith(surface['type']):
            return False

        # TODO: Add logic here to check for semantic surface attributes

        return True

    def get_material(self, surface):
        """Returns the material that corresponds to the semantic surface"""

        matches = [m for m in bpy.data.materials
                   if self.check_material(m, surface)]

        if matches:
            return matches[0]

        return self.create_material(surface)
