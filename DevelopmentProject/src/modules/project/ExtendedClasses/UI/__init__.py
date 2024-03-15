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
from typing import TYPE_CHECKING, List, Union, Callable
if TYPE_CHECKING: # pragma: no cover
    from extronlib.device import ProcessorDevice, UIDevice, SPDevice, eBUSDevice
    from modules.project.ExtendedClasses.Device import ExProcessorDevice, ExUIDevice, ExSPDevice, ExEBUSDevice

#### Python imports

#### Extron Library Imports
from extronlib.ui import Button, Label, Level, Slider, Knob

#### Project imports
from modules.helper.CommonUtilities import Logger
from modules.project.MixIns import InitializeMixin
from modules.project.MixIns.UI import ControlMixIn, EventMixIn, GroupMixIn
import Constants

## End Imports -----------------------------------------------------------------
##
## Begin Class Definitions -----------------------------------------------------

class ButtonEx_Ref(InitializeMixin, ControlMixIn, Button):
    def __init__(self,
                 UIHost: Constants.UI_HOSTS, 
                 ID_Name: Union[int, str],
                 **kwargs) -> None:
        Button.__init__(self, UIHost, ID_Name, None, None)
        InitializeMixin.__init__(self, self.__Initialize)
        ControlMixIn.__init__(self)
        self.UIHost = UIHost
        self.Id = self.ID
        self.Text = None
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
    
    def __repr__(self) -> str:
        return "{} ({})".format(self.Name, self.Id)
    
    def SetText(self, text: str) -> None:
        if text is None:
            text = ''
        self.Text = text
        Button.SetText(self, text)
        
    def SetState(self, state: int) -> None:
        # update state
        Button.SetState(self, state)
        
    def SetRefName(self, Name: str) -> None:
        if self.__RefName is None:
            self.__RefName = Name
        else:
            raise AttributeError('RefName is already set')
        
    def __Initialize(self) -> None:
        ControlMixIn._Initialize(self)

class ButtonEx(InitializeMixin, EventMixIn, ControlMixIn, Button):
    def __init__(self, 
                 UIHost: Constants.UI_HOSTS, 
                 ID_Name: Union[int, str], 
                 holdTime: float = None, 
                 repeatTime: float = None,
                 **kwargs) -> None:
        Button.__init__(self, UIHost, ID_Name, holdTime, repeatTime)
        InitializeMixin.__init__(self, self.__Initialize)
        ControlMixIn.__init__(self)
        EventMixIn.__init__(self)
        
        self.UIHost = UIHost
        self.Id = self.ID
        self.Text = None
        
        self.__InitialState = None
        self.__HoldTime = holdTime
        self.__RepeatTime = repeatTime
        self.__Indicator = None
        
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
        
        # Overload kwargs
        for kw, val in kwargs.items():
            if kw == 'Text':
                # use class's method to set text
                self.SetText(val)
            else:
                setattr(self, kw, val)
                
        # sets char tuple if lc_char and uc_char attributes exist
        if hasattr(self, 'lc_char') and hasattr(self, 'uc_char'):
            setattr(self, "char", (self.lc_char, self.uc_char))
    
    @property
    def Indicator(self) -> 'ButtonEx':
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
        Button.SetText(self, text)
        
    def SetState(self, state: int) -> None:
        if state is None:
            Logger.Debug('None state sent to button set state', self, separator=' | ', logSeverity='warning')
            return None
        # update indicator state
        if self.Indicator is not None:
            self.Indicator.SetState(state % 10)
        # update state
        Button.SetState(self, state)
    
    def HasHold(self) -> bool:
        return (self.__HoldTime is not None)
    
    def HasRepeat(self) -> bool:
        return (self.__RepeatTime is not None)
    
    def SetInitialPressState(self) -> None:
        self.__InitialState = self.State
        
    def GetInitialPressState(self) -> int:
        return self.__InitialState
    
    def ClearInitialPressState(self) -> None:
        self.__InitialState = None
    
    def __Initialize(self) -> None:
        ControlMixIn._Initialize(self)
        EventMixIn._Initialize(self)
        
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
                Logger.Debug('No button found for indicator name: {}'.format(self.indicatorName))
    
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
    
