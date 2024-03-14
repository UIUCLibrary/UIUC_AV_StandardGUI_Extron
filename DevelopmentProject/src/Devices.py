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
if TYPE_CHECKING:                                                               # pragma: no cover
    pass

#### Python imports
import json

#### Extron Library Imports

#### Project imports
from modules.project.Collections import DeviceCollection
from modules.project.PrimitiveObjects import DictObj, Layout
from ui.Feedback.Device import (DSP_GainHandler,
                                DSP_MuteHandler, 
                                DSP_LevelHandler,
                                DSP_PhantomHandler,
                                Display_AudioMuteStatusHandler,
                                Display_PowerStatusHandler,
                                Display_VolumeStatusHandler,
                                # Mic_MuteHandler,
                                WPD_StatusHandler,
                                VMX_InputHandler,
                                VMX_OutputHandler)
# TODO: load this in a more secure way
import secrets_devices
import Variables

## End Imports -----------------------------------------------------------------

# Pull Control System Devices Data from Project File
__ProjectFile = open('/var/nortxe/.gcp/{}'.format(Variables.PROJECT_FILE))
__ProjectData = json.load(__ProjectFile)
__ProjectObj= DictObj(__ProjectData)
ControlDevices = __ProjectObj.devices

# Create empty DeviceCollection to populate with system devices below
SystemDevices = DeviceCollection()

################################################################################
################################################################################
## Source Documentation                                                       ##
## -------------------------------------------------------------------------- ##
##                                                                            ##
##  Icon Map                                                                  ##
##    0 - no source                                                           ##
##    1 - HDMI                                                                ##
##    2 - PC                                                                  ##
##    3 - Wireless                                                            ##
##    4 - Camera                                                              ##
##    5 - Document Camera                                                     ##
##    6 - BluRay                                                              ##
##                                                                            ##
## ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ ##
## Destination Documentation                                                  ##
## -------------------------------------------------------------------------- ##
##                                                                            ##
##  Destination Types                                                         ##
##    proj     - Projector with uncontrolled screen                           ##
##    proj+scn - Projector with controlled screen                             ##
##    mon      - Large format monitor                                         ##
##    conf     - Instructor confidence monitor (no power control)             ##
##    c-conf   - Instructor confidence monitor (with display control)         ##
##                                                                            ##
## ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ ##
## Camera Documentation                                                       ##
## -------------------------------------------------------------------------- ##
##                                                                            ##
## ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ ##
## Microphone Documentation                                                   ##
## -------------------------------------------------------------------------- ##
##                                                                            ##
## ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ ##
## Screen Documentation                                                       ##
## -------------------------------------------------------------------------- ##
##                                                                            ##
## ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ ##
## Light Documentation                                                        ##
## -------------------------------------------------------------------------- ##
##                                                                            ##
## ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ ##
## Shade Documentation                                                        ##
## -------------------------------------------------------------------------- ##
##                                                                            ##
################################################################################
################################################################################
## ADD DEVICES BELOW                                                          ##
## VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV ##

# PC001 - Room PC
SystemDevices.AddNewDevice(
    **{
        'Id': 'PC001',
        'Name': 'Room PC',
        'Manufacturer': 'Lenovo',
        'Model': 'M70Q',
        'Interface': {
            'module': 'uofi_pc_generic',
            'interface_class': 'PCClass',
            'interface_configuration': {
                'host': 'pc001'
            }
        },
        'Subscriptions': [],
        'Polling': [],
        'Options': {
            'Source': {
                'icon': 2,
                'input': 1,
                # 'alert': 'Ensure the PC is awake',
                'srcCtl': 'PC',
                'advSrcCtl': None
            }
        }
    }
)

# WPD001 - Mersive Solstice
SystemDevices.AddNewDevice(
    **{
        'Id': 'WPD001',
        'Name': 'Wireless',
        'Manufacturer': 'Mersive',
        'Model': 'Solstice Pod Gen 3',
        'Interface': {
            'module': 'mersive_solstice_pod',
            'interface_class': 'RESTClass',
            'interface_configuration': {
                'host': 'mainlib019c-wpd001.library.illinois.edu',
                'devicePassword': secrets_devices.mersive_password,
            },
        },
        'Subscriptions': [],
        'Polling': [
            {
                'command': 'PodStatus',
                'callback': WPD_StatusHandler,
                'active_int': 10,
                'inactive_int': 600,
            }
        ],
        'Options':
            {
                'Source': {
                    'icon': 3,
                    'input': 2,
                    # 'alert': 'Contact Library IT for Assistance with this Wireless Device.',
                    'srcCtl': 'WPD',
                    'advSrcCtl': 'WPD'
                }
        }
    }
)

