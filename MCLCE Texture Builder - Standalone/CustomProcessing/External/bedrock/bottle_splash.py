from CustomProcessing import Custom
import TextureLibs.TextureUtility as ut
from TextureLibs.Sheet import SheetExtractor
import TextureLibs.Read as rd
from TextureLibs.SizingImage import SizingImage as Image
import TextureLibs.Global as Global

class bottle_splash(Custom.Function):
    def createImage(self):
        potionTypes = [
            "",
            "_absorption",
            "_blindness",
            "_confusion",
            "_damageBoost",
            "_digSlowdown",
            "_digSpeed",
            "_fireResistance",
            "_harm",
            "_heal",
            "_healthBoost",
            "_hunger",
            "_invisibility",
            "_jump",
            "_levitation",
            "_moveSlowdown",
            "_moveSpeed",
            "_nightVison",
            "_poison",
            "_regeneration",
            "_resistance",
            "_saturation",
            "_slowFall",
            "_turtleMaster",
            "_waterBreathing",
            "_weakness",
            "_wither"
        ]

        stableImage = Image.new("RGBA", (ut.singularSizeOnTexSheet, ut.singularSizeOnTexSheet), "#ffffff00")
        potionsFound = 0
        for currType in potionTypes: # for every bed color
            image = Image.new("RGBA", (ut.singularSizeOnTexSheet, ut.singularSizeOnTexSheet), "#ffffff00")
            # note that this message WILL tolerate image resizing, meaning if images have different sizes there will be sloppy results
            # if only one bed is found, the whole thing will bed sent over to both textures
            try:
                image = rd.readImageSingular(self.wiiuName, f"potion_bottle_splash{currType}", self.type, ut.size(16))
            except rd.notFoundException:
                continue
            except rd.notExpectedException:
                Global.notExpectedErrors.append(self.wiiuName)
                continue
            except rd.notx16Exception as err: # resizes image
                Global.incorrectSizeErrors.append(self.wiiuName)
                image = err.getImage().resize((ut.singularSizeOnTexSheet, ut.singularSizeOnTexSheet))

            # once everything is formatted right and working
            potionsFound += 1
            image = image.convert("RGBA")

            # don't run for the first bed, just copy it over to the stable image
            if (potionsFound == 1):
                stableImage = image
                continue

            # check for stability in all pixels (of each potion)
            i = 0
            while (i < ut.singularSizeOnTexSheet): # for pixels
                j = 0
                while (j < ut.singularSizeOnTexSheet):
                    if (stableImage.getpixel((i, j))[3] == 0): 
                        j += 1
                        continue # if both pixels are clear

                    if (image.getpixel((i, j)) != stableImage.getpixel((i, j))): # if pixels are different, then,
                        stableImage.putpixel((i, j), (0, 0, 0, 0)) # subtract them from the stable image
                    j += 1 
                i += 1

        # functions based on amount of potions found
        if (potionsFound == 0): # potion textures couldn't be determined
            if (Global.errorMode == "error"): # place error texture
                raise rd.notExpectedException()
            elif (Global.errorMode == "replace"): # use the wiiu texture
                raise rd.notFoundException()

        return stableImage
    