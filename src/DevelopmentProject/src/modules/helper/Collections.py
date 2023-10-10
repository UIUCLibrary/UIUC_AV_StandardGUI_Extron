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
from typing import (TYPE_CHECKING, Dict, Iterator, Tuple, List, Union, Callable, TypeVar,
                    ValuesView, ItemsView, KeysView, Any)

import extronlib.interface
import extronlib.ui
if TYPE_CHECKING: # pragma: no cover
    from modules.helper.PrimitiveObjects import ControlObject, FeedbackObject
    from modules.device.classes.Destinations import Destination
    from modules.device.classes.Sources import Source
    from modules.helper.ExtendedDeviceClasses import ExUIDevice, ExEBUSDevice, ExProcessorDevice
    
    _KT = TypeVar('_KT')

#### Python imports
from collections import UserDict, UserList

#### Extron Library Imports
from extronlib.system import MESet

#### Project imports
from modules.helper.ModuleSupport import WatchVariable
from modules.helper.CommonUtilities import DictValueSearchByKey, RunAsync, debug, Logger
from modules.helper.ModuleSupport import eventEx
from modules.project.SystemHardware import SystemHardwareController
from control.PollController import PollObject
from Constants import BLANK_SOURCE

from modules.helper.ExtendedUIClasses import ExButton, ExKnob, ExLabel, ExLevel, ExSlider, RefButton
from extronlib.ui import Button, Level, Label
    
## End Imports -----------------------------------------------------------------
##
## Begin Class Definitions -----------------------------------------------------

class DictObj:
    def __init__(self, src_dict: dict):
        if type(src_dict) is not dict:
            raise TypeError('DictObj src_dict must be of type dict')
        
        for key, val in src_dict.items():
            if isinstance(val, (list, tuple)):
               setattr(self, key, [DictObj(x) if isinstance(x, dict) else x for x in val])
            else:
               setattr(self, key, DictObj(val) if isinstance(val, dict) else val)
               
    def __repr__(self) -> str:
        return str(self.__dict__)

