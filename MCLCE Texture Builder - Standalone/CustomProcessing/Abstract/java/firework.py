from CustomProcessing import Custom
import TextureLibs.TextureUtility as ut
from TextureLibs.Sheet import SheetExtractor
import TextureLibs.Read as rd
import TextureLibs.Global as Global

class firework(Custom.Function):
    def createImage(self):
        # get images
        finalImage = self.wiiuImage
        javaImage = ut.blankImage(ut.singularSizeOnTexSheet)
        try:
            javaImage = rd.readImageSingular(self.wiiuName, "firework_rocket", "item", ut.size(16))
        except rd.notx16Exception as err:
            Global.incorrectSizeErrors.append(self.wiiuName)
            javaImage = err.getImage().resize(ut.mobsize)

        finalImage.paste(javaImage.crop((6, 0, 11, 13)).rotate(-90, expand=True), (4, 0))
        
        return finalImage