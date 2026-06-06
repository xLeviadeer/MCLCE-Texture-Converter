from CustomProcessing import Custom
import TextureLibs.TextureUtility as ut

class seagrass_tall_top(Custom.Function):
    def createImage(self):
        debug = False
        image = Custom.runFunctionFromPath("shared", "kelp_process", self.wiiuName, self.type, self.wiiuImage, True, "tall_seagrass_top")
        if (debug == True):
            image = ut.getImageNoOpacity(image, doZeroDetection=True) # for debugging only
        return image