class DeviceCollection(UserDict):
    # override __init__ to add properties to the device collection
    def __init__(self, __dict: None = None) -> Dict[str, SystemHardwareController]:
        super().__init__(__dict)
        self.DevicesChanged = WatchVariable('Devices Changed Event')
        self.Polling = []
        self.PollingChanged = WatchVariable('Polling Changed Event')
    
    def __repr__(self) -> str:
        sep = ', '
        return "[{}]".format(sep.join([str(val) for val in self.values()]))
    
    # Type cast views for values, items, and keys
    def values(self) -> ValuesView['SystemHardwareController']:
        return super().values()
    
    def items(self) -> ItemsView[str, 'SystemHardwareController']:
        return super().items()
    
    def keys(self) -> KeysView[str]:
        return super().keys()
    
    # Overwrite __setitem__
    # TODO: test this for being able to set a value with a blank index, ie Devices[] = SystemHardwareControllerObject
    def __setitem__(self, key: '_KT', item: 'SystemHardwareController') -> None:
        if type(item) is not SystemHardwareController:
            raise ValueError('DeviceCollection items must be of type SystemHardwareController')
        
        if item.Id in list(self.data.keys()):
            raise ValueError("Duplicate key '{}' found".format(item.Id))
        
        # make sure the collection is properly set for devices as we add them
        if item.Collection is not self:
            item.Collection = self
        
        self.data[item.Id] = item
        
        # Logger.Trace.Log('Devices Changed')
        self.DevicesChanged.Change(self.data)
    
    # Typecasts __getitem__
    def __getitem__(self, key: str) -> 'SystemHardwareController':
        return super().__getitem__(key)
    
    # Add list properties - these generate sublists based on the IsXXX attributes of SystemHardwareController
    @property
    def Destinations(self) -> list:
        return [item for item in self.values() if item.IsDest]
    
    @property
    def Sources(self) -> list:
        return [item for item in self.values() if item.IsSrc]
    
    @property
    def Switches(self) -> list:
        return [item for item in self.values() if item.IsSwitch]
    
    @property
    def Cameras(self) -> list:
        return [item for item in self.values() if item.IsCam]
    
    @property
    def Microphones(self) -> list:
        return [item for item in self.values() if item.IsMic]
    
    @property
    def Screens(self) -> list:
        return [item for item in self.values() if item.IsScn]
    
    @property
    def Lights(self) -> list:
        return [item for item in self.values() if item.IsLight]
    
    @property
    def Shades(self) -> list:
        return [item for item in self.values() if item.IsShade]

    # Special Add Item Methods
    def AddNewDevice(self, **kwargs) -> None:
        device = SystemHardwareController(self, **kwargs)
        self.__setitem__(None, device)
        device.InitializeDevice()
        
    # Search Methods
    def GetDestination(self, id: str=None, name: str=None) -> 'Destination':
        if id != None:
            if hasattr(self.data[id], 'Destination'):
                return self.data[id].Destination
            else:
                raise LookupError("No destination defined for provided id '{}'".format(id))
        elif name != None:
            for dest in self.Destinations:
                if dest.Name == name:
                    return dest.Destination
            raise LookupError("No destination defined for provided name '{}'".format(id))
        else:
            raise ValueError('Either Id or Name must be provided')

    def GetDestinationByOutput(self, outputNum: int) -> 'Destination':
        if outputNum > 0:
            for dest in self.Destinations:
                if dest.Destination.Output == outputNum:
                    return dest.Destination
            raise LookupError("Provided Output '{}' is not configured to a destination".format(outputNum))
        else:
            raise ValueError('ouptutNum must be an integer greater than 0')

    def GetSource(self, id: str=None, name: str=None) -> 'Source':
        if id != None:
            if hasattr(self.data[id], 'Source'):
                return self.data[id].Source
            else:
                raise LookupError("No source defined for provided id '{}'".format(id))
        elif name != None:
            for src in self.Sources:
                if src.Name == name:
                    return src.Source
            raise LookupError("No source defined for provided name '{}'".format(id))
        else:
            raise ValueError('Either Id or Name must be provided')

    def GetSourceByInput(self, inputNum: int) -> 'Source':
        if inputNum == 0:
            return BLANK_SOURCE
        elif inputNum > 0:
            for src in self.Sources:
                if src.Source.Input == inputNum:
                    return src.Source
            raise LookupError("Provided inputNum '{}' is not configured to a destination".format(inputNum))
        else:
            raise ValueError('inputNum must be an integer greater than 0')
        
    # Polling
    def AddPolling(self, device, command, qualifier=None, active_duration: int=None, inactive_duration: int=None):
        # Logger.Log(device, self.data.values(), sep='\n')
        if device not in self.data.values():
            raise LookupError('device must be in DeviceCollection')
            
        self.Polling.append(PollObject(**{
            'Device': device,
            'Command': command,
            'Qualifier': qualifier,
            'ActiveDuration': active_duration,
            'InactiveDuration': inactive_duration
        }))
        
        self.PollingChanged.Change(self.Polling)
        
    def RemovePolling(self, device, command):
        if device not in self.data:
            raise LookupError('device must be in DeviceCollection')
        
        changed = False
        for poll in self.Polling:
            if poll.Device == device and poll.Command == command:
                i = self.Polling.index(poll)
                self.Polling.pop(i)
                changed = True
        
        if changed:
            self.PollingChanged.Change(self.Polling)
        else: 
            raise ValueError('No polling exists to remove for provided device ({}) and command ({})'.format(device.Id, command))
            
    def UpdatePolling(self, device, command, qualifier={}, active_duration: int=None, inactive_duration: int=None):
        if device not in self.data:
            raise LookupError('device must be in DeviceCollection')
        
        matched = False
        changed = False
        for poll in self.Polling:
            if poll.Device == device and poll.Command == command:
                matched = True
                if active_duration is not None and poll.ActiveDuration != active_duration:
                    poll.ActiveDuration = active_duration
                    changed = True
                    
                if inactive_duration is not None and poll.InactiveDuration != inactive_duration:
                    poll.InactiveDuration = inactive_duration
                    changed = True
                
                if poll.Qualifier != qualifier and qualifier != {}:
                    poll.Qualifier =  qualifier
                    changed = True
                    
        if changed:
            self.PollingChanged.Change(self.Polling)
        else:
            if not matched: # not matched or changed
                raise ValueError('No polling exists to update for provided device ({}) and command ({})'.format(device.Id, command))
            else: # matched but not changed
                raise ValueError('No valid update to polling provided')

