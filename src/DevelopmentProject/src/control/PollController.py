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
    from modules.project.Collections import DeviceCollection

#### Extron Library Imports
from extronlib.system import Timer

#### Project Imports
from modules.helper.CommonUtilities import Logger, FullName
from modules.project.SystemHardware import SystemHardwareController
import Variables

## End Imports -----------------------------------------------------------------
##
## Begin Class Definitions -----------------------------------------------------

class PollObject:
    DefaultActiveDuration = 5
    DefaultInactiveDuration = 300
    
    def __init__(self, 
                 Device: 'SystemHardwareController',
                 Command: str,
                 Qualifier: dict=None,
                 ActiveDuration: int=None,
                 InactiveDuration: int=None) -> None:
        
        if type(Device) is SystemHardwareController:
            self.Device = Device
        else:
            raise TypeError('Device ({}) must be of type SystemHardwareController'.format(type(Device)))
        
        self.Interface = self.Device.interface
        
        if type(Command) is str:
            self.Command = Command
        else:
            raise TypeError('Command ({}) must be of type str'.format(type(Command)))
        
        if type(Qualifier) is dict or Qualifier is None:
            self.Qualifier = Qualifier
        else:
            raise TypeError('Qualifier ({}) must be either be of type dict or None'.format(type(Qualifier)))
        
        if type(ActiveDuration) is int or ActiveDuration is None:
            if ActiveDuration is not None:
                self.ActiveDuration = ActiveDuration
            else:
                self.ActiveDuration = self.DefaultActiveDuration
        else:
            raise TypeError('ActiveDuration ({}) must be either of type int or None'.format(type(ActiveDuration)))
        
        if type(InactiveDuration) is int or InactiveDuration is None:
            if InactiveDuration is not None:
                self.InactiveDuration = InactiveDuration
            else:
                self.InactiveDuration = self.DefaultInactiveDuration
        else:
            raise TypeError('InactiveDuration ({}) must be either of type int or None'.format(type(InactiveDuration)))

class PollingController:
    def __init__(self, devices: 'DeviceCollection') -> None:
        
        self.Polling = devices.Polling
        
        self.__PollingState = 'stopped'
        
        self.__InactivePolling = Timer(1, self.__InactivePollingHandler)
        self.__ActivePolling = Timer(1, self.__ActivePollingHandler)
        self.__ActivePolling.Stop()
    
    # Event Handlers +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    def __ActivePollingHandler(self, timer: 'Timer', count: int):
        for poll in self.Polling:
            if (count % poll.ActiveDuration) == 0:
                self.__PollInterface(poll.Interface, poll.Command, poll.Qualifier)
    
    def __InactivePollingHandler(self, timer: 'Timer', count: int):
        for poll in self.Polling:
            if (count % poll.InactiveDuration) == 0:
                self.__PollInterface(poll.Interface, poll.Command, poll.Qualifier)
    
    # Private Methods ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def __PollInterface(self, interface, command: str, qualifier: Dict=None): # pragma: no cover
        if Variables.TESTING:
            if qualifier is not None:
                Logger.Log('Test Poll: {} {} on {}'.format(command, qualifier, FullName(interface)))
            else:
                Logger.Log('Test Poll: {} on {}'.format(command, FullName(interface)))
            
            return
        
        try:
            interface.Update(command, qualifier=qualifier)
        except Exception as inst:
            Logger.Log('An error occured attempting to poll. {} ({})\n    Exception ({}):\n        {}'.format(command, qualifier, type(inst), inst), logSeverity='error')
    
    def __SetPollingActive(self) -> None:
        self.__ActivePolling.Restart()
        if self.__InactivePolling.State != 'Stopped':
            self.__InactivePolling.Stop()
        lastState = self.__PollingState
        self.__PollingState = 'active'
        if lastState == 'stopped':
            Logger.Log('Polling started, Active')
        else:
            Logger.Log('Polling mode switched, Active')
        
    def __SetPollingInactive(self) -> None:
        self.__InactivePolling.Restart()
        if self.__ActivePolling.State != 'Stopped':
            self.__ActivePolling.Stop()
        lastState = self.__PollingState
        self.__PollingState = 'inactive'
        if lastState == 'stopped':
            Logger.Log('Polling started, Inactive')
        else:
            Logger.Log('Polling mode switched, Inactive')
        
    def __SetPollingStopped(self) -> None:
        if self.__InactivePolling.State != 'Stopped':
            self.__InactivePolling.Stop()
        if self.__ActivePolling.State != 'Stopped':
            self.__ActivePolling.Stop()
        lastState = self.__PollingState
        self.__PollingState = 'stopped'
        if lastState != 'stopped':
            Logger.Log('Polling stopped')
    
    # Public Methods +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    def PollEverything(self):
        for poll in self.Polling:
            self.__PollInterface(poll.Interface, poll.Command, poll.Qualifier)
            
    def SetPollingMode(self, mode: str='inactive'):
        if mode == 'inactive': 
            self.__SetPollingInactive()
        elif mode == 'active':
            self.__SetPollingActive()
        elif mode == 'stopped':
            self.__SetPollingStopped()
        else:
            raise ValueError("Mode must be 'inactive', 'active', or 'stopped'")
            
    def StopPolling(self):
        self.__SetPollingStopped()
        
    def TogglePollingMode(self):
        if self.__PollingState == 'inactive':
            self.__SetPollingActive()
        elif self.__PollingState == 'active':
            self.__SetPollingInactive()
        else:
            Logger.Log('Polling stopped. Polling cannot be toggled. Start polling using SetPollingMode.', logSeverity='warning')
    
## End Class Definitions -------------------------------------------------------