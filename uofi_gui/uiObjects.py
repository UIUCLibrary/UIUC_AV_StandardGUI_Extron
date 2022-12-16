## Begin ControlScript Import --------------------------------------------------
from extronlib import event, Version
from extronlib.device import eBUSDevice, ProcessorDevice, UIDevice
from extronlib.interface import (CircuitBreakerInterface, ContactInterface,
    DigitalInputInterface, DigitalIOInterface, EthernetClientInterface,
    EthernetServerInterfaceEx, FlexIOInterface, IRInterface, PoEInterface,
    RelayInterface, SerialInterface, SWACReceptacleInterface, SWPowerInterface,
    VolumeInterface)
from extronlib.ui import Button, Knob, Label, Level, Slider
from extronlib.system import (Email, Clock, MESet, Timer, Wait, File, RFile,
    ProgramLog, SaveProgramLog, Ping, WakeOnLan, SetAutomaticTime, SetTimeZone)

print(Version()) ## Sanity check ControlScript Import
## End ControlScript Import ----------------------------------------------------
##
## Begin Python Imports --------------------------------------------------------
from datetime import datetime
import json
from typing import Dict, Tuple, List, Union, Callable
## End Python Imports ----------------------------------------------------------
##
## Begin User Import -----------------------------------------------------------
#### Custom Code Modules
import vars
#### Extron Global Scripter Modules

## End User Import -------------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------


def BuildButtons(UIHost: UIDevice,
                 jsonObj: Dict = {},
                 jsonPath: str = "") -> Dict:
    """Builds a dictionary of Extron Buttons from a json object or file

    Args (only one json arg required, jsonObj takes precedence over jsonPath):
        UIHost (extronlib.device): UIHost to which the buttons are assigned
        jsonObj (Dict, optional): The json object containing button information.
            Defaults to {}.
        jsonPath (str, optional): The path to the file containing json formatted
            button information. Defaults to "".

    Raises:
        TypeError: if UIHost is not an extron.device.UIDevice object
        ValueError: if specified fileat jsonPath does not exist
        ValueError: if neither jsonObj or jsonPath are specified

    Returns:
        Dict: Returns dictionary object of buttons on success
    """

    if type(UIHost) != UIDevice:
        raise TypeError('UIHost must be an extronlib.device.UIDevice object')
    
    ## do not expect both jsonObj and jsonPath
    ## jsonObj should take priority over jsonPath
    btnDict = {}
    print('Building Buttons')
    print(jsonObj)
    print(jsonPath)
    if jsonObj == {} and jsonPath != "": # jsonObj is empty and jsonPath not blank
        if File.Exists(jsonPath): # jsonPath is valid, so load jsonObj from path
            jsonFile = File(jsonPath)
            jsonStr = jsonFile.read()
            jsonFile.close()
            jsonObj = json.loads(jsonStr)
        else: ## jsonPath was invalid, so return none (error)
            raise ValueError('Specified file does not exist')
    elif jsonObj == {} and jsonPath == "":
        raise ValueError('Either jsonObj or jsonPath must be specified')
    
    ## format button info into btnDict
    for button in jsonObj['buttons']:
        ## only sets holdTime or repeatTime for non null/None values
        if button['holdTime'] == None and button['repeatTime'] == None:
            btnDict[button['Name']] = Button(UIHost, button['ID'])
        elif button['holdTime'] != None and button['repeatTime'] == None:
            btnDict[button['Name']] = Button(UIHost, button['ID'],
                                                holdTime = button['holdTime'])
        elif button['holdTime'] == None and button['repeatTime'] != None:
            btnDict[button['Name']] = Button(UIHost, button['ID'], 
                                                repeatTime = button['repeatTime'])
        elif button['holdTime'] != None and button['repeatTime'] != None:
            btnDict[button['Name']] = Button(UIHost, button['ID'],
                                                holdTime = button['holdTime'],
                                                repeatTime = button['repeatTime'])
        if vars.TESTING:
            btnDict[button['Name']].Name = button['Name']
    ## return btnDict
    return btnDict

