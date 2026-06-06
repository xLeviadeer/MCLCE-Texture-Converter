from CustomProcessing import Custom
import TextureLibs.TextureUtility as ut
from TextureLibs.Sheet import SheetExtractor
import TextureLibs.Read as rd
import TextureLibs.Global as Global
from CodeLibs.Path import Path

class banner_atlas(Custom.Function):
    def createImage(self):
        bannerCls = Custom.getClass("shared", "banner_process") # cls instance for getting banner size data
        patterns = [] # expects patterns of x64 size (in the right (wiiu) order)
        anyTexturesFound = False
        if (ut.checkVersion(14, direction=False)): # earlier than 1.15
            def m(value):
                return value * 64

            bannerImage = rd.readImageSingular(self.wiiuName, Path("banner", "banner").getPath(), "entity", ut.size(512))

            i = 0
            amountOfTextures = 39
            bannerTexturesPerRow = 8
            while i < amountOfTextures: # runs a specific time so it doesn't grab empty banner textures
                x = (i % bannerTexturesPerRow)
                y = (i // bannerTexturesPerRow)
                patterns.append(bannerImage.crop((m(x), m(y), (m(x) + m(1)), (m(y) + m(1)))))

                i += 1
            anyTexturesFound = True
        else: # later than 1.15 or same
            patternNames = ["base", "border", "bricks", "circle", "creeper", "cross", "curly_border", "diagonal_left", "diagonal_right", 
                            "diagonal_up_left", "diagonal_up_right", "flower", "gradient", "gradient_up", "half_horizontal", "half_horizontal_bottom",
                            "half_vertical", "half_vertical_right", "mojang", "rhombus", "skull", "small_stripes", "square_bottom_left", 
                            "square_bottom_right", "square_top_left", "square_top_right", "straight_cross", "stripe_bottom", "stripe_center",
                            "stripe_downleft", "stripe_downright", "stripe_left", "stripe_middle", "stripe_right", "stripe_top", "triangle_bottom", 
                            "triangle_top", "triangles_bottom", "triangles_top"]
            i = 0
            for name in patternNames: # stripe_downright
                currImage = ut.blankImage(ut.mobsize)
                try:
                    # sets the curr image with a black background
                    currImage = rd.readImageSingular(self.wiiuName, Path("banner", f"banner_{name}").getPath(), "entity", ut.mobsize)
                    anyTexturesFound = True
                except rd.notFoundException:
                    # uses wiiu image
                    bannerTexturesPerRow = 6
                    currImage = self.wiiuImage.crop((
                        (i % bannerTexturesPerRow) * bannerCls.bannerSize[0],
                        (i // bannerTexturesPerRow) * bannerCls.bannerSize[1],
                        ((i % bannerTexturesPerRow) * bannerCls.bannerSize[0]) + bannerCls.bannerSize[0],
                        ((i // bannerTexturesPerRow) * bannerCls.bannerSize[1]) + bannerCls.bannerSize[1] ))
                except rd.notExpectedException:
                    Global.notExpectedErrors.append(self.wiiuName)
                    currImage.paste(Global.notFoundImage.resize(bannerCls.bannerSize)) # uses error texture as the banner size
                    anyTexturesFound = True
                patterns.append(currImage)
                i += 1
        if (anyTexturesFound == False): raise rd.notFoundException # will trigger the "use wiiu texture" sequence and ensure the program doesn't think textures have been found
        return Custom.runFunctionFromInstance(bannerCls(self.wiiuName, self.type, self.wiiuImage, isShared=True), True, patterns)