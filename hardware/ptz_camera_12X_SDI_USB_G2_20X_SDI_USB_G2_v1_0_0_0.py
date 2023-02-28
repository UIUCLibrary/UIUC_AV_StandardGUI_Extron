from typing import TYPE_CHECKING, Dict, Tuple, List, Union, Callable
if TYPE_CHECKING:
    from uofi_gui import GUIController

from extronlib.interface import SerialInterface, EthernetClientInterface
from struct import pack

class DeviceClass:

    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}
        self.DeviceID = '1'
        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoFocus': {'Status': {}},
            'BackLight': {'Status': {}},
            'Focus': {'Parameters': ['Focus Speed'], 'Status': {}},
            'Gain': {'Status': {}},
            'Iris': {'Status': {}},
            'PanTilt': {'Parameters': ['Pan Speed', 'Tilt Speed'], 'Status': {}},
            'Power': {'Status': {}},
            'PresetRecall': {'Status': {}},
            'PresetReset': {'Status': {}},
            'PresetSave': {'Status': {}},
            'Zoom': {'Parameters': ['Zoom Speed'], 'Status': {}}
        }

    @property
    def DeviceID(self):
        return self.cameraID

    @DeviceID.setter
    def DeviceID(self, tempID):
        if tempID == 'Broadcast':
            self.cameraID = b'\x88'
        elif 1 <= int(tempID) <= 7:
            self.cameraID = pack('>B', 0x80 + int(tempID))

    def SetAutoFocus(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x02',
            'Off': b'\x03'
        }

        AutoFocusCmdString = b''.join([self.cameraID, b'\x01\x04\x38', ValueStateValues[value], b'\xFF'])
        self.__SetHelper('AutoFocus', AutoFocusCmdString, value, qualifier)

    def UpdateAutoFocus(self, value, qualifier):

        ValueStateValues = {
            b'\x02': 'On',
            b'\x03': 'Off'
        }

        AutoFocusCmdString = b''.join([self.cameraID, b'\x09\x04\x38\xFF'])
        res = self.__UpdateHelper('AutoFocus', AutoFocusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2:3]]
                self.WriteStatus('AutoFocus', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateAutoFocus')

    def SetBackLight(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x02',
            'Off': b'\x03'
        }

        BackLightCmdString = b''.join([self.cameraID, b'\x01\x04\x33', ValueStateValues[value], b'\xFF'])
        self.__SetHelper('BackLight', BackLightCmdString, value, qualifier)

    def UpdateBackLight(self, value, qualifier):

        ValueStateValues = {
            b'\x02': 'On',
            b'\x03': 'Off'
        }

        BackLightCmdString = b''.join([self.cameraID, b'\x09\x04\x33\xFF'])
        res = self.__UpdateHelper('BackLight', BackLightCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2:3]]
                self.WriteStatus('BackLight', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateBackLight')

    def SetFocus(self, value, qualifier):

        ValueStateValues = {
            'Stop': 0x00,
            'Far': 0x20,
            'Near': 0x30
        }

        if 0 <= int(qualifier['Focus Speed']) <= 7:
            if value == 'Stop':
                focusSpeed = b'\x00'
            else:
                focusSpeed = pack('>B', ValueStateValues[value] + int(qualifier['Focus Speed']))

            FocusCmdString = b''.join([self.cameraID, b'\x01\x04\x08', focusSpeed, b'\xFF'])
            self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        else:
            print('Invalid Command for SetFocus')

    def SetGain(self, value, qualifier):

        ValueStateValues = {
            'Up': b'\x02',
            'Down': b'\x03',
            'Reset': b'\x00'
        }

        GainCmdString = b''.join([self.cameraID, b'\x01\x04\x0C', ValueStateValues[value], b'\xFF'])
        self.__SetHelper('Gain', GainCmdString, value, qualifier)

    def SetIris(self, value, qualifier):

        ValueStateValues = {
            'Reset': b'\x00',
            'Up': b'\x02',
            'Down': b'\x03'
        }

        IrisCmdString = b''.join([self.cameraID, b'\x01\x04\x0B', ValueStateValues[value], b'\xFF'])
        self.__SetHelper('Iris', IrisCmdString, value, qualifier)

    def SetPanTilt(self, value, qualifier):

        ValueStateValues = {
            'Up': b'\x03\x01',
            'Down': b'\x03\x02',
            'Left': b'\x01\x03',
            'Right': b'\x02\x03',
            'Up Left': b'\x01\x01',
            'Up Right': b'\x02\x01',
            'Down Left': b'\x01\x02',
            'Down Right': b'\x02\x02',
            'Stop': b'\x03\x03',
            'Home': b'\x04',
            'Reset': b'\x05'
        }

        speedByte = pack('>BB', int(qualifier['Pan Speed']), int(qualifier['Tilt Speed']))

        if 1 <= int(qualifier['Pan Speed']) <= 24 and 1 <= int(qualifier['Tilt Speed']) <= 20:
            if value == 'Home' or value == 'Reset':
                PanTiltCmdString = b''.join([self.cameraID, b'\x01\x06', ValueStateValues[value], b'\xFF'])
            else:
                PanTiltCmdString = b''.join([self.cameraID, b'\x01\x06\x01', speedByte, ValueStateValues[value], b'\xFF'])
            self.__SetHelper('PanTilt', PanTiltCmdString, value, qualifier)
        else:
            print('Invalid Command for SetPanTilt')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x02',
            'Off': b'\x03'
        }

        PowerCmdString = b''.join([self.cameraID, b'\x01\x04\x00', ValueStateValues[value], b'\xFF'])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            b'\x02': 'On',
            b'\x03': 'Off'
        }

        PowerCmdString = b''.join([self.cameraID, b'\x09\x04\x00\xFF'])
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            if res[2:3] == b'\x04':
                print('Internal power circuit error. for UpdatePower')
            else:
                try:
                    value = ValueStateValues[res[2:3]]
                    self.WriteStatus('Power', value, qualifier)
                except (KeyError, IndexError):
                    print('Invalid/unexpected response')

    def SetPresetRecall(self, value, qualifier):

        if 0 <= int(value) <= 254:
            presetByte = pack('>B', int(value))
            PresetRecallCmdString = b''.join([self.cameraID, b'\x01\x04\x3F\x02', presetByte, b'\xFF'])
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            print('Invalid Command for SetPresetRecall')

    def SetPresetReset(self, value, qualifier):

        if 0 <= int(value) <= 254:
            presetByte = pack('>B', int(value))
            PresetResetCmdString = b''.join([self.cameraID, b'\x01\x04\x3F\x00', presetByte, b'\xFF'])
            self.__SetHelper('PresetReset', PresetResetCmdString, value, qualifier)
        else:
            print('Invalid Command for SetPresetReset')

    def SetPresetSave(self, value, qualifier):

        if 0 <= int(value) <= 254:
            presetByte = pack('>B', int(value))
            PresetSaveCmdString = b''.join([self.cameraID, b'\x01\x04\x3F\x01', presetByte, b'\xFF'])
            self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)
        else:
            print('Invalid Command for SetPresetSave')

    def SetZoom(self, value, qualifier):

        ValueStateValues = {
            'Stop': 0x00,
            'Tele': 0x20,
            'Wide': 0x30
        }

        if 0 <= int(qualifier['Zoom Speed']) <= 7:
            if value == 'Stop':
                zoomSpeed = b'\x00'
            else:
                zoomSpeed = pack('>B', int(qualifier['Zoom Speed']) + ValueStateValues[value])

            ZoomCmdString = b''.join([self.cameraID, b'\x01\x04\x07', zoomSpeed, b'\xFF'])
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            print('Invalid Command for SetZoom')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            b'\x02': 'Syntax Error.',
            b'\x03': 'Command Buffer Full.',
            b'\x04': 'Command Canceled.',
            b'\x05': 'No Socket.',
            b'\x41': 'Command Not Executable.'
        }
        if response[1:2] != b'\x50':
            if len(response) == 4:
                print(DEVICE_ERROR_CODES[response[2:3]])
                response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True' or self.cameraID == b'\x88':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\xFF')
            if not res:
                print('No Response')
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self.cameraID == b'\x88':
            print('Inappropriate Command ', command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()
                
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\xFF')
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command, res)

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
        method = 'Set%s' % command
        if hasattr(self, method) and callable(getattr(self, method)):
            getattr(self, method)(value, qualifier)
        else:
            print(command, 'does not support Set.')
    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = 'Update%s' % command
        if hasattr(self, method) and callable(getattr(self, method)):
            getattr(self, method)(None, qualifier)
        else:
            print(command, 'does not support Update.') 

    # This method is to tie an specific command with a parameter to a call back method
    # when its value is updated. It sets how often the command will be query, if the command
    # have the update method.
    # If the command doesn't have the update feature then that command is only used for feedback 
    def SubscribeStatus(self, command, qualifier, callback):
        Command = self.Commands.get(command)
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
            print(command, 'does not exist in the module')

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
        except:
            Status['Live'] = value
            self.NewStatus(command, value, qualifier)            

    # Read the value from a command.
    def ReadStatus(self, command, qualifier=None):
        Command = self.Commands[command]
        Status = Command['Status']
        if qualifier:
            for Parameter in Command['Parameters']:
                try:
                    Status = Status[qualifier[Parameter]]
                except KeyError:
                    return None
        try:
            return Status['Live']
        except:
            return None
class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models: 
                print('Model mismatch')              
            else:
                self.Models[Model]()
                
class EthernetClass(EthernetClientInterface, DeviceClass):

    def __init__(self, GUIHost: 'GUIController', Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Ethernet'
        self.GUIHost = GUIHost
        DeviceClass.__init__(self) 
        # Check if Model belongs to a subclass       
        if len(self.Models) > 0:
            if Model not in self.Models: 
                print('Model mismatch')              
            else:
                self.Models[Model]()
