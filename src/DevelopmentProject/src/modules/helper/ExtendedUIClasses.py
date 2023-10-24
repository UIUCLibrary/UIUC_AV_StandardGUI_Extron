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
    from modules.helper.Collections import RadioSet, SelectSet, VariableRadioSet, ScrollingRadioSet, VolumeControlGroup, HeaderControlGroup
    from modules.helper.PrimitiveObjects import ControlObject

#### Python imports

#### Extron Library Imports
from extronlib.ui import Button, Label, Level, Slider, Knob
from extronlib.system import Wait

#### Project imports
from modules.helper.CommonUtilities import Logger, DictValueSearchByKey, RunAsync, debug
from modules.helper.ModuleSupport import eventEx
from modules.helper.PrimitiveObjects import ControlMixIn


## End Imports -----------------------------------------------------------------
##
## Begin Class Definitions -----------------------------------------------------

class RefButton(ControlMixIn, Button):
    def __init__(self,
                 UIHost: Union['UIDevice', 'eBUSDevice', 'ProcessorDevice', 'SPDevice', 'ExUIDevice', 'ExEBUSDevice', 'ExProcessorDevice', 'ExSPDevice'], 
                 ID_Name: Union[int, str],
                 **kwargs) -> None:
        Button.__init__(self, UIHost, ID_Name, None, None)
        ControlMixIn.__init__(self)
        self.UIHost = UIHost
        self.Id = self.ID
        self.Text = None
        self.Group = None
        self.__RefName = None
        
        for kw, val in kwargs.items():
            if kw == 'Text':
                self.SetText(val)
            else:
                setattr(self, kw, val)
    
    @property
    def Name(self) -> str:
        if self.__RefName is None:
            return self.Name
        else:
            return self.__RefName
        
    # @property
    # def Indicator(self) -> 'ExButton':
    #     if hasattr(self, '__indicator'):
    #         try:
    #             return self.UIHost.Interface.Objects.Buttons[self.__indicator]
    #         except LookupError:
    #             Logger.Log('No button found for indicator name: {}'.format(self.__indicator))
    #             return None
    #     else:
    #         return None
        
    # @Indicator.setter
    # def Indicator(self, val) -> None:
    #     raise AttributeError('Overriding Indicator property is disallowed.')
    
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

class ExButton(ControlMixIn, Button):
    def __init__(self, 
                 UIHost: Union['UIDevice', 'eBUSDevice', 'ProcessorDevice', 'SPDevice', 'ExUIDevice', 'ExEBUSDevice', 'ExProcessorDevice', 'ExSPDevice'], 
                 ID_Name: Union[int, str], 
                 holdTime: float = None, 
                 repeatTime: float = None,
                 **kwargs) -> None:
        Button.__init__(self, UIHost, ID_Name, holdTime, repeatTime)
        ControlMixIn.__init__(self)
        
        self.UIHost = UIHost
        self.Id = self.ID
        self.Text = None
        self.Group = None
        self.Initialized = False
        self.__InitialState = None
        self.__HoldTime = holdTime
        self.__RepeatTime = repeatTime
        self.__Indicator = None
        self.__GroupList = None
        self.__ControlList = None
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
    def Indicator(self) -> 'ExButton':
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
        if self.Indicator is not None:
            self.Indicator.SetState(state % 10)
        # update state
        super().SetState(state)
    
    def HasHold(self) -> bool:
        return (self.__HoldTime is not None)
    
    def HasRepeat(self) -> bool:
        return (self.__RepeatTime is not None)
    
    def SetInitialPressState(self) -> None:
        self.__InitialState = self.State
        # Logger.Log(self, 'Set Initial State', self.__InitialState)
        
    def GetInitialPressState(self) -> int:
        # Logger.Log(self, 'Get Initial State', self.__InitialState)
        return self.__InitialState
    
    def ClearInitialPressState(self) -> None:
        self.__InitialState = None
        # Logger.Log(self, 'Clear Initial State')
    
    def Initialize(self) -> None:
        self.__InitGroupList()
        self.__InitControlList()
        
        Logger.Log(self.Name, [grp.Name for grp in self.GroupList])
        
        self.__InitControlState()
        self.__InitControlShift()
        self.__InitControlLatching()
        self.__InitControlFunctions()
        
        # link indictator
        if hasattr(self, 'indicatorName'):
            try:
                ind = self.UIHost.Interface.Objects.Buttons[self.indicatorName]
                self.__Indicator = ind
                setattr(ind, 'ind-ref', self)
            except LookupError:
                Logger.Log('No button found for indicator name: {}'.format(self.indicatorName))
        
        self.Initialized = True
    
    @property
    def GroupList(self) -> List[Union['ExButton', 'RadioSet', 'SelectSet', 'VariableRadioSet', 'ScrollingRadioSet', 'VolumeControlGroup', 'HeaderControlGroup']]:
        if self.__GroupList is None:
            self.__InitGroupList()
        
        return self.__GroupList
    
    @GroupList.setter
    def GroupList(self, val) -> None:
        raise AttributeError('Setting GroupList property is disallowed')
    
    @property
    def ControlList(self) -> List['ControlObject']:
        if self.__ControlList is None:
            self.__InitControlList()
            
        return self.__ControlList
    
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
        
    def __InitControlList(self) -> None:
        self.__ControlList = [obj for obj in self.GroupList if obj.Control is not None]
    
    def __InitControlState(self) -> None:
        for state in self.__StateDict:
            for ctlobj in self.ControlList:
                if hasattr(ctlobj.Control.States, state):
                    self.__StateDict[state] = getattr(ctlobj.Control.States, state)
    
    def GetControlState(self, State: str) -> int:
        if State not in self.__StateDict.keys():
            raise ValueError('State must be in {}'.format(self.__StateDict.keys()))
        
        if not self.Initialized:
            raise RuntimeError('Button object {} must be initialized prior to using this function'.format(self))
                
        return self.__StateDict[State]
    
    def __InitControlShift(self) -> None:
        for ctlobj in self.ControlList:
            self.__ShiftDict['Press'] = ctlobj.Control.PressStateShift
            self.__ShiftDict['Hold'] = hasattr(ctlobj.Control.States, 'HoldShift')
    
    def GetControlShift(self, Shift: str) -> bool:
        if Shift not in self.__ShiftDict.keys():
            raise ValueError('Shift must be in {}'.format(self.__ShiftDict.keys()))
        
        if not self.Initialized:
            raise RuntimeError('Button object {} must be initialized prior to using this function'.format(self))
            
        return self.__ShiftDict[Shift]
    
    def __InitControlLatching(self) -> None:
        for ctlobj in self.ControlList:
            self.__LatchingDict['Latching'] = ctlobj.Control.Latching
            self.__LatchingDict['HoldLatching'] = ctlobj.Control.HoldLatching
    
    def GetControlLatching(self, Latching: str) -> bool:
        if Latching not in self.__LatchingDict.keys():
            raise ValueError('Latching must be in {}'.format(self.__LatchingDict.keys()))
        
        if not self.Initialized:
            raise RuntimeError('Button object {} must be initialized prior to using this function'.format(self))
            
        return self.__LatchingDict[Latching]
    
    def __InitControlFunctions(self) -> None:
        for mode in self.__FunctDict:
            self.__FunctDict[mode] = []
            for ctlobj in self.ControlList:
                if hasattr(ctlobj.Control.Functions, mode):
                    fn = getattr(ctlobj.Control.Functions, mode)
                    if callable(fn):
                        self.__FunctDict[mode].append(fn)
    
    def GetControlFunctionList(self, Mode: str) -> List[Callable]:
        if Mode not in self.__FunctDict.keys():
            raise ValueError('Mode must be in {}'.format(self.__FunctDict.keys()))
        
        if not self.Initialized:
            raise RuntimeError('Button object {} must be initialized prior to using this function'.format(self))
        
        return self.__FunctDict[Mode]
    

