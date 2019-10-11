# Blender-CityJSON-Plugin

A Blender plugin to import 3D city models encoded in the [CityJSON](http://cityjson.org) format.

## Requirements

- Blender Version >=2.80


## How to install and use the parser

1. Download the `CityJSON_Blender_parser.py` add-on, and install it locally to Blender. Menu `Edit > Preferences >Add-ons`, and `Install`. 

2. Make sure the add-on is enabled (by default it is disabled).

3. Go to `File > Import > CityJSON` and navigate to the directory where the CityJSON file is stored and open it.

4. If you want to visualize a certain area, click `Shift + B` and draw a rectangle with your mouse to zoom in into that specific area of the dataset.

5. To select all the children of a building right click on the building's (parent's) ID and click `Select Hierarchy`

6. To see the properties of each object simply select the object and click on the context.object tab on the bottom right (Blender 2.80 interface). Then click the `Custom Properties` drop down menu. (see the screenshot below)

![](attributes.png)


## Development

Clone this repository and have fun!

If you are using Visual Studio Code, you may:

- Install [Blender Development](jacqueslucke.blender-development
): a plugin that allows starting and debugging Python scripts from VSC.
- Install the [fake-bpy-module](https://github.com/nutti/fake-bpy-module) to enable auto-completion: `pip install fake-bpy-module-2.80`.
