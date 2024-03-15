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



from typing import TYPE_CHECKING
if TYPE_CHECKING: # pragma: no cover
    from modules.project.ExtendedClasses.Device import ExUIDevice
    from modules.project.Devices import SystemHardwareController

from urllib import request, error, parse
import ssl
import json
from extronlib.system import ProgramLog
import traceback

import modules.helper.CommonUtilities as UtilityFunctions

@UtilityFunctions.debug
def PodFeedbackHelper(touchpanel: 'ExUIDevice', hardware: str, blank_on_fail = True) -> None:
    UtilityFunctions.Log('Feedback TP: {} ({})'.format(touchpanel.Id, touchpanel))
    podIdLabel = touchpanel.Lbls['WPD-PodIDs']
    podKeyLabel = touchpanel.Lbls['WPD-Key']
    
    podHW = None
    
    if isinstance(hardware, str):
        # utilityFunctions.Log('Hardware ID String Submitted - {}'.format(hardware))
        podHW = touchpanel.GUIHost.Hardware.get(hardware, None)
    elif type(hardware) is SystemHardwareController:
        podHW = hardware
    
    #if podHW is not None:
    try:
        podStatus = podHW.interface.ReadStatus('PodStatus')
        podName = podStatus['m_displayInformation']['m_displayName']
        podIP = podStatus['m_displayInformation']['m_ipv4']
        podKey = podStatus['m_authenticationCuration']['sessionKey']

        podIdLabel.SetText('{} ({})'.format(podName, podIP))
        podKeyLabel.SetText('Key: {}'.format(podKey))
    except Exception as inst:
        tb = traceback.format_exc()
        print(tb)
        UtilityFunctions.Log('An error occured attempting set pod feedback.\n    Exception ({}):\n        {}\n    Traceback:\n        {}'.format(type(inst), inst, tb), 'error')
        if blank_on_fail:
            # utilityFunctions.Log('Pod HW not found')
            podIdLabel.SetText('')
            podKeyLabel.SetText('')
            
class DeviceClass:
    def __init__(self, host, protocol, port, devicePassword=None):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        
        self.RootURL = '{proto}://{host}:{p}/'.format(proto = protocol, host = host, p = port)
        self.authentication = {
            'GET': 'password={}'.format(devicePassword),
            'POST': {'password': devicePassword}
        }
        
        self._ctx = ssl.create_default_context()
        self._ctx.check_hostname = False
        self._ctx.verify_mode = ssl.CERT_NONE

        if protocol.lower() == 'http':
            self.Opener = request.build_opener(request.HTTPHandler()) 
        elif protocol.lower() == 'https':
            self.Opener = request.build_opener(request.HTTPSHandler(context=self._ctx)) 
        
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Host = host
        self.DefaultPort = port
        self.devicePassword = devicePassword
        self.Models = {}
        self.Commands = {
            'ConnectionStatus': { 'Status': {}},
            'PodStatus': {'Status': {}},
            'UsageStatistics': { 'Status': {}},
            'ClearPosts': { 'Status': {}},
            'BootUsers': { 'Status': {}},
            'RebootPod': { 'Status': {}},
            'ResetKey': { 'Status': {}},
            'Sleep': { 'Status': {}},
            'Wake': { 'Status': {}}
        }       
        
        
## -----------------------------------------------------------------------------
## Start Model Definitions
## -----------------------------------------------------------------------------

## -----------------------------------------------------------------------------
## End Model Definitions
## =============================================================================
## Start Command & Callback Functions
## -----------------------------------------------------------------------------

    def UpdatePodStatus(self, value, qualifier):
        api_path = '/api/config'
        res = self.__UpdateHelper('PodStatus', value, qualifier, url=api_path, method='GET', data=None)
        if res:
            try:
                dataObj = json.loads(res)
                # clean up unnecessary keys
                popKeys = [
                    'm_networkCuration',
                    'm_licenseCuration',
                    'm_userGroupCuration',
                    'm_systemCuration',
                    'm_calendarCuration'
                ]
                for key in popKeys:
                    dataObj.pop(key)
                
                self.WriteStatus('PodStatus', dataObj, qualifier)
            except (KeyError, IndexError):
                self.Error(['PodStatus: Invalid/unexpected response'])
    
    def UpdateUsageStatistics(self, value, qualifier):
        api_path = '/api/stats'
        res = self.__UpdateHelper('UsageStatistics', value, qualifier, url=api_path, method='GET', data=None)
        if res:
            try:
                dataObj = json.loads(res)
                self.WriteStatus('UsageStatistics', dataObj, qualifier)
            except (KeyError, IndexError):
                self.Error(['UsageStatistics: Invalid/unexpected response'])
    
    def SetClearPosts(self, value, qualifier):
        api_path = '/api/control/clear'
        self.__SetHelper('ClearPosts', value, qualifier, url=api_path, method='GET', data=None)
    
    def SetBootUsers(self, value, qualifier):
        api_path = '/api/control/boot'
        self.__SetHelper('BootUsers', value, qualifier, url=api_path, method='GET', data=None)
    
    def SetRebootPod(self, value, qualifier):
        api_path = '/api/control/reboot'
        self.__SetHelper('RebootPod', value, qualifier, url=api_path, method='GET', data=None)
    
    def SetResetKey(self, value, qualifier):
        api_path = '/api/control/resetkey'
        self.__SetHelper('ResetKey', value, qualifier, url=api_path, method='GET', data=None)
    
    def SetSleep(self, value, qualifier):
        api_path = '/api/control/suspend'
        self.__SetHelper('Sleep', value, qualifier, url=api_path, method='GET', data=None)
    
    def SetWake(self, value, qualifier):
        api_path = '/api/control/wake'
        self.__SetHelper('Wake', value, qualifier, url=api_path, method='GET', data=None)

