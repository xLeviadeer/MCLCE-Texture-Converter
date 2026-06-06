from CodeLibs.Path import Path
from typing import Union
import json
from copy import deepcopy
#from os import getcwd as cwd
from TextureLibs.Global import getMainWorkingLoc as cwd

# - processes -

def __processAndTypeCheckPath(
        pathOrString:Union[Path, str], 
        prependCWD:bool=True, 
        formalizePath:bool=False, 
        *, 
        doPrint:bool=False
    ) -> str:
    """
    Description:
        processes the path into a string and type checks all values
    ---
    Arguments:
        - pathOrString : Path or String <>
            - a Path or string path to the file to be opened
        - prependCWD : Boolean <True>
            - true: appends the CWD to the beginning of the path
            - false: doesn't append the CWD to the beginning of the path
        - formalizePath : Boolean <False>
            - only formalizes the path if the pathOrString was of type Path
        - doPrint : Boolean <False>
            - prints the path for debugging
    ---
    Returns:
        - string path
    """
    
    # type check for prependCWD
    if not isinstance(prependCWD, bool):
        raise TypeError(f"value for variable 'prependCWD' was not of type Boolean: {type(prependCWD)}")

    # type check for formalizePath
    if not isinstance(formalizePath, bool):
        raise TypeError(f"value for variable 'formalizePath' was not of type Boolean: {type(formalizePath)}")

    # type check for pathOrString
    pathString = ""
    if isinstance(pathOrString, Path): # if path
        if (prependCWD == True): # if CWD
            # prepend cwd and root path (no first slash)
            pathString = pathOrString.getPathPrependTemp(cwd(), doFormalize=formalizePath, withFirstSlash=False)
        else:
            pathString = pathOrString.getPath(doFormalize=formalizePath)
    elif isinstance(pathOrString, str): # if string
        if (prependCWD == True): pathString += cwd() # path prepension
        if (
            (not pathOrString.startswith("\\")) # doesn't start with slash already
            and (not pathOrString[1] == ":") # not root implicitly
        ): pathString += "\\" # insert slash between path and CWD if needed
        pathString += pathOrString # path extension to CWD
    else: # incorrect
        raise TypeError(f"value for variable 'pathOrString' was not of type Path or String: {type(pathOrString)}")
    
    # check for ending in .json
    if not pathString.endswith(".json"):
        pathString += ".json"

    # print if doPrint true
    if (doPrint == True):
        print(f"path: {pathString}")

    # return stringPath
    return pathString

def __targetPathTypeCheck(
        targetPath:Union[list, tuple]
    ) -> list:
    # type check targetPath
    if isinstance(targetPath, str): # check if it's a string
        targetPath = [targetPath]
    if isinstance(targetPath, tuple): # if tuple, convert to list
        targetPath = list(targetPath)
    if not isinstance(targetPath, list): # if not list
        raise TypeError(f"value for variable 'targetPath' was not of type list or tuple: {type(targetPath)}")

    # type check sub-items of target path (must all be string or int in the case of array)
    if any(
        (
            (not isinstance(value, str))
            and (not isinstance(value, int))
        )
        for value in targetPath
    ):
        raise TypeError("at least one value in variable 'targetPath' was not of type string")
    
    # return path
    return targetPath

