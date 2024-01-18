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
from typing import TYPE_CHECKING, List, Union
if TYPE_CHECKING: # pragma: no cover
    from modules.helper.ExtendedUIClasses import ExButton, ExSlider
    from modules.helper.PrimitiveObjects import ControlObject

#### Python imports

#### Extron Library Imports

#### Project imports
from modules.helper.CommonUtilities import Logger, isinstanceEx
from modules.helper.ModuleSupport import eventEx
import Constants

## End Imports -----------------------------------------------------------------
##
## Begin Class Definitions -----------------------------------------------------

class GroupMixIn(object):
    def __init__(self) -> None:
        
        self.__Group = None
        self.__GroupList = None
        
    @property
    def Group(self) -> Constants.UI_SETS:
        return self.__Group
    
    @Group.setter
    def Group(self, val: Constants.UI_SETS) -> None:
        if isinstanceEx(val, Constants.UI_SETS_MATCH):
            self.__Group = val
        elif val is None:
            self.__Group = val
        else:
            raise TypeError('Group ({}) must be one of {}'.format(type(val), Constants.UI_SETS_MATCH))
    
        self.__GroupList = None
    
    @property
    def GroupList(self) -> List[Constants.UI_ALL]:
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
        
    def _Initialize(self) -> None:
        self.__InitGroupList()
        
class ControlMixIn(GroupMixIn, object):
    def __init__(self) -> None:
        GroupMixIn.__init__(self)
        
        self.__Control = None
        self.__ControlList = None
        
    @property
    def Control(self) -> 'ControlObject':
        return self.__Control
    
    @Control.setter
    def Control(self, val) -> None:
        raise AttributeError('Overriding Control property directly is disallowed. Use "SetControlObject" instead.')
    
    def SetControlObject(self, Control: 'ControlObject'):
        if isinstanceEx(Control, 'ControlObject'):
            self.__Control = Control
        else:
            raise TypeError('Control must be a ControlObject')
        
        Logger.Debug('Set {} ControlObject:'.format(type(self).__name__), Control)
    
    @property
    def ControlList(self) -> List['ControlObject']:
        if self.__ControlList is None:
            self.__InitControlList()
            
        return self.__ControlList
        
    def __InitControlList(self) -> None:
        self.__ControlList = [obj for obj in self.GroupList if obj.Control is not None]
    
    def _Initialize(self) -> None:
        GroupMixIn._Initialize(self)
        self.__InitControlList()
    
