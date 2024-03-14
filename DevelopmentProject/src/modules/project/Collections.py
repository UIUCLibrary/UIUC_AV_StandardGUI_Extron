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
from typing import (TYPE_CHECKING, Dict, Iterator, List, Union, TypeVar,
                    ValuesView, ItemsView, KeysView)
if TYPE_CHECKING: # pragma: no cover
    from modules.project.Classes import Source, Destination
    from modules.project.ExtendedDeviceClasses import ExProcessorDevice
    
    _KT = TypeVar('_KT')

#### Python imports
from collections import UserDict, UserList

#### Extron Library Imports
from extronlib.system import Timer

#### Project imports
from modules.helper.ModuleSupport import WatchVariable
from modules.project.SystemHardware import SystemHardwareController
from modules.helper.CommonUtilities import Logger
from modules.project.mixins import InitializeMixin
from modules.project.mixins.VirtualDevice import VirtualDeviceInterface
from modules.project.PrimitiveObjects import Alert
from control.PollController import PollObject
import Constants
import Variables
    
## End Imports -----------------------------------------------------------------
##
## Begin Class Definitions -----------------------------------------------------

class DeviceCollection(InitializeMixin, UserDict):
    # override __init__ to add properties to the device collection
    def __init__(self, __dict: None = None) -> Dict[str, SystemHardwareController]:
        UserDict.__init__(self, __dict)
        InitializeMixin.__init__(self, self.__Initialize)
        self.DevicesChanged = WatchVariable('Devices Changed Event')
        self.Polling = []
        self.PollingChanged = WatchVariable('Polling Changed Event')
        
        self.SystemHost = None
    
    def __repr__(self) -> str:
        sep = ', '
        return "<DeviceCollection [{}]>".format(sep.join([str(val) for val in self.values()]))
    
    # Type cast views for values, items, and keys
    def values(self) -> ValuesView['SystemHardwareController']:
        return super().values()
    
    def items(self) -> ItemsView[str, 'SystemHardwareController']:
        return super().items()
    
    def keys(self) -> KeysView[str]:
        return super().keys()
    
    # Overwrite __setitem__
    # TEST_THIS: test this for being able to set a value with a blank index, ie Devices[] = SystemHardwareControllerObject
    def __setitem__(self, key: '_KT', item: 'SystemHardwareController') -> None:
        if type(item) is not SystemHardwareController:
            raise ValueError('DeviceCollection items must be of type SystemHardwareController')
        
        if item.Id in list(self.data.keys()):
            raise ValueError("Duplicate key '{}' found".format(item.Id))
        
        # make sure the collection is properly set for devices as we add them
        if item.Collection is not self:
            item.Collection = self
        
        self.data[item.Id] = item
        
        self.DevicesChanged.Change(self.data)
    
    # Typecasts __getitem__
    def __getitem__(self, key: str) -> 'SystemHardwareController':
        return super().__getitem__(key)
    
    # Add list properties - these generate sublists based on the IsXXX attributes of SystemHardwareController
    @property
    def Destinations(self) -> List['SystemHardwareController']:
        return [item for item in self.values() if item.IsDest]
    
    @property
    def Sources(self) -> List['SystemHardwareController']:
        return [item for item in self.values() if item.IsSrc]
    
    @property
    def Switches(self) -> List['SystemHardwareController']:
        return [item for item in self.values() if item.IsSwitch]
    
    @property
    def Cameras(self) -> List['SystemHardwareController']:
        return [item for item in self.values() if item.IsCam]
    
    @property
    def Microphones(self) -> List['SystemHardwareController']:
        return [item for item in self.values() if item.IsMic]
    
    @property
    def Screens(self) -> List['SystemHardwareController']:
        return [item for item in self.values() if item.IsScn]
    
    @property
    def Lights(self) -> List['SystemHardwareController']:
        return [item for item in self.values() if item.IsLight]
    
    @property
    def Shades(self) -> List['SystemHardwareController']:
        return [item for item in self.values() if item.IsShade]
    
    @property
    def Uninitialized(self) -> List['SystemHardwareController']:
        return [item for item in self.values() if not item.Initialized]

    def __Initialize(self) -> None:
        for dev in self.Sources:
            dev.Initialize()
        
        for dev in self.Screens:
            dev.Initialize()
        
        for dev in self.Destinations:
            dev.Initialize()
            
        for dev in self.Switches:
            dev.Initialize()
            
        for dev in self.Cameras:
            dev.Initialize()
            
        for dev in self.Microphones:
            dev.Initialize()
            
        for dev in self.Lights:
            dev.Initialize()
            
        for dev in self.Shades:
            dev.Initialize()
            
        for dev in self.Uninitialized:
            dev.Initialize()
            
        # Associate Virtual Device Hardware after Hardware Initialization
        vDevList = [vDev for vDev in list(self.data.values()) if issubclass(type(getattr(vDev, 'interface', None)), VirtualDeviceInterface)]
        Logger.Debug('VDEV List', vDevList)
        for dev in vDevList:
            dev.interface.FindAssociatedHardware()

    # Special Add Item Methods
    def AddNewDevice(self, **kwargs) -> None:
        device = SystemHardwareController(self, **kwargs)
        self.__setitem__(None, device)
        if self.Initialized:
            device.Initialize()
        
    # Search Methods
    def GetDestination(self, id: str=None, name: str=None) -> 'Destination':
        if id is not None:
            if hasattr(self.data[id], 'Destination'):
                return self.data[id].Destination
            else:
                raise LookupError("No destination defined for provided id '{}'".format(id))
        elif name is not None:
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
        if id is not None:
            if hasattr(self.data[id], 'Source'):
                return self.data[id].Source
            else:
                raise LookupError("No source defined for provided id '{}'".format(id))
        elif name is not None:
            for src in self.Sources:
                if src.Name == name:
                    return src.Source
            raise LookupError("No source defined for provided name '{}'".format(id))
        else:
            raise ValueError('Either Id or Name must be provided')

    def GetSourceByInput(self, inputNum: int) -> 'Source':
        if inputNum == 0:
            return Constants.BLANK_SOURCE
        elif inputNum > 0:
            for src in self.Sources:
                if src.Source.Input == inputNum:
                    return src.Source
            raise LookupError("Provided inputNum '{}' is not configured to a destination".format(inputNum))
        else:
            raise ValueError('inputNum must be an integer greater than 0')
        
    # Polling
    def AddPolling(self, device, command, qualifier=None, active_duration: int=None, inactive_duration: int=None):
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
    def __init__(self, __dict: None = None) -> Dict[str, Constants.UI_OBJECTS]:
        super().__init__(__dict)
        
    def __repr__(self) -> str:
        sep = ', '
        return "<UIObject Collection [{}]>".format(sep.join([str(val) for val in self.values()]))
    
    # Type cast views for values, items, and keys
    def values(self) -> ValuesView[Constants.UI_OBJECTS]:
        return super().values()
    
    def items(self) -> ItemsView[str, Constants.UI_OBJECTS]:
        return super().items()
    
    def keys(self) -> KeysView[str]:
        return super().keys()
    
    # Typecasts __getitem__
    def __getitem__(self, key: Union[str, int]) -> Constants.UI_OBJECTS:
        if isinstance(key, str) and not key.isnumeric():
            return super().__getitem__(key)
        elif isinstance(key, int) or (isinstance(key, str) and key.isnumeric()):
            if isinstance(key, str):
                key = int(key)
                
            for val in self.values():
                if val.Id == key:
                    return val
        else:
            raise TypeError("__getitem__ key must be a string or int")

