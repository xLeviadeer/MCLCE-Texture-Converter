from CustomProcessing import Custom
import TextureLibs.TextureUtility as ut
from TextureLibs.Sheet import SheetExtractor
import TextureLibs.Read as rd
import TextureLibs.Global as Global

class cows_process(Custom.Function):
    def createImage(self, args):
        # version and texture selection
        doFaceMove = False
        fileName = "cow"
        if (Global.inputGame == "java"):
            # change mooshroom file name 
            if (self.wiiuName == "mooshroom"):
                if (ut.checkVersion(13, 2, direction=False)): 
                    fileName = "mooshroom"
                else:
                    fileName = "red_mooshroom"

            # move face above 1.21.7
            if (ut.checkVersion(21, 7)): 
                doFaceMove = True
                if (self.wiiuName == "cow"):
                    fileName = "temperate_cow"
        elif (Global.inputGame == "bedrock"):
            # mooshroom file name
            if (self.wiiuName == "mooshroom"):
                fileName = "mooshroom"

            # move face above 1.21.70
            if (ut.checkVersion(21, 70)):
                doFaceMove = True
                fileName = f"{fileName}_v2"
        else:
            Global.endProgram("cows_process could not find inputGame")
            return

        # read image
        expectedSize = ut.size(ut.mobside, ut.mobsideHalf)
        if (doFaceMove): expectedSize = ut.mobsize
        image = rd.readImageSingular(self.wiiuName, f"cow\\{fileName}", "entity", expectedSize)
        image = image.convert("RGBA")

        # move and resize udders
        udderImage = image.crop((52, 0, 64, 7)) # get udders
        image.paste(ut.blankImage(12, 7), (52, 0)) # erase
        image.paste(udderImage.crop((0, 1, 6, 7)), (53, 2)) # udder bottom
        image.paste(udderImage.crop((0, 1, 1, 7)), (52, 2)) # udder left
        image.paste(udderImage.crop((5, 1, 6, 7)), (59, 2)) # udder right
        image.paste(udderImage.crop((1, 0, 12, 1)), (54, 1)) # udder top (bottom)
        image.paste(udderImage.crop((1, 0, 12, 1)), (54, 0)) # udder top (top)

        # move face if needed
        if (doFaceMove):
            # move face parts
            faceImage = image.crop((2, 34, 8, 37))
            image.paste(faceImage, (7, 11))

            # crop image down
            image = image.crop((0, 0, ut.mobside, ut.mobsideHalf))            

        return image