def __findReferenceSpaceFromTargetPath(
        dictionary:dict,
        targetPath:Union[list, tuple], 
        *, 
        doPrint:bool=False
    ) -> tuple[dict, str]:
    """
    Description:
        backend; runs through the dictionary to find the targetPath and returns reference values which can be used to assign values into the full dictionary at a dynamic amount of keys into the dictionary
    ---
    Arguments:
        - dictionary : Dictionary <>
            - the data to target into
        - targetPath : List or Tuple <>
            - a List, Tuple or string of name(s) to get to the target data
        - doPrint : Boolean <False>
            - prints the path for debugging
    ---
    Returns:
        - a tuple of format, (dictionary reference, key for dictionary reference)
    """
    
    # function for printing most recent data
    def printMostRecent():
        if (doPrint == True):
            print(f"most recently targetable data: \n{dictionary}")
    
    # get sub (shrinkable) and last (last shrinkable)
    subDictionary = dictionary # makes sure data it never entered
    lastDictionary = dictionary # reference only used if write mode

    # attempt to find target
    while True:
        # check if there's no remaining targets in the targetPath
        if (len(targetPath) == 0): break

        # get the curr target
        currTarget = targetPath.pop(0)
        
        if isinstance(subDictionary, dict):
            # check if target is in the dict data
            if (currTarget not in subDictionary.keys()):
                printMostRecent()
                raise KeyError(f"the target, '{currTarget}', could not be found in the JSON data when reading for targetPath")
        elif isinstance(subDictionary, list):
            # check if target is in the dict data
            if not (0 <= currTarget < len(subDictionary)):
                printMostRecent()
                raise KeyError(f"the target, '{currTarget}', is out of bounds of the read JSON list data: (of length) {len(dictionary)}")
        else:
            printMostRecent()
            raise KeyError(f"the dictionary format doesn't match the target attempting to be found")

        # set the last data (only if write mode)
        lastDictionary = subDictionary

        # target must exist, so shrink data to this target
        subDictionary = subDictionary[currTarget]

    return (lastDictionary, currTarget)

def __forContent(
        pathOrString:Union[Path, str], 
        targetPath:Union[list, tuple], 
        content:dict=None,
        prependCWD:bool=True, 
        *, 
        formalizePath:bool=False, 
        prexistingVerifiedPathString=None,
        doPrint:bool=False
    ) -> dict:
    """
    Description:
        backend function for either reading or writing to contect within a dictionary
    ---
    Arguments:
        - pathOrString : Path or String <>
            - a Path or string path to the file to be opened
        - content : Dictionary <>
            - the content to be written
            - tuples will be converted to lists
            - non-string keys will be converted to string keys
        - prependCWD : Boolean <True>
            - true: appends the CWD to the beginning of the path
            - false: doesn't append the CWD to the beginning of the path
        - formalizePath : Boolean <False>
            - only formalizes the path if the pathOrString was of type Path
        - prexistingVerifiedPathString : String <None>
            - None: normal path processing
            - Other: assumes prexistingVerifiedPathString is already verified and uses it
        - doPrint : Boolean <False>
            - prints the path for debugging
    ---
    Returns:
        - if read mode, the targeted data
        - if write mode, the full data with the modified target data section
    """

    # get the content mode
    doWrite = (content != None)

    # type check target path
    targetPath = __targetPathTypeCheck(targetPath)

    # read all json data
        # uses prexisting to avoid duplicately pricessing the pathString when using writeMode
    data = __readAll(pathOrString, prependCWD, formalizePath, doPrint=doPrint, prexistingVerifiedPathString=prexistingVerifiedPathString)

    # find subdata reference and key target    
    (referenceData, key) = __findReferenceSpaceFromTargetPath(data, targetPath, doPrint=doPrint)

    # if read mode
    if (doWrite == False):
        # return shrunken data
        return referenceData[key]
    # write mode
    else:
        # if the targetPath is empty
        if (len(targetPath) == 0):
            # assign all data to the content
            data = content
        else:
            # use data as a refernce and re-assign to the reference
            referenceData[key] = content

        # return full data
        return data