class ControlGroupCollection(UserDict):
    def __init__(self, _dict: None = None) -> Dict[str, Constants.UI_SETS]:
        return super().__init__(_dict)
    
    def __repr__(self) -> str:
        sep = ', '
        return "<ControlGroupCollection [{}]>".format(sep.join([str(val) for val in self.values()]))
    
    # Type cast views for values, items, keys, and getitem
    def values(self) -> ValuesView[Constants.UI_SETS]:
        return super().values()
    
    def items(self) -> ItemsView[str, Constants.UI_SETS]:
        return super().items()
    
    def keys(self) -> KeysView[str]:
        return super().keys()
    
    def __getitem__(self, key: str) -> Constants.UI_SETS:
        return super().__getitem__(key)
    
    def ShowPopups(self) -> None:
        for ctlGrp in self.data.values():
            if hasattr(ctlGrp, 'ShowPopup'):
                ctlGrp.ShowPopup()

class UIDeviceCollection(UserList):
    def __init__(self, __list: None = None) -> List[Constants.UI_HOSTS]:
        return super().__init__(__list)
        
    def __repr__(self) -> str:
        sep = ', '
        return "<UIDeviceCollection [{}]>".format(sep.join([str(val) for val in self]))
    
    # Type cast getitem & iter
    def __getitem__(self, index: int) -> Constants.UI_HOSTS:
        return super().__getitem__(index)
        
    def __iter__(self) -> Iterator[Constants.UI_HOSTS]:
        return super().__iter__()
    