## -----------------------------------------------------------------------------
## End Command & Callback Functions
## -----------------------------------------------------------------------------
    
    def __CheckResponseForErrors(self, sourceCmdName, response):

        res = response.read().decode()
        # Check for and process device provided errors here
        return res
    
    def __SetHelper(self, command, value, qualifier, url='', method='GET', data=None):
        self.Debug = True

        headers = {}
        
        call_url = '{0}{1}'.format(self.RootURL.rstrip('/'), url)
        
        if data is None:
            data = {}
        elif not isinstance(data, dict):
            self.Error(['Data must be a dictionary object'])
        
        if self.authentication is not None:
            if method == 'GET':
                call_url = '{url}?{params}'.format(url = call_url, params = self.authentication['GET'])
            elif method == 'POST':
                tmp_data = data
                data = self.authentication['POST']
                data.update(tmp_data)
            else:
                self.Error(['Method ({}) not supported'.format(method)])
                
        if method == 'GET':
            my_request = request.Request(call_url, headers=headers)
        elif method == 'POST':
            call_data = parse.urlencode(data).encode()
            my_request = request.Request(call_url, data=call_data, headers=headers)
                
        try:
            res = self.Opener.open(my_request, timeout=10)  # open() returns a http.client.HTTPResponse object if successful
        except error.HTTPError as err:  # includes HTTP status codes 101, 300-505
            self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
            res = ''
        except error.URLError as err:  # received if can't reach the server (times out)
            self.Error(['{0} {1}'.format(command, err.reason)])
            res = ''
        except Exception:  # includes HTTP status code 100 and any invalid status code
            res = ''
        else:
            if res.status not in (200, 202):
                self.Error(['{0} {1} - {2}'.format(command, res.status, res.msg)])
                res = ''
            else:
                res = self.__CheckResponseForErrors(command, res)
        return res

    def __UpdateHelper(self, command, value, qualifier, url='', method='GET', data=None):
        # self.__UpdateHelper('TallyInput', value, qualifier, url=api_path, data=None)
        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()
        
        headers = {}
        
        call_url = '{0}{1}'.format(self.RootURL.rstrip('/'), url)
        
        if data is None:
            data = {}
        elif not isinstance(data, dict):
            self.Error(['Data must be a dictionary object'])
        
        if self.authentication is not None:
            if method == 'GET':
                call_url = '{url}?{params}'.format(url = call_url, params = self.authentication['GET'])
            elif method == 'POST':
                tmp_data = data
                data = self.authentication['POST']
                data.update(tmp_data)
            else:
                self.Error(['Method ({}) not supported'.format(method)])
                
        if method == 'GET':
            my_request = request.Request(call_url, headers=headers)
        elif method == 'POST':
            call_data = parse.urlencode(data).encode()
            my_request = request.Request(call_url, data=call_data, headers=headers)

        try:
            res = self.Opener.open(my_request, timeout=10)  # open() returns a http.client.HTTPResponse object if successful
        except error.HTTPError as err:  # includes HTTP status codes 101, 300-505
            self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
            res = ''
        except error.URLError as err:  # received if can't reach the server (times out)
            self.Error(['{0} {1}'.format(command, err.reason)])
            res = ''
        except Exception:  # includes HTTP status code 100 and any invalid status code
            res = ''
        else:
            if res.status not in (200, 202):
                self.Error(['{0} {1} - {2}'.format(command, res.status, res.msg)])
                res = ''
            else:
                res = self.__CheckResponseForErrors(command, res)
        return res   
            
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

    # Send Control Commands
    def Set(self, command, value, qualifier=None):
        method = getattr(self, 'Set%s' % command, None)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            raise AttributeError(command + 'does not support Set.')

    # Send Update Commands
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
                    except Exception:
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
                    except Exception:
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
        except Exception:
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
            except Exception:
                return None
        else:
            raise KeyError('Invalid command for ReadStatus: ' + command)

    def MissingCredentialsLog(self, credential_type):
        ProgramLog("{0} module received a request from the device for a {1}, "
                   "but device{1} was not provided.\n Please provide a device{1} "
                   "and attempt again.\n Ex: dvInterface.device{1} = '{1}'\n Please "
                   "review the communication sheet.\n {2}"
                   .format(__name__, credential_type, self.port_info), 'warning') 
        
class RESTClass(DeviceClass):

    def __init__(self, host, protocol='https', port='443', devicePassword=None, Model=None):
        self.ConnectionType = 'REST'
        DeviceClass.__init__(self, host, protocol, port, devicePassword)
        # Check if Model belongs to a subclass      
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')             
            else:
                self.Models[Model]()

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}'.format(self.RootURL)
        # print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')

        ProgramLog('Mersive Solstice Error: {}\nError Message: {}'.format(portInfo, message[0]), 'error')
  
    def Discard(self, message):
        self.Error([message])