def __readAll(
        pathOrString:Union[Path, str], 
        prependCWD:bool=True, 
        formalizePath:bool=False,
        *, 
        prexistingVerifiedPathString:str=None,
        doPrint:bool=False
    ) -> dict:
    """
    Description:
        backend function for reading all Json and doing type checks
    ---
    Arguments:
        - pathOrString : Path or String <>
            - a Path or string path to the file to be opened
        - prependCWD : Boolean <True>
            - true: appends the CWD to the beginning of the path
            - false: doesn't append the CWD to the beginning of the path
        - formalizePath : Boolean <False>
            - only formalizes the path if the pathOrString was of type Path
        - prexistingVerifiedPathString : String <None>
            - None: normal path processing
            - Other: assumes prexistingVerifiedPathString is already verified and uses it
        - doPrint : Boolean <False>
            - prints the path for debugging
    ---
    Returns:
        - a dict object read from the specified file
    """
    
    # set path string based off of if one prexists
    pathString = None
    if (prexistingVerifiedPathString != None):
        # already type checked
        pathString = prexistingVerifiedPathString
    else:
        # type check and and process path
        pathString = __processAndTypeCheckPath(pathOrString, prependCWD, formalizePath, doPrint=doPrint)
    
    # open file and convert contents to json
    with open(pathString, 'r') as file:
        # check if the file is empty by reading the first character
        if not file.read(1):
            raise ValueError(f"the file attempting to be read is emtpy: '{pathString}'")
        file.seek(0) # reset the read pointer to 0

        # read as json
        data = json.load(file)

        # return data
        return data

# - reads -

def readAll(
        pathOrString:Union[Path, str], 
        prependCWD:bool=True, 
        *, 
        formalizePath:bool=False, 
        doPrint:bool=False
    ) -> dict:
    """
    Description:
        function for reading all contents of a Json file as dictionary
    ---
    Arguments:
        - pathOrString : Path or String <>
            - a Path or string path to the file to be opened
        - prependCWD : Boolean <True>
            - true: appends the CWD to the beginning of the path
            - false: doesn't append the CWD to the beginning of the path
        - formalizePath : Boolean <False>
            - only formalizes the path if the pathOrString was of type Path
        - doPrint : Boolean <False>
            - prints the path for debugging
    ---
    Returns:
        - a dict object read from the specified file
    """

    return __readAll(pathOrString, prependCWD, formalizePath, doPrint=doPrint)

def readFor(
        pathOrString:Union[Path, str], 
        targetPath:Union[list, tuple], 
        prependCWD:bool=True,
        *, 
        formalizePath:bool=False, 
        doPrint:bool=False
    ):
    """
    Description:
        function for reading specific contents of a Json file using a target path
    ---
    Arguments:
        - pathOrString : Path or String <>
            - a Path or string path to the file to be opened
        - targetPath : List or Tuple <>
            - a List, Tuple or string of name(s) to get to the target data
        - prependCWD : Boolean <True>
            - true: appends the CWD to the beginning of the path
            - false: doesn't append the CWD to the beginning of the path
        - formalizePath : Boolean <False>
            - only formalizes the path if the pathOrString was of type Path
        - doPrint : Boolean <False>
            - prints the path for debugging
    ---
    Returns:
        - a dict object read from the specified file
    """

    # run forContent in read mode (where content is set to None)
    return __forContent(pathOrString, targetPath, None, prependCWD, formalizePath=formalizePath, doPrint=doPrint)
    
# - writes -

def writeAll(
        pathOrString:Union[Path, str], 
        content:dict, 
        prependCWD:bool=True, 
        *, 
        formalizePath:bool=False, 
        doPrint:bool=False
    ) -> None:
    """
    Description:
        function for writing all contents to a Json file
    ---
    Arguments:
        - pathOrString : Path or String <>
            - a Path or string path to the file to be opened
        - content : Dictionary <>
            - the content to be written
            - tuples will be converted to lists
            - non-string keys will be converted to string keys
        - prependCWD : Boolean <True>
            - true: appends the CWD to the beginning of the path
            - false: doesn't append the CWD to the beginning of the path
        - formalizePath : Boolean <False>
            - only formalizes the path if the pathOrString was of type Path
        - doPrint : Boolean <False>
            - prints the path for debugging
    ---
    Returns:
        - nothing, writes the file
    """

    # type check content
    if (not isinstance(content, dict)) and (not isinstance(content, list)):
        raise TypeError(f"value for variable 'content' was not of type Dictionary: {type(formalizePath)}")

    # type check and process path
    pathString = __processAndTypeCheckPath(pathOrString, prependCWD, formalizePath, doPrint=doPrint)

    # open file and convert contents to json
    with open(pathString, 'w') as file:
        file.write(json.dumps(content))

