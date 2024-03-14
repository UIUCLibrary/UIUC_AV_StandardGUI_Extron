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
import re

#### Extron Library Imports
from extronlib.interface import EthernetClientInterface
from extronlib.system import ProgramLog

#### Project imports

## End Imports -----------------------------------------------------------------

class DeviceClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self.__receiveBuffer = b''
        self.__maxBufferSize = 4096
        self.__matchStringDict = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        
        self.__lineEnding = '\n'
        
        self.Models = {
            'NMX-ENC-N2312': self.amx_svsi_n2300_enc,
            'NMX-ENC-N2312-C': self.amx_svsi_n2300_enc,
            'NMX-ENC-N2315-WP': self.amx_svsi_n2300_enc,
            'NMX-DEC-N2322': self.amx_svsi_n2300_dec
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'NetStatus': {'Status': {}},
            'Mute': {'Status': {}},
            'LiveLocal': {'Status': {}},
            'RawIRCommand': {'Status': {}},
            'SerialCommand': {'Status': {}},
            'SerialConfig': {'Parameters': ['Baud', 'DataBits', 'Parity', 'Stop'], 'Status': {}},
            'HDMIStatus': {'Status': {}},
            }  
        
        if self.Unidirectional == 'False':
            pass
        
        # Add match strings for callbacks
        self.AddMatchString(re.compile(b'SVSI_NETSTATS:.+\\rchassisID:(.+)\\rsysName:(.+)\\rsysDescr:(.+)\\rportID:(.+)\\rportDescr:(.+)\\r'), self.__CallbackNetStatus, None)
        self.AddMatchString(re.compile(b'(?:SVSI_.+)MUTE:(\d)\\r'), self.__CallbackMute, None)
        self.AddMatchString(re.compile(b'(?:SVSI_.+)PLAYLIST:([0-7])\\r(?:.+)PLAYMODE:(live|local|off)\\r'), self.__CallbackLiveLocal, None)
        self.AddMatchString(re.compile(b'(?:SVSI_.+)BAUD:(\d+)\\rSNUMB:(7|8)\\rSPAR:(even|odd|none)\\rSP2S:(1|2)\\r'), self.__CallbackSerialConfig, None)
        self.AddMatchString(re.compile(b'(?:SVSI_.+)DVI(?:STATUS|INPUT):(connected|disconnected)\\r'), self.__CallbackHDMIStatus, None)
        
        self.UpdateMute = self.UpdateDeviceStatus
        self.UpdateLiveLocal = self.UpdateDeviceStatus
        self.UpdateSerialConfig = self.UpdateDeviceStatus
        self.UpdateHDMIStatus = self.UpdateDeviceStatus
        
        

