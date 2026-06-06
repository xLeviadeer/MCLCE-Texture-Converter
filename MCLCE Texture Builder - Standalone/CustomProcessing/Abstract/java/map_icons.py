from CustomProcessing import Custom
import TextureLibs.TextureUtility as ut
from TextureLibs.Sheet import SheetExtractor
from CodeLibs.Path import Path
import TextureLibs.Global as Global
import TextureLibs.Read as rd

class map_icons(Custom.Function):
    def createImage(self):
        # determine if it's reg or additional
        isReg = None
        if (self.wiiuName == "mapicons"):
            isReg = True
        elif (self.wiiuName == "additionalmapicons"):
            isReg = False
        else:
            Global.endProgram("attempting to run map_icons process without using either mapicons or additionalmapicons")

        # create sheets
        wiiuSheet = SheetExtractor(self.wiiuImage, ut.size(16))
        newSheet = SheetExtractor(ut.size(64), ut.size(16))

        # process for before 1.20.5
        if (ut.checkVersion(20, 4, direction=False)):
            # read images as sheets
            linkSheet = SheetExtractor(Path("map_icons"), ut.size(8), self.wiiuName, "map", ut.size(128))

            # tuple of positions
            positions = None
            if (isReg == True):
                positions = {
                    "player1": {
                        "wiiu": (0, 0),
                        "link": (0, 0)
                    },
                    "player2": {
                        "wiiu": (1, 0),
                        "link": (1, 0)
                    },
                    "player3": {
                        "wiiu": (2, 0),
                        "link": (2, 0)
                    },
                    "player4": {
                        "wiiu": (3, 0),
                        "link": (3, 0)
                    },
                    "endGate": {
                        "wiiu": (0, 1),
                        "link": (4, 0)
                    },
                    "redMarker": {
                        "wiiu": (1, 1),
                        "link": (5, 0)
                    },
                    "offMapSquare": {
                        "wiiu": (2, 1),
                        "link": (6, 0)
                    },
                    "itemFrame": {
                        "wiiu": (3, 1),
                        "link": True
                    },
                    "player5": {
                        "wiiu": (0, 2),
                        "link": True
                    },
                    "player6": {
                        "wiiu": (1, 2),
                        "link": True
                    },
                    "player7": {
                        "wiiu": (2, 2),
                        "link": True
                    },
                    "player8": {
                        "wiiu": (3, 2),
                        "link": True
                    },
                    "greenMarker": {
                        "wiiu": (0, 3),
                        "link": True
                    },
                    "smallOffMapSquare": {
                        "wiiu": (1, 3),
                        "link": (7, 0)
                    },
                    "woodlandMansion": {
                        "wiiu": (2, 3),
                        "link": (8, 0)
                    },
                    "oceanMonument": {
                        "wiiu": (3, 3),
                        "link": (9, 0)
                    }
                }
            else:
                positions = {
                    "player1": {
                        "wiiu": (0, 0),
                        "link": True
                    },
                    "player2": {
                        "wiiu": (1, 0),
                        "link": True
                    },
                    "player3": {
                        "wiiu": (2, 0),
                        "link": True
                    },
                    "player4": {
                        "wiiu": (3, 0),
                        "link": True
                    },
                    "cross": {
                        "wiiu": (0, 1),
                        "link": (10, 1)
                    },
                    "player5": {
                        "wiiu": (0, 2),
                        "link": True
                    },
                    "player6": {
                        "wiiu": (1, 2),
                        "link": True
                    },
                    "player7": {
                        "wiiu": (2, 2),
                        "link": True
                    },
                    "player8": {
                        "wiiu": (3, 2),
                        "link": True
                    },
                }

            # for every position
            for linkedPosition in positions.values():
                # rename positions so they can be referenced with less clutter
                linkPos = linkedPosition["link"]
                wiiuPos = linkedPosition["wiiu"]
                # checks to use wiiu texture or not
                newSheet.insert(wiiuPos, 
                                wiiuSheet.extract(wiiuPos) 
                                if (linkPos == True) else # ^ use wiiu texture if true, else use link texture ⌄ 
                                linkSheet.extract(linkPos).resize(ut.size(16))
                                )
        
        # process after 1.20.5
        else: 
            # layout
            decorationNames = None
            if (isReg):
                decorationNames = (
                    (
                        "player",
                        "frame",
                        "red_marker",
                        "blue_marker"
                    ),
                    (
                        "target_x",
                        "target_point",
                        "player_off_map",
                        False
                    ),
                    (
                        False,
                        False,
                        False,
                        False
                    ),
                    (
                        False,
                        "player_off_limits",
                        "woodland_mansion",
                        "ocean_monument",
                    )
                )
            else:
                decorationNames = (
                    (
                        False,
                        False,
                        False,
                        False
                    ),
                    (
                        "red_x",
                        None,
                        None,
                        None
                    ),
                    (
                        False,
                        False,
                        False,
                        False
                    ),
                    (
                        None,
                        None,
                        None,
                        None
                    )
                )

            # go through the layout, read and place image
            y = 0
            while (y < len(decorationNames)):
                subDecorationNames = decorationNames[y]

                x = 0
                while (x < len(subDecorationNames)):
                    currName = subDecorationNames[x]
                    if (currName == None):
                        x += 1
                        continue
                    elif (currName == False):
                        newSheet.insert((x, y), wiiuSheet.extract((x, y)))
                    else:
                        newSheet.insert(
                            (x, y),
                            rd.readImageSingular(self.wiiuName, f"decorations\\{currName}", "map", ut.size(16))
                        )

                    x += 1
                y += 1

        # return
        return newSheet.getSheet()