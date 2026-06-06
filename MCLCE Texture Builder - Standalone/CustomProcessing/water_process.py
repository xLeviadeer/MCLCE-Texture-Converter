from CustomProcessing import Custom
import TextureLibs.TextureUtility as ut
from TextureLibs.Sheet import SheetExtractor
import TextureLibs.Read as rd
import TextureLibs.Global as Global

class water_process(Custom.Function):
    def createImage(self, args):
        # mip map generation stuff
        level = int(self.wiiuName[-1])
        resizeNum = 1
        i = 1
        while i < level:
            resizeNum *= 2
            i += 1

        # detect flow or still
        key = "water_still"
        height = 512
        width = 16
        if (self.wiiuName[:-1] == "water_flowMip"):
            key = "water_flow"
            height = 1024
            width = 32

        # bedrock modification
        if (Global.inputGame == "bedrock"):
            key += "_grey"

        # read image and resize
        image = rd.readImageSingular(self.wiiuName, key, self.type, ut.size(width, height))
        image = image.resize((int(image.width / resizeNum), int(image.height / resizeNum)))

        return image