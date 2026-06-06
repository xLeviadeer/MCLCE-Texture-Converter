from CustomProcessing import Custom
import TextureLibs.Read as rd
import TextureLibs.TextureUtility as ut
import TextureLibs.SizingImage as si

class cloth(Custom.Function):
    def createImage(self):
        # get cloth number and B status
        clothNumber = int(self.wiiuName[6])
        clothBStatus = ((len(self.wiiuName) >= 9) and (self.wiiuName[8] == 'b'))

        # read image
        image = rd.readImageSingular(self.wiiuName, f"armor\\leather_{clothNumber}", "models", ut.size(64, 32))

        # get opacity portion (and return)
        return ut.getOpacityTexture(image, clothBStatus)


