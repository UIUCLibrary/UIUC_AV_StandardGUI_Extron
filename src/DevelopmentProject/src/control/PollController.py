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
from modules.helper.CommonUtilities import Logger, debug
from modules.project.SystemHardware import SystemHardwareController

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
        self.__InactivePolling.Stop()
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
    def __PollInterface(self, interface, command, qualifier=None): # pragma: no cover
        try:
            interface.Update(command, qualifier=qualifier)
        except Exception as inst:
            Logger.Log('An error occured attempting to poll. {} ({})\n    Exception ({}):\n        {}'.format(command, qualifier, type(inst), inst), logSeverity='error')
    
    # Public Methods +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    def PollEverything(self):
        for poll in self.Polling:
            self.__PollInterface(poll.Interface, poll.Command, poll.Qualifier)
            
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
    
## End Class Definitions -------------------------------------------------------