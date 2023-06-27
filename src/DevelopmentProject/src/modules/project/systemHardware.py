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
    from modules.project.Collections import DeviceCollection
    from uofi_gui.uiObjects import ExUIDevice
    from extronlib.ui import Button, Knob, Label, Level, Slider

## Begin ControlScript Import --------------------------------------------------
from extronlib import event, Version
from extronlib.device import eBUSDevice, ProcessorDevice, UIDevice
from extronlib.interface import (CircuitBreakerInterface, ContactInterface,
    DigitalInputInterface, DigitalIOInterface, EthernetClientInterface,
    EthernetServerInterfaceEx, FlexIOInterface, IRInterface, PoEInterface,
    RelayInterface, SerialInterface, SWACReceptacleInterface, SWPowerInterface,
    VolumeInterface)

from extronlib.system import (Email, Clock, MESet, Timer, Wait, File, RFile,
    ProgramLog, SaveProgramLog, Ping, WakeOnLan, SetAutomaticTime, SetTimeZone)

## End ControlScript Import ----------------------------------------------------
##
## Begin Python Imports --------------------------------------------------------
from datetime import datetime
import importlib
import math
import re
import functools

## End Python Imports ----------------------------------------------------------
##
## Begin User Import -----------------------------------------------------------
#### Custom Code Modules

from modules.helper.ConnectionHandler import GetConnectionHandler
from modules.helper.CommonUtilities import Logger, RunAsync, debug, DictValueSearchByKey, SortKeys

#### Extron Global Scripter Modules

## End User Import -------------------------------------------------------------
##
## Begin Class Definitions -----------------------------------------------------

