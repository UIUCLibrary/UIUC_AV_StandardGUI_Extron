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
from typing import (TYPE_CHECKING, Dict, Tuple, List, Union, Callable, TypeVar,
                    ValuesView, ItemsView, KeysView, Any)

import extronlib.interface
if TYPE_CHECKING: # pragma: no cover
    from modules.device.classes.Destinations import Destination
    from modules.device.classes.Sources import Source
    from modules.project.ExtendedUIClasses import ExButton, ExKnob, ExLabel, ExLevel, ExSlider, SelectObject
    from extronlib.ui import Button, Level, Label
    _KT = TypeVar('_KT')

#### Python imports
from collections import UserDict

#### Extron Library Imports
from extronlib.system import MESet

#### Project imports
from modules.helper.ModuleSupport import WatchVariable
from modules.helper.CommonUtilities import DictValueSearchByKey, RunAsync, debug, Logger
from modules.project.SystemHardware import SystemHardwareController
from control.PollController import PollObject
from Variables import BLANK_SOURCE

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
    def __init__(self, __dict: None = None) -> Dict[str, Union['ExButton', 'ExKnob', 'ExLabel', 'ExLevel', 'ExSlider', 'SelectObject']]:
        super().__init__(__dict)
        
    def __repr__(self) -> str:
        sep = ', '
        return "[{}]".format(sep.join([str(val) for val in self.values()]))
    
    # Type cast views for values, items, and keys
    def values(self) -> ValuesView[Union['ExButton', 'ExKnob', 'ExLabel', 'ExLevel', 'ExSlider', 'SelectObject']]:
        return super().values()
    
    def items(self) -> ItemsView[str, Union['ExButton', 'ExKnob', 'ExLabel', 'ExLevel', 'ExSlider', 'SelectObject']]:
        return super().items()
    
    def keys(self) -> KeysView[str]:
        return super().keys()
    
    # Typecasts __getitem__
    def __getitem__(self, key: Union[str, int]) -> Union['ExButton', 'ExKnob', 'ExLabel', 'ExLevel', 'ExSlider', 'SelectObject']:
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

class RadioSet(MESet):
    def __init__(self, Objects: List[Union['Button', 'ExButton', 'SelectObject']]) -> None:
        super().__init__(Objects)
    
    @property
    def Objects(self) -> List[Union['Button', 'ExButton', 'SelectObject']]:
        return super().Objects
    
    @Objects.setter
    def Objects(self, val) -> None:
        raise ValueError('Overriding the Objects property is not allowed')
    
    def GetCurrent(self) -> Union['Button', 'ExButton', 'SelectObject']:
        return super().GetCurrent()
    
    def Remove(self, obj: Union[List[Union[str, int, 'Button', 'ExButton', 'SelectObject']], str, int, 'Button', 'ExButton', 'SelectObject']) -> None:
        if type(obj) is list:
            for item in obj:
                self.Remove(item)
        elif type(obj) in [int, Button, ExButton, SelectObject]:
            super().Remove(obj)
        elif type (obj) is str:
            i = None
            for o in self.Objects:
                if o.Name == obj:
                    i = self.Objects.index(o)
                    break
            if i is not None:
                super().Remove(i)
            else:
                raise ValueError('No object found for name ({}) in radio set'.format(obj))
        else:
            raise TypeError("Object must be string object name, int index, or the button object (Button or ExButton class)")
    
    def SetCurrent(self, obj: Union[int, str, 'Button', 'ExButton', 'SelectObject']) -> None:
        if type(obj) in [int, Button, ExButton, SelectObject]:
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
    
    def SetStates(self, obj: Union[List[Union[str, int, 'Button', 'ExButton', 'SelectObject']], str, int, 'Button', 'ExButton', 'SelectObject'], offState: int, onState: int) -> None:
        if type(obj) is list:
            for item in obj:
                self.SetStates(item, offState, onState)
        elif type(obj) in [int, Button, ExButton, SelectObject]:
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
        else:
            raise TypeError("Object must be string object name, int index, or the button object (Button or ExButton class)")
    
