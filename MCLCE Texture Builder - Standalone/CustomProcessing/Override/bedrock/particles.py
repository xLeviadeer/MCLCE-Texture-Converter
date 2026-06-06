from CustomProcessing import Custom
import TextureLibs.TextureUtility as ut
from TextureLibs.Sheet import SheetExtractor
import TextureLibs.Read as rd
from TextureLibs.SizingImage import SizingImage as Image
import TextureLibs.SizingImage as si
import TextureLibs.Global as Global

class particles(Custom.Function):
    def createImage(self):
        image = rd.getImage(f"{Global.inputPath}\\particle\\{self.wiiuName}.png")

        # - run edits on the image without using specific sizes -
        # find the size of a singular texture
        sizeOfTexture = int(image.height / 16) # 16 is the number of textures veritcally in the sheet
        sheetWidth = int(sizeOfTexture * 16)
        # clear
        image.paste(Image.new("RGBA", (sheetWidth, sizeOfTexture), "#ffffff00"), (0, (sizeOfTexture * 10)))
        # move
        image.paste(image.crop((0, (sizeOfTexture * 11), (sheetWidth / 2), (sizeOfTexture * 13))), (0, (sizeOfTexture * 10)))
        # clear extra
        image.paste(Image.new("RGBA", (int(sheetWidth / 2), sizeOfTexture), "#ffffff00"), (0, (sizeOfTexture * 12)))

        # run size errors
        particleSheetSize = si.convertTuple((128, 128))
        if (image.size != particleSheetSize):
            if (Global.errorMode == "error"):
                raise rd.notExpectedException(size=particleSheetSize)
            if (Global.errorMode == "replace"):
                raise rd.notx16Exception(None, image)
        return image