class UIObjectCollection(UserDict):
    def __init__(self, __dict: None = None) -> Dict[str, Union['ExButton', 'ExKnob', 'ExLabel', 'ExLevel', 'ExSlider', 'RefButton']]:
        super().__init__(__dict)
        
    def __repr__(self) -> str:
        sep = ', '
        return "[{}]".format(sep.join([str(val) for val in self.values()]))
    
    # Type cast views for values, items, and keys
    def values(self) -> ValuesView[Union['ExButton', 'ExKnob', 'ExLabel', 'ExLevel', 'ExSlider', 'RefButton']]:
        return super().values()
    
    def items(self) -> ItemsView[str, Union['ExButton', 'ExKnob', 'ExLabel', 'ExLevel', 'ExSlider', 'RefButton']]:
        return super().items()
    
    def keys(self) -> KeysView[str]:
        return super().keys()
    
    # Typecasts __getitem__
    def __getitem__(self, key: Union[str, int]) -> Union['ExButton', 'ExKnob', 'ExLabel', 'ExLevel', 'ExSlider', 'RefButton']:
        if (type(key) is str) and not key.isnumeric():
            return super().__getitem__(key)
        elif (type(key) is int) or ((type(key) is str) and key.isnumeric()):
            if type(key) is str:
                key = int(key)
                
            for val in self.values():
                if val.Id == key:
                    return val
        else:
            raise TypeError("__getitem__ key must be a string or int")

class ControlGroupCollection(UserDict):
    def __init__(self, _dict: None = None) -> Dict[str, Union['RadioSet', 'SelectSet', 'VariableRadioSet', 'ScrollingRadioSet']]:
        return super().__init__(_dict)
    
    def __repr__(self) -> str:
        sep = ', '
        return "[{}]".format(sep.join([str(val) for val in self.values()]))
    
    # Type cast views for values, items, keys, and getitem
    def values(self) -> ValuesView[Union['RadioSet', 'SelectSet', 'VariableRadioSet', 'ScrollingRadioSet']]:
        return super().values()
    
    def items(self) -> ItemsView[str, Union['RadioSet', 'SelectSet', 'VariableRadioSet', 'ScrollingRadioSet']]:
        return super().items()
    
    def keys(self) -> KeysView[str]:
        return super().keys()
    
    def __getitem__(self, key: str) -> Union['RadioSet', 'SelectSet', 'VariableRadioSet', 'ScrollingRadioSet']:
        return super().__getitem__(key)
    
    def ShowPopups(self) -> None:
        for ctlGrp in self.data.values():
            if hasattr(ctlGrp, 'ShowPopup'):
                ctlGrp.ShowPopup()

class UIDeviceCollection(UserList):
    def __init__(self, __list: None = None) -> List[Union['ExUIDevice', 'ExEBUSDevice']]:
        return super().__init__(__list)
        
    def __repr__(self) -> str:
        sep = ', '
        return "[{}]".format(sep.join([str(val) for val in self]))
    
    # Type cast getitem & iter
    def __getitem__(self, index: int) -> Union['ExUIDevice', 'ExEBUSDevice']:
        return super().__getitem__(index)
        
    def __iter__(self) -> Iterator[Union['ExUIDevice', 'ExEBUSDevice']]:
        return super().__iter__()
    

class ProcessorCollection(UserList):
    def __init__(self, __list: None = None) -> List['ExProcessorDevice']:
        super().__init__(__list)
        
    def __repr__(self) -> str:
        sep = ', '
        return "[{}]".format(sep.join([str(val) for val in self]))
    
    # Type cast getitem & iter
    def __getitem__(self, index: int) -> 'ExProcessorDevice':
        return super().__getitem__(index)
        
    def __iter__(self) -> Iterator['ExProcessorDevice']:
        return super().__iter__()

