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
    from modules.helper.ExtendedDeviceClasses import ExProcessorDevice, ExUIDevice, ExSPDevice, ExEBUSDevice
    from modules.helper.PrimitiveObjects import ControlObject, FeedbackObject
    from modules.helper.Collections import RadioSet, SelectSet, VariableRadioSet, ScrollingRadioSet, VolumeControlGroup, HeaderControlGroup

#### Python imports

#### Extron Library Imports
from extronlib.ui import Button, Label, Level, Slider, Knob
from extronlib.system import Wait

#### Project imports
from modules.helper.CommonUtilities import Logger, DictValueSearchByKey, RunAsync, debug
from modules.helper.ModuleSupport import eventEx


## End Imports -----------------------------------------------------------------
##
## Begin Class Definitions -----------------------------------------------------

class RefButton(Button):
    def __init__(self,
                 UIHost: Union['UIDevice', 'eBUSDevice', 'ProcessorDevice', 'SPDevice', 'ExUIDevice', 'ExEBUSDevice', 'ExProcessorDevice', 'ExSPDevice'], 
                 ID_Name: Union[int, str],
                 **kwargs) -> None:
        super().__init__(UIHost, ID_Name, None, None)
        self.UIHost = UIHost
        self.Id = self.ID
        self.Text = None
        self.Group = None
        self.__Control = None
        self.__RefName = None
        
        for kw, val in kwargs.items():
            if kw == 'Text':
                self.SetText(val)
            else:
                setattr(self, kw, val)
        
    @property
    def Control(self) -> 'ControlObject':
        return self.__Control
    
    @Control.setter
    def Control(self, val) -> None:
        raise AttributeError('Overriding Control property directly is disallowed. Use "SetControlObject" instead.')
    
    @property
    def Name(self) -> str:
        if self.__RefName is None:
            return self.Name
        else:
            return self.__RefName
        
    @property
    def Indicator(self) -> 'ExButton':
        if hasattr(self, '__indicator'):
            try:
                return self.UIHost.Interface.Objects.Buttons[self.__indicator]
            except LookupError:
                Logger.Log('No button found for indicator name: {}'.format(self.__indicator))
                return None
        else:
            return None
        
    @Indicator.setter
    def Indicator(self, val) -> None:
        raise AttributeError('Overriding Indicator property is disallowed.')
    
    def __repr__(self) -> str:
        return "{} ({})".format(self.Name, self.Id)
    
    def SetText(self, text: str) -> None:
        if text is None:
            text = ''
        self.Text = text
        super().SetText(text)
        
    def SetState(self, state: int) -> None:
        # update indicator state
        indState = state % 10
        self.Indicator.SetState(indState)
        # update state
        return super().SetState(state)
        
    def SetRefName(self, Name: str) -> None:
        if self.__RefName is None:
            self.__RefName = Name
        else:
            raise AttributeError('RefName is already set')
    
    def GetGroupList(self) -> List:
        groupList = []
        continueUp = True
        obj = self
        while continueUp:
            groupList.insert(0, obj)
            if obj.Group is not None:
                obj = obj.Group
            else:
                continueUp = False
                
        return groupList
    
    def SetControlObject(self, Control: 'ControlObject'):
        if type(Control) is ControlObject:
            self.__Control = Control
        else:
            raise TypeError('Control must be a ControlObject')
        
        # TODO: create button events here

