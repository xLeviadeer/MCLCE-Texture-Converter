from CustomProcessing import Custom
import TextureLibs.TextureUtility as ut
import TextureLibs.Read as rd
import TextureLibs.SizingImage as si
from TextureLibs.SizingImage import SizingImage as Image
import TextureLibs.Global as Global

class shine(Custom.Function):
    def createImage(self):
        size = si.deconvertInt(ut.singularSizeOnTexSheet) * 4
        finalImage = Image.new("RGBA", (size, size), "#ffffff00")
        try:
            finalImage = rd.readImageSingular(self.wiiuName, "flash", "particle", ut.size(size))
        except rd.notFoundException:
            # gets the wiiu sheet (which is known to exist) and crops it down for the shine texture
            finalImage = rd.readWiiuImage(False, f"{Global.getLayerGame()}_{(self.type if (not self.type.endswith('s')) else self.type[:-1])}").crop((32, 16, (32 + 32), (16 + 32)))
        except rd.notx16Exception as err:
            Global.incorrectSizeErrors.append(self.wiiuName)
            finalImage = err.getImage().resize((size, size))
        except rd.notExpectedException:
            Global.notExpectedErrors.append(self.wiiuName)
            finalImage = Global.notFoundImage.resize((size, size))

        return finalImage