import TextureLibs.Global as Global
import InterfaceLibs.Interface as Interface

# entry point requirement
Global.name = str(__name__)
if Global.name == "__main__":
    Interface.launch()