def BuildButtonGroups(btnDict: Dict,
                      jsonObj: Dict = {},
                      jsonPath: str = "") -> Dict:
    """Builds a dictionary of mutually exclusive button groups from a json
        object or file

    Args (only one json arg required, jsonObj takes precedence over jsonPath):
        btnDict (Dict): The dictionary of available button objects
        jsonObj (Dict, optional): The json object containing button group
            information. Defaults to {}.
        jsonPath (str, optional): The path to the file containing json formatted
            button group information. Defaults to "".

    Raises:
        ValueError: if specified fileat jsonPath does not exist
        ValueError: if neither jsonObj or jsonPath are specified
    
    Returns:
        Dict: Returns a dictionary containing Extron MESet objects on
            success, or None on failure
    """
    ## do not expect both jsonObj and jsonPath
    ## jsonObj should take priority over jsonPath
    grpDict = {}
    
    if jsonObj == {} and jsonPath != "": # jsonObj is empty and jsonPath not blank
        if File.Exists(jsonPath): # jsonPath is valid, so load jsonObj from path
            jsonFile = File(jsonPath)
            jsonStr = jsonFile.read()
            jsonFile.close()
            jsonObj = json.loads(jsonStr)
        else: ## jsonPath was invalid, so return none (error)
            raise ValueError('Specified file does not exist')
    elif jsonObj == {} and jsonPath == "":
        raise ValueError('Either jsonObj or jsonPath must be specified')

    ## create MESets and build grpDict
    for group in jsonObj['buttonGroups']:
        ## reset btnList and populate it from the jsonObj
        btnList = []
        for btn in group['Buttons']:
            ## get button objects from Dict and add to list
            btnList.append(btnDict[btn])
        grpDict[group['Name']] = MESet(btnList)
    
    ## return grpDict
    return grpDict

def BuildKnobs(UIHost: UIDevice,
               jsonObj: Dict = {},
               jsonPath: str = "") -> Dict:
    """Builds a dictionary of Extron Knobs from a json object or file

    Args (only one json arg required, jsonObj takes precedence over jsonPath):
        UIHost (extronlib.device): UIHost to which the knobs are assigned
        jsonObj (Dict, optional): The json object containing knob information.
            Defaults to {}.
        jsonPath (str, optional): The path to the file containing json formatted
            knob information. Defaults to "".

    Raises:
        ValueError: if specified fileat jsonPath does not exist
        ValueError: if neither jsonObj or jsonPath are specified

    Returns:
        Dict: Returns a dictionary containing Extron Knob objects
    """    
    
    ## do not expect both jsonObj and jsonPath
    ## jsonObj should take priority over jsonPath
    knobDict = {}

    if jsonObj == {} and jsonPath != "": # jsonObj is empty and jsonPath not blank
        if File.Exists(jsonPath): # jsonPath is valid, so load jsonObj from path
            jsonFile = File(jsonPath)
            jsonStr = jsonFile.read()
            jsonFile.close()
            jsonObj = json.loads(jsonStr)
        else: ## jsonPath was invalid, so return none (error)
            raise ValueError('Specified file does not exist')
    elif jsonObj == {} and jsonPath == "":
        raise ValueError('Either jsonObj or jsonPath must be specified')
    
    
    ## format knob info into knobDict
    for knob in jsonObj['knobs']:
        knobDict[knob['Name']] = Knob(UIHost, knob['ID'])
    
    ## return knobDict
    return knobDict

def BuildLevels(UIHost: UIDevice,
                jsonObj: Dict = {},
                jsonPath: str = "") -> Dict:
    """Builds a dictionary of Extron Levels from a json object or file

    Args:
        UIHost (extronlib.device): UIHost to which the levels are assigned
        jsonObj (Dict, optional): The json object containing level information.
            Defaults to {}.
        jsonPath (str, optional): The path to the file containing json formatted
            level information. Defaults to "".

    Raises:
        ValueError: if specified fileat jsonPath does not exist
        ValueError: if neither jsonObj or jsonPath are specified

    Returns:
        Dict: Returns a dictionary containing Extron Level objects
    """    
    
    ## do not expect both jsonObj and jsonPath
    ## jsonObj should take priority over jsonPath
    lvlDict = {}

    if jsonObj == {} and jsonPath != "": # jsonObj is empty and jsonPath not blank
        if File.Exists(jsonPath): # jsonPath is valid, so load jsonObj from path
            jsonFile = File(jsonPath)
            jsonStr = jsonFile.read()
            jsonFile.close()
            jsonObj = json.loads(jsonStr)
        else: ## jsonPath was invalid, so return none (error)
            raise ValueError('Specified file does not exist')
    elif jsonObj == {} and jsonPath == "":
        raise ValueError('Either jsonObj or jsonPath must be specified')
    
    ## format level info into lvlDict
    for lvl in jsonObj['levels']:
        lvlDict[lvl['Name']] = Level(UIHost, lvl['ID'])
        
        if vars.TESTING:
            lvlDict[lvl['Name']].Name = lvl['Name']
    
    ## return lvlDict
    return lvlDict

