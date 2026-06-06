from CustomProcessing import Custom
import TextureLibs.TextureUtility as ut
from TextureLibs.Sheet import SheetExtractor
import TextureLibs.Read as rd
import TextureLibs.Global as Global

class banner_atlas(Custom.Function):
    def createImage(self):
        banner_process = Custom.getClass("shared", "banner_process") # could use direct import, but we dont because we want print statements
        imageSize = (64,) * 2

        bannerNames = [
            "base",
            "border",
            "bricks",
            "circle",
            "creeper",
            "cross",
            "curly_border",
            "diagonal_left",
            "diagonal_right",
            "diagonal_up_left",
            "diagonal_up_right",
            "flower",
            "gradient",
            "gradient_up",
            "half_horizontal",
            "half_horizontal_bottom",
            "half_vertical",
            "half_vertical_right",
            "mojang",
            "rhombus",
            "skull",
            "small_stripes",
            "square_bottom_left",
            "square_bottom_right",
            "square_top_left",
            "square_top_right",
            "straight_cross",
            "stripe_bottom",
            "stripe_center",
            "stripe_downleft",
            "stripe_downright",
            "stripe_left",
            "stripe_middle",
            "stripe_right",
            "stripe_top",
            "triangle_bottom",
            "triangle_top",
            "triangles_bottom",
            "triangles_top"
        ]

        anyTexturesFound = False
        patterns = []
        i = 0
        for name in bannerNames:
            currImage = ut.blankImage(imageSize)
            try:
                currImage = rd.readImageSingular(self.wiiuName, f"banner\\{name}", self.type, imageSize, dox16Handling=False)
                anyTexturesFound = True
            except rd.notFoundException:
                # uses wiiu image
                bannerTexturesPerRow = 6
                currImage = self.wiiuImage.crop((
                    (i % bannerTexturesPerRow) * banner_process.bannerSize[0],
                    (i // bannerTexturesPerRow) * banner_process.bannerSize[1],
                    ((i % bannerTexturesPerRow) * banner_process.bannerSize[0]) + banner_process.bannerSize[0],
                    ((i // bannerTexturesPerRow) * banner_process.bannerSize[1]) + banner_process.bannerSize[1] ))
            except rd.notx16Exception as err:
                Global.incorrectSizeErrors.append(self.wiiuName)
                currImage = err.getImage().resize(imageSize)
                anyTexturesFound = True
            except rd.notExpectedException:
                Global.notExpectedErrors.append(self.wiiuName)
                currImage.paste(Global.notFoundImage.resize(banner_process.bannerSize))
                anyTexturesFound = True
            currImage = currImage.convert("RGBA")
            patterns.append(currImage)
            i += 1

        if (anyTexturesFound == False): raise rd.notFoundException # will trigger the "use wiiu texture" sequence and ensure the program doesn't think textures have been found
        return Custom.runFunctionFromPath("shared", "banner_process", self.wiiuName, self.type, self.wiiuImage, True, patterns)