class SelectSet():
    def __init__(self, Objects: List[Union['Button', 'ExButton', 'SelectObject']]) -> None:
        self.__StateList = []
        
        self.__Objects = Objects
        
        for o in self.__Objects:
            self.__StateList.append({"onState": 0, "offState": 1})
    
    @property
    def Objects(self) -> List[Union['Button', 'ExButton', 'SelectObject']]:
        return self.__Objects
    
    @Objects.setter
    def Objects(self, val) -> None:
        raise ValueError('Overriding the Objects property is not allowed')
    
    def Append(self, obj: Union['Button', 'ExButton', 'SelectObject']) -> None:
        self.__Objects.append(obj)
        self.__StateList.append({"onState": 0, "offState": 1})
        
    def GetActive(self) -> List[Union['Button', 'ExButton', 'SelectObject']]:
        activeList = []
        
        for o in self.__Objects:
            if o.State == self.__StateList[self.__Objects.index(o)]['onState']:
                activeList.append(o)
        
        return activeList
    
    def Remove(self, obj: Union[List[Union[str, int, 'Button', 'ExButton', 'SelectObject']], str, int, 'Button', 'ExButton', 'SelectObject']) -> None:
        if type(obj) is list:
            for item in obj:
                self.Remove(item)
        elif type(obj) is int:
            self.__Objects.pop(obj)
            self.__StateList.pop(obj)
        elif type(obj) in [Button, ExButton, SelectObject]:
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
                self.__Objects.pop(obj)
                self.__StateList.pop(obj)
            else:
                raise ValueError('No object found for name ({}) in select set'.format(obj))
        else:
            raise TypeError("Object must be string object name, int index, or the button object (Button or ExButton class)")
    
    def SetActive(self, obj: Union[List[Union[str, int, 'Button', 'ExButton', 'SelectObject']], str, int, 'Button', 'ExButton', 'SelectObject']) -> None:
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
        elif type(obj) in [Button, ExButton, SelectObject]:
            if obj in self.__Objects:
                obj.SetState(self.__StateList[self.__Objects.index(obj)]['onState'])
            else:
                raise IndexError('Object not found in select list')
        else:
            raise TypeError('Object must be an object name, int index, the button object (Button or ExButton class), or List of these')

    def SetStates(self, obj: Union[List[Union[str, int, 'Button', 'ExButton', 'SelectObject']], str, int, 'Button', 'ExButton', 'SelectObject'], offState: int, onState: int) -> None:
        if type(obj) is list:
            for item in obj:
                self.SetStates(item, offState, onState)
        elif type(obj) is int:
            self.__StateList[obj]['onState'] = onState
            self.__StateList[obj]['offState'] = offState
        elif type(obj) in [Button, ExButton, SelectObject]:
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
        else:
            raise TypeError("Object must be string object name, int index, or the button object (Button or ExButton class)")
    
class VariableSelectSet():
    def __init__(self, 
                 Objects: List[Union['Button', 'ExButton']], 
                 PopupDict: Dict[int, str], 
                 Selects: List['SelectObject']) -> None:
        
        self.__ButtonSet = RadioSet(Objects)
        self.__PopupDict = PopupDict
        self.__SelectSet = RadioSet(Selects)
        
    @property
    def Objects(self) -> List[Union['Button', 'ExButton']]:
        return self.__ButtonSet.Objects
    
    @Objects.setter
    def Objects(self, val) -> None:
        raise ValueError('Overriding the Objects property is disallowed')
    
    @property
    def Selects(self) -> List['SelectObject']:
        return self.__SelectSet.Objects
    
    @Selects.setter
    def Selects(self, val) -> None:
        raise ValueError('Overriding the Selects property is disallowed')
    
    def Append(self, 
               Object: Union['Button', 'ExButton'] = None, 
               Popup: Tuple[Union[int, str]] = None, 
               Select: 'SelectObject' = None) -> None:
        
        if Object is not None:
            self.__ButtonSet.Append(Object)
            
        if Popup is not None:
            self.__PopupDict[Popup[0]] = Popup[1]
            
        if Select is not None:
            self.__SelectSet.append(Select)
            
    def GetCurrent(self) -> 'SelectObject':
        return self.__SelectSet.GetCurrent()
    
    def Remove(self, 
               Object: Union[int, str, 'Button', 'ExButton'] = None, 
               Popup: Union[int, str] = None, 
               Select: Union[int, str, 'SelectObject'] = None) -> None:
        
        if Object is not None:
            self.__ButtonSet.Remove(Object)
            
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
        
        if Select is not None:
            self.__SelectSet.Remove(Select)
            
    def SetCurrent(self, obj: Union[int, str, 'Button', 'ExButton', 'SelectObject']) -> None:
        pass
        # TODO: check for type
        # if int, str, or SelectObject, set current through __SelectSet
        # if Button or ExButton, map Button to Select then set current through __SelectSet
        
    def SetStates(self, 
                  obj: Union[List[Union[int, str, 'Button', 'ExButton']], 
                             int, 
                             str, 
                             'Button', 
                             'ExButton'], 
                  offState: int, 
                  onState: int) -> None:
        
        self.__ButtonSet.SetStates(obj, offState, onState)
        
    
class ScollingSelectSet(VariableSelectSet):
    def __init__(self, 
                 Objects: List[Union['Button', 'ExButton']], 
                 PrevBtn: Union['Button', 'ExButton'], 
                 NextBtn: Union['Button', 'ExButton'], 
                 PopupDict: Dict[int, str], 
                 ConfigList: List['SelectObject']) -> None:
        super().__init__(Objects, PopupDict, ConfigList)
        self.__Prev = PrevBtn
        self.__Next = NextBtn
    
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
        
        self.Name = Name
        
        if type(VolUp) in [Button, ExButton]:
            self.VolUpBtn = VolUp
        else:
            raise TypeError("VolUp must be an Extron Button object")
        
        if type(VolDown) in [Button, ExButton]:
            self.VolDownBtn = VolDown
        else:
            raise TypeError("VolDown must be an Extron Button object")
        
        if type(Mute) in [Button, ExButton]:
            self.MuteBtn = VolUp
        else:
            raise TypeError("Mute must be an Extron Button object")
        
        if type(Feedback) in [Level, ExLevel]:
            self.FeedbackLvl = Feedback
        else:
            raise TypeError("Feedback must be an Extron Level object")
        
        if type(ControlLabel) in [Label, ExLabel] or ControlLabel is None:
            self.ControlLbl = ControlLabel
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

## End Class Definitions -------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------

## End Function Definitions ----------------------------------------------------