class SystemHardwareController:
    def __init__(self, DeviceCollection: 'DeviceCollection', Id: str, Name: str, Manufacturer: str, Model: str, Interface: Dict, Subscriptions: Dict, Polling: Dict, Options: Dict=None) -> None:
        self.Collection = DeviceCollection
        self.Id = Id
        self.Name = Name
        self.Manufacturer = Manufacturer
        self.Model = Model
        self.ConnectionStatus = 'Not Connected'
        self.LastStatusChange = None
        
        self.__Subscriptions = Subscriptions
        self.__Polling = Polling
        
        if Options is not None:
            for key in Options:
                if not hasattr(self, key):
                    setattr(self, key, Options[key])
        
        if Interface is not None:
            # interface = {
            #     "module": module_name,
            #     "interface_class": interface_class,
            #     "ConnectionHandler": {
            #         Connection handler configuration items
            #     }
            #     "interface_configuration": {
            #         interface configuration items
            #     }
            # }
            
            self.__Module = importlib.import_module('modules.device.{}'.format(Interface['module']))
            self.__Constructor = getattr(self.__Module,
                                        Interface['interface_class'])
            
            Interface['interface_configuration']['GUIHost'] = self.Collection
            if 'ConnectionHandler' in Interface and type(Interface['ConnectionHandler']) is dict:
                self.interface = GetConnectionHandler(self.__Constructor(**Interface['interface_configuration']),
                                                    **Interface['ConnectionHandler'])
                
                connInfo = self.interface.Connect()
            else:
                self.interface = self.__Constructor(**Interface['interface_configuration'])
            
            self.interface.SubscribeStatus('ConnectionStatus', None, self.__ConnectionStatus)
    
    def __repr__(self) -> str:
        return 'Device: {} ({}|{})'.format(self.Name, self.Id, self.ConnectionStatus)
    
    def InitializeDevice(self):
        # subscriptions = [
        #     {
        #         'command': subscription command,
        #         'qualifier': qualifier,
        #         'callback': callback function
        #     },
        #     ...
        # ]
        
        if self.__Subscriptions is not None:
            for sub in self.__Subscriptions:
                qualSub = self.GetQualifierList(sub)
                
                for qp in qualSub:
                    # these subscriptions do not poll for updated statuses and appropriate
                    # Update or Set commands must be sent elsewhere in the program
                    # Use these subscriptions to verify changes or to handle control feedback
                    self.AddSubscription(sub, qp)
        
        # polling = [
        #  {
        #     'command': polling command,
        #     'qualifier': command qualifier, Optional
        #     'callback': polling update command, Optional
        #     'active_int': active polling interval, Optional
        #     'inactive_int': inactive polling interval, Optional
        #  },
        #  ...
        # ]
        
        if self.__Polling is not None:
            for poll in self.__Polling:
                qualPoll = self.GetQualifierList(poll)
                
                if 'active_int' in poll:
                    actInt = poll['active_int']
                else:
                    actInt = None
                if 'inactive_int' in poll:
                    inactInt = poll['inactive_int']
                else:
                    inactInt = None
                
                for qp in qualPoll:
                    self.Collection.AddPolling(self,
                                                poll['command'],
                                                qualifier=qp,
                                                active_duration=actInt,
                                                inactive_duration=inactInt
                                                )
                    
                    # To prevent the need to duplicate polling and subscriptions in settings
                    # if a callback is included in the poll, a subscription will automatically
                    # be created on the interface
                    if 'callback' in poll:
                        self.AddSubscription(poll, qp)
                        
        if hasattr(self, 'Destination'):
            # configure destination
            pass
        elif hasattr(self, 'Source'):
            # configure source
            pass
        elif hasattr(self, 'Switch'):
            # configure switch
            pass
        elif hasattr(self, 'Camera'):
            # configure camera
            pass
        elif hasattr(self, 'Microphone'):
            # configure microphone
            pass
        elif hasattr(self, 'Screen'):
            # configure microphone
            pass
        elif hasattr(self, 'Light'):
            # configure light
            pass
        elif hasattr(self, 'Shade'):
            # configure Shade
            pass
    
    # Collection attributes
    @property
    def IsDest(self) -> bool:
        return hasattr(self, 'Destination')
    
    @IsDest.setter
    def IsDest(self, value) -> None:
        raise AttributeError('IsDest property cannot be set, only read')
    
    @property
    def IsSrc(self) -> bool:
        return hasattr(self, 'Source')
    
    @IsSrc.setter
    def IsSrc(self, value) -> None:
        raise AttributeError('IsSrc property cannot be set, only read')
    
    @property
    def IsSwitch(self) -> bool:
        return hasattr(self, 'Switch')
    
    @IsSwitch.setter
    def IsSwitch(self, value) -> None:
        raise AttributeError('IsSwitch property cannot be set, only read')
    
    @property
    def IsCam(self) -> bool:
        return hasattr(self, 'Camera')
    
    @IsCam.setter
    def IsCam(self, value) -> None:
        raise AttributeError('IsCam property cannot be set, only read')
    
    @property
    def IsMic(self) -> bool:
        return hasattr(self, 'Microphone')
    
    @IsMic.setter
    def IsMic(self, value) -> None:
        raise AttributeError('IsMic property cannot be set, only read')
    
    @property
    def IsScn(self) -> bool:
        return hasattr(self, 'Screen')
    
    @IsScn.setter
    def IsScn(self, value) -> None:
        raise AttributeError('IsScn property cannot be set, only read')
    
    @property
    def IsLight(self) -> bool:
        return hasattr(self, 'Light')
    
    @IsLight.setter
    def IsLight(self, value) -> None:
        raise AttributeError('IsLight property cannot be set, only read')
    
    @property
    def IsShade(self) -> bool:
        return hasattr(self, 'Shade')
    
    @IsShade.setter
    def IsShade(self, value) -> None:
        raise AttributeError('IsShade property cannot be set, only read')
    
    # Event Handlers +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    # Private Methods ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    def __ConnectionStatus(self, command, value, qualifier):
        Logger.Log('{} {} Callback; Value: {}; Qualifier {}'.format(self.Name, command, value, qualifier))
        if value != self.ConnectionStatus:
            self.ConnectionStatus = value
            self.LastStatusChange = datetime.now()
    
    # Public Methods +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    def GetQualifierList(self, subscription):
        qualList = [None]
        if 'qualifier' in subscription and subscription['qualifier'] is not None:
            if type(subscription['qualifier']) is list:
                for q in subscription['qualifier']:
                    if type(q) is not dict:
                        raise TypeError('Qualifier ({}) must be a dictionary'.format(q))
                qualList = subscription['qualifier']
            elif type(subscription['qualifier']) is dict:
                qualList = [subscription['qualifier']]
            else:
                raise TypeError('Qualifier must be a dictionary')
        return qualList

    def AddSubscription(self, subscription, qualifier):
        if callable(subscription['callback']):
            if 'tag' in subscription:
                callbackFn = functools.partial(subscription['callback'], hardware=self, tag=subscription['tag'])
            else:
                callbackFn = functools.partial(subscription['callback'], hardware=self)
        elif type(subscription['callback']) is str and hasattr(self.interface, subscription['callback']):
            if 'tag' in subscription:
                callbackFn = functools.partial(getattr(self.interface, subscription['callback']), hardware=self, tag=subscription['tag'])
            else:
                callbackFn = functools.partial(getattr(self.interface, subscription['callback']), hardware=self)
        else:
            raise TypeError('Callback must either be a callable or a string matching a name of an interface method.')
                
        self.interface.SubscribeStatus(subscription['command'],
                                       qualifier,
                                       callbackFn)
    

