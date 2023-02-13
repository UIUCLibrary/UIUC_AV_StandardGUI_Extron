## Begin ControlScript Import --------------------------------------------------
from extronlib import event, Version
from extronlib.device import eBUSDevice, ProcessorDevice, UIDevice
from extronlib.interface import (CircuitBreakerInterface, ContactInterface,
    DigitalInputInterface, DigitalIOInterface, EthernetClientInterface,
    EthernetServerInterfaceEx, FlexIOInterface, IRInterface, PoEInterface,
    RelayInterface, SerialInterface, SWACReceptacleInterface, SWPowerInterface,
    VolumeInterface)
from extronlib.ui import Button, Knob, Label, Level, Slider
from extronlib.system import (Email, Clock, MESet, Timer, Wait, File, RFile,
    ProgramLog, SaveProgramLog, Ping, WakeOnLan, SetAutomaticTime, SetTimeZone)

print(Version()) ## Sanity check ControlScript Import

from ConnectionHandler import GetConnectionHandler

## End ControlScript Import ----------------------------------------------------
##
## Begin Python Imports --------------------------------------------------------
from datetime import datetime
import json
from typing import Dict, Tuple, List, Callable
import importlib
import math
import re
import functools

## End Python Imports ----------------------------------------------------------
##
## Begin User Import -----------------------------------------------------------
#### Custom Code Modules
import utilityFunctions
import settings
import vars

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
        # iterate through vars.Hardware and find devices with matching 'MatrixAssignment'
        for Hw in vars.Hardware.values():
            if hasattr(Hw, self.__AssignmentAttribute) and getattr(Hw, self.__AssignmentAttribute) == self.VirtualDeviceID:
                for key, value in self.__AssignmentDict.items():
                    if hasattr(Hw, key):
                        value[getattr(Hw, key)] = Hw

class SystemHardwareController:
    def __init__(self, Id: str, Name: str, Manufacturer: str, Model: str, Interface: Dict, Subscriptions: Dict, Polling: Dict, Options: Dict=None) -> None:
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
        
        self.__module = importlib.import_module(Interface['module'])
        self.__constructor = getattr(self.__module,
                                     Interface['interface_class'])
        
        
        if 'ConnectionHandler' in Interface and type(Interface['ConnectionHandler']) is dict:
            self.interface = GetConnectionHandler(self.__constructor(**Interface['interface_configuration']),
                                                  **Interface['ConnectionHandler'])
            
            connInfo = self.interface.Connect()
        else:
            self.interface = self.__constructor(**Interface['interface_configuration'])
        
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
            qualSub = [None]
            if 'qualifier' in sub and sub['qualifier'] is not None:
                if type(sub['qualifier']) is list:
                    for q in sub['qualifier']:
                        if type(q) is not dict:
                            raise TypeError('Qualifier ({}) must be a dictionary'.format(q))
                    qualSub = sub['qualifier']
                elif type(sub['qualifier']) is dict:
                    qualSub = [sub['qualifier']]
                else:
                    raise TypeError('Qualifier must be a dictionary')
            
            for qp in qualSub:
                # these subscriptions do not poll for updated statuses and appropriate
                # Update or Set commands must be sent elsewhere in the program
                # Use these subscriptions to verify changes or to handle control feedback
                if callable(sub['callback']):
                    callbackFn = functools.partial(sub['callback'], hardware=self)
                elif type(sub['callback']) is str and hasattr(self.interface, sub['callback']):
                    callbackFn = functools.partial(getattr(self.interface, sub['callback']), hardware=self)
                else:
                    raise TypeError('Callback must either be a callable or a string matching a name of an interface method.')
                
                self.interface.SubscribeStatus(sub['command'],
                                               qp,
                                               callbackFn)
        
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
            qualPoll = [None]
            if 'qualifier' in poll and poll['qualifier'] is not None:
                if type(poll['qualifier']) is list:
                    for q in poll['qualifier']:
                        if type(q) is not dict:
                            raise TypeError('Qualifier ({}) must be a dictionary'.format(q))
                    qualPoll = poll['qualifier']
                elif type(poll['qualifier']) is dict:
                    qualPoll = [poll['qualifier']]
                else:
                    raise TypeError('Qualifier ({}) must be a dictionary'.format(poll['qualifier']))
            
            if 'active_int' in poll:
                actInt = poll['active_int']
            else:
                actInt = None
            if 'inactive_int' in poll:
                inactInt = poll['inactive_int']
            else:
                inactInt = None
            
            for qp in qualPoll:
                vars.PollCtl.AddPolling(self.interface,
                                        poll['command'],
                                        qualifier=qp,
                                        active_duration=actInt,
                                        inactive_duration=inactInt)
                
                # To prevent the need to duplicate polling and subscriptions in settings
                # if a callback is included in the poll, a subscription will automatically
                # be created on the interface
                if 'callback' in poll:
                    if callable(poll['callback']):
                        callbackFn = functools.partial(poll['callback'], hardware=self)
                    elif type(poll['callback']) is str and hasattr(self.interface, poll['callback']):
                        callbackFn = functools.partial(getattr(self.interface, poll['callback']), hardware=self)
                    else:
                        raise TypeError('Callback must either be a callable or a string matching a name of an interface method.')
                    
                    self.interface.SubscribeStatus(poll['command'],
                                                   qp,
                                                   callbackFn)
            
            
    def __ConnectionStatus(self, command, value, qualifier):
        # utilityFunctions.Log('Connection Status Callback ({}): Command: {}; Value: {}, Qualifier: {}'.format(self.Id, command, value, qualifier))
        utilityFunctions.Log('{} {} Callback; Value: {}; Qualifier {}'.format(self.Name, command, value, qualifier))
        if value != self.ConnectionStatus:
            self.ConnectionStatus = value
            self.LastStatusChange = datetime.now()
            
    
