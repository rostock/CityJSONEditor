# Blender-CityJSON-Plugin
A Blender plugin to visualize 3D city models encoded in CityJSON format

cityjson_parser.py --> A simple parser of CityJSON file just for importing the objects into 			       Blender. No semantics or parent-child relationship is stored. 


cityjson_parser_parent-child.py --> The above parser augmented to also store the parent-child relation between buildings/building parts.


shape_by_coords_spyder.py --> A simple test script to test the python code (except the commands that utilize the Blender API -bpy- library).

______________________________________________________________________________________________


How to use the parser(s): Replace the directory of the CityJSON file in line 7 of the parsers scripts with your local directory. Enjoy! 