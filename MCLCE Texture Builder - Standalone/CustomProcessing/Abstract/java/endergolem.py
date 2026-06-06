from CustomProcessing import Custom
import TextureLibs.TextureUtility as ut
from TextureLibs.Sheet import SheetExtractor
import TextureLibs.Read as rd
from TextureLibs.SizingImage import SizingImageOps as ImageOps
from CodeLibs import Logger as log

class endergolem(Custom.Function):
    def createImage(self):
        def __assignFaceAndBody(image, brightness): 
            returnImage = ut.blankImage(64, 128)
            returnImage.paste(ut.grayscale(image.crop((0, 0, 64, 52)), brightness), (0, 0)) # body (only turn this part grayscale)
            returnImage.paste(image.crop((0, 52, 64, 64)), (0, 116)) # face
            return returnImage
        
        return rd.readMulticolorGrayscale(
                self.wiiuName,
                self.type,
                __assignFaceAndBody, # assignment function
                [ # names list (latest is in the list is the highest priority)
                    "",
                    "_black",
                    "_gray",
                    "_silver",
                    "_blue",
                    "_brown",
                    "_cyan",
                    "_green",
                    "_orange",
                    "_purple",
                    "_magenta",
                    "_red",
                    "_light_blue"
                    "_lime",
                    "_pink",
                    "_yellow",
                ],
                "shulker\\shulker", # names path prefix 
                "shulker\\shulker_white", # white path
                ut.size(64, 64)
            )