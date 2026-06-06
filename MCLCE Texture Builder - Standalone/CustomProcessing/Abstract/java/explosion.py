from CustomProcessing import Custom
import TextureLibs.TextureUtility as ut
from TextureLibs.Sheet import SheetExtractor
import TextureLibs.Read as rd
from TextureLibs.SizingImage import SizingImage as Image
import TextureLibs.Global as Global

class explosion(Custom.Function):
    def createImage(self):
        sheetSize = 128 # any use of 128 refers to the size of the sheet
        finalImage = Image.new("RGBA", (sheetSize, sheetSize), "#ffffff00")
        anyTexturesFound = False

        if (int(str.split(Global.inputVersion, ".")[1]) == 13):
            finalImage = rd.readImageSingular(self.wiiuName, "explosion", "entity", ut.size(sheetSize))
            # error handling is automatically done for this one at a higher level, since it's a singular image read
            
        else: # the version isn't 1.13
            amountOfTextures = 16 # any use of 16 refers to the amount of textures
            textureSize = 32 # any use of 32 refers to the texture size

            currImage = Image.new("RGBA", (textureSize, textureSize), "#ffffff00")

            i = 0
            while (i < amountOfTextures): # 16 is count of textures
                top = ((i % 4) * textureSize) 
                left = ((i // 4) * textureSize) 
                try:
                    currImage = rd.readImageSingular(self.wiiuName, f"explosion_{str(i)}", "particle", ut.size(textureSize))
                    anyTexturesFound = True
                except rd.notFoundException: # uses wiiu image
                    currImage = self.wiiuImage.crop((top, left, (top + textureSize), (left + textureSize)))
                except rd.notx16Exception as err: # resize the image as the correct size
                    Global.incorrectSizeErrors.append(self.wiiuName)
                    currImage = err.getImage().resize((textureSize, textureSize))
                    anyTexturesFound = True
                except rd.notExpectedException as err: # place error texture
                    Global.notExpectedErrors.append(self.wiiuName)
                    currImage = Global.notFoundImage.resize(err.getSize())
                    anyTexturesFound = True

                finalImage.paste(currImage, (top, left))
                i += 1

        if (anyTexturesFound == False): raise rd.notFoundException # will trigger the "use wiiu texture" sequence and ensure the program doesn't think textures have been found
        return finalImage