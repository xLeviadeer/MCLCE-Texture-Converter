from CustomProcessing import Custom
import TextureLibs.Read as rd
import TextureLibs.TextureUtility as ut
import TextureLibs.Global as Global

# horse process is intended to be used versionally with java only
# the reason it's a shared process is because it needs to pass arguments

class horse_process(Custom.Function): 
    def createImage(self, args):

        # get read name
        readName = args[0]
        if (not isinstance(readName, str)): 
            Global.stopGen("horse was not supplied a valid reading name")
            return

        # get image
        horseImage = rd.readImageSingular(self.wiiuName, f"horse\\{readName}", "entity", ut.mobsize, doVersionPatches=False)
        horseImage = horseImage.convert("RGBA")

        # find saddle image
        entityType = None
        if (
            (self.wiiuName == "donkey")
            or (self.wiiuName == "mule")
        ):
            entityType = self.wiiuName
        elif (self.wiiuName.startswith("horse_")):
            entityType = "horse"
        saddleImage = rd.readImageSingular(self.wiiuName, f"equipment\\{entityType}_saddle\\saddle", "entity", ut.mobsize, doVersionPatches=False)
        saddleImage = saddleImage.convert("RGBA")

        # add
        horseImage.alpha_composite(saddleImage, doResize=False)
        return horseImage