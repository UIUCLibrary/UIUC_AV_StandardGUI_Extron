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
from typing import TYPE_CHECKING
if TYPE_CHECKING: # pragma: no cover
    pass

#### Python imports

#### Extron Library Imports
from extronlib.system import ProgramLog

#### Project imports
from modules.project.MixIns.VirtualDevice import VirtualDeviceInterface
from modules.helper.CommonUtilities import Logger

## End Imports -----------------------------------------------------------------

class DeviceClass:
    def __init__(self):
        
        self.Unidirectional = 'False'
        self.connectionCounter = 15
        # self.DefaultResponseTimeout = 5
        self.Subscription = {}
        # self.ReceiveData = self.__ReceiveData
        # self.__receiveBuffer = b''
        # self.__maxBufferSize = 4096
        # self.__matchStringDict = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        
        self.VirtualInputDevices = {}
        self.VirtualOutputDevices = {}
        
        self.Model = None
        self.Models = {
            'AMX SVSi N2300': self.amx_svsi_n2300
        }
        
        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'InputSignalStatus': {'Parameters': ['Input'], 'Status': {}},
            'InputTieStatus': {'Parameters': ['Input', 'Output'], 'Status': {}},
            'MatrixTieCommand': {'Parameters': ['Input', 'Output', 'Tie Type'], 'Status': {}},
            'OutputTieStatus': {'Parameters': ['Output', 'Tie Type'], 'Status': {}},
            'Standby': {'Parameters': ['Input'], 'Status': {}},
            'VideoMute': {'Parameters': ['Output'], 'Status': {}},
        }
        
        self.UpdateInputTieStatus = self.UpdateAllMatrixTie
        self.UpdateOutputTieStatus = self.UpdateAllMatrixTie
        
        if self.Unidirectional == 'False':
            pass
        
    @property
    def MatrixSize(self):
        return (self.InputSize, self.OutputSize)
    
    @property
    def InputSize(self):
        return len(self.VirtualInputDevices)
    
    @property
    def OutputSize(self):
        return len(self.VirtualOutputDevices)
        
## -----------------------------------------------------------------------------
## Start Model Definitions
## -----------------------------------------------------------------------------

    def amx_svsi_n2300(self):
        self.__Mute_Local_Playlist = 1
        self.Model = 'AMX SVSi N2300'
    