class ExButton(Button):
    def __init__(self, 
                 UIHost: Union['UIDevice', 'eBUSDevice', 'ProcessorDevice', 'SPDevice', 'ExUIDevice', 'ExEBUSDevice', 'ExProcessorDevice', 'ExSPDevice'], 
                 ID_Name: Union[int, str], 
                 holdTime: float = None, 
                 repeatTime: float = None,
                 **kwargs) -> None:
        super().__init__(UIHost, ID_Name, holdTime, repeatTime)
        
        self.UIHost = UIHost
        self.Id = self.ID
        self.Text = None
        self.Group = None
        self.__InitialState = None
        self.__Control = None
        self.__HoldTime = holdTime
        self.__RepeatTime = repeatTime
        self.__Indicator = None
        self.__GroupList = None
        self.__StateDict = {
            "Inactive": None,
            "Shift": None,
            "Active": None,
            "HoldShift": None,
            "HoldActive": None,
            # "RepeatActive": None
        }
        self.__ShiftDict = {
            'Press': None,
            'Hold': None,
        }
        self.__LatchingDict = {
            'Latching': None,
            'HoldLatching': None
        }
        self.__FunctDict = {
            "Primary": None,
            "Hold": None,
            "Repeat": None
        }
        
        for kw, val in kwargs.items():
            if kw == 'Text':
                self.SetText(val)
            else:
                setattr(self, kw, val)
                
        @eventEx(self, ['Pressed', 'Released', 'Held', 'Repeated', 'Tapped'])
        def ExButtonHandler(source: 'ExButton', event: str) -> None:
            Logger.Log('Button Event', source, event)
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
    
    @property
    def Control(self) -> 'ControlObject':
        return self.__Control
    
    @Control.setter
    def Control(self, val) -> None:
        raise AttributeError('Overriding Control property directly is disallowed. Use "SetControlObject" instead.')
    
    @property
    def Indicator(self) -> 'ExButton':
        if hasattr(self, 'indicatorName') and self.__Indicator is None:
            try:
                self.__Indicator = self.UIHost.Interface.Objects.Buttons[self.indicatorName]
            except LookupError:
                Logger.Log('No button found for indicator name: {}'.format(self.indicatorName))
        
        return self.__Indicator
        
    @Indicator.setter
    def Indicator(self, val) -> None:
        raise AttributeError('Overriding Indicator property is disallowed.')
    
    def __repr__(self) -> str:
        return "{} ({}, {} [{}])".format(self.Name, 
                                         self.Id, 
                                         'Enabled' if self.Enabled else 'Disabled', 
                                         self.State)
        
    def SetText(self, text: str) -> None:
        if text is None:
            text = ''
        self.Text = text
        super().SetText(text)
        
    def SetState(self, state: int) -> None:
        if state is None:
            Logger.Log('None state sent to button set state', self, separator=' | ', logSeverity='warning')
            return None
        # update indicator state
        indBtn = self.Indicator
        if indBtn is not None:
            indBtn.SetState(state % 10)
        # update state
        super().SetState(state)
    
    def HasHold(self) -> bool:
        return (self.__HoldTime is not None)
    
    def HasRepeat(self) -> bool:
        return (self.__RepeatTime is not None)
    
    def SetInitialPressState(self) -> None:
        self.__InitialState = self.State
        Logger.Log(self, 'Set Initial State', self.__InitialState)
        
    def GetInitialPressState(self) -> int:
        Logger.Log(self, 'Get Initial State', self.__InitialState)
        return self.__InitialState
    
    def ClearInitialPressState(self) -> None:
        self.__InitialState = None
        Logger.Log(self, 'Clear Initial State')
    
    def GetGroupList(self) -> List[Union['ExButton', 'RadioSet', 'SelectSet', 'VariableRadioSet', 'ScrollingRadioSet', 'VolumeControlGroup', 'HeaderControlGroup']]:
        if self.__GroupList is None:
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
                
        return self.__GroupList
    
    def GetControlState(self, mode: str) -> int:
        stateDict = {
            "Inactive": None,
            "Shift": None,
            "Active": None,
            "HoldShift": None,
            "HoldActive": None,
            # "RepeatActive": None
        }
        if mode not in stateDict.keys():
            raise ValueError('mode must be in {}'.format(stateDict.keys()))
        
        if self.__StateDict[mode] is None:
            for ctlobj in [obj for obj in self.GetGroupList() if obj.Control is not None]:
                if hasattr(ctlobj.Control.States, mode):
                    stateDict[mode] = getattr(ctlobj.Control.States, mode)
            self.__StateDict[mode] = stateDict[mode]
                
        return self.__StateDict[mode]
    
    def GetControlShift(self, mode: str) -> bool:
        shiftDict = {
            'Press': None,
            'Hold': None,
        }
        if mode not in shiftDict.keys():
            raise ValueError('mode must be in {}'.format(shiftDict.keys()))
        
        if self.__ShiftDict[mode] is None:
            for ctlobj in [obj for obj in self.GetGroupList() if obj.Control is not None]:
                shiftDict['Press'] = ctlobj.Control.PressStateShift
                shiftDict['Hold'] = hasattr(ctlobj.Control.States, 'HoldShift')
            self.__ShiftDict = shiftDict
            
        return self.__ShiftDict[mode]
    
    def GetControlLatching(self, mode: str) -> bool:
        latchDict = {
            'Latching': None,
            'HoldLatching': None
        }
        if mode not in latchDict.keys():
            raise ValueError('mode must be in {}'.format(latchDict.keys()))
        
        if self.__LatchingDict[mode] is None:
            for ctlobj in [obj for obj in self.GetGroupList() if obj.Control is not None]:
                latchDict['Latching'] = ctlobj.Control.Latching
                latchDict['HoldLatching'] = ctlobj.Control.HoldLatching
            self.__LatchingDict = latchDict
            
        return self.__LatchingDict[mode]
    
    def GetControlFunctionList(self, mode: str) -> List[Callable]:
        functDict = {
            "Primary": None,
            "Hold": None,
            "Repeat": None
        }
        if mode not in functDict.keys():
            raise ValueError('mode must be in {}'.format(functDict.keys()))
        
        if self.__FunctDict[mode] is None:
            functDict[mode] = []
            for ctlobj in [obj for obj in self.GetGroupList() if obj.Control is not None]:
                functDict[mode].append(getattr(ctlobj.Control.Functions, mode))
            
            for fn in functDict[mode]:
                if not callable(fn):
                    functDict[mode].remove(fn)
            
            self.__FunctDict[mode] = functDict[mode]
        
        return self.__FunctDict[mode]
    
    def SetControlObject(self, Control: 'ControlObject'):
        self.__Control = Control
        
        # Logger.Log('Assigning Control Event', self, Control)
        # # TODO: make sure this covers button usage
        # @eventEx(self, ['Pressed', 'Released', 'Held', 'Repeated', 'Tapped'])
        # def ButtonHandler(source: 'ExButton', event: str):
        #     Logger.Log("Button Event (ExButton)", source, event)
            
        #     if event is 'Pressed':
        #         source.SetInitialPressState()
        #         if source.Control.PressStateShift:
        #             source.SetState(source.Control.States.Shift)
                
        #     elif event is 'Released':
        #         if not source.HasHold():
        #             source.Control.Functions.Primary(source, event)
                    
        #             if source.Control.IsLatching:
        #                 source.SetState(source.Control.States.Active)
        #             else:
        #                 source.SetState(source.Control.States.Inactive)
        #         else:
        #             source.Control.Functions.Hold(source, event)
        #             if source.Control.HoldLatching:
        #                 source.SetState(source.Control.States.HoldActive)
        #             else:
        #                 source.SetState(source.GetInitialPressState())
        #         source.ClearInitialPressState()
        #     elif event is 'Held':
        #         if hasattr(source.Control.States, 'HoldShift'):
        #             source.SetState(source.Control.States.HoldShift)
                    
        #     elif event is 'Repeated':
        #         source.Control.Functions.Repeat(source, event)
                
        #     elif event is 'Tapped':
        #         source.Control.Functions.Primary(source, event)
                
        #         if source.Control.IsLatching:
        #             source.SetState(source.Control.States.Active)
        #         else:
        #             source.SetState(source.Control.States.Inactive)
                
        #         source.ClearInitialPressState()
                    