class RadioSet(MESet):
    def __init__(self, 
                 Name: str,
                 Objects: List[Union['Button', 'ExButton', 'RefButton']]) -> None:
        super().__init__(Objects)
        self.__Name = Name
        
        for btn in self.Objects:
            setattr(btn, 'Group', self)
    
    def __repr__(self) -> str:
        sep = ', '
        return "RadioSet (Current: {}) [{}]".format(self.GetCurrent(), sep.join([str(val) for val in self.Objects]))
    
    @property
    def Name(self) -> str:
        return self.__Name
    
    @Name.setter
    def Name(self, val) -> None:
        raise AttributeError('Overriding the Name property is disallowed')
    
    @property
    def Objects(self) -> List[Union['Button', 'ExButton', 'RefButton']]:
        return super().Objects
    
    @Objects.setter
    def Objects(self, val) -> None:
        raise AttributeError('Overriding the Objects property is not allowed')
    
    def GetCurrent(self) -> Union['Button', 'ExButton', 'RefButton']:
        return super().GetCurrent()
    
    def Append(self, obj: Union['Button', 'ExButton']) -> None:
        setattr(obj, 'Group', self)
        return super().Append(obj)
    
    def Remove(self, obj: Union[List[Union[str, int, 'Button', 'ExButton', 'RefButton']], str, int, 'Button', 'ExButton', 'RefButton']) -> None:
        if type(obj) is list:
            for item in obj:
                self.Remove(item)
        elif type(obj) in [int, Button, ExButton, RefButton]:
            if type(obj) is int:
                delattr(self.Objects[obj], 'Group')
            elif obj in self.Objects:
                delattr(obj, 'Group')
            super().Remove(obj)
        elif type (obj) is str:
            i = None
            for o in self.Objects:
                if o.Name == obj:
                    i = self.Objects.index(o)
                    break
            if i is not None:
                delattr(self.Objects[i], 'Group')
                super().Remove(i)
            else:
                raise ValueError('No object found for name ({}) in radio set'.format(obj))
        elif obj is not None:
            raise TypeError("Object must be string object name, int index, or the button object (Button or ExButton class)")
    
    def SetCurrent(self, obj: Union[int, str, 'Button', 'ExButton', 'RefButton']) -> None:
        if type(obj) in [int, Button, ExButton, RefButton]:
            super().SetCurrent(obj)
        elif obj is None:
            super().SetCurrent(obj)
        elif type(obj) is str:
            i = None
            for o in self.Objects:
                if o.Name == obj:
                    i = self.Objects.index(o)
                    break
            if i is not None:
                super().SetCurrent(i)
            else:
                raise ValueError('No object found for name ({}) in radio set'.format(obj))
        else:
            raise TypeError("Object must be string object name, int index, or the button object (Button or ExButton class)")
    
    def SetStates(self, obj: Union[List[Union[str, int, 'Button', 'ExButton', 'RefButton']], str, int, 'Button', 'ExButton', 'RefButton'], offState: int, onState: int) -> None:
        if type(obj) is list:
            for item in obj:
                self.SetStates(item, offState, onState)
        elif type(obj) in [int, Button, ExButton, RefButton]:
            super().SetStates(obj, offState, onState)
        elif type(obj) is str:
            i = None
            for o in self.Objects:
                if o.Name == obj:
                    i = self.Objects.index(o)
                    break
            if i is not None:
                super().SetStates(i, offState, onState)
            else:
                raise ValueError('No object found for name ({}) in radio set'.format(obj))
        elif obj is not None:
            raise TypeError("Object must be string object name, int index, or the button object (Button or ExButton class)")
    
    def SetControlObject(self, Control: 'ControlObject'):
        if type(Control) is ControlObject:
            self.__Control = Control
        else:
            raise TypeError('Control must be a ControlObject')
        
        # TODO: create button events here
        Logger.Log('RadioSet ControlObject:', Control)
    