# MON001 - Confidence Monitor
SystemDevices.AddNewDevice(
    **{
        'Id': 'MON001',
        'Name': 'Confidence Monitor',
        'Manufacturer': 'TBD',
        'Model': 'TBD',
        'Interface': None,
        'Subscriptions': None,
        'Polling': None,
        'Options': {
            'Destination': {
                'output': 1,
                'destType': 'conf',
                'groupWrkSrc': 'WPD001',
                'advLayout': Layout(row=0, col=1),
                'confFollow': 'MON002'
            }
        }
    }
)


# MON002 - Room Monitor
SystemDevices.AddNewDevice(
    **{
        'Id': 'MON002',
        'Name': 'Room Monitor',
        'Manufacturer': 'SharpNEC',
        'Model': 'LC-52LE64OU',
        'Interface':
        {
            'module': 'shrp_display_LC_xxC6400U_xxLE640U_xxLE633U_v1_0_1_1',
            'interface_class': 'SerialOverEthernetClass',
            'ConnectionHandler': {
                'keepAliveQuery': 'AspectRatio',
                'DisconnectLimit': 5,
                'pollFrequency': 60
            },
            'interface_configuration': {
                'Hostname': 'mainlib019c-dec002.library.illinois.edu',
                'IPPort': 50004,
                'Model': 'LC-52LE64OU'
            }
        },
        'Subscriptions': [],
        'Polling':
        [
            {
                'command': 'Power',
                'callback': Display_PowerStatusHandler,
                'active_int': 10,
                'inactive_int': 30
            },
            {
                'command': 'AudioMute',
                'callback': Display_AudioMuteStatusHandler,
                'active_int': 10,
                'inactive_int': 600
            },
            {
                'command': 'Volume',
                'callback': Display_VolumeStatusHandler,
                'active_int': 10,
                'inactive_int': 600
            }
        ],
        'Options':
        {
            'PowerCommand':
            {
                'command': 'Power',
            },
            'SourceCommand':
            {
                'command': 'Input',
                'value': 'HDMI 1'
            },
            'MuteCommand':
            {
                'command': 'AudioMute',
            },
            'VolumeCommand':
            {
                'command': 'Volume'
            },
            'VolumeRange': (0, 100),
            'Destination': {
                'output': 2,
                'destType': 'mon',
                'groupWrkSrc': 'WPD001',
                'advLayout': Layout(row=1, col=0)
            }
        }
    }
)