class LabelEx(InitializeMixin, GroupMixIn, Label):
    def __init__(self, 
                 UIHost: Constants.UI_HOSTS, 
                 ID_Name: Union[int, str],
                 **kwargs) -> None:
        Label.__init__(self, UIHost, ID_Name)
        InitializeMixin.__init__(self, self.__Initialize)
        GroupMixIn.__init__(self)
        
        self.UIHost = UIHost
        self.Id = self.ID
        self.Text = None
        
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
        
    def __Initialize(self) -> None:
        GroupMixIn._Initialize(self)

class LevelEx(InitializeMixin, GroupMixIn, Level):
    def __init__(self, 
                 UIHost: Constants.UI_HOSTS, 
                 ID_Name: Union[int, str],
                 **kwargs) -> None:
        Level.__init__(self, UIHost, ID_Name)
        InitializeMixin.__init__(self, self.__Initialize)
        GroupMixIn.__init__(self)
        
        self.UIHost = UIHost
        self.Id = self.ID
        
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

    def __Initialize(self) -> None:
        GroupMixIn._Initialize(self)

class SliderEx(InitializeMixin, EventMixIn, ControlMixIn, Slider):
    def __init__(self, 
                 UIHost: Union['UIDevice', 'ProcessorDevice', 'SPDevice', 'ExUIDevice', 'ExProcessorDevice', 'ExSPDevice'], 
                 ID_Name: Union[int, str],
                 **kwargs) -> None:
        Slider.__init__(self, UIHost, ID_Name)
        InitializeMixin.__init__(self, self.__Initialize)
        ControlMixIn.__init__(self)
        EventMixIn.__init__(self)
        
        self.UIHost = UIHost
        self.Id = self.ID
        
        self.__InitialFill = None
        
        self.__FunctDict = {
            "Primary": None
        }
        
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

    def __Initialize(self) -> None:
        ControlMixIn._Initialize(self)
        EventMixIn._Initialize(self)
        
        self.__InitControlFunctions()
        
    def SetInitialPressFill(self) -> None:
        self.__InitialFill = self.Fill
        
    def GetInitialPressFill(self) -> int:
        return self.__InitialFill
    
    def __InitControlFunctions(self) -> None:
        mode = 'Primary'
        self.__FunctDict[mode] = []
        for ctlobj in self.ControlList:
            if hasattr(ctlobj.Control.Functions, mode):
                fn = getattr(ctlobj.Control.Functions, mode)
                if callable(fn):
                    self.__FunctDict[mode].append(fn)
    
    def GetControlFunctionList(self, Mode: str = 'Primary') -> List[Callable]:
        if Mode not in self.__FunctDict.keys():
            raise ValueError('Mode must be in {}'.format(self.__FunctDict.keys()))
        
        if not self.Initialized:
            raise RuntimeError('Slider object {} must be initialized prior to using this function'.format(self))
        
        return self.__FunctDict[Mode]

class KnobEx(InitializeMixin, EventMixIn, ControlMixIn, Knob):
    def __init__(self, 
                 UIHost: Union['UIDevice', 'eBUSDevice', 'ProcessorDevice', 'ExUIDevice', 'ExEBUSDevice', 'ExProcessorDevice'],
                 **kwargs) -> None:
        Knob.__init__(self, UIHost, 61001) # All current extron knobs use the same ID, only ever one per device
        InitializeMixin.__init__(self, self.__Initialize)
        ControlMixIn.__init__(self)
        EventMixIn.__init__(self)
        
        self.UIHost = UIHost
        self.Id = self.ID
        
        for kw, val in kwargs.items():
            setattr(self, kw, val)
            
    def __repr__(self) -> str:
        return "Knob ({})".format(self.Id)
    
    def __Initialize(self) -> None:
        ControlMixIn._Initialize(self)
        EventMixIn._Initialize(self)

## End Class Definitions -------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------

## End Function Definitions ----------------------------------------------------