class SelectSet():
    def __init__(self, 
                 Name: str,
                 Objects: List[Union['Button', 'ExButton', 'RefButton']]) -> None:
        self.__Name = Name
        self.__StateList = []
        
        self.__Objects = Objects
        
        for o in self.__Objects:
            self.__StateList.append({"onState": 0, "offState": 1})
            setattr(o, 'Group', self)
    
    def __repr__(self) -> str:
        sep = ', '
        return "SelectSet (Current: [{}]) [{}]".format(sep.join([str(val) for val in self.GetActive()]), sep.join([str(val) for val in self.Objects]))
    
    @property
    def Name(self) -> str:
        return self.__Name
    
    @Name.setter
    def Name(self, val) -> None:
        raise AttributeError('Overriding the Name property is disallowed')
    
    @property
    def Objects(self) -> List[Union['Button', 'ExButton', 'RefButton']]:
        return self.__Objects
    
    @Objects.setter
    def Objects(self, val) -> None:
        raise AttributeError('Overriding the Objects property is not allowed')
    
    def Append(self, obj: Union['Button', 'ExButton', 'RefButton']) -> None:
        setattr(obj, 'Group', self)
        self.__Objects.append(obj)
        self.__StateList.append({"onState": 0, "offState": 1})
        
    def GetActive(self) -> List[Union['Button', 'ExButton', 'RefButton']]:
        activeList = []
        
        for o in self.__Objects:
            if o.State == self.__StateList[self.__Objects.index(o)]['onState']:
                activeList.append(o)
        
        return activeList
    
    def Remove(self, obj: Union[List[Union[str, int, 'Button', 'ExButton', 'RefButton']], str, int, 'Button', 'ExButton', 'RefButton']) -> None:
        if type(obj) is list:
            for item in obj:
                self.Remove(item)
        elif type(obj) is int:
            delattr(self.__Objects[obj], 'Group')
            self.__Objects.pop(obj)
            self.__StateList.pop(obj)
        elif type(obj) in [Button, ExButton, RefButton]:
            delattr(obj, 'Group')
            i = self.__Objects.index(obj)
            self.__Objects.pop(obj)
            self.__StateList.pop(obj)
        elif type(obj) is str:
            i = None
            for o in self.__Objects:
                if o.Name == obj:
                    i = self.__Objects.index(o)
                    break
            if i is not None:
                delattr(self.__Objects[obj], 'Group')
                self.__Objects.pop(obj)
                self.__StateList.pop(obj)
            else:
                raise ValueError('No object found for name ({}) in select set'.format(obj))
        elif obj is not None:
            raise TypeError("Object must be string object name, int index, or the button object (Button or ExButton class)")
    
    def SetActive(self, obj: Union[List[Union[str, int, 'Button', 'ExButton', 'RefButton']], str, int, 'Button', 'ExButton', 'RefButton']) -> None:
        if type(obj) is list:
            for item in obj:
                self.SetActive(item)
        elif obj in ['all', 'All', 'ALL']:
            for o in self.__Objects:
                o.SetState(self.__StateList[self.__Objects.index(o)]['onState'])
        elif obj in ['none', 'None', 'NONE'] or obj is None:
            for o in self.__Objects:
                o.SetState(self.__StateList[self.__Objects.index(o)]['offState'])
        elif type(obj) is int:
            self.__Objects[obj].SetState(self.__StateList[obj]['onState'])
        elif type(obj) is str:
            i = None
            for o in self.__Objects:
                if o.Name == obj:
                    i = self.__Objects.index(o)
                    break
            if i is not None:
                self.__Objects[i].SetState(self.__StateList[i]['onState'])
            else:
                raise ValueError('No object found for name ({}) in select set'.format(obj))
        elif type(obj) in [Button, ExButton, RefButton]:
            if obj in self.__Objects:
                obj.SetState(self.__StateList[self.__Objects.index(obj)]['onState'])
            else:
                raise IndexError('Object not found in select list')
        elif obj is not None:
            raise TypeError('Object must be an object name, int index, the button object (Button or ExButton class), or List of these')

    def SetStates(self, obj: Union[List[Union[str, int, 'Button', 'ExButton', 'RefButton']], str, int, 'Button', 'ExButton', 'RefButton'], offState: int, onState: int) -> None:
        if type(obj) is list:
            for item in obj:
                self.SetStates(item, offState, onState)
        elif type(obj) is int:
            self.__StateList[obj]['onState'] = onState
            self.__StateList[obj]['offState'] = offState
        elif type(obj) in [Button, ExButton, RefButton]:
            i = self.__Objects.index(obj)
            self.__StateList[i]['onState'] = onState
            self.__StateList[i]['offState'] = offState
        elif type(obj) is str:
            i = None
            for o in self.__Objects:
                if o.Name == obj:
                    i = self.__Objects.index(o)
                    break
            if i is not None:
                self.__StateList[i]['onState'] = onState
                self.__StateList[i]['offState'] = offState
            else:
                raise ValueError('No object found for name ({}) in select set'.format(obj))
        elif obj is not None:
            raise TypeError("Object must be string object name, int index, or the button object (Button or ExButton class)")
    
    def SetControlObject(self, Control: 'ControlObject'):
        if type(Control) is ControlObject:
            self.__Control = Control
        else:
            raise TypeError('Control must be a ControlObject')
        
        # TODO: create button events here
        Logger.Log('SelectSet ControlObject:', Control)
    