## -----------------------------------------------------------------------------
## End Model Definitions
## =============================================================================
## Start Command & Callback Functions
## -----------------------------------------------------------------------------

    def UpdateAllMatrixTie(self, value=None, qualifier=None):
        # ProgramLog('Matrix Size: {}'.format(self.MatrixSize), 'info')
        for OutputHw in self.VirtualOutputDevices.values():
            OutputHw.interface.Update('Stream', None) # This will query both Stream and AudioStream
            StreamTuple = (OutputHw.interface.ReadStatus('Stream'),
                           OutputHw.interface.ReadStatus('AudioStream'))
            # utilityFunctions.Log('Output {} ({}) StreamTuple = {}'.format(OutputHw.MatrixOutput, OutputHw.Name, StreamTuple), 'info')
            # If elements 0 & 1 of StreamTuple match, tie type must be AudioVideo
            # if StreamTuple[1] == 0 audio follows video and tie type must be AudioVideo
            if StreamTuple != (None, None):
                if StreamTuple[0] == StreamTuple[1] or StreamTuple[1] == 0: # AudioVideo
                    mInput = 0
                    for InputHw in self.VirtualInputDevices.values():
                        devStatus = InputHw.interface.ReadStatus('DeviceStatus')
                        if devStatus is not None:
                            # utilityFunctions.Log('{} Enc Stream {} ({})'.format(InputHw.Name, devStatus['Stream'], (devStatus['Stream'] == StreamTuple[0])))
                            if devStatus['Stream'] == StreamTuple[0]:
                                mInput = InputHw.MatrixInput
                                self.WriteStatus('InputTieStatus', 'AudioVideo', {'Input': InputHw.MatrixInput, 'Output': OutputHw.MatrixOutput})
                            else:
                                self.WriteStatus('InputTieStatus', 'Untied', {'Input': InputHw.MatrixInput, 'Output': OutputHw.MatrixOutput})
                        else:
                            Logger.Log('Device Status for {} is undefined'.format(InputHw.Name))
                    self.WriteStatus('OutputTieStatus', mInput, {'Output': OutputHw.MatrixOutput, 'Tie Type': 'AudioVideo'})
                    self.WriteStatus('OutputTieStatus', mInput, {'Output': OutputHw.MatrixOutput, 'Tie Type': 'Video'})
                    self.WriteStatus('OutputTieStatus', mInput, {'Output': OutputHw.MatrixOutput, 'Tie Type': 'Audio'})
                else: # individual audio and video
                    mInputA = 0
                    mInputV = 0
                    for InputHw in self.VirtualInputDevices.values():
                        devStatus = InputHw.interface.ReadStatus('DeviceStatus')
                        if devStatus is not None:
                            # utilityFunctions.Log('{} Enc Stream {} ({}/{})'.format(InputHw.Name, devStatus['Stream'], (devStatus['Stream'] == StreamTuple[0]), (devStatus['Stream'] == StreamTuple[1])))
                            if devStatus['Stream'] == StreamTuple[0]:
                                mInputV = InputHw.MatrixInput
                                self.WriteStatus('InputTieStatus', 'Video', {'Input': InputHw.MatrixInput, 'Output': OutputHw.MatrixOutput})
                            elif devStatus['Stream'] == StreamTuple[1]:
                                mInputA = InputHw.MatrixInput
                                self.WriteStatus('InputTieStatus', 'Audio', {'Input': InputHw.MatrixInput, 'Output': OutputHw.MatrixOutput})
                            else:
                                self.WriteStatus('InputTieStatus', 'Untied', {'Input': InputHw.MatrixInput, 'Output': OutputHw.MatrixOutput})
                        else:
                            Logger.Log('Device Status for {} is undefined'.format(InputHw.Name))
                    self.WriteStatus('OutputTieStatus', 0, {'Output': OutputHw.MatrixOutput, 'Tie Type': 'AudioVideo'})
                    self.WriteStatus('OutputTieStatus', mInputV, {'Output': OutputHw.MatrixOutput, 'Tie Type': 'Video'})
                    self.WriteStatus('OutputTieStatus', mInputA, {'Output': OutputHw.MatrixOutput, 'Tie Type': 'Audio'})
            else:
                Logger.Log('Stream info for {} is undefined'.format(OutputHw.Name))
                
        self.__ConnectHelper()

    def UpdateInputSignalStatus(self, value, qualifier):
        if qualifier is not None and 'Input' in qualifier:
            InputHw = self.VirtualInputDevices[qualifier['Input']]
            InputHw.interface.Update('HDMIStatus')
            InputStatus = 'Active' if InputHw.interface.ReadStatus('HDMIStatus') == 'connected' else 'Not Active'
            self.WriteStatus('InputSignalStatus', InputStatus, {'Input': InputHw.MatrixInput})
        else:
            for InputHw in self.VirtualInputDevices.values():
                InputHw.interface.Update('HDMIStatus')
                InputStatus = 'Active' if InputHw.interface.ReadStatus('HDMIStatus') == 'connected' else 'Not Active'
                self.WriteStatus('InputSignalStatus', InputStatus, {'Input': InputHw.MatrixInput})
                
            self.__ConnectHelper()

    def __MatrixSetOutput(self, Output, TieType, Stream):
        # Use tie type to send commands to output device to switch
        if TieType == 'AudioVideo':
            Output.interface.Set('Stream', Stream)
            Output.interface.Set('AudioStream', Stream)
        elif TieType == 'Video':
            if Output.interface.ReadStatus('AudioStream') == 0:
                # If audio is following video, grab the current video stream,
                # then set audio stream to previous stream and video stream
                # to the new stream
                PrevStream = Output.interface.ReadStatus('Stream')
                Output.interface.Set('AudioStream', PrevStream)
            Output.interface.Set('Stream', Stream)
        elif TieType == 'Audio':
            Output.interface.Set('AudioStream', Stream)

    def SetMatrixTieCommand(self, value, qualifier):
        # Value: None
        # Qualifier: 'Input', 'Output', 'Tie Type' = ('Audio' or 'Video' or 'AudioVideo')
        
        Logger.Log('Set Matrix Tie - Input: {}, Output: {}, Tie Type: {}'.format(qualifier['Input'], qualifier['Output'], qualifier['Tie Type']))
        
        # SVSi hardware
        if self.Model == 'AMX SVSi N2300':
            # Get SVSi stream number from device with MatrixInput attribute matching provided Input value
            if qualifier['Input'] == 0:
                Stream = 0
            elif qualifier['Input'] in self.VirtualInputDevices:
                # utilityFunctions.Log('Getting Stream from Encoder')
                devStatus = self.VirtualInputDevices[qualifier['Input']].interface.ReadStatus('DeviceStatus')
                if devStatus is not None:
                    Stream = devStatus['Stream']
                else:
                    Stream = 9999
            else:
                #TODO: determine handling for non-existent encoders in the virtual matrix
                Stream = 9998
            
            # Get Output device with MatrixOutput attribute matching provided Output value
            if qualifier['Output'] in self.VirtualOutputDevices:
                Output = self.VirtualOutputDevices[qualifier['Output']]
                self.__MatrixSetOutput(Output, qualifier['Tie Type'], Stream)
            elif qualifier['Output'].strip().lower() == 'all':
                for Output in self.VirtualOutputDevices.values():
                    self.__MatrixSetOutput(Output, qualifier['Tie Type'], Stream)
            else:
                self.Discard('Invalid Output provided.')
                return
        else:
            pass
        
        self.UpdateAllMatrixTie()
        self.__ConnectHelper()
        
    def UpdateStandby(self, value, qualifier):
        if qualifier is not None and 'Input' in qualifier:
            status = self.VirtualInputDevices[qualifier['Input']].interface.ReadStatus('Tx')
            self.WriteStatus('Standby', status, qualifier)
        else:
            for Hw in self.VirtualInputDevices.values():
                qual = {'Input': Hw.MatrixInput}
                status = Hw.interface.ReadStatus('Tx')
                self.WriteStatus('Standby', status, qual)
                
        self.__ConnectHelper()
    
    def SetStandby(self, value, qualifier):
        if value in [True, 1, 'on', 'On', 'ON', 'Standby']:
            cmdVal = 'on'
        elif value in [False, 0, 'off', 'Off', 'OFF', 'Unstandby']:
            cmdVal = 'off'
        
        if qualifier is not None and 'Input' in qualifier:
            self.VirtualInputDevices[qualifier['Input']].interface.Set('Tx', cmdVal)
        else:
            for Hw in self.VirtualInputDevices.values():
                Hw.interface.Set('Tx', cmdVal)
                
        self.Update('Standby')
        self.__ConnectHelper()
    
    def SetVideoMute(self, value, qualifier):
        if qualifier is not None and 'Output' in qualifier:
            Output = self.VirtualOutputDevices[qualifier['Output']]
            if value == 'Video':
                Output.interface.Set('LiveLocal', self.__Mute_Local_Playlist)
            elif value == 'Video & Sync':
                Output.interface.Set('LiveLocal', self.__Mute_Local_Playlist)
                Output.interface.Set('HDMIOutput', 'off')
            elif value == 'Off':
                Output.interface.Set('LiveLocal', 'live')
                Output.interface.Set('HDMIOutput', 'on')
        else:
            for Output in self.VirtualOutputDevices.values():
                if value == 'Video':
                    Output.interface.Set('LiveLocal', self.__Mute_Local_Playlist)
                elif value == 'Video & Sync':
                    Output.interface.Set('LiveLocal', self.__Mute_Local_Playlist)
                    Output.interface.Set('HDMIOutput', 'off')
                elif value == 'Off':
                    Output.interface.Set('LiveLocal', 'live')
                    Output.interface.Set('HDMIOutput', 'on')
            
        self.Update('VideoMute')
        self.__ConnectHelper()
    
    def UpdateVideoMute(self, value, qualifier):
        for OutputHw in self.VirtualOutputDevices.values():
            OutputHw.interface.Update('DeviceStatus')
            VideoMuteStatus = OutputHw.interface.ReadStatus('LiveLocal')
            SyncMuteStatus = OutputHw.interface.ReadStatus('HDMIOutput')
            
            if VideoMuteStatus != 'live' and not SyncMuteStatus: # Video&Sync
                self.WriteStatus('VideoMute', 'Video & Sync', {'Output': OutputHw.MatrixOutput})
            elif VideoMuteStatus != 'live' and SyncMuteStatus: # Video
                self.WriteStatus('VideoMute', 'Video', {'Output': OutputHw.MatrixOutput})
            elif VideoMuteStatus == 'live' and SyncMuteStatus: # Off
                self.WriteStatus('VideoMute', 'Off', {'Output': OutputHw.MatrixOutput})
        self.__ConnectHelper()

