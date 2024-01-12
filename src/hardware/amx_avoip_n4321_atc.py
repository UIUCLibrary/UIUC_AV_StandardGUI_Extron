from typing import TYPE_CHECKING
if TYPE_CHECKING: # pragma: no cover
    from uofi_gui import GUIController

from extronlib.interface import EthernetClientInterface
import re
from extronlib.system import ProgramLog

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
        
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'Tx': {'Status': {}}, # TODO
            'Rx': {'Status': {}}, # TODO
            'Stream': {'Parameters': ['Instance'], 'Status': {}}, # TODO
            'Volume': {'Parameters': ['Channel'], 'Status': {}}, # TODO
            'AudioDelay': {'Parameters': ['Instance'], 'Status': {}}, # TODO
            'Mute': {'Status': {}}, # TODO
            'Input': {'Parameters': ['Gain', 'Trim', 'SampleRate', 'PhantomPower'], 'Status': {}}, # TODO
            }  
        
        if self.Unidirectional == 'False':
            pass
        
        # Add match strings for callbacks
        # primary match and status logging callback
        self.AddMatchString(re.compile(b'SVSI_N4000:(\w+)\\rID:(\d+)\\rNAME:(.+)\\rtxName:(.+)\\rrxName:(.+)\\rMAC:([0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2})\\rIP:(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\\rNM:(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\\rGW:(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\\rIPTRIAL:(0|1)\\rIPMODE:(.+)\\rrel:(.+)\\rSWVER:(.+)\\rWEBVER:(.+)\\rUPDATE:(.+)\\rUPDTRY:(.+)\\rUPDFAILED:(.+)\\rMASTERVOL_L:(\d{0,3})\\rMASTERVOL_R:(\d{0,3})\\rHEADPHONEVOL_L:(\d{0,3})\\rHEADPHONEVOL_R:(\d{0,3})\\rLINEOUTVOL_L:(\d{0,3})\\rLINEOUTVOL_R:(\d{0,3})\\rLINEIN:(.+)\\rINPUTGAINLEFT:(\-?\d{0,2})\\rINPUTGAINRIGHT:(\-?\d{0,2})\\rPORTSD1:(no|yes)\\rUSERMCMODE:(on|off)\\rUSERMCIP:(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\\rDISABLED:(0|1)\\rMEDIASRC:(0|1)\\rOUTSTREAM:(\d{1,4})\\rTXSAMPLE:(\d+)\\rTXUNICAST:(0|1)\\rTXUNICASTIP2:(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\\rTXAUDIODELAY:(\d{1,7})\\rRXMUTE:(0|1)\\rRXDISABLED:(0|1)\\rRXMEDIASRC:(0|1)\\rRXSTREAM:(\d{1,4})\\rRXUNICAST:(0|1)\\rRXAUDIODELAY:(\d{1,7})\\rDM_A_EN:(on|off)\\rDM_A_IEN:(on|off)\\rDM_A_SRC:(\d)\\rDM_CGAIN:(\-?\d{0,2})\\rDM_FGAIN:(\-?\d{0,2})\\rDM_SLGAIN:(\-?\d{0,2})\\rDM_SRGAIN:(\-?\d{0,2})\\rAGAINL:(\-?\d{0,2})\\rAGAINR:(\-?\d{0,2})\\rMEDIAPORT0:(on|off)\\rMEDIAPORT1:(on|off)\\rrelay1State:(open|closed)\\rrelay2State:(open|closed)\\rrelayInterlock:(on|off)\\rphantomPower:(on|off)\\rHTTPS:(on|off)\\rgpiHighEvntDly:(\-?\d{0,4})\\rgpiLowEvntDly:(\-?\d{0,4})\\rgpiLevel:([hH]igh|[lL]ow)\\rGRATARP:(on|off)\\rGRATARPINT:(\d{1,4})\\rUNSOLSTATUS:(on|off)\\rUNSOLSTATUSINT:(\d{1,4})\\rDIVASEN:(\d{1,4})\\rDIVASIP:(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\\rdiscoveryIP:(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\\renableDiscoveryPackets:(on|off)\\rdiscoveryIntervalSec:(\d{1,4})\\rdiscoveryPort:(\d{1,5})\\rchassisID:mac ([0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2})\\rsysName:(.+)\\rsysDescr:(.+?)\\rportID:(.+?)\\rportDescr:(.+)\\rstreamTone:(on|off)\\rplayTone:(on|off)\\rtonePct:(\d{1,3})\\rtoneFreq:(\d{1,5})\\rleftTone:(on|off)\\rrightTone:(on|off)\\r(?:.+$|toneType:(.+)\\r)'),
                            self.__CallbackDeviceStatus,
                            None)
        # submatches for specific commands
        self.AddMatchString(re.compile(b'DISABLED:(0|1)'),
                            self.__CallbackTx,
                            None)
        self.AddMatchString(re.compile(b'RXDISABLED:(0|1)'),
                            self.__CallbackRx,
                            None)
        self.AddMatchString(re.compile(b'OUTSTREAM:(\d{1,4})'),
                            self.__CallbackStream,
                            {'Instance': 'Tx'})
        self.AddMatchString(re.compile(b'RXSTREAM:(\d{1,4})'),
                            self.__CallbackStream,
                            {'Instance': 'Rx'})
        self.AddMatchString(re.compile(b'MASTERVOL_L:(\d{0,3})\\rMASTERVOL_R:(\d{0,3})\\rHEADPHONEVOL_L:(\d{0,3})\\rHEADPHONEVOL_R:(\d{0,3})\\rLINEOUTVOL_L:(\d{0,3})\\rLINEOUTVOL_R:(\d{0,3})'),
                            self.__CallbackVolume,
                            None)
        self.AddMatchString(re.compile(b'TXAUDIODELAY:(\d{1,4})'),
                            self.__CallbackAudioDelay,
                            {'Instance': 'Tx'})
        self.AddMatchString(re.compile(b'RXAUDIODELAY:(\d{1,4})'),
                            self.__CallbackAudioDelay,
                            {'Instance': 'Rx'})
        self.AddMatchString(re.compile(b'RXMUTE:(0|1)'),
                            self.__CallbackMute,
                            None)
        self.AddMatchString(re.compile(b'INPUTGAINLEFT:(\-?\d{0,2})\\rINPUTGAINRIGHT:(\-?\d{0,2})'),
                            self.__CallbackInput,
                            {'Property': 'Trim'})
        self.AddMatchString(re.compile(b'TXSAMPLE:(\d+)'),
                            self.__CallbackInput,
                            {'Property': 'SampleRate'})
        self.AddMatchString(re.compile(b'AGAINL:(\-?\d{0,2})\\rAGAINR:(\-?\d{0,2})'),
                            self.__CallbackInput,
                            {'Property': 'Gain'})
        self.AddMatchString(re.compile(b'phantomPower:(on|off)'),
                            self.__CallbackInput,
                            {'Property': 'PhantomPower'})
        
        self.UpdateTx = self.UpdateDeviceStatus
        self.UpdateRx = self.UpdateDeviceStatus
        self.UpdateStream = self.UpdateDeviceStatus
        self.UpdateVolume = self.UpdateDeviceStatus
        self.UpdateAudioDelay = self.UpdateDeviceStatus
        self.UpdateMute = self.UpdateDeviceStatus
        self.UpdatePhantomPower = self.UpdateDeviceStatus
        self.UpdateInput = self.UpdateDeviceStatus