class VariableRadioSet():
    def __init__(self, 
                 Name: str,
                 Objects: List[Union['Button', 'ExButton']],
                 PopupCallback: Callable,
                 PopupGroups: List[Dict[str, str]] = None) -> None:
        
        self.__Name = Name
        self.__BtnSet = RadioSet('{}-Objects'.format(self.Name), Objects)
        self.__PopupCallback = PopupCallback
        self.__PopupGroups = PopupGroups
        self.__Control = None
        
        for btn in self.Objects:
            setattr(btn, 'Group', self)
    
    def __repr__(self) -> str:
        sep = ', '
        return "VariableRadioSet (Current: {}, Popup: {}) [{}]".format(self.GetCurrent(), self.PopupName, sep.join([str(val) for val in self.Objects]))
    
    @property
    def Name(self) -> str:
        return self.__Name
    
    @Name.setter
    def Name(self, val) -> None:
        raise AttributeError('Overriding the Name property is disallowed')
    
    @property
    def Objects(self) -> List[Union['Button', 'ExButton']]:
        return self.__BtnSet.Objects
    
    @Objects.setter
    def Objects(self, val) -> None:
        raise AttributeError('Overriding the Objects property is disallowed')
    
    @property
    def PopupName(self) -> str:
        return self.__PopupCallback(self.__BtnSet.Objects)
    
    @PopupName.setter
    def PopupName(self, val) -> None:
        raise AttributeError('Overriding the PopupName property is disallowed')
    
    @property
    def Control(self) -> 'ControlObject':
        return self.__Control
    
    @Control.setter
    def Control(self, val) -> None:
        raise AttributeError('Overriding Control property directly is disallowed. Use "SetControlObject" instead.')
    
    
    def Append(self, obj: Union['Button', 'ExButton'] = None) -> None:
        if obj is not None:
            setattr(obj, 'Group', self)
            self.__BtnSet.Append(obj)
            
    def GetCurrent(self) -> Union['Button', 'ExButton']:
        return self.__BtnSet.GetCurrent()
    
    def Remove(self, 
               Object: Union[int, str, 'Button', 'ExButton'] = None, 
               Popup: Union[int, str] = None) -> None:
        
        if Object is not None:
            self.__BtnSet.Remove(Object)
            
        if Popup is not None:
            if type(Popup) is int:
                self.__PopupDict.pop(Popup)
            elif type(Popup) is str:
                for key, val in self.__PopupDict:
                    if val == Popup:
                        self.__PopupDict.pop(key)
                        break
            else:
                raise TypeError('Popup must either by an int or str')
            
        self.__PopupKey = self.__GetPopupKey()
            
    def SetCurrent(self, obj: Union[int, str, 'Button', 'ExButton']) -> None:
        self.__BtnSet.SetCurrent(obj)
        
    def SetStates(self, 
                  obj: Union[List[Union[int, str, 'Button', 'ExButton']], 
                             int, 
                             str, 
                             'Button', 
                             'ExButton'], 
                  offState: int, 
                  onState: int) -> None:
        
        self.__BtnSet.SetStates(obj, offState, onState)
        
    def ShowPopup(self) -> None:
        if self.__PopupGroups is not None:
            for pug in self.__PopupGroups:
                if pug['Suffix'] is None:
                    self.__BtnSet.Objects[0].Host.ShowPopup(self.PopupName)
                else:
                    self.__BtnSet.Objects[0].Host.ShowPopup('{}_{}'.format(self.PopupName, str(pug['Suffix'])))
        else:
            self.__BtnSet.Objects[0].Host.ShowPopup(self.PopupName)
    
    def SetControlObject(self, Control: 'ControlObject'):
        self.__Control = Control
        
        Logger.Log('Assigning Control Event', self, Control)
        
        @eventEx(self.Objects, ['Pressed', 'Released', 'Held', 'Repeated', 'Tapped'])
        def ButtonHandler(source: 'ExButton', event: str):
            Logger.Log('Button Event', source, event)
            initialState = source.State
            
            if event is 'Pressed':
                if self.Control.PressStateShift:
                    source.SetState(self.Control.States.Shift)
                
            elif event is 'Released':
                if not source.HasHold():
                    self.Control.Functions.Primary(source, event)
                    self.SetCurrent(source)
                else:
                    self.Control.Functions.Hold(source, event)
                    if self.Control.HoldLatching:
                        source.SetState(self.Control.States.HoldActive)
                    else:
                        source.SetState(initialState)
            elif event is 'Held':
                if hasattr(source.Control.States, 'HoldShift'):
                    source.SetState(source.Control.States.HoldShift)
            elif event is 'Repeated':
                source.Control.Functions.Repeat(source, event)
            elif event is 'Tapped':
                source.Control.Functions.Primary(source, event)
                self.SetCurrent(source)
        
