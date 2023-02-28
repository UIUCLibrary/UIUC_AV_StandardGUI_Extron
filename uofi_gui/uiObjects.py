from typing import TYPE_CHECKING, Dict, Tuple, List, Union, Callable
if TYPE_CHECKING:
    from uofi_gui import GUIController

## Begin ControlScript Import --------------------------------------------------
from extronlib.device import UIDevice
from extronlib.ui import Button, Knob, Label, Level, Slider
from extronlib.system import MESet, File
## End ControlScript Import ----------------------------------------------------
##
## Begin Python Imports --------------------------------------------------------
import json
import sys
TESTING = ('unittest' in sys.modules.keys())

## End Python Imports ----------------------------------------------------------
##
## Begin User Import -----------------------------------------------------------
#### Custom Code Modules
from uofi_gui.activityControls import ActivityController
from uofi_gui.sourceControls import SourceController
from uofi_gui.headerControls import HeaderController
from uofi_gui.systemHardware import SystemStatusController
from uofi_gui.techControls import TechMenuController
from uofi_gui.pinControl import PINController
from uofi_gui.keyboardControl import KeyboardController
from uofi_gui.deviceControl import CameraController, DisplayController, AudioController
from uofi_gui.scheduleControls import AutoScheduleController

#### Extron Global Scripter Modules

## End User Import -------------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------