## -----------------------------------------------------------------------------
## Start Model Definitions
## -----------------------------------------------------------------------------

    def amx_svsi_n2300_enc(self):
        self.EndpointType = 'ENC'
        self.AddMatchString(re.compile(b'SVSI_TXGEN2:(\w+)\\rNAME:(.+)\\rMAC:([0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2})\\rIP:(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\\rNM:(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\\rGW:(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\\rIPTRIAL:(0|1)\\rIPMODE:(.+)\\rID:(.+)\\rrel:(.+)\\rSWVER:(.+)\\rWEBVER:(.+)\\rUPDATE:(.+)\\rUPDTRY:(.+)\\rUPDFAILED:(.+)\\rMEDIAPORT0:(on|off)\\rMEDIAPORT1:(on|off)\\rDIVASEN:(.+)\\rDIVASIP:(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(?:\\r.+\\r)PORTSD1:(yes|no)\\rDVICEVTDLY:(\d{1,5})\\rDVIDEVTDLY:(\d{1,5})\\rUSERMCMODE:(on|off)\\rUSERMCIP:(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(?:\\r.+\\r)STREAM:(\d{1,4})\\rSAMPLE:(\d+)\\rHDMIAUDIO:(auto|on|off)\\rvidDetectMode:(auto|digital|analog)(?:\\r.+\\r)DVIINPUT:(connected|disconnected)\\rMODE:(.*?)\\rLINEINVOL_L:(\d{1,3})\\rLINEINVOL_R:(\d{1,3})\\rLIVEAUDIOHP:(on|off)\\r'), self.__CallbackDeviceStatus_Enc, None)

        enc_commands = \
            {
                'Tx': {'Status': {}},
                'VidSource': {'Status': {}},
            }
        
        self.Commands.update(enc_commands)
        
        # No match string for Tx or VidSource.
        # Tx is set for encoders in __CallbackLiveLocal
        # VidSource status is not provided by N2300 encoders, so the status is emulated in SetVidSource
        
        self.UpdateTx = self.UpdateDeviceStatus
        self.UpdateVidSource = self.UpdateDeviceStatus

    def amx_svsi_n2300_dec(self):
        self.EndpointType = 'DEC'
        self.AddMatchString(re.compile(b'SVSI_RXGEN2:(\w+)\\rNAME:(.+)\\rMAC:([0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2})\\rIP:(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\\rNM:(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\\rGW:(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\\rIPTRIAL:(0|1)\\rIPMODE:(.+)\\rID:(.+)\\rrel:(.+)\\rSWVER:(.+)\\rWEBVER:(.+)\\rUPDATE:(.+)\\rUPDTRY:(.+)\\rUPDFAILED:(.+)\\rMEDIAPORT0:(on|off)\\rMEDIAPORT1:(on|off)\\rDIVASEN:(.+)\\rDIVASIP:(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(?:\\r.+\\r)PORTSD1:(yes|no)\\rDVICEVTDLY:(\d{1,5})\\rDVIDEVTDLY:(\d{1,5})\\rUSERMCMODE:(on|off)\\rUSERMCIP:(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(?:\\r.+\\r)FCPC:(\w+)(?:\\r.+\\r)LIVEAUDIOLP:(on|off)\\rYUVOUT:(on|off)\\rFRAMEHOLD:(on|off)\\rVIDOFFNOSTRM:(on|off)(?:\\r.+\\r)MODE:(.*?)\\r'), self.__CallbackDeviceStatus_Dec, None)

        dec_commands = \
            {
                'Stream': {'Status': {}},
                'AudioStream': {'Status': {}},
                'KVMMasterIP': {'Parameters': ['VideoFollow'], 'Status': {}},
                'Volume': {'Status': {}},
                'HDMIOutput': {'Status': {}},
                'Scaler': {'Status': {}},
                'ScalerMode': {'Status': {}},
                'IRCommand': {'Status': {}},
                'IRPassthrough': {'Status': {}},
                'IRDestination': {'Status': {}},
                'VideoWall': {'Status': {}},
                'VideoWall_HorMons': {'Status': {}},
                'VideoWall_VerMons': {'Status': {}},
                'VideoWall_PosHor': {'Status': {}},
                'VideoWall_PosVer': {'Status': {}},
                'VideoWall_Stretch': {'Status': {}},
                'VideoWall_HShift': {'Status': {}},
                'VideoWall_VShift': {'Status': {}},
            }
        
        self.Commands.update(dec_commands)
        
        self.AddMatchString(re.compile(b'(?:SVSI_.+)STREAM:(\d{1,4})\\r'), self.__CallbackStream, None)
        self.AddMatchString(re.compile(b'(?:SVSI_.+)STREAMAUDIO:(\d{1,4})\\r'), self.__CallbackAudioStream, None)
        self.AddMatchString(re.compile(b'(?:SVSI_.+)KVMMasterIP:(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\\r'), self.__CallbackKVMMasterIP, None)
        self.AddMatchString(re.compile(b'(?:SVSI_.+)LINEOUTVOL_L:(\d{1,3})\\rLINEOUTVOL_R:(\d{1,3})\\r'), self.__CallbackVolume, None)
        self.AddMatchString(re.compile(b'(?:SVSI_.+)DVIOFF:(0|1)\\r'), self.__CallbackHDMIOutput, None)
        self.AddMatchString(re.compile(b'(?:SVSI_.+)MODE:(auto|1080p59\.94|1080p60|720p60|4K30|4K25)\\r'), self.__CallbackScalerMode, None)
        self.AddMatchString(re.compile(b'(?:SVSI_.+)SCALERBYPASS:(on|off)\\r'), self.__CallbackScaler, None)
        self.AddMatchString(re.compile(b'(?:SVSI_.+)wallEnable:(0|1)\\r'), self.__CallbackVideoWall, None)
        self.AddMatchString(re.compile(b'(?:SVSI_.+)wallHorMons:(\d{1,2})\\r'), self.__CallbackVideoWall_HorMons, None)
        self.AddMatchString(re.compile(b'(?:SVSI_.+)wallVerMons:(\d{1})\\r'), self.__CallbackVideoWall_VerMons, None)
        self.AddMatchString(re.compile(b'(?:SVSI_.+)wallMonPosH:(\d{1,2})\\r'), self.__CallbackVideoWall_PosHor, None)
        self.AddMatchString(re.compile(b'(?:SVSI_.+)wallMonPosV:(\d{1})\\r'), self.__CallbackVideoWall_PosVer, None)
        self.AddMatchString(re.compile(b'(?:SVSI_.+)wallStretch:(.+?)\\r'), self.__CallbackVideoWall_Stretch, None)
        
        self.UpdateStream = self.UpdateDeviceStatus
        self.UpdateAudioStream = self.UpdateDeviceStatus
        self.UpdateKVMMasterIP = self.UpdateDeviceStatus
        self.UpdateVolume = self.UpdateDeviceStatus
        self.UpdateHDMIOutput = self.UpdateDeviceStatus
        self.UpdateScaler = self.UpdateDeviceStatus
        self.UpdateScalerMode = self.UpdateDeviceStatus
        self.UpdateIRPassthrough = self.UpdateDeviceStatus
        self.UpdateIRDestination = self.UpdateDeviceStatus
        self.UpdateVideoWall = self.UpdateDeviceStatus
        self.UpdateVideoWall_HorMons = self.UpdateDeviceStatus
        self.UpdateVideoWall_VerMons = self.UpdateDeviceStatus
        self.UpdateVideoWall_PosHor = self.UpdateDeviceStatus
        self.UpdateVideoWall_PosVer = self.UpdateDeviceStatus
        self.UpdateVideoWall_Strech = self.UpdateDeviceStatus

