# Blender-CityJSON-Plugin

A Blender plugin to visualize 3D city models encoded in [CityJSON](http://cityjson.org) format

## Requirements

- Blender Version 2.80
- Python Version 3.x

## Files included in the repository

- `CityJSON_Blender_parser.py` is the parser script
- `attributes.png`
- `README.md`

## How to install and use the parser

1. Download the `CityJSON_Blender_parser.py` add-on, and install it locally to Blender. 

2. Make sure the add-on is enabled (by default it is disabled).

3. Go to `File > Import > CityJSON` and navigate to the directory where the CityJSON file is stored and open it.

4. Select a building / building part and make sure the object is a `cube_mesh_data.XXXX` and NOT `empty.XXXX`. To check that click on the drop down symbol next to the ID of the object/building on the top right of the interface. Then click on the `View` tab and click `Frame Selected` (sometimes after `Frame Selected` is clicked you need to zoom in for the render to appear on your screen). 

    If the buildings behave weirdly as you rotate change the view from `Perspective` to `Orthographic` by clicking  the `numpad 5` key.

    If you want to visualize a certain area, click `Shift + B` and draw a rectangle with your mouse to zoom in into that specific area of the dataset.


5. To select all the children of a building right click on the building's (parent's) ID and click `Select Hierarchy`

6. To see the properties of each object simply select the object and click on the context.object tab on the bottom right (Blender 2.80 interface). Then click the `Custom Properties` drop down menu. (See the screenshot `attributes.png` for more info.)

## Development

Clone this repository and have fun!

If you are using Visual Studio Code, you may:

- Install [Blender Development](jacqueslucke.blender-development
): a plugin that allows starting and debugging Python scripts from VSC.
- Install the [fake-bpy-module](https://github.com/nutti/fake-bpy-module) to enable auto-completion: `pip install fake-bpy-module-2.80`.
