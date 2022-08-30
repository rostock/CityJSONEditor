class FeatureTypes:
    featuretypes = {
        "building":[
            "Building",
            "BuildingPart",
            "BuildingInstallation",
            "IntBuildingInstallation",
            "RoofSurface",
            "WallSurface",
            "GroundSurface",
            "ClosureSurface",
            "FloorSurface",
            "OuterFloorSurface",
            "CeilingSurface",
            "OuterCeilingSurface",
            "Door",
            "Window",
            "Room",
            "BuildingFurniture",
        ],
        "bridge":[
            "Bridge",
            "BridgePart",
            "BridgeInstallation",
            "IntBridgeInstallation",
            "BridgeConstructionElement",
            "RoofSurface",
            "WallSurface",
            "GroundSurface",
            "ClosureSurface",
            "FloorSurface",
            "OuterFloorSurface",
            "InteriorWallSurface",
            "CeilingSurface",
            "OuterCeilingSurface",
            "Door",
            "Window",
            "BridgeRoom",
            "BridgeFurniture"
        ]
    }

#<classColor className="bldg:Building" color="#e0e0e0ff"/>
#      <classColor className="bldg:BuildingPart" color="#ffffffff"/>
#      <classColor className="bldg:BuildingInstallation" color="#ae825aff"/>
#      <classColor className="bldg:IntBuildingInstallation" color="#ae825aff"/>
#      <classColor className="bldg:RoofSurface" color="#9c4444ff"/>
#      <classColor className="bldg:WallSurface" color="#dbdbdbff"/>
#      <classColor className="bldg:GroundSurface" color="#747474ff"/>
#      <classColor className="bldg:ClosureSurface" color="#ffffffff"/>
#      <classColor className="bldg:FloorSurface" color="#ffffffff"/>
#      <classColor className="bldg:OuterFloorSurface" color="#854c7bff"/>
#      <classColor className="bldg:InteriorWallSurface" color="#ffffffff"/>
#      <classColor className="bldg:CeilingSurface" color="#ffffffff"/>
#      <classColor className="bldg:OuterCeilingSurface" color="#7e7d54ff"/>
#      <classColor className="bldg:Door" color="#4d4de8ff"/>
#      <classColor className="bldg:Window" color="#80c7c8ff"/>
#      <classColor className="bldg:Room" color="#ffffffff"/>
#      <classColor className="bldg:BuildingFurniture" color="#ffffffff"/>
#      <classColor className="brid:Bridge" color="#a77600ff"/>
#      <classColor className="brid:BridgePart" color="#ffffffff"/>
#      <classColor className="brid:BridgeInstallation" color="#3753aeff"/>
#      <classColor className="brid:IntBridgeInstallation" color="#ffffffff"/>
#      <classColor className="brid:BridgeConstructionElement" color="#7737aeff"/>
#      <classColor className="brid:RoofSurface" color="#ffffffff"/>
#      <classColor className="brid:WallSurface" color="#ffffffff"/>
#      <classColor className="brid:GroundSurface" color="#ffffffff"/>
#      <classColor className="brid:ClosureSurface" color="#ffffffff"/>
#      <classColor className="brid:FloorSurface" color="#ffffffff"/>
#      <classColor className="brid:OuterFloorSurface" color="#ffffffff"/>
#      <classColor className="brid:InteriorWallSurface" color="#ffffffff"/>
#      <classColor className="brid:CeilingSurface" color="#ffffffff"/>
#      <classColor className="brid:OuterCeilingSurface" color="#ffffffff"/>
#      <classColor className="brid:Door" color="#ffffffff"/>
#      <classColor className="brid:Window" color="#ffffffff"/>
#      <classColor className="brid:BridgeRoom" color="#ffffffff"/>
#      <classColor className="brid:BridgeFurniture" color="#ffffffff"/>


    def getAllElementsOfFeatureType(self, type):
        return self.featuretypes
        pass

    def getAllLODs(self):
        pass

    def getAllFeatures(self):
        print(list(self.featuretypes))
        return list(self.featuretypes)