class ExUIDevice(UIDevice):
    def __init__(self, GUIHost: 'GUIController', DeviceAlias: str, PartNumber: str = None) -> object:
        UIDevice.__init__(DeviceAlias, PartNumber)
        self.GUIHost = GUIHost
        self.Id = DeviceAlias
        self.TP_Lights = Button(self, 65533)
        self.TP_Lights.StateIds = \
            {
                'red': 16711680,
                'green': 65280,
                'off': 0
            }
        self.Btns = {}
        self.Btn_Grps = {}
        self.Knobs = {}
        self.Lvls = {}
        self.Slds = {}
        self.Lbls = {}
        
        self.ModalPageList = \
            [
                "Modal-Scheduler",
                "Modal-ScnCtl",
                "Modal-SrcCtl-Camera",
                "Modal-SrcCtl-WPD",
                "Modal-SrcErr"
            ]
        self.PopoverPageList = \
            [
                "Popover-Ctl-Alert",
                "Popover-Ctl-Audio_1",
                "Popover-Ctl-Camera_0",
                "Popover-Ctl-Camera_1",
                "Popover-Ctl-Camera_2",
                "Popover-Ctl-Help",
                "Popover-Ctl-Lights_0",
                "Popover-Room"
            ]
        self.PopupGroupList = \
            [
                "Tech-Popups",
                "Tech-Menus",
                "Activity-Menus",
                "Activity-Open-Menus",
                "Source-Menus",
                "Source-Controls",
                "Audio-Controls",
                "Activity-Controls"
            ]
        
        #### Activity Control Module
        self.ActCtl = ActivityController(self)
        
        #### Source Control Module
        self.SrcCtl = SourceController(self)
        
        #### Header Control Module
        self.HdrCtl = HeaderController(self)
        
        #### Tech Menu Control Module
        self.TechCtl = TechMenuController(self)
        
        #### System Status Module
        self.StatusCtl = SystemStatusController(self)
        
        #### Camera Controller Module
        if self.GUIHost.CameraSwitcherId is not None:
            self.CamCtl = CameraController(self)
        
        #### Display Control Module
        self.DispCtl = DisplayController(self)
        
        #### Audio Control Module
        self.AudioCtl = AudioController(self)
        
        #### Schedule Module
        self.SchedCtl = AutoScheduleController(self.TP_Main)
        
        #### Keyboard Module
        self.KBCtl = KeyboardController(self)
        
        #### PIN Code Module
        self.TechPINCtl = PINController(self,
                                    self.GUIHost.TechPIN, 
                                    'Tech',
                                    self.TechCtl.OpenTechMenu)

    def BlinkLights(self, Rate: str='Medium', StateList: List=None):
        if StateList is None:
            StateList = [self.TP_Lights.StateIds['off'], self.TP_Lights.StateIds['red']]
        
        allowedRates = ['Slow', 'Medium', 'Fast']
        if Rate not in allowedRates:
            raise ValueError('Rate must be one of {}'.format(allowedRates))
        
        self.TP_Lights.SetBlinking(Rate, StateList)
        
    def LightsOff(self):
        self.TP_Lights.SetState(self.TP_Lights.StateIds['off'])
    
    def BuildAll(self, jsonObj: Dict = {}, jsonPath: str = '') -> None:
        self.BuildButtons(jsonObj=jsonObj, jsonPath=jsonPath)
        self.BuildButtonGroups(jsonObj=jsonObj, jsonPath=jsonPath)
        self.BuildKnobs(jsonObj=jsonObj, jsonPath=jsonPath)
        self.BuildLevels(jsonObj=jsonObj, jsonPath=jsonPath)
        self.BuildSliders(jsonObj=jsonObj, jsonPath=jsonPath)
        self.BuildButtons(jsonObj=jsonObj, jsonPath=jsonPath)
        self.BuildLabels(jsonObj=jsonObj, jsonPath=jsonPath)
        
    def BuildButtons(self,
                    jsonObj: Dict = {},
                    jsonPath: str = "") -> None:
        """Builds a dictionary of Extron Buttons from a json object or file

        Args (only one json arg required, jsonObj takes precedence over jsonPath):
            jsonObj (Dict, optional): The json object containing button information.
                Defaults to {}.
            jsonPath (str, optional): The path to the file containing json formatted
                button information. Defaults to "".

        Raises:
            ValueError: if specified fileat jsonPath does not exist
            ValueError: if neither jsonObj or jsonPath are specified
        """

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
                btnDict[button['Name']] = Button(self, button['ID'])
            elif button['holdTime'] != None and button['repeatTime'] == None:
                btnDict[button['Name']] = Button(self, button['ID'],
                                                    holdTime = button['holdTime'])
                btnDict[button['Name']].holdTime = button['holdTime']
            elif button['holdTime'] == None and button['repeatTime'] != None:
                btnDict[button['Name']] = Button(self, button['ID'], 
                                                    repeatTime = button['repeatTime'])
                btnDict[button['Name']].repeatTime = button['repeatTime']
            elif button['holdTime'] != None and button['repeatTime'] != None:
                btnDict[button['Name']] = Button(self, button['ID'],
                                                    holdTime = button['holdTime'],
                                                    repeatTime = button['repeatTime'])
                btnDict[button['Name']].holdTime = button['holdTime']
                btnDict[button['Name']].repeatTime = button['repeatTime']
            
            if TESTING is True:
                btnDict[button['Name']].Name = button['Name']
        ## return btnDict
        self.Btns = btnDict

    def BuildButtonGroups(self,
                        jsonObj: Dict = {},
                        jsonPath: str = "")-> None:
        """Builds a dictionary of mutually exclusive button groups from a json
            object or file

        Args (only one json arg required, jsonObj takes precedence over jsonPath):
            jsonObj (Dict, optional): The json object containing button group
                information. Defaults to {}.
            jsonPath (str, optional): The path to the file containing json formatted
                button group information. Defaults to "".

        Raises:
            ValueError: if specified file at jsonPath does not exist
            ValueError: if neither jsonObj or jsonPath are specified
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
                btnList.append(self.Btns[btn])
            grpDict[group['Name']] = MESet(btnList)
        
        ## return grpDict
        self.Btn_Grps = grpDict

    def BuildKnobs(self,
                jsonObj: Dict = {},
                jsonPath: str = "")-> None:
        """Builds a dictionary of Extron Knobs from a json object or file

        Args (only one json arg required, jsonObj takes precedence over jsonPath):
            jsonObj (Dict, optional): The json object containing knob information.
                Defaults to {}.
            jsonPath (str, optional): The path to the file containing json formatted
                knob information. Defaults to "".

        Raises:
            ValueError: if specified fileat jsonPath does not exist
            ValueError: if neither jsonObj or jsonPath are specified
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
            knobDict[knob['Name']] = Knob(self, knob['ID'])
        
        ## return knobDict
        self.Knobs = knobDict

    def BuildLevels(self,
                    jsonObj: Dict = {},
                    jsonPath: str = "")-> None:
        """Builds a dictionary of Extron Levels from a json object or file

        Args:
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
            lvlDict[lvl['Name']] = Level(self, lvl['ID'])
            
            if TESTING is True:
                lvlDict[lvl['Name']].Name = lvl['Name']
        
        ## return lvlDict
        self.Lvls = lvlDict

    def BuildSliders(self,
                    jsonObj: Dict = {},
                    jsonPath: str = "")-> None:
        """Builds a dictionary of Extron Sliders from a json object or file

        Args (only one json arg required, jsonObj takes precedence over jsonPath):
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
            sliderDict[slider['Name']] = Slider(self, slider['ID'])
            
            if TESTING is True:
                sliderDict[slider['Name']].Name = slider['Name']
        
        ## return sliderDict
        self.Slds = sliderDict

    def BuildLabels(self,
                    jsonObj: Dict = {},
                    jsonPath: str = "")-> None:
        """Builds a dictionary of Extron Labels from a json object or file

        Args (only one json arg required, jsonObj takes precedence over jsonPath):
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
            labelDict[lbl['Name']] = Label(self, lbl['ID'])
            
            if TESTING is True:
                labelDict[lbl['Name']].Name = lbl['Name']
        
        ## return labelDict
        self.Lbls = labelDict

## End Function Definitions ----------------------------------------------------