def BuildSliders(UIHost: UIDevice,
                 jsonObj: Dict = {},
                 jsonPath: str = "") -> Dict:
    """Builds a dictionary of Extron Sliders from a json object or file

    Args (only one json arg required, jsonObj takes precedence over jsonPath):
        UIHost (extronlib.device): UIHost to which the sliders are assigned
        jsonObj (Dict, optional): The json object containing slider information.
            Defaults to {}.
        jsonPath (str, optional): The path to the file containing json formatted
            slider information. Defaults to "".

    Raises:
        ValueError: if specified fileat jsonPath does not exist
        ValueError: if neither jsonObj or jsonPath are specified

    Returns:
        Dict: Returns a dictionary containing Extron Slider objects
    """    
    
    ## do not expect both jsonObj and jsonPath
    ## jsonObj should take priority over jsonPath
    sliderDict = {}
    
    if jsonObj == {} and jsonPath != "": # jsonObj is empty and jsonPath not blank
        if File.Exists(jsonPath): # jsonPath is valid, so load jsonObj from path
            jsonFile = File(jsonPath)
            jsonStr = jsonFile.read()
            jsonFile.close()
            jsonObj = json.loads(jsonStr)
        else: ## jsonPath was invalid, so return none (error)
            raise ValueError('Specified file does not exist')
    elif jsonObj == {} and jsonPath == "":
        raise ValueError('Either jsonObj or jsonPath must be specified')
        
    ## format slider info into sliderDict
    for slider in jsonObj['sliders']:
        sliderDict[slider['Name']] = Slider(UIHost, slider['ID'])
        
        if vars.TESTING:
            sliderDict[slider['Name']].Name = slider['Name']
    
    ## return sliderDict
    return sliderDict

def BuildLabels(UIHost: UIDevice,
                jsonObj: Dict = {},
                jsonPath: str = "") -> Dict:
    """Builds a dictionary of Extron Labels from a json object or file

    Args (only one json arg required, jsonObj takes precedence over jsonPath):
        UIHost (extronlib.device): UIHost to which the labels are assigned
        jsonObj (Dict, optional): The json object containing label information.
            Defaults to {}.
        jsonPath (str, optional): The path to the file containing json formatted
            label information. Defaults to "".

    Raises:
        ValueError: if specified fileat jsonPath does not exist
        ValueError: if neither jsonObj or jsonPath are specified

    Returns:
        Dict: Returns a dictionary of Extron Label objects
    """    
    
    ## do not expect both jsonObj and jsonPath
    ## jsonObj should take priority over jsonPath
    labelDict = {}

    if jsonObj == {} and jsonPath != "": # jsonObj is empty and jsonPath not blank
        if File.Exists(jsonPath): # jsonPath is valid, so load jsonObj from path
            jsonFile = File(jsonPath)
            jsonStr = jsonFile.read()
            jsonFile.close()
            jsonObj = json.loads(jsonStr)
        else: ## jsonPath was invalid, so return none (error)
            raise ValueError('Specified file does not exist')
    elif jsonObj == {} and jsonPath == "":
        raise ValueError('Either jsonObj or jsonPath must be specified')
    
    ## format label info into labelDict
    for lbl in jsonObj['labels']:
        labelDict[lbl['Name']] = Label(UIHost, lbl['ID'])
        
        if vars.TESTING:
            labelDict[lbl['Name']].Name = lbl['Name']
    
    ## return labelDict
    return labelDict

## End Function Definitions ----------------------------------------------------