def writeFor(
        pathOrString:Union[Path, str], 
        targetPath:Union[list, tuple], 
        content:dict, 
        prependCWD:bool=True, 
        *, 
        formalizePath:bool=False, 
        doPrint:bool=False
    ) -> None:
    """
    Description:
        function for writing specific contents to a Json file using a target path
    ---
    Arguments:
        - pathOrString : Path or String <>
            - a Path or string path to the file to be opened
        - content : Dictionary <>
            - the content to be written
            - tuples will be converted to lists
            - non-string keys will be converted to string keys
        - targetPath : List or Tuple <>
            - a List, Tuple or string of name(s) to get to the target data
        - prependCWD : Boolean <True>
            - true: appends the CWD to the beginning of the path
            - false: doesn't append the CWD to the beginning of the path
        - formalizePath : Boolean <False>
            - only formalizes the path if the pathOrString was of type Path
        - doPrint : Boolean <False>
            - prints the path for debugging
    ---
    Returns:
        - a dict object read from the specified file
    """

    # type check content
    if (not isinstance(content, dict)) and (not isinstance(content, list)):
        raise TypeError(f"value for variable 'content' was not of type Dictionary: {type(formalizePath)}")

    # type check and get path
    pathString = __processAndTypeCheckPath(pathOrString, prependCWD, formalizePath, doPrint=doPrint)

    # run forContent in write mode (where content is set to something)
    data = __forContent(pathOrString, targetPath, content, prependCWD, formalizePath=formalizePath, doPrint=doPrint, prexistingVerifiedPathString=pathString)

    # write updated data
    with open(pathString, 'w') as file:
        file.write(json.dumps(data))
    
# - utilities -

def castFor(
        dictionary:dict, 
        targetPath:Union[list, tuple], 
        castToType, 
        castKeys:bool=False, 
        targetSubValues:bool=False, 
        *, 
        doPrint:bool=False
    ) -> dict:
    """
    Description:
        casts all keys at the targeted position to the specified type
    ---
    Arguments:
        - dictionary : Dictionary <>
            - the dictionary to cast from and to
        - targetPath : List or Tuple <>
            - a List, Tuple or string of name(s) to get to the target data
        - castToType : a type to cast to <>
        - castKeys : Boolean <False>
            - whether to cast keys or values
            - True: casts the key(s) specified
            - False: casts the value(s) associated with the specified key
        - targetSubValues : Boolean <False>
            - whether to cast the targeted key or cast the keys in the value of the target
            - True: casts the keys or values of the list/dict associated with the target
                - if the target is not a dictionary, values will always be casted instead
                - if the target is not a dictionary or list, will always cast the value rather than sub-values/keys
            - False: casts the specified key (last thing in targetPath)
    --- 
    Returns
        - nothing, directly modified the passed dictionary
    """

    # type check dictionary
    if (not isinstance(dictionary, dict)) and (not isinstance(dictionary, list)):
        raise TypeError(f"value for variable 'dictionary' was not of type Dictionary: {type(dictionary)}")
    
    # type check castkeys
    if not isinstance(castKeys, bool):
        raise TypeError(f"value for variable 'castKeys' was not of type Boolean: {type(castKeys)}")
    
    # type check targetSubValues
    if not isinstance(targetSubValues, bool):
        raise TypeError(f"value for variable 'targetSubValues' was not of type Boolean: {type(targetSubValues)}")
    
    # casting function, handles exception with doPrint
    def cast(value):
        try:
            return castToType(value)
        except (ValueError, TypeError):
            if (doPrint == True):
                print(f"attempting to cast '{value}' to type '{castToType}' failed: {referenceData}")
                raise ValueError(f"could not cast value '{value}' to '{castToType}'; are you sure this value can be casted to this type?")

    # type check target path
    targetPath = __targetPathTypeCheck(targetPath)

    # find subdata reference and key target
    dictionaryCopy = deepcopy(dictionary) # copied dict ensures we dont update the original dict
    (referenceData, referenceKey) = __findReferenceSpaceFromTargetPath(dictionaryCopy, targetPath, doPrint=doPrint)

    # -- casting area --

    # check whether or not to target sub-values
    if (targetSubValues == True): # targets sub-values
        # check if the type of target value is one which has subvalues
        if isinstance(referenceData[referenceKey], dict): # is a dictionary, determine to cast keys or values
            if (castKeys == True): # cast the keys
                # take a copy of the reference data so the content/assignment of the reference doesn't change during looping
                referenceDataValueCopy = deepcopy(referenceData[referenceKey])

                # for each k, v in the copy
                for key, value in referenceDataValueCopy.items():
                    referenceData[referenceKey][cast(key)] = value
                    del referenceData[referenceKey][key]

            else: # cast the values
                for key, value in referenceData[referenceKey].items():
                    referenceData[referenceKey][key] = cast(value)

        elif isinstance(referenceData[referenceKey], list): # is a list, always cast list values
            for i, value in enumerate(referenceData[referenceKey]):
                referenceData[referenceKey][i] = cast(value)

        else: # not list or dict, always cast value
            referenceData[referenceKey] = cast(referenceData[referenceKey])

    else: # targets self
        # check to cast keys or values
        if (castKeys == True): # casts self key
            referenceData[cast(referenceKey)] = referenceData[referenceKey]
            del referenceData[referenceKey]

        else: # casts the value
            referenceData[referenceKey] = cast(referenceData[referenceKey])

    # return copy dictionary after casting
    return dictionaryCopy