class SystemPollingController:
    def __init__(self, active_duration: int=5, inactive_duration: int=300) -> None:
        self.polling = []
        
        self.__polling_state = 'stopped'
        
        self.__default_active_dur = active_duration
        self.__default_inactive_dur = inactive_duration
        
        self.__inactive_polling = Timer(1, self.__InactivePollingHandler)
        self.__inactive_polling.Stop()
        self.__active_polling = Timer(1, self.__ActivePollingHandler)
        self.__active_polling.Stop()
        
    def __ActivePollingHandler(self, timer, count):
        for poll in self.polling:
            if (count % poll['active_duration']) == 0:
                self.__PollInterface(poll['interface'], poll['command'], poll['qualifier'])
    
    def __InactivePollingHandler(self, timer, count):
        for poll in self.polling:
            if (count % poll['inactive_duration']) == 0:
                self.__PollInterface(poll['interface'], poll['command'], poll['qualifier'])
                    
    def PollEverything(self):
        for poll in self.polling:
            self.__PollInterface(poll['interface'], poll['command'], poll['qualifier'])
            
    def __PollInterface(self, interface, command, qualifier=None):
        try:
            interface.Update(command, qualifier=qualifier)
        except:
            utilityFunctions.Log('An error occured attempting to poll. {} ({})'.format(command, qualifier), 'error')
    
    def StartPolling(self, mode: str='inactive'):
        if mode == 'inactive': 
            self.__inactive_polling.Restart()
            self.__active_polling.Stop()
            self.__polling_state = 'inactive'
        elif mode == 'active':
            self.__active_polling.Restart()
            self.__inactive_polling.Stop()
            self.__polling_state = 'active'
            
    def StopPolling(self):
        self.__inactive_polling.Stop()
        self.__active_polling.Stop()
        self.__polling_state = 'stopped'
        
    def TogglePollingMode(self):
        if self.__polling_state == 'inactive':
            self.__inactive_polling.Stop()
            self.__active_polling.Restart()
            self.__polling_state = 'active'
        elif self.__polling_state == 'active':
            self.__active_polling.Stop()
            self.__inactive_polling.Restart()
            self.__polling_state = 'inactive'
            
    def SetPollingMode(self, mode: str):
        if mode == 'inactive':
            if self.__active_polling.State == 'Running':
                self.__inactive_polling.Restart()
            self.__active_polling.Stop()
            self.__polling_state = 'inactive'
        elif mode == 'active':
            if self.__inactive_polling.State == 'Running':
                self.__active_polling.Restart()
            self.__inactive_polling.Stop()
            self.__polling_state = 'active'
        else:
            raise ValueError("Mode must be 'inactive' or 'active'")
    
    def AddPolling(self, interface, command, qualifier=None, active_duration: int=None, inactive_duration: int=None):
        if active_duration is not None:
            act_dur = active_duration
        else:
            act_dur = self.__default_active_dur
            
        if inactive_duration is not None:
            inact_dur = inactive_duration
        else:
            inact_dur = self.__default_inactive_dur
            
        self.polling.append({
            'interface': interface,
            'command': command,
            'qualifier': qualifier,
            'active_duration': act_dur,
            'inactive_duration': inact_dur
        })
        
    def RemovePolling(self, interface, command):
        for i in range(len(self.polling)):
            if interface is self.polling[i]['interface'] and command == self.polling[i]['command']:
                self.polling.pop(i)
                break
            
    def UpdatePolling(self, interface, command, active_duration: int=None, inactive_duration: int=None):
        for i in range(len(self.polling)):
            if interface is self.polling[i]['interface'] and command == self.polling[i]['command']:
                if active_duration is not None:
                    self.polling[i]['active_duration'] = active_duration
                if inactive_duration is not None:
                    self.polling[i]['inactive_duration'] = inactive_duration
                break
    
