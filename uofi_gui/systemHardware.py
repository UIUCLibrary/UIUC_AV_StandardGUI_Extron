from typing import TYPE_CHECKING, Dict, Tuple, List, Union, Callable
if TYPE_CHECKING: # pragma: no cover
    from uofi_gui import GUIController
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

from ConnectionHandler import GetConnectionHandler
from utilityFunctions import Log, RunAsync, debug, DictValueSearchByKey, SortKeys

#### Extron Global Scripter Modules

## End User Import -------------------------------------------------------------
##
## Begin Class Definitions -----------------------------------------------------

class VirtualDeviceInterface:
    def __init__(self, VirtualDeviceID, AssignmentAttribute: str, AssignmentDict: Dict) -> None:
        self.VirtualDeviceID = VirtualDeviceID
        self.__AssignmentAttribute = AssignmentAttribute
        self.__AssignmentDict = AssignmentDict
    
    def FindAssociatedHardware(self):
        # iterate through self.GUIHost.Hardware and find devices with matching 'MatrixAssignment'
        for Hw in self.GUIHost.Hardware.values(): # GUIHost attribute must exist in parent class
            if hasattr(Hw, self.__AssignmentAttribute) and getattr(Hw, self.__AssignmentAttribute) == self.VirtualDeviceID:
                for key, value in self.__AssignmentDict.items():
                    if hasattr(Hw, key):
                        value[getattr(Hw, key)] = Hw

class SystemHardwareController:
    def __init__(self, GUIHost: 'GUIController', Id: str, Name: str, Manufacturer: str, Model: str, Interface: Dict, Subscriptions: Dict, Polling: Dict, Options: Dict=None) -> None:
        self.GUIHost = GUIHost
        self.Id = Id
        self.Name = Name
        self.Manufacturer = Manufacturer
        self.Model = Model
        self.ConnectionStatus = 'Not Connected'
        self.LastStatusChange = None
        
        if Options is not None:
            for key in Options:
                if not hasattr(self, key):
                    setattr(self, key, Options[key])
        
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
        
        self.__Module = importlib.import_module(Interface['module'])
        self.__Constructor = getattr(self.__Module,
                                     Interface['interface_class'])
        
        Interface['interface_configuration']['GUIHost'] = self.GUIHost
        if 'ConnectionHandler' in Interface and type(Interface['ConnectionHandler']) is dict:
            self.interface = GetConnectionHandler(self.__Constructor(**Interface['interface_configuration']),
                                                  **Interface['ConnectionHandler'])
            
            connInfo = self.interface.Connect()
        else:
            self.interface = self.__Constructor(**Interface['interface_configuration'])
        
        self.interface.SubscribeStatus('ConnectionStatus', None, self.__ConnectionStatus)

        # subscriptions = [
        #     {
        #         'command': subscription command,
        #         'qualifier': qualifier,
        #         'callback': callback function
        #     },
        #     ...
        # ]
        
        for sub in Subscriptions:
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
        
        for poll in Polling:
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
                self.GUIHost.PollCtl.AddPolling(self.interface,
                                                poll['command'],
                                                qualifier=qp,
                                                active_duration=actInt,
                                                inactive_duration=inactInt)
                
                # To prevent the need to duplicate polling and subscriptions in settings
                # if a callback is included in the poll, a subscription will automatically
                # be created on the interface
                if 'callback' in poll:
                    self.AddSubscription(poll, qp)
                    
    # Event Handlers +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    # Private Methods ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    def __ConnectionStatus(self, command, value, qualifier):
        Log('{} {} Callback; Value: {}; Qualifier {}'.format(self.Name, command, value, qualifier))
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
    
