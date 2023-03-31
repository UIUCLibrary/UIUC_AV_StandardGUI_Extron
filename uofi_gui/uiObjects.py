from typing import TYPE_CHECKING, Dict, Tuple, List, Union, Callable
if TYPE_CHECKING: # pragma: no cover
    from uofi_gui import GUIController

## Begin ControlScript Import --------------------------------------------------
from extronlib import event
from extronlib.device import UIDevice
from extronlib.ui import Button, Knob, Label, Level, Slider
from extronlib.system import MESet, File
from extronlib.system import Wait
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
from uofi_gui.sourceControls import SourceController
from uofi_gui.headerControls import HeaderController
from uofi_gui.systemHardware import SystemStatusController
from uofi_gui.techControls import TechMenuController
from uofi_gui.pinControl import PINController
from uofi_gui.keyboardControl import KeyboardController
from uofi_gui.deviceControl import CameraController, DisplayController, AudioController
from uofi_gui.scheduleControls import AutoScheduleController

#### Extron Global Scripter Modules

from utilityFunctions import Log, RunAsync, debug

## End User Import -------------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------

class ExUIDevice(UIDevice):
    def __init__(self, GUIHost: 'GUIController', DeviceAlias: str, PartNumber: str = None) -> object:
        UIDevice.__init__(self, DeviceAlias, PartNumber)
        self.GUIHost = GUIHost
        self.Id = DeviceAlias
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
        
        self.HideAllPopups()
        
    def InitializeUIControllers(self):        
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
        self.SchedCtl = AutoScheduleController(self)
        
        #### Keyboard Module
        self.KBCtl = KeyboardController(self)
        
        #### PIN Code Module
        self.TechPINCtl = PINController(self,
                                        self.GUIHost.TechPIN, 
                                        'Tech',
                                        self.TechCtl.OpenTechMenu)

    def BlinkLights(self, Rate: str='Medium', StateList: List=None, Timeout: Union[int, float]=0):
        if StateList is None:
            StateList = ['Off', 'Red']
        
        for State in StateList:
            if State not in ['Off', 'Green', 'Red']:
                raise ValueError('State must be one of "Off", "Red", or "Green"')
        
        allowedRates = ['Slow', 'Medium', 'Fast']
        if Rate not in allowedRates:
            raise ValueError('Rate must be one of {}'.format(allowedRates))
        
        # self.TP_Lights.SetBlinking(Rate, StateList) 
        self.SetLEDBlinking(65533, Rate, StateList)
        
        if Timeout > 0:
            Wait(float(Timeout), self.LightsOff())
    
    def SetLights(self, State, Timeout: Union[int, float]=0):
        if State not in ['Off', 'Green', 'Red']:
            raise ValueError('State must be one of "Off", "Red", or "Green"')
        self.SetLEDState(65533, State)
        
        if Timeout > 0:
            Wait(float(Timeout), self.LightsOff())
    
    def LightsOff(self):
        # self.TP_Lights.SetState(self.TP_Lights.StateIds['off'])
        self.SetLEDState(65533, 'Off')
    
    def BuildAll(self, jsonObj: Dict = {}, jsonPath: str = '') -> None:
        # Log('Build All Buttons for TP: {}'.format(self.Id))
        self.BuildButtons(jsonObj=jsonObj, jsonPath=jsonPath)
        self.BuildButtonGroups(jsonObj=jsonObj, jsonPath=jsonPath)
        self.BuildKnobs(jsonObj=jsonObj, jsonPath=jsonPath)
        self.BuildLevels(jsonObj=jsonObj, jsonPath=jsonPath)
        self.BuildSliders(jsonObj=jsonObj, jsonPath=jsonPath)
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
            ValueError: if specified file at jsonPath does not exist
            ValueError: if neither jsonObj or jsonPath are specified
        """
        
        ## do not expect both jsonObj and jsonPath
        ## jsonObj should take priority over jsonPath
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
        
        ## format button info into self.Btns
        for button in jsonObj['buttons']:
            btnName = button['Name']
            button.pop('Name')
            self.Btns[btnName] = Button(self, **button)
            self.Btns[btnName].holdTime = button['holdTime']
            self.Btns[btnName].repeatTime = button['repeatTime']
                
            if TESTING is True: # TODO: figure out how to make this work in the button class
                self.Btns[btnName].Name = btnName
                
            self.Btns[btnName].SetState(0)
            
            @event(self.Btns[btnName], 'Pressed')
            def TempBtnHandler(button: 'Button', event: str): # pragma: no cover
                Log('Unconfigured Press Action: {} ({}, {})'.format(button.Name, button.ID, button))

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

        ## create MESets and build self.Btn_Grps
        for group in jsonObj['buttonGroups']:
            ## reset btnList and populate it from the jsonObj
            btnList = []
            for btn in group['Buttons']:
                ## get button objects from Dict and add to list
                btnList.append(self.Btns[btn])
            self.Btn_Grps[group['Name']] = MESet(btnList)
            
        # Log(['Button: {} ({}, {})'.format(btn.Name, btn.ID, btn) for btn in self.Btn_Grps['Activity-Select'].Objects])

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
            ValueError: if specified file at jsonPath does not exist
            ValueError: if neither jsonObj or jsonPath are specified
        """    
        
        ## do not expect both jsonObj and jsonPath
        ## jsonObj should take priority over jsonPath

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
        
        
        ## format knob info into self.Knobs
        for knob in jsonObj['knobs']:
            self.Knobs[knob['Name']] = Knob(self, knob['ID'])

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
            ValueError: if specified file at jsonPath does not exist
            ValueError: if neither jsonObj or jsonPath are specified
        """    
        
        ## do not expect both jsonObj and jsonPath
        ## jsonObj should take priority over jsonPath
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
        
        ## format level info into self.Lvls
        for lvl in jsonObj['levels']:
            self.Lvls[lvl['Name']] = Level(self, lvl['ID'])
            
            if TESTING is True:
                self.Lvls[lvl['Name']].Name = lvl['Name']

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
            ValueError: if specified file at jsonPath does not exist
            ValueError: if neither jsonObj or jsonPath are specified
        """    
        
        ## do not expect both jsonObj and jsonPath
        ## jsonObj should take priority over jsonPath
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
            
        ## format slider info into self.Slds
        for slider in jsonObj['sliders']:
            self.Slds[slider['Name']] = Slider(self, slider['ID'])
            
            if TESTING is True:
                self.Slds[slider['Name']].Name = slider['Name']

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
            ValueError: if specified file at jsonPath does not exist
            ValueError: if neither jsonObj or jsonPath are specified
        """    
        
        ## do not expect both jsonObj and jsonPath
        ## jsonObj should take priority over jsonPath
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
        
        ## format label info into self.Lbls
        for lbl in jsonObj['labels']:
            self.Lbls[lbl['Name']] = Label(self, lbl['ID'])
            
            if TESTING is True:
                self.Lbls[lbl['Name']].Name = lbl['Name']

## End Function Definitions ----------------------------------------------------
