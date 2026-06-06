from CustomProcessing import Custom
import TextureLibs.Read as rd
import TextureLibs.Global as Global

class spawn__egg_spots(Custom.Function):
    def createImage(self): return rd.readWiiuImage(False, f"{Global.getLayerGame()}_item").crop((144, 160, 160, 176))