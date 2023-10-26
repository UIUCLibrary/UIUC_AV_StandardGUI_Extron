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
    from modules.helper.Collections import RadioSet, SelectSet, VariableRadioSet, ScrollingRadioSet, VolumeControlGroup, HeaderControlGroup
    from modules.helper.ExtendedUIClasses import ExButton, ExSlider, RefButton

#### Python imports

#### Extron Library Imports

#### Project imports
from modules.helper.CommonUtilities import Logger
from modules.helper.ModuleSupport import eventEx
from modules.helper.PrimitiveObjects import ControlObject

## End Imports -----------------------------------------------------------------
##
## Begin Class Definitions -----------------------------------------------------

class ControlMixIn():
    def __init__(self) -> None:
        self.Group = None
        
        self.__Control = None
        self.__GroupList = None
        self.__ControlList = None
        
    @property
    def Control(self) -> 'ControlObject':
        return self.__Control
    
    @Control.setter
    def Control(self, val) -> None:
        raise AttributeError('Overriding Control property directly is disallowed. Use "SetControlObject" instead.')
    
    def SetControlObject(self, Control: 'ControlObject'):
        if type(Control) is ControlObject:
            self.__Control = Control
        else:
            raise TypeError('Control must be a ControlObject')
        
        Logger.Log('{} ControlObject:'.format(type(self).__name__), Control)
        
    @property
    def GroupList(self) -> List[Union['ExButton', 'RadioSet', 'SelectSet', 'VariableRadioSet', 'ScrollingRadioSet', 'VolumeControlGroup', 'HeaderControlGroup']]:
        if self.__GroupList is None:
            self.__InitGroupList()
        
        return self.__GroupList
    
    @GroupList.setter
    def GroupList(self, val) -> None:
        raise AttributeError('Setting GroupList property is disallowed')
    
    def __InitGroupList(self) -> None:
        groupList = []
        continueUp = True
        obj = self
        while continueUp:
            groupList.insert(0, obj)
            if obj.Group is not None:
                obj = obj.Group
            else:
                continueUp = False
        self.__GroupList = groupList
    
    @property
    def ControlList(self) -> List['ControlObject']:
        if self.__ControlList is None:
            self.__InitControlList()
            
        return self.__ControlList
        
    def __InitControlList(self) -> None:
        self.__ControlList = [obj for obj in self.GroupList if obj.Control is not None]
    
    def Initialize(self) -> None:
        self.__InitGroupList()
        self.__InitControlList()
    
class EventMixIn():
    def __init__(self) -> None:
        pass
    
    def Initialize(self) -> None:
        if type(self).__name__ == "ExButton":
            @eventEx(self, ['Pressed', 'Released', 'Held', 'Repeated', 'Tapped'])
            def ExButtonHandler(source, event) -> None:
                self.__ExButtonHandler(source, event)
        elif type(self).__name__ == "ExSlider":
            Logger.Log('Slider event def goes here')
    
    def __ExButtonHandler(self, source: 'ExButton', event: str) -> None:
        Logger.Log('ExButton Event', source, event)
        if event is 'Pressed':
            # Capture initial press state
            source.SetInitialPressState()
            
            # Change state to Shift state
            if source.GetControlShift('Press'):
                source.SetState(source.GetControlState('Shift'))
            
        elif event is 'Released':
            # Released no Hold
            if not source.HasHold():
                # Do primary functionality
                for fn in source.GetControlFunctionList('Primary'):
                    fn(source, event)
                
                # Determine after release state
                ## Control is latching (active after release)
                if source.GetControlLatching('Latching'):
                    # Change state to Active state
                    if source.Group is not None:
                        if hasattr(source.Group, 'SetCurrent'):
                            source.Group.SetCurrent(source)
                        elif hasattr(source.Group, 'SetCurrentButton'):
                            source.Group.SetCurrentButton(source)
                        elif hasattr(source.Group, 'SetActive'):
                            source.Group.SetActive(source)
                    source.SetState(source.GetControlState('Active'))
                ## Control is non-latching (inactive after release)
                else:
                    # Change state to Inactive state
                    source.SetState(source.GetControlState('Inactive'))
                    
            # Relased after hold
            else:
                # Do Hold functionality
                for fn in source.GetControlFunctionList('Hold'):
                    fn(source, event)
                
                # Determine after release state
                ## Control is hold latching (HoldActive after release)
                if source.GetControlLatching('HoldLatching'):
                    # Change to HoldActive state
                    source.SetState(source.GetControlState('HoldActive'))
                else:
                    # Return to initial press state
                    source.SetState(source.GetInitialPressState())
                    
            # Clear initial press state
            source.ClearInitialPressState()
            
        elif event is 'Held':
            source.UIHost.Click()
            # Determine if state change is needed
            source.SetState(source.GetControlState('HoldShift'))
                
        elif event is 'Repeated':
            # Do Repeat functionality
            for fn in source.GetControlFunctionList('Repeat'):
                fn(source, event)
            
        elif event is 'Tapped':
            source.Control.Functions.Primary(source, event)
            
            # Do primary functionality
            for fn in source.GetControlFunctionList('Primary'):
                fn(source, event)
            
            # Determine after release state
            ## Control is latching (active after release)
            if source.GetControlLatching('Latching'):
                # Change state to Active state
                if source.Group is not None:
                    if hasattr(source.Group, 'SetCurrent'):
                        source.Group.SetCurrent(source)
                    elif hasattr(source.Group, 'SetCurrentButton'):
                        source.Group.SetCurrentButton(source)
                    elif hasattr(source.Group, 'SetActive'):
                        source.Group.SetActive(source)
                source.SetState(source.GetControlState('Active'))
            ## Control is non-latching (inactive after release)
            else:
                # Change state to Inactive state
                source.SetState(source.GetControlState('Inactive'))
            
            # Clear initial press state
            source.ClearInitialPressState()

## End Class Definitions -------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------

## End Function Definitions ----------------------------------------------------



