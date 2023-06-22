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

from typing import TYPE_CHECKING, Dict, Tuple, List, Union, Callable
if TYPE_CHECKING: # pragma: no cover
    from uofi_gui import GUIController
    from uofi_gui.uiObjects import ExUIDevice
    from modules.device.classes.destinations import Destination
    from modules.device.classes.sources import Source


## Begin ControlScript Import --------------------------------------------------

## End ControlScript Import ----------------------------------------------------
##
## Begin Python Imports --------------------------------------------------------

from collections import UserDict, ValuesView, ItemsView, KeysView, _KT

## End Python Imports ----------------------------------------------------------
##
## Begin User Import -----------------------------------------------------------
#### Custom Code Modules
from modules.helper.ModuleSupport import WatchVariable
from modules.helper.UtilityFunctions import DictValueSearchByKey, RunAsync, debug
from modules.project.systemHardware import SystemHardwareController
from variables import PROG, TRACE, BLANK_SOURCE



## End User Import -------------------------------------------------------------
##
## Begin Class Definitions -----------------------------------------------------

class DictObj:
    def __init__(self, src_dict: dict) -> None:
        if type(src_dict) is not dict:
            raise TypeError('DictObj src_dict must be of type dict')
        
        for key, val in src_dict.items():
            if isinstance(val, (list, tuple)):
               setattr(self, key, [DictObj(x) if isinstance(x, dict) else x for x in val])
            else:
               setattr(self, key, DictObj(val) if isinstance(val, dict) else val)

class DeviceCollection(UserDict):
    # override __init__ to add properties to the device collection
    def __init__(self, __dict: None = None) -> Dict[str, SystemHardwareController]:
        super().__init__(__dict)
        self.DevicesChanged = WatchVariable('Devices Changed Event')
        self.Polling = []
        self.PollingChanged = WatchVariable('Polling Changed Event')
        self.DefaultActiveDuration = 5
        self.DefaultInactiveDuration = 300
    
    # Type cast views for values, items, and keys
    def values(self) -> ValuesView['SystemHardwareController']:
        return super().values()
    
    def items(self) -> ItemsView[str, 'SystemHardwareController']:
        return super().items()
    
    def keys(self) -> KeysView[str]:
        return super().keys()
    
    # Overwrite __setitem__
    # TODO: test this for being able to set a value with a blank index, ie Devices[] = SystemHardwareControllerObject
    def __setitem__(self, key: _KT, item: 'SystemHardwareController') -> None:
        if type(item) is not SystemHardwareController:
            raise ValueError('DeviceCollection items must be of type SystemHardwareController')
        
        if item.Id in list(self.data.keys()):
            raise ValueError("Duplicate key '{}' found".format(item.Id))
        
        # make sure the collection is properly set for devices as we add them
        if item.Collection is not self:
            item.Collection = self
        
        self.data[item.Id] = item
        
        TRACE.Log('Devices Changed')
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
        if device not in self.data:
            raise LookupError('device must be in DeviceCollection')
        
        if active_duration is not None:
            act_dur = active_duration
        else:
            act_dur = self.DefaultActiveDur
            
        if inactive_duration is not None:
            inact_dur = inactive_duration
        else:
            inact_dur = self.DefaultInactiveDur
            
        self.Polling.append(DictObj({
            'Device': device,
            'Interface': device.interface,
            'Command': command,
            'Qualifier': qualifier,
            'ActiveDuration': act_dur,
            'InactiveDuration': inact_dur
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

## End Class Definitions -------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------

## End Function Definitions ----------------------------------------------------