# DSP001 - Biamp TesiraFORTE VT4 AVB
SystemDevices.AddNewDevice(
    **{
        'Id': 'DSP001',
        'Name': 'DSP',
        'Manufacturer': 'Biamp',
        'Model': 'TesiraFORTE AI AVB',
        'Interface':
        {
            'module': 'biam_dsp_TesiraSeries_v1_15_1_0',
            'interface_class': 'SSHClass',
            'ConnectionHandler': {
                'keepAliveQuery': 'VerboseMode',
                'DisconnectLimit': 5,
                'pollFrequency': 20
            },
            'interface_configuration': {
                'Hostname': 'mainlib019c-dsp001.library.illinois.edu',
                'IPPort': 22,
                'Credentials': ('admin', secrets_devices.biamp_password)
            }
        },
        'Subscriptions': [],
        'Polling':
        [
            {
                'command': 'LevelControl',
                'qualifier': {'Instance Tag': 'ProgLevel', 'Channel': '1'},
                'callback': DSP_LevelHandler,
                'tag': ('prog',),
                'active_int': 30,
                'inactive_int': 120,
            },
            {
                'command': 'LevelControl',
                'qualifier': {'Instance Tag': 'Mic1Level', 'Channel': '1'},
                'callback': DSP_LevelHandler,
                'tag': ('mics', '1'),
                'active_int': 30,
                'inactive_int': 120,
            },
            {
                'command': 'LevelControl',
                'qualifier': {'Instance Tag': 'Mic2Level', 'Channel': '1'},
                'callback': DSP_LevelHandler,
                'tag': ('mics', '2'),
                'active_int': 30,
                'inactive_int': 120,
            },
            {
                'command': 'MuteControl',
                'qualifier': {'Instance Tag': 'ProgLevel', 'Channel': '1'},
                'callback': DSP_MuteHandler,
                'tag': ('prog',),
                'active_int': 30,
                'inactive_int': 120,
            },
            {
                'command': 'MuteControl',
                'qualifier': {'Instance Tag': 'Mic1Level', 'Channel': '1'},
                'callback': DSP_MuteHandler,
                'tag': ('mics', '1'),
                'active_int': 30,
                'inactive_int': 120,
            },
            {
                'command': 'AECGain',
                'qualifier': [
                    {'Instance Tag': 'AecInput1', 'Channel': '1'},
                    {'Instance Tag': 'AecInput1', 'Channel': '2'},
                    {'Instance Tag': 'AecInput1', 'Channel': '3'},
                    {'Instance Tag': 'AecInput1', 'Channel': '4'}
                ],
                'callback': DSP_GainHandler,
                'active_int': 30,
                'inactive_int': 120
            },
            {
                'command': 'AECPhantomPower',
                'qualifier': [
                    {'Instance Tag': 'AecInput1', 'Channel': '1'},
                    {'Instance Tag': 'AecInput1', 'Channel': '2'},
                    {'Instance Tag': 'AecInput1', 'Channel': '3'},
                    {'Instance Tag': 'AecInput1', 'Channel': '4'}
                ],
                'callback': DSP_PhantomHandler,
                'active_int': 60,
                'inactive_int': 600
            }
        ],
        'Options':
        {
            'Program':
            {
                'Range': (-36, 12),
                'Step': 1,
                'StartUp': 0
            },
            'ProgramMuteCommand':
            {
                'command': 'MuteControl',
                'qualifier': {'Instance Tag': 'ProgLevel', 'Channel': '1'}
            },
            'ProgramLevelCommand':
            {
                'command': 'LevelControl',
                'qualifier': {'Instance Tag': 'ProgLevel', 'Channel': '1'}
            },
            'Mic1MuteCommand':
            {
                'command': 'MuteControl',
                'qualifier': {'Instance Tag': 'Mic1Level', 'Channel': '1'}
            },
            'Mic1LevelCommand':
            {
                'command': 'LevelControl',
                'qualifier': {'Instance Tag': 'Mic1Level', 'Channel': '1'}
            },
            'Mic2LevelCommand':
            {
                'command': 'LevelControl',
                'qualifier': {'Instance Tag': 'Mic2Level', 'Channel': '1'}
            },
            'InputControls':
            [
                {
                    'Name': 'Program L',
                    'Block': 'AecInput1',
                    'Channel': '1',
                    'GainCommand': 'AECGain',
                    'PhantomCommand': 'AECPhantomPower'
                },
                {
                    'Name': 'Program R',
                    'Block': 'AecInput1',
                    'Channel': '2',
                    'GainCommand': 'AECGain',
                    'PhantomCommand': 'AECPhantomPower'
                },
                {
                    'Name': 'Mic - RF001',
                    'Block': 'AecInput1',
                    'Channel': '3',
                    'GainCommand': 'AECGain',
                    'PhantomCommand': 'AECPhantomPower'
                },
                {
                    'Name': 'Unused Input',
                    'Block': 'AecInput1',
                    'Channel': '4',
                    'GainCommand': 'AECGain',
                    'PhantomCommand': 'AECPhantomPower'
                },
            ]
        }
    }
)

# CAM001 - PTZOptics 12X-NDI
SystemDevices.AddNewDevice(
    **{
        'Id': 'CAM001',
        'Name': 'Conference Camera',
        'Manufacturer': 'Huddle Cam',
        'Model': 'HCX10X-SV',
        'Interface':
        {
            'module': 'vsca_camera_Visca_v1_0_1_2',
            'interface_class': 'SerialClass',
            'interface_configuration': {
                'Host': 'CTL001',
                'Port': 'COM1',
            }
        },
        'Subscriptions': [],
        'Polling':
        [
            {
                'command': 'Power',
                'active_int': 30,
                'inactive_int': 600
            }
        ],
        'Options':
        {
            'PTCommand':
            {
                'command': 'PanTilt',
                'qualifier': {'Pan Speed': 5, 'Tilt Speed': 5},
            },
            'ZCommand':
            {
                'command': 'Zoom',
                'qualifier': {'Zoom Speed': 2},
            },
            'PresetSaveCommand':
            {
                'command': 'PresetSave'
            },
            'PresetRecallCommand':
            {
                'command': 'PresetRecall'
            },
            'Presets': {},
            'Camera': {
                
            }
        }
    }
)

# DEC001 - AMX N2300 Decoder
SystemDevices.AddNewDevice(
    **{
        'Id': 'DEC001',
        'Name': 'Conf. Mon. Decoder',
        'Manufacturer': 'AMX',
        'Model': 'NMX-DEC-N2322',
        'Interface':
        {
            'module': 'amx_avoip_n2300_series',
            'interface_class': 'EthernetClass',
            'ConnectionHandler': {
                'keepAliveQuery': 'DeviceStatus',
                'DisconnectLimit': 5,
                'pollFrequency': 60
            },
            'interface_configuration': {
                'Hostname': 'mainlib019c-dec001.library.illinois.edu',
                'IPPort': 50002,
                'Model': 'NMX-DEC-N2322'
            }
        },
        'Subscriptions': [],
        'Polling': [],
        'Options': {
            'MatrixAssignment': 'VMX001',
            'MatrixOutput': 1
        }
    }
)