class SystemStatusController:
    def __init__(self, UIHost: 'ExUIDevice') -> None:

        self.UIHost = UIHost
        self.GUIHost = self.UIHost.GUIHost
        self.Hardware = list(self.GUIHost.Hardware.values())
        self.Hardware.sort(key=SortKeys.HardwareSort)
        
        self.__StatusIcons = DictValueSearchByKey(self.UIHost.Btns, r'DeviceStatusIcon-\d+', regex=True)
        self.__StatusIcons.sort(key=SortKeys.StatusSort)
        self.__StatusLabels = DictValueSearchByKey(self.UIHost.Lbls, r'DeviceStatusLabel-\d+', regex=True)
        self.__StatusLabels.sort(key=SortKeys.StatusSort)
        self.__Arrows = \
            {
                'prev': self.UIHost.Btns['DeviceStatus-PageDown'],
                'next': self.UIHost.Btns['DeviceStatus-PageUp']
            }
        self.__PageLabels = \
            {
                'current': self.UIHost.Lbls['DeviceStatusPage-Current'],
                'total': self.UIHost.Lbls['DeviceStatusPage-Total'],
                'div': self.UIHost.Lbls['PaginationSlash']
            }
        
        self.__CurrentPageIndex = 0
        
        self.UpdateTimer = Timer(15, self.__UpdateHandler)
        self.UpdateTimer.Stop()
        
        self.__ClearStatusIcons()
            
        self.__UpdatePagination()
        
        @event(list(self.__Arrows.values()), ['Pressed','Released']) # pragma: no cover
        def paginationHandler(button: 'Button', action: str):
            self.__PaginationHandler(button, action)
    
    @property
    def __HardwareCount(self) -> int:
        return len(self.Hardware)
    
    @property
    def __DisplayPages(self) -> int:
        return math.ceil(self.__HardwareCount / 15)
    
    # Event Handlers +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    def __PaginationHandler(self, button: 'Button', action: str):
        if action == 'Pressed':
            button.SetState(1)
        elif action == 'Released':
            button.SetState(0)
            if button.Name.endswith('Up'):
                # do page up
                self.__CurrentPageIndex += 1
                if self.__CurrentPageIndex >= self.__DisplayPages:
                    self.__CurrentPageIndex = self.__DisplayPages
            elif button.Name.endswith('Down'):
                # do page down
                self.__CurrentPageIndex -= 1
                if self.__CurrentPageIndex < 0:
                    self.__CurrentPageIndex = 0
                
            self.__UpdatePagination()
            self.__ShowStatusIcons()
            
    def __UpdateHandler(self, timer: 'Timer', count: int):
        self.UpdateStatusIcons()

    # Private Methods ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    def __ClearStatusIcons(self):
        for ico in self.__StatusIcons:
            ico.SetEnable(False)
            ico.SetVisible(False)
            ico.HW = None
            
        for lbl in self.__StatusLabels:
            lbl.SetText('')
    
    def __ShowStatusIcons(self):
        self.__ClearStatusIcons()
        
        indexStart = self.__CurrentPageIndex * 15
        indexEnd = ((self.__CurrentPageIndex + 1) * 15)

        displayList = []
        for i in range(indexStart, indexEnd):
            if i >= len(self.Hardware):
                break
            displayList.append(self.Hardware[i])
        
        if len(displayList) < len(self.__StatusIcons):
            loadRange = len(displayList)
        else:
            loadRange = 15
        
        for j in range(loadRange):
            ico = self.__StatusIcons[j]
            lbl = self.__StatusLabels[j]
            hw = displayList[j]
            
            ico.SetState(self.__GetStatusState(hw))
            ico.SetVisible(True)
            ico.HW = hw
            lbl.SetText(hw.Name)
    
    def __GetStatusState(self, hw) -> int: # pragma: no cover
        if hw.ConnectionStatus == 'Connected':
            return 2
        else:
            if type(hw.LastStatusChange) != datetime:
                return 3
            else:
                delta = datetime.now() - hw.LastStatusChange
                secs = delta.total_seconds()
                if secs < 180:
                    return 2
                elif secs >= 180 and secs < 300:
                    return 1
                elif secs >= 300:
                    return 0
                    
    def __UpdatePagination(self):
        if self.__DisplayPages == 1:
            # No page flips. Show no pagination
            self.__Arrows['prev'].SetEnable(False)
            self.__Arrows['prev'].SetVisible(False)
            self.__Arrows['next'].SetEnable(False)
            self.__Arrows['next'].SetVisible(False)
            
            self.__PageLabels['current'].SetVisible(False)
            self.__PageLabels['total'].SetVisible(False)
            self.__PageLabels['div'].SetVisible(False)
            
        elif self.__DisplayPages > 1 and self.__CurrentPageIndex == 0:
            # Show page flips, disable prev button
            self.__Arrows['prev'].SetEnable(False)
            self.__Arrows['prev'].SetVisible(True)
            self.__Arrows['next'].SetEnable(True)
            self.__Arrows['next'].SetVisible(True)
            
            self.__Arrows['prev'].SetState(2)
            self.__Arrows['next'].SetState(0)

            self.__PageLabels['current'].SetVisible(True)
            self.__PageLabels['current'].SetText(str(self.__CurrentPageIndex + 1))
            self.__PageLabels['total'].SetVisible(True)
            self.__PageLabels['total'].SetText(str(self.__DisplayPages))
            self.__PageLabels['div'].SetVisible(True)
            
        elif self.__DisplayPages > 1 and (self.__CurrentPageIndex + 1) == self.__DisplayPages:
            # Show page flips, disable next button
            self.__Arrows['prev'].SetEnable(True)
            self.__Arrows['prev'].SetVisible(True)
            self.__Arrows['next'].SetEnable(False)
            self.__Arrows['next'].SetVisible(True)
            
            self.__Arrows['prev'].SetState(0)
            self.__Arrows['next'].SetState(2)
        
            self.__PageLabels['current'].SetVisible(True)
            self.__PageLabels['current'].SetText(str(self.__CurrentPageIndex + 1))
            self.__PageLabels['total'].SetVisible(True)
            self.__PageLabels['total'].SetText(str(self.__DisplayPages))
            self.__PageLabels['div'].SetVisible(True)
        
        elif self.__DisplayPages > 1:
            # Show page flips, both arrows enabled
            self.__Arrows['prev'].SetEnable(True)
            self.__Arrows['prev'].SetVisible(True)
            self.__Arrows['next'].SetEnable(True)
            self.__Arrows['next'].SetVisible(True)
            
            self.__Arrows['prev'].SetState(0)
            self.__Arrows['next'].SetState(0)
            
            self.__PageLabels['current'].SetVisible(True)
            self.__PageLabels['current'].SetText(str(self.__CurrentPageIndex + 1))
            self.__PageLabels['total'].SetVisible(True)
            self.__PageLabels['total'].SetText(str(self.__DisplayPages))
            self.__PageLabels['div'].SetVisible(True)
    
    # Public Methods +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    def ResetPages(self):
        self.__CurrentPageIndex = 0
        self.__UpdatePagination()
        self.__ShowStatusIcons()
        
    def UpdateStatusIcons(self):
        for ico in self.__StatusIcons:
            if ico.HW is not None:
                ico.SetState(self.__GetStatusState(ico.HW))

    

## End Class Definitions -------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------

## End Function Definitions ----------------------------------------------------