## -----------------------------------------------------------------------------
## Start Model Definitions
## -----------------------------------------------------------------------------

## -----------------------------------------------------------------------------
## End Model Definitions
## =============================================================================
## Start Command & Callback Functions
## -----------------------------------------------------------------------------

    def UpdateDeviceStatus(self, value, qualifier):
        self.__UpdateHelper('DeviceStatus', 'getStatus{}'.format(self.__lineEnding), value, qualifier)
    
    def __CallbackDeviceStatus(self, match, tag):
        #1# SVSI_N4000:(\w+)
        #2# ID:(\d+)
        #3# NAME:(.+)
        #4# txName:(.+)
        #5# rxName:(.+)
        #6# MAC:([0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2})
        #7# IP:(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})
        #8# NM:(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})
        #9# GW:(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})
        #10# IPTRIAL:(0|1)
        #11# IPMODE:(.+)
        #12# rel:(.+)
        #13# SWVER:(.+)
        #14# WEBVER:(.+)
        #15# UPDATE:(.+)
        #16# UPDTRY:(.+)
        #17# UPDFAILED:(.+)
        #18# MASTERVOL_L:(\d{0,3})
        #19# MASTERVOL_R:(\d{0,3})
        #20# HEADPHONEVOL_L:(\d{0,3})
        #21# HEADPHONEVOL_R:(\d{0,3})
        #22# LINEOUTVOL_L:(\d{0,3})
        #23# LINEOUTVOL_R:(\d{0,3})
        #24# LINEIN:(.+)
        #25# INPUTGAINLEFT:(\-?\d{0,2})
        #26# INPUTGAINRIGHT:(\-?\d{0,2})
        #27# PORTSD1:(no|yes)
        #28# USERMCMODE:(on|off)
        #29# USERMCIP:(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})
        #30# DISABLED:(0|1)
        #31# MEDIASRC:(0|1)
        #32# OUTSTREAM:(\d{1,4})
        #33# TXSAMPLE:(\d+)
        #34# TXUNICAST:(0|1)
        #35# TXUNICASTIP2:(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})
        #36# TXAUDIODELAY:(\d{1,4})
        #37# RXMUTE:(0|1)
        #38# RXDISABLED:(0|1)
        #39# RXMEDIASRC:(0|1)
        #40# RXSTREAM:(\d{1,4})
        #41# RXUNICAST:(0|1)
        #42# RXAUDIODELAY:(\d{1,4})
        #43# DM_A_EN:(on|off)
        #44# DM_A_IEN:(on|off)
        #45# DM_A_SRC:(\d)
        #46# DM_CGAIN:(\-?\d{0,2})
        #47# DM_FGAIN:(\-?\d{0,2})
        #48# DM_SLGAIN:(\-?\d{0,2})
        #49# DM_SRGAIN:(\-?\d{0,2})
        #50# AGAINL:(\-?\d{0,2})
        #51# AGAINR:(\-?\d{0,2})
        #52# MEDIAPORT0:(on|off)
        #53# MEDIAPORT1:(on|off)
        #54# relay1State:(open|closed)
        #55# relay2State:(open|closed)
        #56# relayInterlock:(on|off)
        #57# phantomPower:(on|off)
        #58# HTTPS:(on|off)
        #59# gpiHighEvntDly:(\-?\d{0,4}) - ignored
        #60# gpiLowEvntDly:(\-?\d{0,4}) - ignored
        #61# gpiLevel:([hH]igh|[lL]ow) - ignored
        #62# GRATARP:(on|off) - ignored
        #63# GRATARPINT:(\d{1,4}) - ignored
        #64# UNSOLSTATUS:(on|off) - ignored
        #65# UNSOLSTATUSINT:(\d{1,4}) - ignored
        #66# DIVASEN:(\d{1,4}) - ignored
        #67# DIVASIP:(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) - ignored
        #68# discoveryIP:(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) - ignored
        #69# enableDiscoveryPackets:(on|off) - ignored
        #70# discoveryIntervalSec:(\d{1,4}) - ignored
        #71# discoveryPort:(\d{1,5}) - ignored
        #72# chassisID:mac ([0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}) - ignored
        #73# sysName:(.+) - ignored
        #74# sysDescr:(.+) - ignored
        #75# portID:mac ([0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}) - ignored
        #76# portDescr:(.+) - ignored
        #77# streamTone:(on|off)
        #78# playTone:(on|off)
        #79# tonePct:(\d{1,3})
        #80# toneFreq:(\d{1,5})
        #81# leftTone:(on|off)
        #82# rightTone:(on|off)
        #83# toneType:(.+)
