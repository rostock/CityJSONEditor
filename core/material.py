"""Module to manipulate materials in Blender regarding CityJSON

This module provides a set of factory classes to create materials
based on the semantics of the CityJSON file.
"""

import bpy
from .utils import assign_properties, clean_list

class BasicMaterialFactory:
    """A factory that creates a simple material for every city object"""

    material_colors = {
        "WallSurface": (0.8, 0.8, 0.8, 1),
        "RoofSurface": (0.9, 0.057, 0.086, 1),
        "GroundSurface": (0.507, 0.233, 0.036, 1)
    }

    default_color = (0, 0, 0, 1)

    def get_surface_color(self, surface_type):
        """Returns the material color of the appropriate surface type"""

        if surface_type in self.material_colors:
            return self.material_colors[surface_type]

        return self.default_color

    def create_material(self, surface):
        """Returns a new material based on the semantic surface of the object"""
        mat = bpy.data.materials.new(name=surface['type'])

        assign_properties(mat, surface)

        mat.diffuse_color = self.get_surface_color(surface['type'])

        return mat

    def check_material(self, material, surface):
        """Checks if the material can represent the provided surface"""

        if not material.name.startswith(surface['type']):
            return False

        # TODO: Add logic here to check for semantic surface attributes

        return True

    def get_material(self, surface):
        """Returns the material that corresponds to the semantic surface"""

        return self.create_material(surface)
    
    def get_materials(self, geom):
        mats = []
        values = []
        if 'semantics' in geom:
            values = geom['semantics']['values']

            for surface in geom['semantics']['surfaces']:
                mats.append(self.get_material(surface))

            values = clean_list(values)
        
        return (mats, values)

class ReuseMaterialFactory(BasicMaterialFactory):
    """A class that re-uses a material with similar semantics"""

    def get_material(self, surface):
        """Returns the material that corresponds to the semantic surface"""

        matches = [m for m in bpy.data.materials
                   if self.check_material(m, surface)]

        if matches:
            return matches[0]

        return self.create_material(surface)
