from CustomProcessing import Custom
import TextureLibs.TextureUtility as ut
import TextureLibs.Read as rd
from CodeLibs.Path import Path
import TextureLibs.Global as Global

class banner__pattern(Custom.Function):
    def createImage(self):
        # list of image names
        nameAppension = "_banner_pattern"
        patterns = [
            "mojang",
            "creeper",
            "globe",
            "skull",
            "flower",
            "piglin"
        ]

        # set variables 
        imageToUse = None
        anyImagesFound = "False"

        # loop through and find the best image
        for currPattern in map(lambda p: f"{p}{nameAppension}", patterns):

            # try to read the current pattern
                # if no images are found anyImagesFound = False
                # if no correctly scaled images were found (and it's error mode) anyImagesFound = NotExpected
                # if no correctly scaled images were found (and it's replace mode) anyImagesFound = True
                # if a correctly scaled image was found anyImagesFound = True
            try:
                imageToUse = rd.readImageSingular(
                    self.wiiuName,
                    Path(currPattern),
                    self.type,
                    ut.size(16),
                    dox16Handling=False
                )
                anyImagesFound = "True"
                break # if successful (perfect scaled image found) break
            except rd.notx16Exception as err:
                Global.incorrectSizeErrors.append(currPattern)
                if (imageToUse != None): continue # don't actually get images if an image has been found (ensures the first one found will always be the one used)
                imageToUse = err.getImage().resize(ut.size(16))
                anyImagesFound = "True"
            except rd.notExpectedException: # if the image wasn't the correct size
                Global.notExpectedErrors.append(currPattern)
                if (anyImagesFound != "True"): anyImagesFound = "NotExpected"
            except rd.notFoundException: # if no image found, do nothing
                pass

        # check if any images were found and error/return accordingly
        match (anyImagesFound):
            case "NotExpected": raise rd.notExpectedException
            case "False": raise rd.notFoundException
            case "True": return imageToUse