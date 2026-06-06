from CustomProcessing import Custom
import TextureLibs.TextureUtility as ut
from TextureLibs.Sheet import SheetExtractor
import TextureLibs.Read as rd
from CodeLibs.Path import Path
import TextureLibs.Global as Global

class villager_process(Custom.Function):
    argsJava = { # this is only here so it's obvious what values are associated with what names/keys
            "villagerFolderName": "villager", 
            "zombieFolderName": "zombie_villager",
            "villagerBaseTexName": "villager",
            "zombieBaseTexName": "zombie_villager",
            "biomeFolderName": "type",
            "villagerPlainsBaseTexName": "plains",
            "zombiePlainsBaseTexName": "plains",
            "professionFolderName": "profession",
            "doVersionPatches": False
        }
    @classmethod
    def getJavaArgsList(cls):
        return list(cls.argsJava.values())
    argsBedrock = { # this is only here so it's obvious what values are associated with what names/keys 
        "villagerFolderName": "villager2", 
        "zombieFolderName": "zombie_villager2",
        "villagerBaseTexName": "villager",
        "zombieBaseTexName": "zombie-villager",
        "biomeFolderName": "biomes",
        "villagerPlainsBaseTexName": "biome_plains",
        "zombiePlainsBaseTexName": "biome-plains-zombie",
        "professionFolderName": "professions",
        "doVersionPatches": False
    }
    @classmethod
    def getBedrockArgsList(cls):
        return list(cls.argsBedrock.values())

    def createImage(self, args):
        if (len(args) == 1): args = args[0] # removes multitupling from passing a list as a single argument
        # set arguments to values
        villagerFolderName = args[0]
        zombieFolderName = args[1]
        villagerBaseTexName = args[2]
        zombieBaseTexName = args[3]
        biomeFolderName = args[4]
        villagerPlainsBaseTexName = args[5]
        zombiePlainsBaseTexName = args[6]
        professionFolderName = args[7]
        doVersionPatches = args[8]

        path = Path()
        # changes based on zombie/villager
        if (self.wiiuName.startswith("zombie_")):
            path.append(zombieFolderName)
        else:
            path.append(villagerFolderName)

        # changes based on profession
        profession = None
        match (self.wiiuName.replace("zombie_", "")):
            case "villager": profession = "nitwit"
            case "butcher": profession = "butcher"
            case "farmer": profession = None
            case "librarian": profession = "librarian"
            case "priest": profession = "cleric"
            case "smith": profession = "weaponsmith"
        
        baseImage = rd.readImageSingular(self.wiiuName, path.getPathAppendTemp((zombieBaseTexName if (self.wiiuName.startswith("zombie")) else villagerBaseTexName)), "entity", ut.mobsize, doVersionPatches).convert("RGBA")
        typeImage = rd.readImageSingular(self.wiiuName, path.getPathAppendTemp(biomeFolderName, (zombiePlainsBaseTexName if (self.wiiuName.startswith("zombie")) else villagerPlainsBaseTexName)), "entity", ut.mobsize, doVersionPatches).convert("RGBA")
        baseImage.alpha_composite(typeImage, (0, 0)) # paste onto base
        if (profession == None): return baseImage # early return for nitwits
        overImage = ut.blankImage(ut.mobsize)
        if (Global.inputGame == "java"): # uses the zombie\\profession
            overImage = rd.readImageSingular(self.wiiuName, path.getPathAppendTemp(professionFolderName, profession), "entity", ut.mobsize, doVersionPatches)
        else: # uses the villager\\profession (even for zombies)
            overImage = rd.readImageSingular(self.wiiuName, Path(villagerFolderName, professionFolderName, profession), "entity", ut.mobsize, doVersionPatches)
        overImage = overImage.convert("RGBA")
        baseImage.alpha_composite(overImage, (0, 0)) # paste onto base

        return baseImage
