# Blender-CityJSON-Plugin
A Blender plugin to visualize 3D city models encoded in CityJSON format

cityjson_parser.py --> A simple parser of CityJSON file just for importing the objects into Blender. No semantics or parent-child relationship is stored. 


cityjson_parser_parent-child.py --> The above parser augmented to also store the parent-child relation between buildings/building parts and all their attributes.


shape_by_coords_spyder.py --> A simple test script to test the python code in a python console (except the commands that utilize the Blender API -bpy- library).

______________________________________________________________________________________________


How to use the parser(s): 1. Replace the directory of the CityJSON file in line 7 of the parsers scripts with your local directory. Enjoy! 

2.To see the properties of each object simply select the object and click on the context.object tab on the bottom right. (Blender 2.80 interface). Then click the "Custom Properties" drop down menu. (See the screenshot "attributes.png")