class ProcessorCollection(UserList):
    def __init__(self, __list: None = None) -> List['ExProcessorDevice']:
        super().__init__(__list)
        
    def __repr__(self) -> str:
        sep = ', '
        return "<ProcessorCollection [{}]>".format(sep.join([str(val) for val in self]))
    
    # Type cast getitem & iter
    def __getitem__(self, index: int) -> 'ExProcessorDevice':
        return super().__getitem__(index)
        
    def __iter__(self) -> Iterator['ExProcessorDevice']:
        return super().__iter__()
    
    def GetProcessorById(self, Id=str) -> 'ExProcessorDevice':
        for proc in self:
            if proc.Id == Id:
                return proc

class AlertCollection(InitializeMixin, UserList):
    def __init__(self, __list: Union[List[Dict[str, any]], Dict[str, any]] = None) -> List['Alert']:
        InitializeMixin.__init__(self, self.__Initialize)
        self.SystemHost = None
        self.__Timer = Timer(5, self.__Handler)
        self.__Timer.Stop()
        if isinstance(__list, list):
            alert_list = []
            for list_item in __list:
                if not isinstance(list_item, dict):
                    raise AttributeError("Alert Collection can only be initialized for None, Alert KwArgs Dictionary, or List of Alert KwArgs Dict")
                alert_list.append(Alert(self, **list_item))
            UserList.__init__(self, alert_list)
        elif isinstance(__list, dict):
            UserList.__init__(self, [Alert(self, **__list)])
        elif __list is None:
            UserList.__init__(self, None)
        else:
            raise AttributeError("Alert Collection can only be initialized for None, Alert KwArgs Dictionary, or List of Alert KwArgs Dict")
    
    def __repr__(self) -> str:
        sep = ', '
        return "<AlertCollection [{}]>".format(sep.join([str(val) for val in self]))
    
    # Type cast getitem & iter
    def __getitem__(self, index: int) -> 'Alert':
        return UserList.__getitem__(self, index)
    
    def __iter__(self) -> Iterator['Alert']:
        return UserList.__iter__(self)
    
    def __Initialize(self) -> None:
        for alert in self:
            alert.Initialize()
            
        self.__Timer.Restart()
    
    def __Handler(self, timer: 'Timer', count: int) -> None:
        for alert in self:
            if Variables.TESTING:
                Logger.Debug('TESTING: Checking alert ({}) state'.format(alert.Name))
            else:
                alert.Check()

    def AddNewAlert(self, **kwargs) -> None:
        newAlert = Alert(self, **kwargs)
        self.data.append(newAlert)
        
        if self.Initialized:
            newAlert.Initialize()

    def GetAlertsByDevice(self, Device: Union[str, 'SystemHardwareController']) -> List['Alert']:
        rtnList = []
        
        if isinstance(Device, str):
            dev = Device
        elif isinstance(Device, SystemHardwareController):
            dev = Device.Id
        else:
            raise ValueError('Device must be a string Id or SystemHardwareController object')
        
        for alert in self:
            if alert.DeviceId == dev:
                rtnList.append(alert)
                
        return rtnList

## End Class Definitions -------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------

## End Function Definitions ----------------------------------------------------



