# CityJSONEditor

A Blender add-on to import, edit and export new instances of [CityJSON](http://cityjson.org)-encoded 3D city models. All buildings' levels of detail (LoD), attributes and semantic surfaces are stored and can be accesed via Blender's graphical interface.

This Addon has is a fork of Konstantinos Mastorakis's Project `UP3DATE` which can be found [here](https://github.com/cityjson/Up3date). It was further developed and changed to serve the special purpose we had in mind for it. This purpose is to gain a tool for editing the 3D models of individual buildings for our 3D-City-Model, to add more detail and to manually texture buildings of special importance. 

Changes to the original include the addition of support for the import and export of textured models. We also added context menus in both `Object-Mode` and `Edit-Mode` to facilitate easier assignment of SurfaceTypes.

## Credit

*This add-on was originally developed by Konstantinos Mastorakis ([konmast3r](https://github.com/konmast3r/)) as part of their research orientation project for the MSc Geomatics programme of TU Delft. Its functionality was further developed for the needs of their MSc thesis [An integrative workflow for 3D city model versioning](http://resolver.tudelft.nl/uuid:a7f7f0c8-7a34-454e-973a-d55f5b8b0dfe)*

## Requirements

The addon was developed using:

- Blender Version 3.2
- CityJSON v1.1.2


## Installation

1. Download this repository as zip (through GitHub this can be done through the `Clone or download` > `Download ZIP` button).

2. Run `Blender` and go to `Edit > Preferences > Add-ons` and press the `Install...` button.

3. Select the downloaded ZIP and press `Install Add-on from File...`.

4. Enable the add-on from the list, by ticking the empty box next to the add-on's name.<br>
*(Optional: If you wish to update to a newer version, un-tick and tick again the add-on to reload it!)*


## Usage

### CityJSON?

- If you are unfamiliar with CityJSON we strongly advise you to first explore the format as you otherwise won't understand the options you will be given by this addon! You can do so on the official [Website](https://www.cityjson.org/).


### Importing a 3D city objet

Go to `File > Import > CityJSON (.json)` and navigate to the directory where the `CityJSON` file is stored and open it.

#### Notes

- only one object is intendet to be imported in a file
- the import action will delete everything from the scene including the scene itself

### Editing

This addon is intendet to be used in a way where you, the user, import a CityJSON geometry eg. a ground surface of a building as a first step of any workflow. Blender is not a GIS, so we do not have propper ways of georeferencing objects that have been made in a "standart" .blend file. The importer of the module we based the addon off had a way to deal with large coordinates of CRSs so we used this existing approach. So please always start with some form of a referenced object or otherwise your spend time , creating a detailed Object, goes to waste.
It is also not intendet to import other objects into the scene as the importer constructs a special semantic, wich is to be upheld in order to be able to export a valid CityJSON file.

#### Standard Workflow

- enable `Developer` Extras in the blender preferences to see the custom properties you will add

In order to be able export objects correctly the following steps need to be followed:

1. In `Object Mode` right-click the object and select the option `set initial attributes`.
This initializes all the custom properties you will be able to set later. You should always start with this step, even if you import an object you have previously given these attributes. The assigned values will not be overwritten, so no worries there.

2. Now, still in `Object Mode`, you can assign values for LOD (`set LOD`), ObjectType (`set Construction`) and GeometryType (`set Type`). Use the context menus options to do so respectivly. 

3. After you have assigned the `CJEOconstruction` attribute, which declares the Object as a Bridge, Building etc., you can switch into `Edit Mode` to assign SurfaceTypes to your geometry. This is done by selecting a face, right-click to open the context menu and selecting the desired SurfaceType.
This action will create materials of the corresponding name which have attributes that will be used in the export to CityJSON.

*We advise you to declare a separate material for every surface as we intendet to use this addon for texturing and that capability hinges on having a material for every face.*

4. If you wish to add `Textures` you can do so by altering existing materials.  

### Exporting a 3D city object

To export your Object simply go to `File > Export > CityJSON (.json)`.


## Further Development

We plan to add further functionality to this addon at a later point in time. Plans and issus will be placed in the issues tab of this github repo. 
 
