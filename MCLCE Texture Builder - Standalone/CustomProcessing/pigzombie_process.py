from CustomProcessing import Custom
import TextureLibs.TextureUtility as ut
from TextureLibs.Sheet import SheetExtractor
import TextureLibs.Read as rd

class pigzombie_process(Custom.Function):
    def createImage(self, args):
        inputImage = args[0] # gets the input image out of the args

        # copy
        image = ut.blankImage(ut.mobside, int(ut.mobside / 2))
        # head
        head = ut.blankImage(32, 16)
        head.paste(inputImage.crop((0, 8, 8, 16)), (0, 8)) # left
        head.paste(inputImage.crop((8, 8, 18, 16)).resize((8, 8)), (8, 8)) # front
        head.paste(inputImage.crop((18, 8, 26, 16)), (16, 8)) # right
        head.paste(inputImage.crop((26, 8, 36, 16)).resize((8, 8)), (24, 8)) # back
        head.paste(inputImage.crop((8, 0, 18, 8)).resize((8, 8)), (8, 0)) # top
        head.paste(inputImage.crop((18, 0, 28, 8)).resize((8, 8)), (16, 0)) # back
        image.paste(head, (0, 0))
        # body
        image.paste(inputImage.crop((0, 16, 64, 32)), (0, 16))

        return image