class SystemPollingController:
    def __init__(self, active_duration: int=5, inactive_duration: int=300) -> None:
        self.Polling = []
        
        self.__PollingState = 'stopped'
        
        self.__DefaultActiveDur = active_duration
        self.__DefaultInactiveDur = inactive_duration
        
        self.__InactivePolling = Timer(1, self.__InactivePollingHandler)
        self.__InactivePolling.Stop()
        self.__ActivePolling = Timer(1, self.__ActivePollingHandler)
        self.__ActivePolling.Stop()
    
    # Event Handlers +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    def __ActivePollingHandler(self, timer: 'Timer', count: int):
        for poll in self.Polling:
            if (count % poll['active_duration']) == 0:
                self.__PollInterface(poll['interface'], poll['command'], poll['qualifier'])
    
    def __InactivePollingHandler(self, timer: 'Timer', count: int):
        for poll in self.Polling:
            if (count % poll['inactive_duration']) == 0:
                self.__PollInterface(poll['interface'], poll['command'], poll['qualifier'])
    
    # Private Methods ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    def __PollInterface(self, interface, command, qualifier=None): # pragma: no cover
        try:
            interface.Update(command, qualifier=qualifier)
        except Exception as inst:
            Log('An error occured attempting to poll. {} ({})\n    Exception ({}):\n        {}'.format(command, qualifier, type(inst), inst), 'error')
    
    # Public Methods +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    def PollEverything(self):
        for poll in self.Polling:
            self.__PollInterface(poll['interface'], poll['command'], poll['qualifier'])
            
    def StartPolling(self, mode: str='inactive'):
        if mode == 'inactive': 
            self.__InactivePolling.Restart()
            self.__ActivePolling.Stop()
            self.__PollingState = 'inactive'
        elif mode == 'active':
            self.__ActivePolling.Restart()
            self.__InactivePolling.Stop()
            self.__PollingState = 'active'
        else:
            raise ValueError("Mode must be 'inactive' or 'active'")
            
    def StopPolling(self):
        self.__InactivePolling.Stop()
        self.__ActivePolling.Stop()
        self.__PollingState = 'stopped'
        
    def TogglePollingMode(self):
        if self.__PollingState == 'inactive':
            self.__InactivePolling.Stop()
            self.__ActivePolling.Restart()
            self.__PollingState = 'active'
        elif self.__PollingState == 'active':
            self.__ActivePolling.Stop()
            self.__InactivePolling.Restart()
            self.__PollingState = 'inactive'
            
    def SetPollingMode(self, mode: str):
        if mode == 'inactive':
            if self.__ActivePolling.State == 'Running':
                self.__InactivePolling.Restart()
            self.__ActivePolling.Stop()
            self.__PollingState = 'inactive'
        elif mode == 'active':
            if self.__InactivePolling.State == 'Running':
                self.__ActivePolling.Restart()
            self.__InactivePolling.Stop()
            self.__PollingState = 'active'
        else:
            raise ValueError("Mode must be 'inactive' or 'active'")
    
    def AddPolling(self, interface, command, qualifier=None, active_duration: int=None, inactive_duration: int=None):
        if active_duration is not None:
            act_dur = active_duration
        else:
            act_dur = self.__DefaultActiveDur
            
        if inactive_duration is not None:
            inact_dur = inactive_duration
        else:
            inact_dur = self.__DefaultInactiveDur
            
        self.Polling.append({
            'interface': interface,
            'command': command,
            'qualifier': qualifier,
            'active_duration': act_dur,
            'inactive_duration': inact_dur
        })
        
    def RemovePolling(self, interface, command):
        for i in range(len(self.Polling)):
            if interface is self.Polling[i]['interface'] and command == self.Polling[i]['command']:
                self.Polling.pop(i)
                break
            
    def UpdatePolling(self, interface, command, qualifier={}, active_duration: int=None, inactive_duration: int=None):
        for i in range(len(self.Polling)):
            if interface is self.Polling[i]['interface'] and command == self.Polling[i]['command']:
                if active_duration is not None and self.Polling[i]['active_duration'] != active_duration:
                    self.Polling[i]['active_duration'] = active_duration
                    
                if inactive_duration is not None and self.Polling[i]['inactive_duration'] != inactive_duration:
                    self.Polling[i]['inactive_duration'] = inactive_duration
                
                if self.Polling[i]['qualifier'] != qualifier and qualifier != {}:
                    self.Polling[i]['qualifier'] =  qualifier
                
                break
    
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
    
    def __GetStatusState(self, hw) -> int:
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