def referenceFor(
        dictionary:dict, 
        targetPath:Union[list, tuple], 
        *, 
        doPrint:bool=False
    ):
    """
    Description:
        gets a reference from the targetPath and returns reference values, value and the key for that value
    ---
    Arguments:
        - dictionary : Dictionary <>
            - the data to target into
        - targetPath : List or Tuple <>
            - a List, Tuple or string of name(s) to get to the target data
        - doPrint : Boolean <False>
            - prints the path for debugging
    ---
    Returns:
        - a tuple of format, (dictionary reference, key for dictionary reference)
    """

    # type check dictionary
    if (not isinstance(dictionary, dict)) and (not isinstance(dictionary, list)):
        raise TypeError(f"value for variable 'dictionary' was not of type Dictionary: {type(dictionary)}")
    
    # type check target path
    targetPath = __targetPathTypeCheck(targetPath)

    return __findReferenceSpaceFromTargetPath(dictionary, targetPath, doPrint=doPrint)

def removeFor(
        dictionary:dict, 
        targetPath:Union[list, tuple], 
        *, 
        doPrint:bool=False
    ):
    """
    Description:
        deletes the value from the given dictionary at the target path
    ---
    Arguments:
        - dictionary : Dictionary <>
            - the data to target into
        - targetPath : List or Tuple <>
            - a List, Tuple or string of name(s) to get to the target data
        - doPrint : Boolean <False>
            - prints the path for debugging
    ---
    Returns:
        - a dictionary with the value removed
    """

    # type check dictionary
    if (not isinstance(dictionary, dict)) and (not isinstance(dictionary, list)):
        raise TypeError(f"value for variable 'dictionary' was not of type Dictionary: {type(dictionary)}")
    
    # type check target path
    targetPath = __targetPathTypeCheck(targetPath)

    # find reference and key target
    dictionaryCopy = deepcopy(dictionary) # copied dict ensures we dont update the original dict
    (referenceData, referenceKey) = __findReferenceSpaceFromTargetPath(dictionaryCopy, targetPath, doPrint=doPrint)

    # delete
    del referenceData[referenceKey]

    # return copy
    return dictionaryCopy