## -----------------------------------------------------------------------------
## End Command & Callback Functions
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
        # ProgramLog('Write Status: {}, Value: {}, Qaulifier: {}'.format(command, value, qualifier), 'info')
        self.counter = 0
        if not self.connectionFlag:
            self.OnConnected()
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
            if qualifier:
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

class VirtualDeviceClass(VirtualDeviceInterface, DeviceClass):

    def __init__(self, VirtualDeviceID: str, AssignmentAttribute: str, Model: str=None):
        DeviceClass.__init__(self) 
        VirtualDeviceInterface.__init__(self,
                                        VirtualDeviceID,
                                        AssignmentAttribute,
                                        {
                                            'MatrixInput': self.VirtualInputDevices,
                                            'MatrixOutput': self.VirtualOutputDevices
                                        })
        self.ConnectionType = 'Virtual'
        # Check if Model belongs to a subclass       
        if len(self.Models) > 0:
            if Model not in self.Models: 
                print('Model mismatch') 
                ProgramLog('Model mismatch')              
            else:
                self.Models[Model]()

    def Error(self, message):
        portInfo = 'VirtualDeviceClass - Virtual Matrix Interface'
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
        Logger.Log('Error Message: {}'.format(message[0]))
  
    def Discard(self, message):
        Logger.Log('Discarding Command')
        self.Error([message])

    def Disconnect(self):
        # EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()