## -----------------------------------------------------------------------------
## End Model Definitions
## =============================================================================
## Start Command & Callback Functions
## -----------------------------------------------------------------------------

    def UpdateDeviceStatus(self, value, qualifier):
        self.__UpdateHelper('DeviceStatus', 'getStatus{}'.format(self.__lineEnding), value, qualifier)
    
    def __CallbackDeviceStatus_Dec(self, match, tag):
        #1# SVSI_RXGEN2:(\w+)
        #2# NAME:(.+)
        #3# MAC:([0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2})
        #4# IP:(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})
        #5# NM:(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})
        #6# GW:(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})
        #7# IPTRIAL:(0|1)
        #8# IPMODE:(.+)
        #9# ID:(.+)
        #10# rel:(.+)
        #11# SWVER:(.+)
        #12# WEBVER:(.+)
        #13# UPDATE:(.+)
        #14# UPDTRY:(.+)
        #15# UPDFAILED:(.+)
        #16# MEDIAPORT0:(on|off)
        #17# MEDIAPORT1:(on|off)
        #18# DIVASEN:(.+) - ignored
        #19# DIVASIP:(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) - ignored
        #20# PORTSD1:(yes|no)
        #21# DVICEVTDLY:(\d{1,5})
        #22# DVIDEVTDLY:(\d{1,5})
        #23# USERMCMODE:(on|off)
        #24# USERMCIP:(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})
        #25# FCPC:(\w+) - ignored
        #26# LIVEAUDIOLP:(on|off)
        #27# YUVOUT:(on|off)
        #28# FRAMEHOLD:(on|off)
        #29# VIDOFFNOSTRM:(on|off)
        #30# MODE:(.*?)
        statusDict = {
            'Name': str(match.group(2), 'UTF-8'),
            'SerialNumber': str(match.group(1), 'UTF-8'),
            'DeviceNetwork': {
                'MAC': str(match.group(3), 'UTF-8'),
                'IP': str(match.group(4), 'UTF-8'),
                'Netmask': str(match.group(5), 'UTF-8'),
                'Gateway': str(match.group(6), 'UTF-8'),
                'IPMode': str(match.group(8), 'UTF-8'),
                'IPTrailMode': bool(int(match.group(7)))
            },
            'ID': str(match.group(9), 'UTF-8'),
            'Firmware': {
                'Version': str(match.group(10), 'UTF-8'),
                'Date': str(match.group(11), 'UTF-8'),
                'WebVersion': str(match.group(12), 'UTF-8'),
                'Update': {
                    'Updating': bool(int(match.group(13))),
                    'Tries': int(match.group(14)),
                    'Fails': int(match.group(15))
                }
            },
            'MulticastTraffic': (
                (True if str(match.group(16), 'UTF-8') == 'on' else False),
                (True if str(match.group(17), 'UTF-8') == 'on' else False)
            ),
            "P1Disabled": (False if str(match.group(20), 'UTF-8') == 'yes' else True),
            'NActEventDelay': {
                'connect': int(match.group(21)),
                'disconnect': int(match.group(22))
            },
            'UserMulticast': (True if str(match.group(23), 'UTF-8') == 'on' else False),
            'UserMulticastAddr': str(match.group(24), 'UTF-8'),
            'LiveAudioInLocalPlay': (True if str(match.group(26), 'UTF-8') == 'on' else False),
            'YUVOut': (True if str(match.group(27), 'UTF-8') == 'on' else False),
            'FrameHold': (True if str(match.group(28), 'UTF-8') == 'on' else False),
            'VidOffOnNoStream': (True if str(match.group(29), 'UTF-8') == 'on' else False),
            'Mode': str(match.group(30), 'UTF-8')
        }
        self.WriteStatus('DeviceStatus', statusDict)
    
    def __CallbackDeviceStatus_Enc(self, match, tag):
        #1# SVSI_TXGEN2:(\w+)
        #2# NAME:(.+)
        #3# MAC:([0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2})
        #4# IP:(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})
        #5# NM:(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})
        #6# GW:(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})
        #7# IPTRIAL:(0|1)
        #8# IPMODE:(.+)
        #9# ID:(.+)
        #10# rel:(.+)
        #11# SWVER:(.+)
        #12# WEBVER:(.+)
        #13# UPDATE:(.+)
        #14# UPDTRY:(.+)
        #15# UPDFAILED:(.+)
        #16# MEDIAPORT0:(on|off)
        #17# MEDIAPORT1:(on|off)
        #18# DIVASEN:(.+) - ignored
        #19# DIVASIP:(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) - ignored
        #20# PORTSD1:(yes|no)
        #21# DVICEVTDLY:(\d{1,5})
        #22# DVIDEVTDLY:(\d{1,5})
        #23# USERMCMODE:(on|off)
        #24# USERMCIP:(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})
        #25# STREAM:(\d{1,4})
        #26# SAMPLE:(\d+)
        #27# HDMIAUDIO:(auto|on|off)
        #28# vidDetectMode:(auto|digital|analog)
        #29# DVIINPUT:(connected|disconnected)
        #30# MODE:(.*?)
        #31# LINEINVOL_L:(\d{1,3})
        #32# LINEINVOL_R:(\d{1,3})
        #33# LIVEAUDIOHP:(on|off)
        statusDict = {
            'Name': str(match.group(2), 'UTF-8'),
            'SerialNumber': str(match.group(1), 'UTF-8'),
            'DeviceNetwork': {
                'MAC': str(match.group(3), 'UTF-8'),
                'IP': str(match.group(4), 'UTF-8'),
                'Netmask': str(match.group(5), 'UTF-8'),
                'Gateway': str(match.group(6), 'UTF-8'),
                'IPMode': str(match.group(8), 'UTF-8'),
                'IPTrailMode': bool(int(match.group(7)))
            },
            'ID': str(match.group(9), 'UTF-8'),
            'Firmware': {
                'Version': str(match.group(10), 'UTF-8'),
                'Date': str(match.group(11), 'UTF-8'),
                'WebVersion': str(match.group(12), 'UTF-8'),
                'Update': {
                    'Updating': bool(int(match.group(13))),
                    'Tries': int(match.group(14)),
                    'Fails': int(match.group(15))
                }
            },
            'MulticastTraffic': (
                (True if str(match.group(16), 'UTF-8') == 'on' else False),
                (True if str(match.group(17), 'UTF-8') == 'on' else False)
            ),
            "P1Disabled": (False if str(match.group(20), 'UTF-8') == 'yes' else True),
            'NActEventDelay': {
                'connect': int(match.group(21)),
                'disconnect': int(match.group(22))
            },
            'UserMulticast': (True if str(match.group(23), 'UTF-8') == 'on' else False),
            'UserMulticastAddr': str(match.group(24), 'UTF-8'),
            'Stream': int(match.group(25)),
            'AudioSampleRate': int(match.group(26)),
            'HDMIAudioMode': str(match.group(27), 'UTF-8'),
            'VideoDetectionMode': str(match.group(28), 'UTF-8'),
            'Mode': str(match.group(30), 'UTF-8'),
            'LineInVol': (int(match.group(31)), int(match.group(32))),
            'LiveAudioInHostPlay': (True if str(match.group(33), 'UTF-8') == 'on' else False)
        }
        self.WriteStatus('DeviceStatus', statusDict)
    
    def UpdateNetStatus(self, value, qualifier):
        self.__UpdateHelper('NetStatus', 'getNetStatus{}'.format(self.__lineEnding), value, qualifier)
    
    def __CallbackNetStatus(self, match, tag):
        # chassisID:(.+)
        # sysName:(.+)
        # sysDescr:(.+)
        # portID:(.+)
        # portDescr:(.+)
        netStatusDict = {
            'ChassisId': str(match.group(1), 'UTF-8'),
            'SystemName': str(match.group(2), 'UTF-8'),
            'SystemDescription': str(match.group(3), 'UTF-8'),
            'PortId': str(match.group(4), 'UTF-8'),
            'PortDescription': str(match.group(5), 'UTF-8')
        }
        self.WriteStatus('NetStatus', netStatusDict)
    
    def SetMute(self, value, qualifier):
        if value is True or value == 1 or value == 'on':
            self.__SetHelper('Mute', 'mute{}'.format(self.__lineEnding), value, qualifier)
        elif value is False or value == 0 or value == 'off':
            self.__SetHelper('Mute', 'unmute{}'.format(self.__lineEnding), value, qualifier)
    
    def __CallbackMute(self, match, tag):
        # MUTE:(\d)
        dataVal = bool(int(match.group(1)))
        self.WriteStatus('Mute', dataVal)
    
    def SetLiveLocal(self, value, qualifier):
        if value == 'live':
            self.__SetHelper('LiveLocal', 'live{}'.format(self.__lineEnding), value, qualifier)
        elif isinstance(value, int) and value >= 0 and value <= 7:
            self.__SetHelper('LiveLocal', 'local:{}{}'.format(value, self.__lineEnding), value, qualifier)
    
    def __CallbackLiveLocal(self, match, tag):
        # PLAYLIST:([0-7])\\r(?:.+)PLAYMODE:(live|local|off)
        dataVal = {
            'Mode': str(match.group(2), 'UTF-8'),
            'Playlist': int(match.group(1))
        }
        self.WriteStatus('LiveLocal', dataVal)
        
        if self.EndpointType == 'ENC':
            if str(match.group(2), 'UTF-8') == 'off':
                txVal = False
            else:
                txVal = True
            self.WriteStatus('Tx', txVal)
    
    def SetRawIRCommand(self, value, qualifier):
        self.__SetHelper('RawIRCommand', 'sendirraw:{}{}'.format(value, self.__lineEnding), value, qualifier)
    
    def SetIRCommand(self, value, qualifier):
        self.__SetHelper('IRCommand', 'sendir:{}{}'.format(value, self.__lineEnding), value, qualifier)
    
    def SetSerialCommand(self, value, qualifier):
        self.__SetHelper('SerialCommand', 'sendser:{}{}'.format(value, self.__lineEnding), value, qualifier)
    
    def SetSerialConfig(self, value, qualifier):
        self.__SetHelper('SerialConfig',
                         'serSet:{baud},{data},{parity},{stop}{le}'.format(baud = qualifier['Baud'],
                                                                           data = qualifier['DataBits'],
                                                                           parity = qualifier['Parity'],
                                                                           stop = qualifier['Stop'],
                                                                           le = self.__lineEnding),
                         value,
                         qualifier)
    
    def __CallbackSerialConfig(self, match, tag):
        # BAUD:(\d+)\\rSNUMB:(7|8)\\rSPAR:(even|odd|none)\\rSP2S:(1|2)
        dataVal = {
            'Baud': int(match.group(1)),
            'DataBits': int(match.group(2)),
            'Parady': str(match.group(3), 'UTF-8'),
            'Stop': int(match.group(4))
        }
        self.WriteStatus('SerialConfig', dataVal)
    
    def SetTx(self, value, qualifier):
        if value is True or value == 1 or value == 'on':
            self.__SetHelper('Tx', 'txenable{}'.format(self.__lineEnding), value, qualifier)
        elif value is False or value == 0 or value == 'off':
            self.__SetHelper('Tx', 'txdisable{}'.format(self.__lineEnding), value, qualifier)
    
    def SetVidSource(self, value, qualifier):
        if value == 'auto':
            src = 'auto'
        elif value == 'HDMI' or value == 'hdmi' or value == 'hdmionly':
            src = 'hdmionly'
        elif value == 'VGA' or value == 'vga' or value == 'vgaonly':
            src = 'vgaonly'
        self.__SetHelper('VidSource', 'vidsrc:{}{}'.format(src, self.__lineEnding), value, qualifier)
        self.WriteStatus('VidSource', src) # N2300 series do not send this data with the status so we will emulate this status
    
    def SetStream(self, value, qualifier):
        self.__SetHelper('Stream', 'set:{}{}'.format(value, self.__lineEnding), value, qualifier)
    
    def __CallbackStream(self, match, tag):
        # STREAM:(\d{1,4})
        dataVal = int(match.group(1))
        self.WriteStatus('Stream', dataVal)
    
    def SetAudioStream(self, value, qualifier):
        self.__SetHelper('Stream', 'seta:{}{}'.format(value, self.__lineEnding), value, qualifier)
    
    def __CallbackAudioStream(self, match, tag):
        # STREAMAUDIO:(\d{1,4})
        dataVal = int(match.group(1))
        self.WriteStatus('AudioStream', dataVal)
    
    def SetKVMMasterIP(self, value, qualifier):
        if qualifier is not None and 'VideoFollow' in qualifier:
            if qualifier['VideoFollow'] == 1 or qualifier['VideoFollow'] is True or qualifier['VideoFollow'] == 'on':
                qualifier['VideoFollow'] = 1
            else:
                qualifier['VideoFollow'] = 0
        else:
            qualifier['VideoFollow'] = 0
        self.__SetHelper('KVMMasterIP',
                         'KVMMaster:{ip},{vf}{le}'.format(ip = value,
                                                          vf = qualifier['VideoFollow'],
                                                          le = self.__lineEnding),
                         value,
                         qualifier)
    
    def __CallbackKVMMasterIP(self, match, tag):
        # KVMMasterIP:(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})
        dataVal = str(match.group(1), 'UTF-8')
        self.WriteStatus('KVMMasterIP', dataVal)
    
    def SetVolume(self, value, qualifier):
        self.__SetHelper('Volume', 'lovol:{}{}'.format(value, self.__lineEnding), value, qualifier)
    
    def __CallbackVolume(self, match, tag):
        # LINEOUTVOL_L:(\d{1,3})\\rLINEOUTVOL_R:(\d{1,3})
        if match.group(1) == match.group(2):
            dataVal = int(match.group(1))
        else:
            dataVal = (int(match.group(1)), int(match.group(2)))
        self.WriteStatus('Volume', dataVal)
    
    def SetHDMIOutput(self, value, qualifier):
        if value is True or value == 1 or value == 'on':
            self.__SetHelper('HDMIOutput', 'hdmiOn{}'.format(self.__lineEnding), value, qualifier)
        elif value is False or value == 0 or value == 'off':
            self.__SetHelper('HDMIOutput', 'hdmiOff{}'.format(self.__lineEnding), value, qualifier)
    
    def __CallbackHDMIOutput(self, match, tag):
        # DVIOFF:(0|1)
        # Documentation seems to be wrong, DVI is used instead of HDMI
        dataVal = not bool(int(match.group(1)))
        self.WriteStatus('HDMIOutput', dataVal)
    
    def __CallbackHDMIStatus(self, match, tag):
        # DVI(?:STATUS|INPUT):(connected|disconnected)
        # Documentation seems to be wrong, DVI is used instead of HDMI
        dataVal = str(match.group(1), 'UTF-8')
        self.WriteStatus('HDMIStatus', dataVal)
    
    def SetScaler(self, value, qualifier):
        if value is True or value == 1 or value == 'on':
            self.__SetHelper('Scaler', 'scalerenable{}'.format(self.__lineEnding), value, qualifier)
        elif value is False or value == 0 or value == 'off':
            self.__SetHelper('Scaler', 'scalerdisable{}'.format(self.__lineEnding), value, qualifier)
    
    def __CallbackScaler(self, match, tag):
        # SCALERBYPASS:(on|off)
        dataVal = True if str(match.group(1), 'UTF-8') == 'off' else False
        self.WriteStatus('Scaler', dataVal)
    
    def SetScalerMode(self, value, qualifier):
        if value == 'auto' or value == '1080p59.94' or value == '1080p60' or value == '720p60' or value == '4K30' or value == '4K25':
            self.__SetHelper('ScalerMode', 'modeset:{}{}'.format(value, self.__lineEnding), value, qualifier)
        else:
            self.__SetHelper('ScalerMode', 'modeset:auto{}'.format(self.__lineEnding), 'auto', qualifier)
    
    def __CallbackScalerMode(self, match, tag):
        # MODE:(auto|1080p59\.94|1080p60|720p60|4K30|4K25)
        dataVal = str(match.group(1), 'UTF-8')
        self.WriteStatus('ScalerMode', dataVal)
    
    def SetIRPassthrough(self, value, qualifier):
        if value is True or value == 1 or value == 'on':
            self.__SetHelper('IRPassthrough', 'setSettings:irPassThroughEnable:on{}'.format(self.__lineEnding), value, qualifier)
        elif value is False or value == 0 or value == 'off':
            self.__SetHelper('IRPassthrough', 'setSettings:irPassThroughEnable:off{}'.format(self.__lineEnding), value, qualifier)
    
    def SetIRDestination(self, value, qualifier):
        self.__SetHelper('IRDestination', 'irClientIP:{}{}'.format(value, self.__lineEnding), value, qualifier)
    
    def SetVideoWall(self, value, qualifier):
        if value is True or value == 1 or value == 'on':
            self.__SetHelper('VideoWall', 'setSettings:wallEnable:on{}'.format(self.__lineEnding), value, qualifier)
        elif value is False or value == 0 or value == 'off':
            self.__SetHelper('VideoWall', 'setSettings:wallEnable:off{}'.format(self.__lineEnding), value, qualifier)
    
    def __CallbackVideoWall(self, match, tag):
        # wallEnable:(0|1)
        dataVal = bool(int(match.group(1)))
        self.WriteStatus('VideoWall', dataVal)
    
    def SetVideoWall_HorMons(self, value, qualifier):
        self.__SetHelper('VideoWall_HorMons', 
                         'setSettings:wallHorMons:{}{}'.format(value, self.__lineEnding), 
                         value, 
                         qualifier)
    
    def __CallbackVideoWall_HorMons(self, match, tag):
        # wallHorMons:(\d{1,2})
        dataVal = int(match.group(1))
        self.WriteStatus('VideoWall_HorMons', dataVal)
    
    def SetVideoWall_VerMons(self, value, qualifier):
        self.__SetHelper('VideoWall_VerMons', 
                         'setSettings:wallVerMons:{}{}'.format(value, self.__lineEnding), 
                         value, 
                         qualifier)
    
    def __CallbackVideoWall_VerMons(self, match, tag):
        # wallVerMons:(\d{1})
        dataVal = int(match.group(1))
        self.WriteStatus('VideoWall_VerMons', dataVal)
    
    def SetVideoWall_PosHor(self, value, qualifier):
        self.__SetHelper('VideoWall_PosHor', 
                         'setSettings:wallMonPosH:{}{}'.format(value, self.__lineEnding), 
                         value, 
                         qualifier)
    
    def __CallbackVideoWall_PosHor(self, match, tag):
        # wallMonPosH:(\d{1,2})
        dataVal = int(match.group(1))
        self.WriteStatus('VideoWall_PosHor', dataVal)
    
    def SetVideoWall_PosVer(self, value, qualifier):
        self.__SetHelper('VideoWall_PosVer', 
                         'setSettings:wallMonPosV:{}{}'.format(value, self.__lineEnding), 
                         value, 
                         qualifier)
    
    def __CallbackVideoWall_PosVer(self, match, tag):
        dataVal = int(match.group(1))
        self.WriteStatus('VideoWall_PosVer', dataVal)
    
    def SetVideoWall_Stretch(self, value, qualifier):
        self.__SetHelper('VideoWall_Stretch', 
                         'setSettings:wallStretch:{}{}'.format(value, self.__lineEnding), 
                         value, 
                         qualifier)
    
    def __CallbackVideoWall_Stretch(self, match, tag):
        # wallStretch:(.+)
        # documentation and realworld testing do not match
        dataVal = str(match.group(1), 'UTF-8')
        self.WriteStatus('VideoWall_Stretch', dataVal)
    
    def SetVideoWall_HShift(self, value, qualifier):
        self.__SetHelper('VideoWall_HShift', 
                         'setSettings:wallHShift:{}{}'.format(value, self.__lineEnding), 
                         value, 
                         qualifier)
    
    def SetVideoWall_VShift(self, value, qualifier):
        self.__SetHelper('VideoWall_VShift', 
                         'setSettings:wallVShift:{}{}'.format(value, self.__lineEnding), 
                         value, 
                         qualifier)
        

