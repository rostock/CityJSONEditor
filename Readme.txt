# Blender-CityJSON-Plugin
A Blender plugin to visualize 3D city models encoded in CityJSON format


Blender Version 2.80 , Python Version 3.x
__________________________________________



Files included in the repository:

1. CityJSON_Blender_parser.py --> Parser script

2. attributes.png

3. Readme.txt
______________________________________________________________________________________________



How to use the parser: 


1. Open the script in the Blender API

2.Replace the directory of the CityJSON file in line 7 of the parsers scripts with your local directory.

3.Run the script

4. Select a building / building part and make sure the object is a "cube_mesh_data.XXXX" and NOT "empty.XXXX". To check that click on the drop down symbol next to the ID of the object/building on the top right of the interface. Then click on the "View" tab and click "Frame Selected" (sometimes after "Frame Selected" is clicked you need to zoom in for the render to appear on your screen). 

If the buildings behave weirdly as you rotate change the view "from Perspective" to "Orthographic" by clicking  the "numpad 5" key.

If you want to visualize a certain area, click "Shift + B" and draw a rectangle with your mouse to zoom in into that specific area of the dataset.


5. To select all the children of a building right click on the building's (parent's) ID and click "Select Hierarchy"

6.To see the properties of each object simply select the object and click on the context.object tab on the bottom right (Blender 2.80 interface). Then click the "Custom Properties" drop down menu. (See the screenshot "attributes.png" for more info.)

