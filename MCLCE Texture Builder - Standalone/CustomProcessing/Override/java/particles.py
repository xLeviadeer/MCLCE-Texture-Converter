from CustomProcessing import Custom
import TextureLibs.TextureUtility as ut
import TextureLibs.Read as rd
import TextureLibs.SizingImage as si
import TextureLibs.Global as Global

class particles(Custom.Function):
    def createImage(self):
        if (ut.checkVersion(13, 2, direction=False)):
            particleSheetSize = si.convertTuple((128, 128))
            image = rd.getImage(f"{Global.inputPath}\\particle\\{self.wiiuName}.png")
            image = image.crop((0, 0, (image.height / 2), (image.width / 2)), doResize=False) # cropped java texture sheet (crops to top-left quadrant)
            if (image.size != particleSheetSize): # if it's not the expected size
                if (Global.errorMode == "error"):
                    raise rd.notExpectedException(size=(particleSheetSize))
                if (Global.errorMode == "replace"):
                    raise rd.notx16Exception(None, image)
            return image
        else:
            return False # skip override