class ScrollingRadioSet():
    def __init__(self, 
                 Name: str,
                 Objects: List[Union['Button', 'ExButton']], 
                 RefObjects: List['RefButton'],
                 PrevBtn: Union['Button', 'ExButton'], 
                 NextBtn: Union['Button', 'ExButton'], 
                 PopupCallback: Callable,
                 PopupGroups: List[Dict[str, str]] = None) -> None:
        self.__Name = Name
        self.__Offset = 0
        self.__BtnSet = RadioSet('{}-Objects'.format(self.Name), Objects)
        setattr(self.__BtnSet, 'Group', self)
        self.__RefSet = RadioSet('{}-RefObjects'.format(self.Name), RefObjects)
        setattr(self.__RefSet, 'Group', self)
        self.__Prev = PrevBtn
        setattr(self.__Prev, 'Group', self)
        self.__Next = NextBtn
        setattr(self.__Next, 'Group', self)
        
        self.__PopupCallback = PopupCallback
        self.__PopupGroups = PopupGroups
        
        for btn in self.Objects:
            btn.Group = self
        for btn in self.RefObjects:
            btn.Group = self

    def __repr__(self) -> str:
        sep = ', '
        return "ScrollingRadioSet (Current: {}, Popup: {}) [{}]".format(self.GetCurrentRef(), self.PopupName, sep.join([str(val) for val in self.RefObjects]))
    
    @property
    def Name(self) -> str:
        return self.__Name
    
    @Name.setter
    def Name(self, val) -> None:
        raise AttributeError('Overriding the Name property is disallowed')
    
    @property
    def Objects(self) -> List[Union['Button', 'ExButton']]:
        return self.__BtnSet.Objects
    
    @Objects.setter
    def Objects(self, val) -> None:
        raise AttributeError('Overriding the Objects property is disallowed')
    
    @property
    def RefObjects(self) -> List['RefButton']:
        return self.__RefSet.Objects
    
    @RefObjects.setter
    def RefObjects(self, val) -> None:
        raise AttributeError('Overriding the RefObjects property is disallowed')
    
    @property
    def Offset(self) -> int:
        return self.__Offset
    
    @Offset.setter
    def Offset(self, val) -> None:
        raise AttributeError('Overriding the Offset property is disallowed')
    
    @property
    def PopupName(self) -> str:
        return self.__PopupCallback(self.__RefSet.Objects)
    
    @PopupName.setter
    def PopupName(self, val) -> None:
        raise AttributeError('Overriding the PopupName property is disallowed')
    
    def GetRefByObject(self, obj: Union[int, str, 'Button', 'ExButton']) -> 'RefButton':
        if type(obj) is int:
            return self.__RefSet.Objects[obj + self.__Offset]
        elif type(obj) is str:
            for btn in self.__BtnSet.Objects:
                if btn.Name == obj:
                    return self.__RefSet.Objects[self.__BtnSet.Objects.index(btn)]
            return None
        elif type(obj) in [Button, ExButton]:
            return self.__RefSet.Objects[self.__BtnSet.Objects.index(obj)]
        else:
            raise TypeError('obj must be an index int, name str, Button or ExButton object')
    
    def GetCurrentButton(self) -> Union['Button', 'ExButton']:
        return self.__BtnSet.GetCurrent()
    
    def GetCurrentRef(self) -> 'RefButton':
        return self.__RefSet.GetCurrent()
    
    def AppendButton(self, btn: Union['Button', 'ExButton']) -> None:
        self.__BtnSet.Append(btn)
        btn.Group = self
    
    def AppendRef(self, ref: 'RefButton') -> None:
        self.__RefSet.Append(ref)
        ref.Group = self
        
    def RemoveButton(self, btn: Union[List[Union[int, str, 'Button', 'ExButton']], int, str, 'Button', 'ExButton']) -> None:
        self.__BtnSet.Remove(btn)
        
    def RemoveRef(self, btn: Union[List[Union[int, str, 'RefButton']], int, str, 'RefButton']) -> None:
        self.__RefSet.Remove(btn)
        
    def SetCurrentButton(self, btn: Union[int, str, 'Button', 'ExButton', None]) -> None:
        self.__BtnSet.SetCurrent(btn)
        
        index = self.__BtnSet.Objects.index(self.__BtnSet.GetCurrent())
        refIndex = index + self.__Offset
        self.__RefSet.SetCurrent(refIndex)
        
    def SetCurrentRef(self, ref: Union[int, str, 'RefButton']) -> None:
        self.__RefSet.SetCurrent(ref)
        
        index = self.__RefSet.Objects.index(self.__RefSet.GetCurrent())
        btnIndex = index - self.__Offset
        
        if btnIndex < 0:
            self.__BtnSet.SetCurrent(None)
        elif btnIndex >= 0 and btnIndex < len(self.__BtnSet.Objects):
            self.__BtnSet.SetCurrent(btnIndex)
        elif btnIndex > len(self.__BtnSet.Objects):
            self.__BtnSet.SetCurrent(None)
            
    def SetStates(self, obj: Union[List[Union[int, str, 'Button', 'ExButton']], int, str, 'Button', 'ExButton'], offState: int, onState: int) -> None:
        self.__BtnSet.SetStates(obj, offState, onState)
        
    def ShowPopup(self, suffix: str=None) -> None:
        if self.__PopupGroups is not None:
            for pug in self.__PopupGroups:
                if pug['Suffix'] is None:
                    self.__BtnSet.Objects[0].Host.ShowPopup(self.PopupName)
                else:
                    self.__BtnSet.Objects[0].Host.ShowPopup('{}_{}'.format(self.PopupName, str(pug['Suffix'])))
        else:
            self.__BtnSet.Objects[0].Host.ShowPopup(self.PopupName)
    
    def SetControlObject(self, Control: 'ControlObject'):
        if type(Control) is ControlObject:
            self.__Control = Control
        else:
            raise TypeError('Control must be a ControlObject')
        
        # TODO: create button events here
        Logger.Log('ScrollingRadioSet ControlObject:', Control)
        