class ExLabel(Label):
    def __init__(self, 
                 UIHost: Union['UIDevice', 'ExUIDevice', 'ProcessorDevice', 'ExProcessorDevice'], 
                 ID_Name: Union[int, str],
                 **kwargs) -> None:
        super().__init__(UIHost, ID_Name)
        
        self.UIHost = UIHost
        self.Id = self.ID
        self.Text = None
        self.Group = None
        
        for kw, val in kwargs.items():
            if kw == 'Text':
                self.SetText(val)
            else:
                setattr(self, kw, val)
            
    def __repr__(self) -> str:
        return "{} ({})".format(self.Name, self.Id)
    
    def SetText(self, text: str) -> None:
        if text is None:
            text = ''
        self.Text = text
        super().SetText(text)

class ExLevel(Level):
    def __init__(self, 
                 UIHost: Union['UIDevice', 'eBUSDevice', 'ProcessorDevice', 'SPDevice', 'ExUIDevice', 'ExEBUSDevice', 'ExProcessorDevice', 'ExSPDevice'], 
                 ID_Name: Union[int, str],
                 **kwargs) -> None:
        super().__init__(UIHost, ID_Name)
        
        self.UIHost = UIHost
        self.Id = self.ID
        self.Group = None
        
        for kw, val in kwargs.items():
            setattr(self, kw, val)
    
    @property
    def Fill(self) -> int:
        return self.Level
    
    @Fill.setter
    def Fill(self, Fill) -> None:
        raise AttributeError('Fill property cannot be set, use SetFill instead')
    
    def SetFill(self, Fill: int) -> None:
        self.SetLevel(Fill)
    
    def __repr__(self) -> str:
        return "{} ({}, {} [{}|{}])".format(self.Name, self.Id, self.Level, self.Min, self.Max)

