# Blender-CityJSON-Plugin

A Blender plugin to import 3D city models encoded in the [CityJSON](http://cityjson.org) format. All building attributes and faces semantics are stored and can be accesed via Blender's graphic user interface.

## Requirements

- Blender Version >=2.80

## Testing Datasets

You can find sample datasets at the official [CityJSON](https://www.cityjson.org/datasets/#datasets-converted-from-citygml) website. In case you have 3D City Model datasets encoded in CityGML you can use the free [Conversion Tool](https://www.cityjson.org/help/users/conversion/) to convert to and from CityGML and CityJSON.

Trying to import really big datasets such as `New York` will take several minutes because of the amount of information contained. With the rest sample CityJSON files everything should work noticeably faster. Depending on your machine, it could take some seconds up to few minutes minute to import the 3D City Model. 

## How to install and use the parser

1. Download the `CityJSON_Blender_parser.py` add-on and install it locally to Blender. Menu `Edit > Preferences >Add-ons`, and `Install`. 

2. Make sure the add-on is enabled (by default it is disabled).

3. Go to `File > Import > CityJSON` and navigate to the directory where the CityJSON file is stored and open it.

4. In case you run `Blender` through the console, useful feedback is given in it, informing about the progress of the import procedure. 

5. After a successful import, you should be able to see the model somewhere close to the axis origin. Rotation of the scene and zooming in and out might prove useful at this point, to locate the model.

6. For different `Collections` are created for `LoD 0 to 3` respectively. In case more than 1 geometries exist for the objects -representing different `LODs` (level of detail)-, every geometry is stored under the appropriate `Collection`, under the parent object (if there is any). You can display different `Collections` by clicking on the `eye icon` in the `Outliner` at the top right of the interface (see screenshot below). By default all the `LOD_x` collections should be visible right after importing the 3D City Model. In case you see any artefacts that is the reason! Choosing only one visible collection should remove all artefacts. 

7. In case you want to visualize a certain area, click `Shift + B` and draw a rectangle with your mouse to zoom into that specific area of the 3D City Model. This also moves the rotation center at that poin, which will come handy when you want to rotate the model for further inspection.

8. To see the attributes of each object, simply select the object on the screen and click on the `Context.Object` tab on the bottom right (Blender 2.80 interface). Then click `Custom Properties` drop down menu (see screenshot below).

9. To see the semantics of each surface, select an object in `Object Mode`, hit `TAB` to toggle `Edit Mode` and click `Face Select` (top left of the viewport between the `Edit Mode` and the `View` button). Select a face of the object and click on the `Context.Material` tab at the bottom right. Scroll down and click on `Custom Properties`(see screenshot below).


![](attributes.png) 
![](semantics.png)


## Development

Clone this repository and have fun!

If you are using Visual Studio Code, you may:

- Install [Blender Development](jacqueslucke.blender-development
): a plugin that allows starting and debugging Python scripts from VSC.
- Install the [fake-bpy-module](https://github.com/nutti/fake-bpy-module) to enable auto-completion: `pip install fake-bpy-module-2.80`.


