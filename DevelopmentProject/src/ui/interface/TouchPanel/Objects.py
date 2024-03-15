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
from typing import TYPE_CHECKING, Dict, List, Union
if TYPE_CHECKING: # pragma: no cover
    from extronlib.device import UIDevice
    from modules.project.ExtendedClasses.Device import ExUIDevice

#### Python imports
import json

#### Extron Library Imports
from extronlib.system import File

#### Project imports
from modules.project.ExtendedClasses.UI import ButtonEx, LabelEx, LevelEx, SliderEx, KnobEx, ButtonEx_Ref
from modules.project.ExtendedClasses.UI.ControlObject import ControlObject
from modules.project.Collections import UIObjectCollection, ControlGroupCollection
from modules.helper.CommonUtilities import Logger

import modules.project.Collections.UISets
import modules.project.callbacks.RefCallbacks
import modules.project.callbacks.PopupCallbacks

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
        self.Refs = UIObjectCollection()
        
        self.ControlGroups = ControlGroupCollection()
        
        self.ModalPages = []
        self.PopoverPages = []
        self.PopupGroups = []

    def __repr__(self) -> str:
        output = {
            "Buttons": self.Buttons,
            "Knobs": self.Knobs,
            "Labels": self.Labels,
            "Levels": self.Levels,
            "Sliders": self.Sliders,
            "Refs": self.Refs,
            "ControlGroups": self.ControlGroups,
            "ModalPages": self.ModalPages,
            "PopoverPages": self.PopoverPages,
            "PopupGroups": self.PopupGroups
        }
        return str(output)

    def __GetSelectId(self) -> int:
        select = self.__SelectIdCurrent
        self.__SelectIdCurrent = select + 1
        
        return select

    def LoadRefs(self,
                    UIHost: Union['ExUIDevice', 'UIDevice'],
                    refDict: Dict) -> List:
        RefList = []
        for ref in refDict:
            # fix attributes for ButtonEx
            kwargs = dict(ref)
            kwargs.pop('Name')
            
            self.Refs[ref['Name']] = ButtonEx_Ref(UIHost=UIHost,
                                               ID_Name=self.__GetSelectId(),
                                               **kwargs)
            self.Refs[ref['Name']].SetRefName(ref['Name'])
            RefList.append(self.Refs[ref['Name']])
        return RefList
        
    def LoadButtons(self,
                    UIHost: Union['ExUIDevice', 'UIDevice'],
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
        
        ## format button info into self.Buttons
        for button in jsonObj['buttons']:
            # fix attributes for ButtonEx
            kwargs = dict(button)
            kwargs.pop('Name')
            kwargs.pop('ID')
            
            self.Buttons[button['Name']] = ButtonEx(UIHost=UIHost,
                                                    ID_Name=button['ID'],
                                                    **kwargs)
            self.Buttons[button['Name']].SetState(0)

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
            # fix attributes for ButtonEx
            kwargs = dict(knob)
            kwargs.pop('Name')
            kwargs.pop('ID')
            
            self.Knobs[knob['Name']] = KnobEx(UIHost=UIHost, **kwargs)

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
            # fix attributes for ButtonEx
            kwargs = dict(lvl)
            kwargs.pop('Name')
            kwargs.pop('ID')
            
            self.Levels[lvl['Name']] = LevelEx(UIHost=UIHost,
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
            # fix attributes for ButtonEx
            kwargs = dict(slider)
            kwargs.pop('Name')
            kwargs.pop('ID')
            
            self.Sliders[slider['Name']] = SliderEx(UIHost=UIHost,
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
            # fix attributes for ButtonEx
            kwargs = dict(lbl)
            kwargs.pop('Name')
            kwargs.pop('ID')
            self.Labels[lbl['Name']] = LabelEx(UIHost=UIHost,
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
        
    def LoadControlGroups(self,
                         UIHost: Union['ExUIDevice', 'UIDevice'],
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

        subGroups = []
        ## create MESets and build self.ButtonGroups
        for group in jsonObj['buttonGroups']:
            kwargs = {"Name": group['Name']}
            CollectionModule = modules.project.Collections.UISets
            Constructor = getattr(CollectionModule, group['Class'])
            
            ## reset btnList and populate it from the jsonObj
            if 'Buttons' in group.keys():
                kwargs['Objects'] = []
                for btn in group['Buttons']:
                    ## get button objects from Dict and add to list
                    kwargs['Objects'].append(self.Buttons[btn])
            
            if 'ButtonLabels' in group.keys():
                kwargs['ObjectLabels'] = []
                for lbl in group['ButtonLabels']:
                    # get label objects from Dict and add to list
                    kwargs['ObjectLabels'].append(self.Labels[lbl])
            
            if 'PopupCallback' in group.keys():
                PopupCBModule = modules.project.callbacks.PopupCallbacks
                PopupCB = getattr(PopupCBModule, group['PopupCallback'])
                kwargs['PopupCallback'] = PopupCB
                
                if 'PopupGroups' in group.keys():
                    kwargs['PopupGroups'] = group['PopupGroups']
                
            if 'Controls' in group.keys():
                for key, val in group['Controls'].items():
                    if self.Buttons.get(val) is not None:
                        kwargs[key] = self.Buttons[val]
                    elif self.Sliders.get(val) is not None:
                        kwargs[key] = self.Sliders[val]
                    elif self.Knobs.get(val) is not None:
                        kwargs[key] = self.Knobs[val]
                    else:
                        raise KeyError('Value ({}) for Key ({}) not found in Buttons, Sliders, or Knobs'.format(val, key))
            
            if 'Labels' in group.keys():
                for key, val in group['Labels'].items():
                    kwargs[key] = self.Labels[val]
            
            if 'RefCallback' in group.keys():
                RefCBModule = modules.project.callbacks.RefCallbacks
                RefCB = getattr(RefCBModule, group['RefCallback'])
                refs = self.LoadRefs(UIHost, RefCB(UIHost))
                kwargs['RefObjects'] = refs
                
            if 'OffsetShift' in group.keys():
                kwargs['OffsetShift'] = group['OffsetShift']

            self.ControlGroups[group['Name']] = Constructor(**kwargs)
            
            # Get SubGroups created by ControlGroups
            subGroups.extend(self.ControlGroups[group['Name']].GetSubGroups())
            
        for sg in subGroups:
            self.ControlGroups[sg.Name] = sg
            
    def LoadControls(self, 
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
        
        for ctl in jsonObj:
            kwargs = dict(ctl)
            if 'ControlObject' in kwargs.keys():
                kwargs.pop('ControlObject')
            if 'ControlCollection' in kwargs.keys():
                kwargs.pop('ControlCollection')
            
            ctlObj = ControlObject(**kwargs)
            
            if 'ControlObject' in ctl and 'ControlCollection' not in ctl:
                if ctl['ControlObject'] in self.Buttons.keys():
                    ctlObj.LinkControlObject(ControlObject=self.Buttons[ctl['ControlObject']])
                elif ctl['ControlObject'] in self.Sliders.keys():
                    ctlObj.LinkControlObject(ControlObject=self.Sliders[ctl['ControlObject']])
                elif ctl['ControlObject'] in self.Knobs.keys():
                    ctlObj.LinkControlObject(ControlObject=self.Knobs[ctl['ControlObject']])
                else:
                    Logger.Log('Control Object ({}) not found'.format(ctl['ControlObject']), logSeverity='warning')
            elif 'ControlCollection' in ctl and 'ControlObject' not in ctl:
                if ctl['ControlCollection'] in self.ControlGroups.keys():
                    ctlObj.LinkControlObject(ControlCollection=self.ControlGroups[ctl['ControlCollection']])
                else: 
                    Logger.Log('Control Collection ({}) not found'.format(ctl['ControlCollection']), logSeverity='warning')
            elif 'ControlObject' in ctl and 'ControlCollection' in ctl:
                if ctl['ControlObject'] in self.Buttons.keys() and ctl['ControlCollection'] in self.ControlGroups.keys():
                    ctlObj.LinkControlObject(ControlObject=self.Buttons[ctl['ControlObject']], ControlCollection=self.ControlGroups[ctl['ControlCollection']])
                elif ctl['ControlObject'] in self.Sliders.keys() and ctl['ControlCollection'] in self.ControlGroups.keys():
                    ctlObj.LinkControlObject(ControlObject=self.Sliders[ctl['ControlObject']], ControlCollection=self.ControlGroups[ctl['ControlCollection']])
                elif ctl['ControlObject'] in self.Knobs.keys() and ctl['ControlCollection'] in self.ControlGroups.keys():
                    ctlObj.LinkControlObject(ControlObject=self.Knobs[ctl['ControlObject']], ControlCollection=self.ControlGroups[ctl['ControlCollection']])
                else:
                    Logger.Log('Control Object ({}) not found'.format(ctl['ControlObject']), 'Control Collection ({}) not found'.format(ctl['ControlCollection']), logSeverity='warning')
    def GetPopupGroupByPage(self, PopupPage: str) -> str:
        for group, list in self.PopupGroups.items():
            if PopupPage in list:
                return group
        return None
## End Class Definitions -------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------

## End Function Definitions ----------------------------------------------------