class ExLabel(ControlMixIn, Label):
    def __init__(self, 
                 UIHost: Union['UIDevice', 'ExUIDevice', 'ProcessorDevice', 'ExProcessorDevice'], 
                 ID_Name: Union[int, str],
                 **kwargs) -> None:
        Label.__init__(self, UIHost, ID_Name)
        ControlMixIn.__init__(self)
        
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

class ExLevel(ControlMixIn, Level):
    def __init__(self, 
                 UIHost: Union['UIDevice', 'eBUSDevice', 'ProcessorDevice', 'SPDevice', 'ExUIDevice', 'ExEBUSDevice', 'ExProcessorDevice', 'ExSPDevice'], 
                 ID_Name: Union[int, str],
                 **kwargs) -> None:
        Level.__init__(self, UIHost, ID_Name)
        ControlMixIn.__init__(self)
        
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

class ExSlider(ControlMixIn, Slider):
    def __init__(self, 
                 UIHost: Union['UIDevice', 'ProcessorDevice', 'SPDevice', 'ExUIDevice', 'ExProcessorDevice', 'ExSPDevice'], 
                 ID_Name: Union[int, str],
                 **kwargs) -> None:
        Slider.__init__(self, UIHost, ID_Name)
        ControlMixIn.__init__(self)
        
        self.UIHost = UIHost
        self.Id = self.ID
        self.Group = None
        
        for kw, val in kwargs.items():
            setattr(self, kw, val)
            
    @property
    def Level(self) -> Union[int,float]:
        return self.Fill
    
    @Level.setter
    def Level(self, Level) -> None:
        raise AttributeError('Level property cannot be set, use SetLevel instead')
    
    def SetLevel(self, Level: Union[int,float]) -> None:
        self.SetFill(Level)
    
    def __repr__(self) -> str:
        return "{} ({}, {} [{}|{}])".format(self.Name, self.Id, self.Fill, self.Min, self.Max)

class ExKnob(ControlMixIn, Knob):
    def __init__(self, 
                 UIHost: Union['UIDevice', 'eBUSDevice', 'ProcessorDevice', 'ExUIDevice', 'ExEBUSDevice', 'ExProcessorDevice'],
                 **kwargs) -> None:
        Knob.__init__(self, UIHost, 61001) # All current extron knobs use the same ID, only ever one per device
        
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
