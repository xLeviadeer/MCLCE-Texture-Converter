# default settings & package enforcement
from xLPyBasics.PathAPI import Path
from xLPyBasics import Dependencies
if not Dependencies.is_frozen():
    Dependencies.enforce_proj(Path.get_meipassp(Path.cwd()))
Path.default_prepension.set(Path.cwd())

# multithreading block
import InterfaceLibs.Interface as Interface
import multiprocessing
if __name__ == "__main__":
    multiprocessing.freeze_support() # stops pyinstaller multithreading looping
    Interface.launch()