class EventMixIn():
    def __init__(self) -> None:
        pass
    
    def _Initialize(self) -> None:
        if isinstanceEx(self, 'ExButton'):
            @eventEx(self, Constants.EVENTS_BUTTON)
            def ExButtonHandler(source, event) -> None:
                self.__ExButtonHandler(source, event)
        elif isinstanceEx(self, 'ExSlider'):
            @eventEx(self, Constants.EVENTS_SLIDER)
            def ExSliderHdnler(source, event, value) -> None:
                self.__ExSliderHandler(source, event, value)
        elif isinstanceEx(self, 'ExKnob'):
            # TODO: knob event definition
            Logger.Log('Knob event def goes here')
    
    def __ExButtonHandler(self, source: 'ExButton', event: str) -> None:
        Logger.Debug('ExButton Event', source, event)
        if event == 'Pressed':
            # Capture initial press state
            source.SetInitialPressState()
            
            # Change state to Shift state
            if source.GetControlShift('Press'):
                self.__SetButtonState(source, 'Shift')
            
        elif event == 'Released':
            # Released no Hold
            if not source.HasHold():
                if source.Enabled:
                    # Determine after release state
                    ## Control is latching (active after release)
                    if source.GetControlLatching('Latching'):
                        self.__SetButtonLatchingState(source)
                    ## Control is non-latching (inactive after release)
                    else:
                        # Change state to Inactive state
                        self.__SetButtonState(source, 'Inactive')
                    
                
                # Do primary functionality
                for fn in source.GetControlFunctionList('Primary'):
                    fn(source, event)
            # Relased after hold
            else:
                if source.Enabled:
                    # Determine after release state
                    ## Control is hold latching (HoldActive after release)
                    if source.GetControlLatching('HoldLatching'):
                        # Change to HoldActive state
                        self.__SetButtonState(source, 'HoldActive')
                    else:
                        # Return to initial press state
                        source.SetState(source.GetInitialPressState())
                        
                # Do Hold functionality
                for fn in source.GetControlFunctionList('Hold'):
                    fn(source, event)
                    
            # Clear initial press state
            source.ClearInitialPressState()
            
        elif event == 'Held':
            source.UIHost.Click()
            
            if source.Enabled:
                # Determine if state change is needed
                self.__SetButtonState(source, 'HoldShift')
                
        elif event == 'Repeated':
            # Do Repeat functionality
            for fn in source.GetControlFunctionList('Repeat'):
                fn(source, event)
            
        elif event == 'Tapped':
            if source.Enabled:
                # Determine after release state
                ## Control is latching (active after release)
                if source.GetControlLatching('Latching'):
                    self.__SetButtonLatchingState(source)
                ## Control is non-latching (inactive after release)
                else:
                    # Change state to Inactive state
                    self.__SetButtonState(source, 'Inactive')
            
            # Do primary functionality
            for fn in source.GetControlFunctionList('Primary'):
                fn(source, event)
            
            # Clear initial press state
            source.ClearInitialPressState()

    def __SetButtonLatchingState(self, source: 'ExButton'):
        if source.GetInitialPressState() == source.GetControlState('Inactive'):
                            # Change state to Active state if initially Inactive
            if source.Group is not None:
                if hasattr(source.Group, 'SetCurrent'):
                    source.Group.SetCurrent(source)
                elif hasattr(source.Group, 'SetCurrentButton'):
                    source.Group.SetCurrentButton(source)
                elif hasattr(source.Group, 'SetActive'):
                    source.Group.SetActive(source)
            else:
                source.SetState(source.GetControlState('Active'))
        elif source.GetInitialPressState() == source.GetControlState('Active'):
                            # Change state to Inactive state if initially Active
            if source.Group is not None:
                if hasattr(source.Group, 'SetCurrent'):
                    source.Group.SetCurrent(None)
                elif hasattr(source.Group, 'SetCurrentButton'):
                    source.Group.SetCurrentButton(None)
                elif hasattr(source.Group, 'SetInactive'):
                    source.Group.SetInactive(source)
            else:
                source.SetState(source.GetControlState('Inactive'))

    def __SetButtonState(self, source: 'ExButton', state: str):
        if hasattr(source, 'Group') and \
                   hasattr(source.Group, 'Group') and \
                   isinstanceEx(source.Group.Group, 'ScrollingRadioSet'):
            index = source.Group.Group.Objects.index(source)
            endOffset = source.Group.Group.Offset + len(source.Group.Group.Objects)
            curRefSet = source.Group.Group.RefObjects[source.Group.Group.Offset:endOffset]
            curRefBtn = curRefSet[index]
            if hasattr(curRefBtn, 'icon'):
                source.SetState(int('{}{}'.format(curRefBtn.icon,
                                                  source.GetControlState(state))))
            else:
                source.SetState(source.GetControlState(state))
        else:
            source.SetState(source.GetControlState(state))

    def __ExSliderHandler(self, source: 'ExSlider', event: str, value: Union[int, float]) -> None:
        Logger.Debug('ExSlider Event', source, event, value)
        
        if event == 'Pressed':
            source.SetInitialPressFill()
        
        elif event == 'Changed':
            source.SetFill(value)
        
        elif event == 'Released':
            source.SetFill(value)
            
            for fn in source.GetControlFunctionList('Primary'):
                fn(source, event, value)

## End Class Definitions -------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------

## End Function Definitions ----------------------------------------------------



