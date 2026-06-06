from CustomProcessing import Custom
import TextureLibs.TextureUtility as ut
import TextureLibs.Read as rd
from TextureLibs.Sheet import SheetExtractor
from CodeLibs.Path import Path

class kz(Custom.Function):
    def createImage(self):
        PAINTINGSIZE = 16

        # read the wiiu image as a sheet and create new sheet
        wiiuSheet = SheetExtractor(self.wiiuImage, ut.size(PAINTINGSIZE))
        newSheet = SheetExtractor(ut.size(256), ut.size(PAINTINGSIZE))

        # list of painting image names and their respective position on the sheet
        assets = [
            {
                "name": "alban",
                "pos": (2, 0),
                "chunk": (1, 1)
            },
            {
                "name": "aztec",
                "pos": (1, 0),
                "chunk": (1, 1)
            },
            {
                "name": "aztec2",
                "pos": (3, 0),
                "chunk": (1, 1)
            },
            {
                "name": "back",
                "pos": (12, 0),
                "chunk": (4, 4)
            },
            {
                "name": "bomb",
                "pos": (4, 0),
                "chunk": (1, 1)
            },
            {
                "name": "burning_skull",
                "pos": (8, 12),
                "chunk": (4, 4)
            },
            {
                "name": "bust",
                "pos": (2, 8),
                "chunk": (2, 2)
            },
            {
                "name": "courbet",
                "pos": (2, 2),
                "chunk": (2, 1)
            },
            {
                "name": "creebet",
                "pos": (8, 2),
                "chunk": (2, 1)
            },
            {
                "name": "donkey_kong",
                "pos": (12, 7),
                "chunk": (4, 3)
            },
            {
                "name": "fighters",
                "pos": (0, 6),
                "chunk": (4, 2)
            },
            {
                "name": "graham",
                "pos": (1, 4),
                "chunk": (1, 2)
            },
            {
                "name": "kebab",
                "pos": (0, 0),
                "chunk": (1, 1)
            },
            {
                "name": "match",
                "pos": (0, 8),
                "chunk": (2, 2)
            },
            {
                "name": "pigscene",
                "pos": (4, 12),
                "chunk": (4, 4)
            },
            {
                "name": "plant",
                "pos": (5, 0),
                "chunk": (1, 1)
            },
            {
                "name": "pointer",
                "pos": (0, 12),
                "chunk": (4, 4)
            },
            {
                "name": "pool",
                "pos": (0, 2),
                "chunk": (2, 1)
            },
            {
                "name": "sea",
                "pos": (4, 2),
                "chunk": (2, 1)
            },
            {
                "name": "skeleton",
                "pos": (12, 4),
                "chunk": (4, 3)
            },
            {
                "name": "skull_and_roses",
                "pos": (8, 8),
                "chunk": (2, 2)
            },
            {
                "name": "stage",
                "pos": (4, 8),
                "chunk": (2, 2)
            },
            {
                "name": "sunset",
                "pos": (6, 2),
                "chunk": (2, 1)
            },
            {
                "name": "void",
                "pos": (6, 8),
                "chunk": (2, 2)
            },
            {
                "name": "wanderer",
                "pos": (0, 4),
                "chunk": (1, 2)
            },
            {
                "name": "wasteland",
                "pos": (6, 0),
                "chunk": (1, 1)
            },
            {
                "name": "wither",
                "pos": (10, 8),
                "chunk": (2, 2)
            }
        ]

        # read images, if an image is missing read it as the wiiu texture
        anyTexturesFound = False
        for asset in assets:
            # find the currImage
            currImage = None
            try: # try to read image
                currImage = rd.readImageSingular(
                    self.wiiuName, 
                    Path(asset["name"]), 
                    "painting", 
                    ut.size(
                        (asset["chunk"][0] * PAINTINGSIZE), 
                        (asset["chunk"][1] * PAINTINGSIZE)
                    ), 
                    doVersionPatches=False
                )
                anyTexturesFound = True
            except (rd.notFoundException, rd.notExpectedException): # use wiiu image if not found or wrong size
                currImage = wiiuSheet.extract(asset["pos"], asset["chunk"])
            except rd.notExpectedException:
                currImage = wiiuSheet.extract(asset["pos"], asset["chunk"])
                anyTexturesFound = True

            # paste the currImage onto the newSheet
            if (asset["name"] == "back"): # paste for back
                for x in range(asset["chunk"][0]):
                    for y in range(asset["chunk"][1]):
                        newSheet.insert(
                            (
                                (asset["pos"][0] + x),
                                (asset["pos"][1] + y)
                            ),
                            currImage,
                            isDestructive=True
                        )

            else: # regular paste
                newSheet.insert(asset["pos"], currImage, isDestructive=True)

        # return
        if (anyTexturesFound == False): raise rd.notFoundException # will trigger the "use wiiu texture" sequence and ensure the program doesn't think textures have been found
        return newSheet.getSheet()
