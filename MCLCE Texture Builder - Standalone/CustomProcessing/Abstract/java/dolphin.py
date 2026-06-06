from CustomProcessing import Custom
import TextureLibs.TextureUtility as ut
from TextureLibs.Sheet import SheetExtractor
import TextureLibs.Read as rd
from TextureLibs.SizingImage import SizingImage as Image
from TextureLibs.SizingImage import SizingImageOps as ImageOps
import TextureLibs.Global as Global

class dolphin(Custom.Function):
    def createImage(self):
        finalImage = Image.new("RGBA", ut.mobsize, "#ffffff00")
        javaImage = Image.new("RGBA", ut.mobsize, "#ffffff00")
        try:
            javaImage = rd.readImageSingular(self.wiiuName, "dolphin", self.type, ut.mobsize)
        except rd.notx16Exception as err:
            Global.incorrectSizeErrors.append(self.wiiuName)
            javaImage = err.getImage().resize(ut.mobsize)

        # move things around and copy them as they are supposed to be
        finalImage.paste(javaImage.crop((0, 0, 28, 13)), (0, 0)) # head
        finalImage.paste(javaImage.crop((0, 13, 12, 19)), (0, 13)) # nose
        finalImage.paste(javaImage.crop((35, 0, 51, 13)), (13, 13)) # body (upper)
        finalImage.paste(javaImage.crop((22, 13, 64, 20)), (0, 26)) # body (lower)
        finalImage.paste(javaImage.crop((11, 19, 19, 30)), (11, 33)) # back (upper)
        finalImage.paste(javaImage.crop((0, 30, 30, 35)), (0, 44)) # back (lower)
        finalImage.paste(javaImage.crop((19, 20, 51, 27)), (0, 49)) # tail
        finalImage.paste(javaImage.crop((56, 0, 58, 5)).resize((2, 4)), (33, 0)) # top fin (upper)
        finalImage.paste(javaImage.crop((51, 5, 63, 9)).resize((10, 5)), (29, 4)) # top fin (lower)
        # side fin hanlding
        fin = {
            "left": ImageOps.flip(javaImage.crop((48, 27, 55, 31))),
            "front": ImageOps.flip(javaImage.crop((55, 27, 56, 31))),
            "right": ImageOps.flip(javaImage.crop((56, 27, 63, 31))),
            "back": ImageOps.flip(javaImage.crop((63, 27, 64, 31))),
            "top": ImageOps.flip(javaImage.crop((55, 20, 56, 27))),
            "bottom": ImageOps.flip(javaImage.crop((56, 20, 57, 27)))
        }

        # fin line (sides)
        finline = Image.new("RGBA", (24, 1), "#ffffff00")
        finline.paste(fin["front"].rotate(-90, expand=True), (0, 0)) # right (left)
        finline.paste(fin["top"].rotate(90, expand=True).resize((8, 1)), (4, 0)) # right (front)
        finline.paste(fin["bottom"].rotate(90, expand=True).resize((8, 1)), (12, 0)) # right (right)
        finline.paste(fin["back"].rotate(90, expand=True), (20, 0)) # right (back)

        finalImage.paste(finline, (40, 4)) # right (finline)

        finline = ImageOps.mirror(finline) # mirror and move the finline
        leftLine = finline.crop((0, 0, 8, 1))
        rightLine = finline.crop((8, 0, 24, 1))
        finline.paste(rightLine, (0, 0))
        finline.paste(leftLine, (16, 0))

        finalImage.paste(finline, (40, 10)) # left (finline)

        # left top and bottoms
        finalImage.paste(fin["right"].resize((8, 4)), (44, 0)) # right (top)
        finalImage.paste(fin["right"].resize((8, 4)), (52, 0)) # right (bottom)
        finalImage.paste(fin["left"].resize((8, 4)), (44, 6)) # left (top)
        finalImage.paste(fin["left"].resize((8, 4)), (52, 6)) # left (bottom)

        return finalImage