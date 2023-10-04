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

# TODO: Look at this more indepth. Since  WOL can't be forwarded between VLANs, 
# this might require a client application to be running on the PC.

## Begin Imports ---------------------------------------------------------------

#### Type Checking
from typing import TYPE_CHECKING, Dict, Tuple, List, Union, Callable
if TYPE_CHECKING: # pragma: no cover
    pass

#### Python imports

#### Extron Library Imports
from extronlib.system import Timer, Ping, WakeOnLan

#### Project imports
from modules.helper.CommonUtilities import Logger

## End Imports -----------------------------------------------------------------
##
## Begin Class Definitions -----------------------------------------------------

class DeviceClass:
    def __init__(self, host, WOLport) -> None:
        self.Unidirectional = 'True'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Host = host
        self.DefaultPort = WOLport
        self.Models = {}
        self.Commands = {
            'ConnectionStatus': { 'Status': {}},
            'Wake': { 'Status': {}}
        }       
        self.PingInterval = 120
        self.PingCount = 5
        self.PingTimer = Timer(self.PingInterval, self.PingHandler)
        self.PingTimer.Restart()
        
        
    def PingHandler(self, timer, count):
        pingStatus = Ping(self.Host, self.PingCount)
        
        if (pingStatus[0]/pingStatus[1]) > 1:
            self.OnConnected()
        else:
            self.OnDisconnected
            
## -----------------------------------------------------------------------------
## Start Model Definitions
## -----------------------------------------------------------------------------
## no models for generic module
## -----------------------------------------------------------------------------
## End Model Definitions
## =============================================================================
## Start Command & Callback Functions
## -----------------------------------------------------------------------------
    
    def SetWake(self, value, qualifier):
        
        
        self.__ConnectHelper()
    
## -----------------------------------------------------------------------------
## End Command & Callback Functions
## =============================================================================
## Start Helper Functions
## -----------------------------------------------------------------------------
    
    def __ConnectHelper(self):
        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()
    
    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    ######################################################    
    # RECOMMENDED not to modify the code below this point
    ######################################################

    def Set(self, command, value, qualifier=None):
        method = getattr(self, 'Set%s' % command, None)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            raise AttributeError(command + 'does not support Set.')

    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command, None)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            raise AttributeError(command + 'does not support Update.')

    # This method is to tie an specific command with a parameter to a call back method
    # when its value is updated. It sets how often the command will be query, if the command
    # have the update method.
    # If the command doesn't have the update feature then that command is only used for feedback 
    def SubscribeStatus(self, command, qualifier, callback):
        Command = self.Commands.get(command, None)
        if Command:
            if command not in self.Subscription:
                self.Subscription[command] = {'method':{}}
        
            Subscribe = self.Subscription[command]
            Method = Subscribe['method']
        
            if qualifier:
                for Parameter in Command['Parameters']:
                    try:
                        Method = Method[qualifier[Parameter]]
                    except:
                        if Parameter in qualifier:
                            Method[qualifier[Parameter]] = {}
                            Method = Method[qualifier[Parameter]]
                        else:
                            return
        
            Method['callback'] = callback
            Method['qualifier'] = qualifier
        else:
            raise KeyError('Invalid command for SubscribeStatus ' + command)

    # This method is to check the command with new status have a callback method then trigger the callback
    def NewStatus(self, command, value, qualifier):
        if command in self.Subscription :
            Subscribe = self.Subscription[command]
            Method = Subscribe['method']
            Command = self.Commands[command]
            if qualifier:
                for Parameter in Command['Parameters']:
                    try:
                        Method = Method[qualifier[Parameter]]
                    except:
                        break
            if 'callback' in Method and Method['callback']:
                Method['callback'](command, value, qualifier)  

    # Save new status to the command
    def WriteStatus(self, command, value, qualifier=None):
        self.counter = 0
        # if not self.connectionFlag:
        #     self.OnConnected()
        Command = self.Commands[command]
        Status = Command['Status']
        if qualifier:
            for Parameter in Command['Parameters']:
                try:
                    Status = Status[qualifier[Parameter]]
                except KeyError:
                    if Parameter in qualifier:
                        Status[qualifier[Parameter]] = {}
                        Status = Status[qualifier[Parameter]]
                    else:
                        return  
        try:
            if Status['Live'] != value:
                Status['Live'] = value
                self.NewStatus(command, value, qualifier)
        except:
            Status['Live'] = value
            self.NewStatus(command, value, qualifier)

    # Read the value from a command.
    def ReadStatus(self, command, qualifier=None):
        Command = self.Commands.get(command, None)
        if Command:
            Status = Command['Status']
            if qualifier and 'Parameters' in Command: # "'Parameters' in Command" is used to prevent key errors for qualifiers other than command parameters
                for Parameter in Command['Parameters']:
                    try:
                        Status = Status[qualifier[Parameter]]
                    except KeyError:
                        return None
            try:
                return Status['Live']
            except:
                return None
        else:
            raise KeyError('Invalid command for ReadStatus: ' + command)

class PCClass (DeviceClass):
    def __init__(self, host: Union[str, int], WOLport: int=0) -> None:
        DeviceClass.__init__(self, host, WOLport)
        
    def Error(self, message):
        portInfo = 'IP Address/Host: {0}'.format(self.RootURL)
        # print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')

        print('Mersive Solstice Error: {}\nError Message: {}'.format(portInfo, message[0]), 'error')
  
    def Discard(self, message):
        self.Error([message])