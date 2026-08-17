from builtins import type as typeof
import traceback
import TextureLibs.Global as Global

def testPath(value):
    if (typeof(value) is not Path): # checks if the value is a path
        for line in traceback.format_stack()[:-1]: # prints a traceback (but not the last trace)
            print(line.strip())
        Global.stopGen(f"variable input was not the correct type. It is currently type '{typeof(value)}' when it needs to be 'Path'")

class Path():
    def __init__(self, *args, isRootDirectory:bool=False, doFormalize:bool=False):
        self.path = []

        self.path.clear()
        if (args):
            self.__addToPath(args)
        self.isRootDirectory = isRootDirectory # determines whether or not to always include/disinclude first slash

        if doFormalize: self.formalize()

    def __str__(self) -> str:
        return self.getPath()

    def __addToPath(self, *args, index=None):
        count = 0 # for returning the count completely accurate to the ammount of added things
        args = args[0] # fixes multi-tupling
        if (type(args) is str): # is a single string
            self.path.append(args)
            count += 1
            return
        for arg in args:
            if ((type(arg) is list) or (type(arg) is tuple)):
                count += self.__addToPath(arg, index=index)
            elif (type(arg) is str):
                if (index != None):
                    self.path.insert(index, arg)
                    index += 1 # increments the index as the array gets bigger (and hence bigger indexes are needed to keep the correct order)
                    count += 1
                else:
                    self.path.append(arg)
                    count += 1
        return count

    def append(self, *args):
        self.__addToPath(args)

    def prepend(self, *args):
        self.addAt(0, args)

    def addAt(self, index, *args):
        self.__addToPath(args, index=index)

    def remove(self, value):
        self.path.remove(value)

    def removeAt(self, index):
        del self.path[index]

    def __slice(self, start=0, end=None):
        if (end == None):
            end = len(self.path)
        self.path = self.path[start:end]

    def slice(self, start=0, end=None, doFormalize=False):
        # formalize if doFormalize is true
        if (doFormalize == True):
            self.formalize()
        if (end == None): end = len(self.path)
        return Path(self.path[start:end], isRootDirectory=self.isRootDirectory) # slices and turns the path into a new path so it can be output in the correct format
    
    def formalize(self):
        """
        Description:
            Formalizes the path by removing any strings that contain '\\' (backslash) and turnning them into regular path elements
        """
        self.path = self.getPath(withFirstSlash=False).split("\\")

    def merge(self, path, *, mergeAtBeginning=True):
        if (mergeAtBeginning == True):
            self.prepend(path._getRaw())
        else:
            self.append(path._getRaw())

    def getLength(self, doFormalize=False):
        # formalize if doFormalize is true
        if (doFormalize == True):
            self.formalize()
        return len(self.path)
    
    def __len__(self):
        return self.getLength()

    def getAt(self, index, doFormalize=False):
        # formalize if doFormalize is true
        if (doFormalize == True):
            self.formalize()
        return self.path[index]
    
    def getFirst(self, doFormalize=False):
        # formalize if doFormalize is true
        if (doFormalize == True):
            self.formalize()
        return self.path[0]
    
    def replaceAt(self, index, string):
        self.removeAt(index)
        self.addAt(index, string)
    
    def getLast(self, doFormalize=False):
        # formalize if doFormalize is true
        if (doFormalize == True):
            self.formalize()
        return self.path[self.getLength() - 1]

    def _getRaw(self):
        return self.path

    def getPath(self, withFirstSlash=True, withLastSlash=False, doFormalize=False):
        # formalize if doFormalize is true
        if (doFormalize == True):
            self.formalize()
        
        # isRootDirectory handling
        if (self.isRootDirectory == True):
            withFirstSlash = False

        string = "\\".join(self.path)
        if (withFirstSlash):
            string = f"\\{string}"
        if (withLastSlash):
            string = f"{string}\\"
        return string
    
    def getPathAppend(self, *args, withFirstSlash=True, withLastSlash=False, doFormalize=False):
        self.__addToPath(args)
        return self.getPath(withFirstSlash=withFirstSlash, withLastSlash=withLastSlash, doFormalize=doFormalize)

    def getPathAppendTemp(self, *args, withFirstSlash=True, withLastSlash=False, doFormalize=False):
        # add to path and get output
        count = self.__addToPath(args)
        copyOutput = self.getPath(withFirstSlash=withFirstSlash, withLastSlash=withLastSlash, doFormalize=doFormalize)
        # remove from path
        self.__slice(end=(len(self.path) - count))
        return copyOutput
    
    def getPathPrepend(self, *args, withFirstSlash=True, withLastSlash=False, doFormalize=False):
        self.__addToPath(args, index=0)
        return self.getPath(withFirstSlash=withFirstSlash, withLastSlash=withLastSlash, doFormalize=doFormalize)
    
    def getPathPrependTemp(self, *args, withFirstSlash=True, withLastSlash=False, doFormalize=False):
        # add to path and get output
        count = self.__addToPath(args, index=0)
        copyOutput = self.getPath(withFirstSlash=withFirstSlash, withLastSlash=withLastSlash, doFormalize=doFormalize)
        # remove from path
        self.__slice(start=count)
        return copyOutput
    
    def copy(self):
        return Path(self.path, isRootDirectory=self.isRootDirectory)