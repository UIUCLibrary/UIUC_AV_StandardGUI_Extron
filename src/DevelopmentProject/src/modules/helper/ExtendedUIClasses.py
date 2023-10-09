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
    
    def __repr__(self) -> str:
        return "{} ({})".format(self.Name, self.Id)
    
    def SetText(self, text: str) -> None:
        if text is None:
            text = ''
        self.Text = text
        super().SetText(text)
        
    def SetRefName(self, Name: str) -> None:
        if self.__RefName is None:
            self.__RefName = Name
        else:
            raise AttributeError('RefName is already set')
    
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
        self.__Control = None
        self.__HoldTime = holdTime
        self.__RepeatTime = repeatTime
        
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
    
    def HasHold(self) -> bool:
        return (self.__HoldTime is not None)
    
    def HasRepeat(self) -> bool:
        return (self.__RepeatTime is not None)
    
    def SetControlObject(self, Control: 'ControlObject'):
        self.__Control = Control
        
        Logger.Log('Assigning Control Event', self, Control)
        # TODO: make sure this covers button usage
        @eventEx(self, ['Pressed', 'Released', 'Held', 'Repeated', 'Tapped'])
        def ButtonHandler(source: 'ExButton', event: str):
            Logger.Log("Button Event", source, event)
            initialState = source.State
            if event is 'Pressed':
                if source.Control.PressStateShift:
                    source.SetState(source.Control.States.Shift)
                
            elif event is 'Released':
                if not source.HasHold():
                    source.Control.Functions.Primary(source, event)
                    
                    if source.Control.IsLatching:
                        source.SetState(source.Control.States.Active)
                    else:
                        source.SetState(source.Control.States.Inactive)
                else:
                    source.Control.Functions.Hold(source, event)
                    if source.Control.HoldLatching:
                        source.SetState(source.Control.States.HoldActive)
                    else:
                        source.SetState(initialState)
            elif event is 'Held':
                if hasattr(source.Control.States, 'HoldShift'):
                    source.SetState(source.Control.States.HoldShift)
            elif event is 'Repeated':
                source.Control.Functions.Repeat(source, event)
            elif event is 'Tapped':
                source.Control.Functions.Primary(source, event)
                
                if source.Control.IsLatching:
                    source.SetState(source.Control.States.Active)
                else:
                    source.SetState(source.Control.States.Inactive)
                        
                    

class ExLabel(Label):
    def __init__(self, 
                 UIHost: Union['UIDevice', 'ExUIDevice', 'ProcessorDevice', 'ExProcessorDevice'], 
                 ID_Name: Union[int, str],
                 **kwargs) -> None:
        super().__init__(UIHost, ID_Name)
        
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

class ExLevel(Level):
    def __init__(self, 
                 UIHost: Union['UIDevice', 'eBUSDevice', 'ProcessorDevice', 'SPDevice', 'ExUIDevice', 'ExEBUSDevice', 'ExProcessorDevice', 'ExSPDevice'], 
                 ID_Name: Union[int, str],
                 **kwargs) -> None:
        super().__init__(UIHost, ID_Name)
        
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

class ExSlider(Slider):
    def __init__(self, 
                 UIHost: Union['UIDevice', 'ProcessorDevice', 'SPDevice', 'ExUIDevice', 'ExProcessorDevice', 'ExSPDevice'], 
                 ID_Name: Union[int, str],
                 **kwargs) -> None:
        super().__init__(UIHost, ID_Name)
        
        self.UIHost = UIHost
        self.Id = self.ID
        
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
        
        for kw, val in kwargs.items():
            setattr(self, kw, val)
            
    def __repr__(self) -> str:
        return "Knob ({})".format(self.Id)

## End Class Definitions -------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------

## End Function Definitions ----------------------------------------------------