class SystemStatusController:
    def __init__(self, HardwareDict, StatusDict) -> None:
        self.Hardware = list(HardwareDict.values())
        self.Hardware.sort(key=self.__hardware_sort)
        
        self.__status_icons = StatusDict['icons']
        self.__status_icons.sort(key=self.__status_sort)
        self.__status_labels = StatusDict['labels']
        self.__status_labels.sort(key=self.__status_sort)
        self.__arrows = StatusDict['arrows']
        self.__page_lables = StatusDict['pages']
        
        self.__hardware_count = len(self.Hardware)
        self.__display_pages = math.ceil(self.__hardware_count / 15)
        self.__current_page_index = 0
        
        self.UpdateTimer = Timer(15, self.__update_handler)
        self.UpdateTimer.Stop()
        
        self.__clear_status_icos()
            
        self.__update_pagination()
        
        @event(list(self.__arrows.values()), ['Pressed','Released'])
        def paginationHandler(button, action):
            if action == 'Pressed':
                button.SetState(1)
            elif action == 'Released':
                button.SetState(0)
                if button.Name.endswith('Up'):
                    # do page up
                    self.__current_page_index += 1
                elif button.Name.endswith('Down'):
                    # do page down
                    self.__current_page_index -= 1
                    
                self.__update_pagination()
                self.__show_status_icos()
                
    def resetPages(self):
        self.__current_page_index = 0
        self.__update_pagination()
        self.__show_status_icos()
        
    def update_status_icos(self):
        for ico in self.__status_icons:
            if ico.HW is not None:
                ico.SetState(self.__get_status_state(ico.HW))

    def __status_sort(self, e):
        res = re.match(r'DeviceStatus(?:Icon|Label)-(\d+)', e.Name)
        sortInt = int(res.group(1))
        return sortInt
    
    def __hardware_sort(self, e):
        return e.Id
    
    def __update_handler(self, timer, count):
        self.update_status_icos()
        
    def __clear_status_icos(self):
        for ico in self.__status_icons:
            ico.SetEnable(False)
            ico.SetVisible(False)
            ico.HW = None
            
        for lbl in self.__status_labels:
            lbl.SetText('')
    
    def __show_status_icos(self):
        self.__clear_status_icos()
        
        indexStart = self.__current_page_index * 15
        indexEnd = ((self.__current_page_index + 1) * 15)

        displayList = []
        for i in range(indexStart, indexEnd):
            if i == len(self.Hardware):
                break
            displayList.append(self.Hardware[i])
        
        if len(displayList) < len(self.__status_icons):
            loadRange = len(displayList)
        else:
            loadRange = 15
        
        for j in range(loadRange):
            ico = self.__status_icons[j]
            lbl = self.__status_labels[j]
            hw = displayList[j]
            
            ico.SetState(self.__get_status_state(hw))
            ico.SetVisible(True)
            ico.HW = hw
            lbl.SetText(hw.Name)
    
    def __get_status_state(self, hw) -> int:
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
                    
    def __update_pagination(self):
        if self.__display_pages == 1:
            # No page flips. Show no pagination
            self.__arrows['prev'].SetEnable(False)
            self.__arrows['prev'].SetVisible(False)
            self.__arrows['next'].SetEnable(False)
            self.__arrows['next'].SetVisible(False)
            
            self.__page_lables['current'].SetVisible(False)
            self.__page_lables['total'].SetVisible(False)
            self.__page_lables['div'].SetVisible(False)
            
        elif self.__current_page_index == 0:
            # Show page flips, disable prev button
            self.__arrows['prev'].SetEnable(False)
            self.__arrows['prev'].SetVisible(True)
            self.__arrows['next'].SetEnable(True)
            self.__arrows['next'].SetVisible(True)
            
            self.__arrows['prev'].SetState(2)
            self.__arrows['next'].SetState(0)

            self.__page_lables['current'].SetVisible(True)
            self.__page_lables['current'].SetText(str(self.__current_page_index + 1))
            self.__page_lables['total'].SetVisible(True)
            self.__page_lables['total'].SetText(str(self.__display_pages))
            self.__page_lables['div'].SetVisible(True)
            
        elif (self.__current_page_index + 1) == self.__display_pages:
            # Show page flips, disable next button
            self.__arrows['prev'].SetEnable(True)
            self.__arrows['prev'].SetVisible(True)
            self.__arrows['next'].SetEnable(False)
            self.__arrows['next'].SetVisible(True)
            
            self.__arrows['prev'].SetState(0)
            self.__arrows['next'].SetState(2)
        
            self.__page_lables['current'].SetVisible(True)
            self.__page_lables['current'].SetText(str(self.__current_page_index + 1))
            self.__page_lables['total'].SetVisible(True)
            self.__page_lables['total'].SetText(str(self.__display_pages))
            self.__page_lables['div'].SetVisible(True)
        
        else:
            # Show page flips, both arrows enabled
            self.__arrows['prev'].SetEnable(True)
            self.__arrows['prev'].SetVisible(True)
            self.__arrows['next'].SetEnable(True)
            self.__arrows['next'].SetVisible(True)
            
            self.__arrows['prev'].SetState(0)
            self.__arrows['next'].SetState(0)
            
            self.__page_lables['current'].SetVisible(True)
            self.__page_lables['current'].SetText(str(self.__current_page_index + 1))
            self.__page_lables['total'].SetVisible(True)
            self.__page_lables['total'].SetText(str(self.__display_pages))
            self.__page_lables['div'].SetVisible(True)
            
        # utilityFunctions.Log('Tech Status Pagination Updated')

## End Class Definitions -------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------

## End Function Definitions ----------------------------------------------------