# DEC002 - AMX N2300 Decoder
SystemDevices.AddNewDevice(
    **{
        'Id': 'DEC002',
        'Name': 'Room Mon. Decoder',
        'Manufacturer': 'AMX',
        'Model': 'NMX-DEC-N2322',
        'Interface':
        {
            'module': 'amx_avoip_n2300_series',
            'interface_class': 'EthernetClass',
            'ConnectionHandler': {
                'keepAliveQuery': 'DeviceStatus',
                'DisconnectLimit': 5,
                'pollFrequency': 60
            },
            'interface_configuration': {
                'Hostname': 'mainlib019c-dec002.library.illinois.edu',
                'IPPort': 50002,
                'Model': 'NMX-DEC-N2322'  # TODO: skip this duplication
            }
        },
        'Subscriptions': [],
        'Polling': [],
        'Options': {
            'MatrixAssignment': 'VMX001',
            'MatrixOutput': 2
        }
    }
)

# ENC001 - AMX N2300 Encoder
SystemDevices.AddNewDevice(
    **{
        'Id': 'ENC001',
        'Name': 'PC Encoder',
        'Manufacturer': 'AMX',
        'Model': 'NMX-ENC-N2312',
        'Interface':
        {
            'module': 'amx_avoip_n2300_series',
            'interface_class': 'EthernetClass',
            'ConnectionHandler': {
                'keepAliveQuery': 'DeviceStatus',
                'DisconnectLimit': 15,
                'pollFrequency': 60
            },
            'interface_configuration': {
                'Hostname': 'mainlib019c-enc001.library.illinois.edu',
                'IPPort': 50002,
                'Model': 'NMX-ENC-N2312'
            }
        },
        'Subscriptions': [],
        'Polling': [],
        'Options': {
            'MatrixAssignment': 'VMX001',
            'MatrixInput': 1
        }
    }
)

# ENC002 - AMX N2300 Encoder
SystemDevices.AddNewDevice(
    **{
        'Id': 'ENC002',
        'Name': 'WPD Encoder',
        'Manufacturer': 'AMX',
        'Model': 'NMX-ENC-N2312',
        'Interface':
        {
            'module': 'amx_avoip_n2300_series',
            'interface_class': 'EthernetClass',
            'ConnectionHandler': {
                'keepAliveQuery': 'DeviceStatus',
                'DisconnectLimit': 15,
                'pollFrequency': 60
            },
            'interface_configuration': {
                'Hostname': 'mainlib019c-enc002.library.illinois.edu',
                'IPPort': 50002,
                'Model': 'NMX-ENC-N2312'
            }
        },
        'Subscriptions': [],
        'Polling': [],
        'Options': {
            'MatrixAssignment': 'VMX001',
            'MatrixInput': 2
        }
    }
)

# VMX001 - SVSi Virtual Matrix Switcher
SystemDevices.AddNewDevice(
    **{
        'Id': 'VMX001',
        'Name': 'SVSi Matrix',
        'Manufacturer': 'AMX',
        'Model': 'N2300 Virtual Matrix',
        'Interface':
        {
            'module': 'uofi_avoip_virtual_matrix',
            'interface_class': 'VirtualDeviceClass',
            'interface_configuration': {
                'VirtualDeviceID': 'VMX001',
                'AssignmentAttribute': 'MatrixAssignment',
                'Model': 'AMX SVSi N2300'
            }
        },
        'Subscriptions':
        [
            {
                'command': 'OutputTieStatus',
                'qualifier': [
                    {'Output': 1, 'Tie Type': 'Video'},
                    {'Output': 1, 'Tie Type': 'Audio'},
                    {'Output': 2, 'Tie Type': 'Video'},
                    {'Output': 2, 'Tie Type': 'Audio'},
                ],
                'callback': VMX_OutputHandler,
            },
            {
                'command': 'InputSignalStatus',
                'qualifier': [
                    {'Input': 1},
                    {'Input': 2},
                ],
                'callback': VMX_InputHandler
            }
        ],
        'Polling':
        [
            {
                'command': 'InputSignalStatus',
                'active_int': 10,
                'inactive_int': 600
            },
            {
                'command': 'OutputTieStatus',
                'active_int': 10,
                'inactive_int': 600
            }
        ],
        'Options':
        {
            'InputSignalStatusCommand':
            {
                'command': 'InputSignalStatus'
            },
            'SystemAudioOuput': 1
        }
    }
)