class ExSlider(Slider):
    def __init__(self, 
                 UIHost: Union['UIDevice', 'ProcessorDevice', 'SPDevice', 'ExUIDevice', 'ExProcessorDevice', 'ExSPDevice'], 
                 ID_Name: Union[int, str],
                 **kwargs) -> None:
        super().__init__(UIHost, ID_Name)
        
        self.UIHost = UIHost
        self.Id = self.ID
        self.Group = None
        
        self.__Control = None
        
        for kw, val in kwargs.items():
            setattr(self, kw, val)
            
    @property
    def Level(self) -> Union[int,float]:
        return self.Fill
    
    @Level.setter
    def Level(self, Level) -> None:
        raise AttributeError('Level property cannot be set, use SetLevel instead')
    
    @property
    def Control(self) -> 'ControlObject':
        return self.__Control
    
    @Control.setter
    def Control(self, val) -> None:
        raise AttributeError('Overriding Control property directly is disallowed. Use "SetControlObject" instead.')
    
    def SetLevel(self, Level: Union[int,float]) -> None:
        self.SetFill(Level)
    
    def __repr__(self) -> str:
        return "{} ({}, {} [{}|{}])".format(self.Name, self.Id, self.Fill, self.Min, self.Max)

    def SetControlObject(self, Control: 'ControlObject'):
        if type(Control) is ControlObject:
            self.__Control = Control
        else:
            raise TypeError('Control must be a ControlObject')
        
        # TODO: create events here

class ExKnob(Knob):
    def __init__(self, 
                 UIHost: Union['UIDevice', 'eBUSDevice', 'ProcessorDevice', 'ExUIDevice', 'ExEBUSDevice', 'ExProcessorDevice'],
                 **kwargs) -> None:
        super().__init__(UIHost, 61001) # All current extron knobs use the same ID, only ever one per device
        
        self.UIHost = UIHost
        self.Id = self.ID
        self.Group = None
        
        for kw, val in kwargs.items():
            setattr(self, kw, val)
            
    def __repr__(self) -> str:
        return "Knob ({})".format(self.Id)

## End Class Definitions -------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------

## End Function Definitions ----------------------------------------------------