# Note: for some reason TXUNICASTIP1 isn't included by default, this may cause future problems if using unicast transmit

        statusDict = {
            'Name': str(match.group(3), 'UTF-8'),
            'SerialNumber': str(match.group(1), 'UTF-8'),
            'DeviceNetwork': {
                'MAC': str(match.group(6), 'UTF-8'),
                'IP': str(match.group(7), 'UTF-8'),
                'Netmask': str(match.group(8), 'UTF-8'),
                'Gateway': str(match.group(9), 'UTF-8'),
                'IPMode': str(match.group(11), 'UTF-8'),
                'IPTrailMode': bool(int(match.group(10)))
            },
            'ID': str(match.group(2), 'UTF-8'),
            'Firmware': {
                'Version': str(match.group(12), 'UTF-8'),
                'Date': str(match.group(13), 'UTF-8'),
                'WebVersion': str(match.group(14), 'UTF-8'),
                'Update': {
                    'Updating': bool(int(match.group(15))),
                    'Tries': int(match.group(16)),
                    'Fails': int(match.group(17))
                }
            },
            'MulticastTraffic': (
                (True if str(match.group(52), 'UTF-8') == 'on' else False),
                (True if str(match.group(53), 'UTF-8') == 'on' else False)
            ),
            "P1Disabled": (False if str(match.group(27), 'UTF-8') == 'yes' else True),
            'UserMulticast': (True if str(match.group(28), 'UTF-8') == 'on' else False),
            'UserMulticastAddr': str(match.group(29), 'UTF-8'),
            'MutlicastTraffic': (
                (True if str(match.group(52), 'UTF-8') == 'on' else False),
                (True if str(match.group(53), 'UTF-8') == 'on' else False)
            ),
            'InputAudio': {
                'Type': str(match.group(24), 'UTF-8'),
                'Gain': (int(match.group(50)), int(match.group(51))),
                'Trim': (int(match.group(25)), int(match.group(26))),
                'PhantomPower': (True if str(match.group(57), 'UTF-8') == 'on' else False)
            },
            'OutputAudio': {
                'Master': (int(match.group(18)), int(match.group(19))),
                'Headphone': (int(match.group(20)), int(match.group(21))),
                'Lineout': (int(match.group(22)), int(match.group(23))),
                'Downmix': {
                    'Enabled': (True if str(match.group(77), 'UTF-8') == 'on' else False),
                    'Source': int(match.group(45)),
                    'CenterGain': int(match.group(46)),
                    'FrontGain': int(match.group(47)),
                    'SurroundGain': (int(match.group(48)), int(match.group(49)))
                }
            },
            'Transmit': {
                'Name': str(match.group(4), 'UTF-8'),
                'Enabled': not bool(int(match.group(30))),
                'MediaSource': bool(int(match.group(31))),
                'Stream': int(match.group(32)),
                'AudioSampleRate': int(match.group(33)),
                'Unicast': {
                    'Enabled': bool(int(match.group(34))),
                    'IP1': None,
                    'IP2': str(match.group(35), 'UTF-8')
                },
                'Delay': int(match.group(36))
            },
            'Receive': {
                'Name': str(match.group(5), 'UTF-8'),
                'Enabled': not bool(int(match.group(38))),
                'Mute': bool(int(match.group(37))),
                'MediaSource': bool(int(match.group(39))),
                'Stream': int(match.group(40)),
                'Unicast': bool(int(match.group(41))),
                'Delay': int(match.group(42))
            },
            'Relay': {
                'Interlock': (True if str(match.group(56)) == 'on' else False),
                'State': (str(match.group(54), 'UTF-8'), str(match.group(55), 'UTF-8'))
            },
            'HTTPS': (True if str(match.group(58)) == 'on' else False),
            'TestGen': {
                'SteamEnabled': (True if str(match.group(77), 'UTF-8') == 'on' else False),
                'LineEnabled': (True if str(match.group(78), 'UTF-8') == 'on' else False),
                'LeftChEnabled': (True if str(match.group(81), 'UTF-8') == 'on' else False),
                'RightChEnabled': (True if str(match.group(82), 'UTF-8') == 'on' else False),
                'Type': None,
                'ToneFreq': int(match.group(80)),
                'Volume': int(match.group(79))
            }
        }
        if match.lastindex == 83:
            statusDict['TestGen']['Type'] = str(match.group(83), 'UTF-8')
        # ProgramLog("ATC Status: {}".format(statusDict))
        self.WriteStatus('DeviceStatus', statusDict)
    
    def SetTx(self, value, qualifier):
        if value in [True, 1, 'on', 'On', 'ON', 'Enable']:
            self.__SetHelper('Tx', 'txenable{}'.format(self.__lineEnding), value, None)
        elif value in [False, 0, 'off', 'Off', 'OFF', 'Disable']:
            self.__SetHelper('Tx', 'txdisable{}'.format(self.__lineEnding), value, None)
    
    def __CallbackTx(self, match, tag):
        status = not bool(int(match.group(1)))
        self.WriteStatus('Tx', status)
    
    def SetRx(self, value, qualifier):
        if value in [True, 1, 'on', 'On', 'ON', 'Enable']:
            self.__SetHelper('Rx', 'rxenable{}'.format(self.__lineEnding), value, qualifier)
        elif value in [False, 0, 'off', 'Off', 'OFF', 'Disable']:
            self.__SetHelper('Rx', 'rxdisable{}'.format(self.__lineEnding), value, qualifier)
    
    def __CallbackRx(self, match, tag):
        status = not bool(int(match.group(1)))
        self.WriteStatus('Rx', status)
    
    def SetStream(self, value, qualifier):
        instance = qualifier.get('Instance', None)
        
        if instance is not None:
            if instance == 'Tx':
                self.__SetHelper('Stream', 'setSettings:setStream:{}{}'.format(value, self.__lineEnding), value, qualifier)
            elif instance == 'Rx':
                self.__SetHelper('Stream', 'seta:stream:{}{}'.format(value, self.__lineEnding), value, qualifier)
            else:
                raise ValueError('Instance must be one of "Tx" or "Rx"')
        else:
            raise AttributeError('No Instance key provided in qualifier dict')

    def __CallbackStream(self, match, tag):
        self.WriteStatus('Stream', int(match.group(1)), tag)
    
    def SetVolume(self, value, qualifier):
        channel = qualifier.get('Channel', None)
        if channel is None:
            raise AttributeError('Channel must be included in qualifer dict')
        
        if isinstance(value, (int, float)):
            if value >= 0 and value <= 100:
                vol = (value, value)
            else:
                raise ValueError('Volume must be 0-100')
        elif isinstance(value, tuple):
            if len(value) == 2 and \
                (isinstance(value[0], (int, float)) and value[0] >= 0 and value[0] <= 100) and \
                (isinstance(value[1], (int, float)) and value[1] >= 0 and value[1] <= 100):
                vol = value
            else: 
                raise ValueError('Volume tuple must be 2 int/float objects 0-100')
        else:
            raise TypeError('Either an int/float or a volume tuple must be provided')
        
        if channel == 'Master':
            self.__SetHelper('Volume',
                             'mastervolleft:{volL}{le}mastervolright:{volR}{le}'.format(volL=vol[0], 
                                                                                        volR=vol[1],
                                                                                        le=self.__lineEnding),
                             value,
                             qualifier)
        elif channel == 'Headphones':
            self.__SetHelper('Volume',
                             'hpvolleft:{volL}{le}hpvolright:{volR}{le}'.format(volL=vol[0], 
                                                                                volR=vol[1],
                                                                                le=self.__lineEnding),
                             value,
                             qualifier)
        elif channel == 'Lineout':
            self.__SetHelper('Volume',
                             'lovolleft:{volL}{le}lovolright:{volR}{le}'.format(volL=vol[0], 
                                                                                volR=vol[1],
                                                                                le=self.__lineEnding),
                             value,
                             qualifier)
    
    def __CallbackVolume(self, match, tag):
        #1# MASTERVOL_L:(\d{0,3})
        #2# MASTERVOL_R:(\d{0,3})
        #3# HEADPHONEVOL_L:(\d{0,3})
        #4# HEADPHONEVOL_R:(\d{0,3})
        #5# LINEOUTVOL_L:(\d{0,3})
        #6# LINEOUTVOL_R:(\d{0,3})
        self.WriteStatus('Volume', (int(match.group(1)), int(match.group(2))), {'Channel': 'Master'})
        self.WriteStatus('Volume', (int(match.group(3)), int(match.group(4))), {'Channel': 'Headphones'})
        self.WriteStatus('Volume', (int(match.group(5)), int(match.group(6))), {'Channel': 'Lineout'})
    
    def SetAudioDelay(self, value, qualifier):
        instance = qualifier.get('Instance', None)
        if not isinstance(value, int) or (value < 0):
            raise ValueError('Value must be a non-negative int')
        if instance is not None:
            if instance == 'Tx':
                if value > 2000000:
                    raise ValueError('Transmit value must be 2000000ms or less')
                self.__SetHelper('Stream', 'setSettings:audioDelay:{}{}'.format(value, self.__lineEnding), value, qualifier)
            elif instance == 'Rx':
                if value > 1000000:
                    raise ValueError('Receive value must be 1000000ms or less')
                self.__SetHelper('Stream', 'setSettings:outAudioDelay:{}{}'.format(value, self.__lineEnding), value, qualifier)
            else:
                raise ValueError('Instance must be one of "Tx" or "Rx"')
        else:
            raise AttributeError('No Instance key provided in qualifier dict')
    
    def __CallbackAudioDelay(self, match, tag):
        self.WriteStatus('AudioDelay', int(match.group(1)), tag)
    
    def SetMute(self, value, qualifier):
        if value in [True, 1, 'on', 'On', 'ON', 'Enable']:
            self.__SetHelper('Mute', 'mute{}'.format(self.__lineEnding), value, qualifier)
        elif value in [False, 0, 'off', 'Off', 'OFF', 'Disable']:
            self.__SetHelper('Mute', 'unmute{}'.format(self.__lineEnding), value, qualifier)
    
    def __CallbackMute(self, match, tag):
        self.WriteStatus('Mute', bool(int(match.group(1))))
    
    def SetInput(self, value, qualifier):
        property = qualifier.get('Property', None)
        trimList = [0, -1.5, -3, -4.5, -6, -7.5, -9, -10.5, -12]
        srList = [32000, 44100, 48000]
        
        if property is None:
            raise ValueError('Property must be one of Gain, Trim, SampleRate, or PhantomPower')
        
        if property in ['Gain', 'Trim']:
            if isinstance(value, int):
                if property == 'Trim' and value not in trimList:
                    raise ValueError('Trim must be one of {}'.format(trimList))
                setData = (value, value)
            elif isinstance(value, tuple) and len(value) == 2 and isinstance(value[0], int) and isinstance(value[1], int):
                if property == 'Trim' and (value[0] not in trimList or value[1] not in trimList):
                    raise ValueError('Trim must be one of {}'.format(trimList))
                setData = value
                
            if property == 'Gain':
                setCmd = 'setSettings:adcLeftGain:{gainL}{le}setSettings:adcRightGain:{gainR}{le}'.format(gainL = setData[0], gainR = setData[1], le = self.__lineEnding)
            elif property == 'Trim':
                setCmd = 'setSettings:inputGainLeft:{trimL}{le}setSettings:inputGainRight:{trimR}{le}'.format(trimL = setData[0], trimR = setData[1], le = self.__lineEnding)
        
        elif property == 'SampleRate':
            if not isinstance(value, int) or value not in srList:
                raise ValueError("SampleRate must be one of 32000, 44100, 48000")
            setData = value
            setCmd = 'setSettings:sample:{}{}'.format(setData, self.__lineEnding)
        
        elif property == 'PhantomPower':
            if value in [True, 1, 'On', 'on', 'ON', 'Enable']:
                setData = 'on'
            else:
                setData = 'off'
            setCmd = 'setSettings:phantomPower:{}{}'.format(setData, self.__lineEnding)
            
        self.__SetHelper('Input', setCmd, value, qualifier)
        
    
    def __CallbackInput(self, match, tag):
        property = tag.get('Property', None)
        
        if property in ['Gain', 'Trim']:
            self.WriteStatus('Input', (int(match.group(1)), int(match.group(2))), tag)
        elif property == 'SampleRate':
            self.WriteStatus('Input', int(match.group(1)), tag)
        elif property == 'PhantomPower':
            self.WriteStatus('Input', True if str(match.group(1), 'UTF-8') == 'on' else False, tag)

## -----------------------------------------------------------------------------
## End Command & Callback Functions
## -----------------------------------------------------------------------------

    def __SetHelper(self, command, commandstring, value, qualifier):
        # ProgramLog('Set {} - cmdStr: {}; val: {}; qual: {}'.format(command,
        #                                                               commandstring,
        #                                                               value,
        #                                                               qualifier))
        
        # self.Debug = True

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
            except:
                return None
        else:
            raise KeyError('Invalid command for ReadStatus: ' + command)

    def __ReceiveData(self, interface, data):
        self.counter = 0
        # Handle incoming data
        self.__receiveBuffer += data
        index = 0    # Start of possible good data
        
        # ProgramLog('SVSI N4321 Buffer Length: {}'.format(len(self.__receiveBuffer)), 'info')
        
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
                # ProgramLog('Regex String Mismatch:\n  {}\n  {}'.format(regexString, self.__receiveBuffer))
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

    def __init__(self, GUIHost: 'GUIController', Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None, Credentials=('admin','password')):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort, Credentials)
        self.ConnectionType = 'Ethernet'
        self.GUIHost = GUIHost
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