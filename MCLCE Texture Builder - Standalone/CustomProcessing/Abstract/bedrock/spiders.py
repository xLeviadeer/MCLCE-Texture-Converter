from xLPyBasics.PathAPI import Path

from CustomProcessing import Custom
import TextureLibs.TextureUtility as ut
import TextureLibs.Read as rd

class spiders(Custom.Function):
    def createImage(self):
        if (self.wiiuName == "spider_eyes"):
            return ut.getOpacityTexture(
                        rd.readImageSingular(self.wiiuName, Path("spider", "spider"), "entity", ut.size(ut.mobside, (ut.mobside / 2))),
                        True,
                    )
        else: # spider, cavespider
            textureName = "spider" if (self.wiiuName != "cavespider") else "cave_spider"
            return ut.getImageNoOpacity( 
                    rd.readImageSingular(self.wiiuName, Path("spider", textureName), "entity", ut.size(ut.mobside, (ut.mobside / 2)))
                )