## -----------------------------------------------------------------------------
## End Command & Callback Functions
## -----------------------------------------------------------------------------

    def __SetHelper(self, command, commandstring, value, qualifier):
        # ProgramLog('Set {} - cmdStr: {}; val: {}; qual: {}'.format(command,
        #                                                               commandstring,
        #                                                               value,
        #                                                               qualifier))
        
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):
        # ProgramLog('Update {} - cmdStr: {}; val: {}; qual: {}'.format(command,
        #                                                               commandstring,
        #                                                               value,
        #                                                               qualifier))
        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            self.Send(commandstring)

    def __MatchError(self, match, tag):
        self.counter = 0

        ErrCode = {}

        value = ErrCode[match.group(1).decode()]
        self.Error([value])

    def OnConnected(self):

        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0


    def OnDisconnected(self):
        # ProgramLog('On Disconnect: Counter {}, ConnCount {}, ConnFlag {}'.format(self.counter, self.connectionCounter, self.connectionFlag))
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

    def __ReceiveData(self, interface, data):
        self.counter = 0
        # Handle incoming data
        self.__receiveBuffer += data
        index = 0    # Start of possible good data
        
        #check incoming data if it matched any expected data from device module
        for regexString, CurrentMatch in self.__matchStringDict.items():
            result = re.search(regexString, self.__receiveBuffer)
            #ProgramLog("Regex String: {}".format(regexString))
            if result:
                #ProgramLog("Callback: {}".format(CurrentMatch['callback']))
                if result.end() > index:
                    index = result.end() # increase index to track the end of the further match
                CurrentMatch['callback'](result, CurrentMatch['para'])
            else:
                #ProgramLog('Regex String Mismatch:\n  {}\n  {}'.format(regexString, self.__receiveBuffer))
                pass
                    
        if index: 
            # Clear out any data that has already been matched.
            self.__receiveBuffer = self.__receiveBuffer[index:]
        else:
            # In rare cases, the buffer could be filled with garbage quickly.
            # Make sure the buffer is capped.  Max buffer size set in init.
            self.__receiveBuffer = self.__receiveBuffer[-self.__maxBufferSize:]

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self.__matchStringDict:
            self.__matchStringDict[regex_string] = {'callback': callback, 'para':arg}

    def MissingCredentialsLog(self, credential_type):
        if isinstance(self, EthernetClientInterface):
            port_info = 'IP Address: {0}:{1}'.format(self.IPAddress, self.IPPort)
        else:
            return 
        ProgramLog("{0} module received a request from the device for a {1}, "
                   "but device{1} was not provided.\n Please provide a device{1} "
                   "and attempt again.\n Ex: dvInterface.device{1} = '{1}'\n Please "
                   "review the communication sheet.\n {2}"
                   .format(__name__, credential_type, port_info), 'warning') 

class EthernetClass(EthernetClientInterface, DeviceClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None, Credentials=('admin','password')):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort, Credentials)
        self.ConnectionType = 'Ethernet'
        DeviceClass.__init__(self) 
        # Check if Model belongs to a subclass       
        if len(self.Models) > 0:
            if Model not in self.Models: 
                print('Model mismatch') 
                ProgramLog('Model mismatch')              
            else:
                self.Models[Model]()

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        ProgramLog('Class Disconnect Method Called')
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()