class VolumeControlGroup():
    def __init__(self,
                 Name: str,
                 VolUp: Union['Button', 'ExButton'],
                 VolDown: Union['Button', 'ExButton'],
                 Mute: Union['Button', 'ExButton'],
                 Feedback: Union['Level', 'ExLevel'],
                 ControlLabel: Union['Label', 'ExLabel']=None,
                 DisplayName: str=None,
                 Range: Tuple[int, int, int]=(0, 100, 1)
                 ) -> None:
        
        self.__Name = Name
        
        if type(VolUp) in [Button, ExButton]:
            self.VolUpBtn = VolUp
            setattr(self.VolUpBtn, 'Group', self)
        else:
            raise TypeError("VolUp must be an Extron Button object")
        
        if type(VolDown) in [Button, ExButton]:
            self.VolDownBtn = VolDown
            setattr(self.VolDownBtn, 'Group', self)
        else:
            raise TypeError("VolDown must be an Extron Button object")
        
        if type(Mute) in [Button, ExButton]:
            self.MuteBtn = Mute
            setattr(self.MuteBtn, 'Group', self)
        else:
            raise TypeError("Mute must be an Extron Button object")
        
        if type(Feedback) in [Level, ExLevel]:
            self.FeedbackLvl = Feedback
            setattr(self.FeedbackLvl, 'Group', self)
        else:
            raise TypeError("Feedback must be an Extron Level object")
        
        if type(ControlLabel) in [Label, ExLabel] or ControlLabel is None:
            self.ControlLbl = ControlLabel
            setattr(self.ControlLbl, 'Group', self)
        else:
            raise TypeError("ControlLabel must either be an Extron Label object or None (default)")
        
        if DisplayName is not None:
            self.DisplayName = DisplayName
        else:
            self.DisplayName = Name
            
        if type(Range) is tuple and len(Range) == 3:
            for i in Range:
                if type(i) is not int:
                    raise TypeError("Range tuple may only consist of int values")
            self.__Range = Range
            self.FeedbackLvl.SetRange(*Range)
        
    @property
    def Name(self) -> str:
        return self.__Name
    
    @Name.setter
    def Name(self, val) -> None:
        raise AttributeError('Overriding the Name property is disallowed')
    
    def SetControlObject(self, Control: 'ControlObject'):
        if type(Control) is ControlObject:
            self.__Control = Control
        else:
            raise TypeError('Control must be a ControlObject')
        
        # TODO: create button events here
        Logger.Log('VolumeControlGroup ControlObject:', Control)

## End Class Definitions -------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------

## End Function Definitions ----------------------------------------------------



