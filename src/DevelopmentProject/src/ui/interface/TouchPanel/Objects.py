################################################################################
# Copyright © 2023 The Board of Trustees of the University of Illinois
#
# Licensed under the MIT License (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://opensource.org/licenses/MIT
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
################################################################################

## Begin Imports ---------------------------------------------------------------

#### Type Checking
from typing import TYPE_CHECKING, Dict, Tuple, List, Union, Callable
if TYPE_CHECKING: # pragma: no cover
    from extronlib.device import ProcessorDevice, UIDevice, SPDevice, eBUSDevice
    from modules.project.ExtendedDeviceClasses import ExUIDevice, ExEBUSDevice, ExProcessorDevice, ExSPDevice

#### Python imports
import json

#### Extron Library Imports
from extronlib import event
from extronlib.system import MESet, File

#### Project imports
from modules.helper.CommonUtilities import Logger
from modules.project.ExtendedUIClasses import ExButton, ExLabel, ExLabel, ExLevel, ExSlider, ExKnob
from modules.project.Collections import UIObjectCollection
import System

## End Imports -----------------------------------------------------------------
##
## Begin Class Definitions -----------------------------------------------------

class TouchPanelObjects():
    __SelectIdStart = 15000
    def __init__(self) -> None:
        self.__SelectIdCurrent = self.__SelectIdStart + 1
        
        self.Buttons = UIObjectCollection()
        self.Knobs = UIObjectCollection()
        self.Labels = UIObjectCollection()
        self.Levels = UIObjectCollection()
        self.Sliders = UIObjectCollection()
        self.Selects = UIObjectCollection()
        
        self.ButtonGroups = {}
        
        self.ModalPages = []
        self.PopoverPages = []
        self.PopupGroups = []

    def __GetSelectId(self) -> int:
        select = self.__SelectIdCurrent
        self.__SelectIdCurrent = select + 1
        
        return select

    def LoadSelects(self,
                    UIHost: Union['ExUIDevice', 'UIDevice'],
                    jsonObj: Dict = {},
                    jsonPath: str = "") -> Dict:
        
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
        
        for select in jsonObj['selects']:
            # fix attributes for ExButton
            kwargs = dict(select)
            kwargs.pop('Name')
            kwargs.pop('ID')
            
            self.Selects[select['Name']] = ExButton(UIHost=UIHost,
                                                    ID_Name=self.__GetSelectId(),
                                                    **kwargs)
            self.Selects[select['Name']].Name = select['Name']
            self.Selects[select['Name']].SetState(0)
        
    def LoadButtons(self,
                    UIHost: Union['ExUIDevice', 'UIDevice'],
                    jsonObj: Dict = {},
                    jsonPath: str = "") -> Dict:
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
        
        ## format button info into self.Buttons
        for button in jsonObj['buttons']:
            # fix attributes for ExButton
            kwargs = dict(button)
            kwargs.pop('Name')
            kwargs.pop('ID')
            
            self.Buttons[button['Name']] = ExButton(UIHost=UIHost,
                                                    ID_Name=button['ID'],
                                                    **kwargs)
            self.Buttons[button['Name']].SetState(0)

    def LoadButtonGroups(self,
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

        ## create MESets and build self.ButtonGroups
        for group in jsonObj['buttonGroups']:
            ## reset btnList and populate it from the jsonObj
            btnList = []
            for btn in group['Buttons']:
                ## get button objects from Dict and add to list
                btnList.append(self.Buttons[btn])
            self.ButtonGroups[group['Name']] = MESet(btnList)
            
        # Logger.Log(['Button: {} ({}, {})'.format(btn.Name, btn.ID, btn) for btn in self.ButtonGroups['Activity-Select'].Objects])

    def LoadKnobs(self,
                  UIHost: Union['ExUIDevice', 'UIDevice'],
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
            # fix attributes for ExButton
            kwargs = dict(knob)
            kwargs.pop('Name')
            kwargs.pop('ID')
            
            self.Knobs[knob['Name']] = ExKnob(UIHost=UIHost, **kwargs)

    def LoadLevels(self,
                   UIHost: Union['ExUIDevice', 'UIDevice'],
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
            # fix attributes for ExButton
            kwargs = dict(lvl)
            kwargs.pop('Name')
            kwargs.pop('ID')
            
            self.Levels[lvl['Name']] = ExLevel(UIHost=UIHost,
                                               ID_Name=lvl['ID'],
                                               **kwargs)

    def LoadSliders(self,
                    UIHost: Union['ExUIDevice', 'UIDevice'],
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
            # fix attributes for ExButton
            kwargs = dict(slider)
            kwargs.pop('Name')
            kwargs.pop('ID')
            
            self.Sliders[slider['Name']] = ExSlider(UIHost=UIHost,
                                                    ID_Name=slider['ID'],
                                                    **kwargs)

    def LoadLabels(self,
                   UIHost: Union['ExUIDevice', 'UIDevice'],
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
            # fix attributes for ExButton
            kwargs = dict(lbl)
            kwargs.pop('Name')
            kwargs.pop('ID')
            self.Labels[lbl['Name']] = ExLabel(UIHost=UIHost,
                                               ID_Name=lbl['ID'],
                                               **kwargs)

    def LoadModalPages(self,
                       jsonObj: Dict = {},
                       jsonPath: str = "") -> None:
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
        
        self.ModalPages = jsonObj['modalPages']
    
    def LoadPopoverPages(self,
                         jsonObj: Dict = {},
                         jsonPath: str = "") -> None:
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
        
        self.PopoverPages = jsonObj['popoverPages']
    
    def LoadPopupGroups(self,
                        jsonObj: Dict = {},
                        jsonPath: str = "") -> None:
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
        
        self.PopupGroups = jsonObj['popupGroups']
    
## End Class Definitions -------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------

## End Function Definitions ----------------------------------------------------



