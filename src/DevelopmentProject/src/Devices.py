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
from modules.helper.Collections import DeviceCollection
from modules.helper.PrimitiveObjects import DictObj
from Variables import PROJECT_FILE
from ui.Feedback.Device import (DSP_GainHandler,
                                DSP_MuteHandler, 
                                DSP_LevelHandler,
                                DSP_PhantomHandler,
                                Display_AudioMuteStatusHandler,
                                Display_PowerStatusHandler,
                                Display_VolumeStatusHandler,
                                Mic_MuteHandler,
                                WPD_StatusHandler,
                                VMX_InputHandler,
                                VMX_OutputHandler)
# TODO: load this in a more secure way
import secrets_devices

## End Imports -----------------------------------------------------------------

# Pull Control System Devices Data from Project File
__ProjectFile = open('/var/nortxe/.gcp/{}'.format(PROJECT_FILE))
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
            'module': 'generic_pc',
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
                'input': 3,
                'alert': 'Ensure the PC is awake',
                'srcCtl': 'PC',
                'advSrcCtl': None
            }
        }
    }
)

# UI001 - HDMI1
SystemDevices.AddNewDevice(
    **{
        'Id': 'UI001',
        'Name': 'HDMI 1',
        'Manufacturer': None,
        'Model': None,
        'Interface': None,
        'Subscriptions': None,
        'Polling': None,
        'Options': {
            'Source': {
                'icon': 1,
                'input': 1,
                'alert': 'Ensure all cables and adapters to your HDMI device are fully seated',
                'srcCtl': 'HDMI',
                'advSrcCtl': None
            }
        }
    }
)

# UI002 - HDMI2
SystemDevices.AddNewDevice(
    **{
        'Id': 'UI002',
        'Name': 'HDMI 2',
        'Manufacturer': None,
        'Model': None,
        'Interface': None,
        'Subscriptions': None,
        'Polling': None,
        'Options': {
            'Source': {
                'icon': 1,
                'input': 2,
                'alert': 'Ensure all cables and adapters to your HDMI device are fully seated',
                'srcCtl': 'HDMI',
                'advSrcCtl': None
            }
        }
    }
)

# WPD001 - Mersive Solstice
SystemDevices.AddNewDevice(
    **{
        'Id': 'WPD001',
        'Name': 'Inst. Wireless',
        'Manufacturer': 'Mersive',
        'Model': 'Solstice Pod Gen 3',
        'Interface': {
            'module': 'mersive_solstice_pod',
            'interface_class': 'RESTClass',
            'interface_configuration': {
                'host': 'wpd001',
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
                    'input': 4,
                    'alert': 'Contact Library IT for Assistance with this Wireless Device.',
                    'srcCtl': 'WPD',
                    'advSrcCtl': 'WPD'
                }
        }
    }
)

# WPD002 - Mersive Solstice
SystemDevices.AddNewDevice(
    **{
        'Id': 'WPD002',
        'Name': 'North Wireless',
        'Manufacturer': 'Mersive',
        'Model': 'Solstice Pod Gen 3',
        'Interface':
            {
                'module': 'mersive_solstice_pod',
                'interface_class': 'RESTClass',
                'interface_configuration': {
                    'host': 'wpd002',
                    'devicePassword': secrets_devices.mersive_password
                }
            },
        'Subscriptions': [],
        'Polling':
            [
                {
                    'command': 'PodStatus',
                    'callback': WPD_StatusHandler,
                    'active_int': 10,
                    'inactive_int': 600
                }
                ],
        'Options':
            {
                'Source': {
                    'icon': 3,
                    'input': 5,
                    'alert': 'Contact Library IT for Assistance with this Wireless Device.',
                    'srcCtl': 'WPD',
                    'advSrcCtl': 'WPD'
                }
                }
    }
)

# WPD003 - Mersive Solstice
SystemDevices.AddNewDevice(
    **{
        'Id': 'WPD003',
        'Name': 'South Wireless',
        'Manufacturer': 'Mersive',
        'Model': 'Solstice Pod Gen 3',
        'Interface':
            {
                'module': 'mersive_solstice_pod',
                'interface_class': 'RESTClass',
                'interface_configuration': {
                    'host': 'wpd003',
                    'devicePassword': secrets_devices.mersive_password
                }
            },
        'Subscriptions': [],
        'Polling':
            [
                {
                    'command': 'PodStatus',
                    'callback': WPD_StatusHandler,
                    'active_int': 10,
                    'inactive_int': 600
                }
                ],
        'Options':
            {
                'Source':
                    {
                        'icon': 3,
                        'input': 6,
                        'alert': 'Contact Library IT for Assistance with this Wireless Device',
                        'srcCtl': 'WPD',
                        'advSrcCtl': 'WPD'
                    }
                }
    }
)

# PRJ001 - Projector
SystemDevices.AddNewDevice(
    **{
        'Id': 'PRJ001',
        'Name': 'Projector',
        'Manufacturer': 'SharpNEC',
        'Model': 'NP-PA703UL',
        'Interface':
        {
            'module': 'nec_vp_NP_PA_Series2_v1_0_5_0',
            'interface_class': 'EthernetClass',
            'ConnectionHandler': {
                'keepAliveQuery': 'DeviceStatus',
                'DisconnectLimit': 5,
                'pollFrequency': 60
            },
            'interface_configuration': {
                'Hostname': 'prj001',
                'IPPort': 7142
            }
        },
        'Subscriptions': [],
        'Polling': [],
        'Options': {
            'Destination': {
                'output': 3,
                'type': 'proj',
                'groupWrkSrc': 'WPD001',
                'advLayout': {
                    'row': 0,
                    'pos': 0
                },
                'screen': 'SCN001'
            }
        }
    }
)

# MON001 - North Monitor
SystemDevices.AddNewDevice(
    **{
        'Id': 'MON001',
        'Name': 'North Monitor',
        'Manufacturer': 'SharpNEC',
        'Model': 'V625',
        'Interface':
        {
            'module': 'nec_display_P_V_X_Series_v1_4_1_0',
            'interface_class': 'EthernetClass',
            'ConnectionHandler': {
                'keepAliveQuery': 'AmbientCurrentIlluminance',
                'DisconnectLimit': 5,
                'pollFrequency': 60
            },
            'interface_configuration': {
                'Hostname': 'mon001',
                'IPPort': 7142,
                'Model': 'V625'
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
                'value': 'HDMI'
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
                'type': 'mon',
                'groupWrkSrc': 'WPD002',
                'advLayout': {
                    'row': 1,
                    'pos': 0
                }
            }
        }
    }
)

# MON002 - South Monitor
SystemDevices.AddNewDevice(
    **{
        'Id': 'MON002',
        'Name': 'South Monitor',
        'Manufacturer': 'SharpNEC',
        'Model': 'V625',
        'Interface':
        {
            'module': 'nec_display_P_V_X_Series_v1_4_1_0',
            'interface_class': 'EthernetClass',
            'ConnectionHandler': {
                'keepAliveQuery': 'AmbientCurrentIlluminance',
                'DisconnectLimit': 5,
                'pollFrequency': 60
            },
            'interface_configuration': {
                'Hostname': 'mon002',
                'IPPort': 7142,
                'Model': 'V625'
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
                'value': 'HDMI'
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
                'output': 4,
                'type': 'mon',
                'groupWrkSrc': 'WPD003',
                'advLayout': {
                    'row': 1,
                    'pos': 1
                }
            }
        }
    }
)

# MON003 - Confidence Monitor
SystemDevices.AddNewDevice(
    **{
        'Id': 'MON003',
        'Name': 'Confidence Monitor',
        'Manufacturer': 'TBD',
        'Model': 'TBD',
        'Interface': None,
        'Subscriptions': None,
        'Polling': None,
        'Options': {
            'Destination': {
                'output': 1,
                'type': 'conf',
                'groupWrkSrc': 'WPD001',
                'advLayout': {
                    'row': 0,
                    'pos': 1
                },
                'confFollow': 'PRJ001'
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
                'Hostname': 'libavstest10.library.illinois.edu',
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

# RF001 - Shure QLXD4
SystemDevices.AddNewDevice(
    **{
        'Id': 'RF002',
        'Name': 'Wireless Lav',
        'Manufacturer': 'Shure',
        'Model': 'ULXD4',
        'Interface':
            {
                'module': 'shur_other_QLX_D_ULX_D_Series_v1_1_5_0',
                'interface_class': 'EthernetClass',
                'ConnectionHandler':
                    {
                        'keepAliveQuery': 'AntennaStatus',
                        'DisconnectLimit': 5,
                        'pollFrequency': 60
                    },
                'interface_configuration': {
                    'Hostname': 'rf001',
                    'IPPort': 2022
                }
            },
        'Subscriptions': [],
        'Polling': [],
        'Options': {
            'Microphone': {
                'Number': 1,
                'Control': {
                    'level':
                    {
                        'DeviceId': 'DSP001',
                        'Cmd': 'Mic1LevelCommand',
                        'Range': (-36, 12),
                        'Step': 1,
                        'StartUp': 0
                    },
                    'mute':
                    {
                        'DeviceId': 'DSP001',
                        'Cmd': 'Mic1MuteCommand'
                    }
                }
            }
        }
    }
)

# MIC002 - Shure MXA920
SystemDevices.AddNewDevice(
    **{
        'Id': 'MIC001',
        'Name': 'Overhead Mic',
        'Manufacturer': 'Shure',
        'Model': 'MXA920',
        'Interface':
        {
            'module': 'shur_dsp_MXA_Series_v1_3_0_0',
            'interface_class': 'EthernetClass',
            'ConnectionHandler': {
                'keepAliveQuery': 'ActiveMicChannels',
                'DisconnectLimit': 5,
                'pollFrequency': 60
            },
            'interface_configuration': {
                'Hostname': 'mic001',
                'IPPort': 2202,
                'Model': 'MXA920'
            }
        },
        'Subscriptions': [],
        'Polling':
        [
            {
                'command': 'DeviceAudioMute',
                'callback': Mic_MuteHandler,
                'tag': ('mics', '2'),
                'active_int': 10,
                'inactive_int': 30
            }
        ],
        'Options':
        {
            'MuteCommand':
            {
                'command': 'DeviceAudioMute'
            },
            'Microphone': {
                'Number': 2,
                'Control': {
                    'level':
                    {
                        'DeviceId': 'DSP001',
                        'Cmd': 'Mic2LevelCommand',
                        'Range': (-36, 12),
                        'Step': 1,
                        'StartUp': 0
                    },
                    'mute':
                    {
                        'DeviceId': 'MIC001',
                        'Cmd': 'MuteCommand'
                    }
                }
            }
        }
    }
)

# DEC001 - Magewell Pro Covert for NDI to HDMI
SystemDevices.AddNewDevice(
    **{
        'Id': 'DEC001',
        'Name': 'Camera Decoder',
        'Manufacturer': 'Magewell',
        'Model': 'Pro Convert for NDI to HDMI',
        'Interface':
        {
            'module': 'mgwl_sm_Pro_Convert_Series_v1_0_1_0',
            'interface_class': 'HTTPClass',
            'interface_configuration': {
                'ipAddress': 'dec001',
                'port': '80',
                'deviceUsername': 'admin',
                'devicePassword': secrets_devices.magewell_password
            }
        },
        'Subscriptions': [],
        'Polling':
        [
            {
                'command': 'CurrentSelectedSourceStatus',
                'active_int': 30,
                'inactive_int': 600
            }
        ],
        'Options':
        {
            'SwitchCommand':
            {
                'command': 'SourcePresetsListSelect',
                'qualifier': {'NDI Source': 'True'}
            }
        }
    }
)

# CAM001 - PTZOptics 12X-NDI
SystemDevices.AddNewDevice(
    **{
        'Id': 'CAM001',
        'Name': 'North Camera',
        'Manufacturer': 'PTZOptics',
        'Model': 'PT12X-NDI-GY',
        'Interface':
        {
            'module': 'ptz_camera_PT30XNDI_GY_WH_v1_0_0_0',
            'interface_class': 'EthernetClass',
            'interface_configuration': {
                'Hostname': 'cam001',
                'IPPort': 5678
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
            'Camera': {'input': 1}
        }
    }
)

# CAM002 - PTZOptics 12X-NDI
SystemDevices.AddNewDevice(
    **{
        'Id': 'CAM002',
        'Name': 'South Camera',
        'Manufacturer': 'PTZOptics',
        'Model': 'PT12X-NDI-GY',
        'Interface':
        {
            'module': 'ptz_camera_PT30XNDI_GY_WH_v1_0_0_0',
            'interface_class': 'EthernetClass',
            'interface_configuration': {
                'Hostname': 'cam002',
                'IPPort': 5678
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
            'Camera': {'input': 2}
        }
    }
)

# DEC002 - AMX N2300 Decoder
SystemDevices.AddNewDevice(
    **{
        'Id': 'DEC002',
        'Name': 'Projector Decoder',
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
                'Hostname': 'dec002',
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

# DEC003 - AMX N2300 Decoder
SystemDevices.AddNewDevice(
    **{
        'Id': 'DEC003',
        'Name': 'North Monitor Decoder',
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
                'Hostname': 'dec003',
                'IPPort': 50002,
                'Model': 'NMX-DEC-N2322'
            }
        },
        'Subscriptions': [],
        'Polling': [],
        'Options': {
            'MatrixAssignment': 'VMX001',
            'MatrixOutput': 3
        }
    }
)

# DEC004 - AMX N2300 Decoder
SystemDevices.AddNewDevice(
    **{
        'Id': 'DEC004',
        'Name': 'South Monitor Decoder',
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
                'Hostname': 'dec004',
                'IPPort': 50002,
                'Model': 'NMX-DEC-N2322'
            }
        },
        'Subscriptions': [],
        'Polling': [],
        'Options': {
            'MatrixAssignment': 'VMX001',
            'MatrixOutput': 4
        }
    }
)

# DEC005 - AMX N2300 Decoder
SystemDevices.AddNewDevice(
    **{
        'Id': 'DEC005',
        'Name': 'Confidence Monitor Decoder',
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
                'Hostname': 'dec005',
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

# ENC001 - AMX N2300 Encoder
SystemDevices.AddNewDevice(
    **{
        'Id': 'ENC001',
        'Name': 'HDMI 1 Encoder',
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
                'Hostname': 'enc001',
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
        'Name': 'HDMI 2 Encoder',
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
                'Hostname': 'enc002',
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

# ENC003 - AMX N2300 Encoder
SystemDevices.AddNewDevice(
    **{
        'Id': 'ENC003',
        'Name': 'Room PC Encoder',
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
                'Hostname': 'enc003',
                'IPPort': 50002,
                'Model': 'NMX-ENC-N2312'
            }
        },
        'Subscriptions': [],
        'Polling': [],
        'Options': {
            'MatrixAssignment': 'VMX001',
            'MatrixInput': 3
        }
    }
)

# ENC004 - AMX N2300 Encoder
SystemDevices.AddNewDevice(
    **{
        'Id': 'ENC004',
        'Name': 'Inst. Pod Encoder',
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
                'Hostname': 'enc004',
                'IPPort': 50002,
                'Model': 'NMX-ENC-N2312'
            }
        },
        'Subscriptions': [],
        'Polling': [],
        'Options': {
            'MatrixAssignment': 'VMX001',
            'MatrixInput': 4
        }
    }
)

# ENC005 - AMX N2300 Encoder
SystemDevices.AddNewDevice(
    **{
        'Id': 'ENC005',
        'Name': 'North Pod Encoder',
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
                'Hostname': 'enc005',
                'IPPort': 50002,
                'Model': 'NMX-ENC-N2312'
            }
        },
        'Subscriptions': [],
        'Polling': [],
        'Options': {
            'MatrixAssignment': 'VMX001',
            'MatrixInput': 5
        }
    }
)

# ENC006 - AMX N2300 Encoder
SystemDevices.AddNewDevice(
    **{
        'Id': 'ENC006',
        'Name': 'South Pod Encoder',
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
                'Hostname': 'enc006',
                'IPPort': 50002,
                'Model': 'NMX-ENC-N2312'
            }
        },
        'Subscriptions': [],
        'Polling': [],
        'Options': {
            'MatrixAssignment': 'VMX001',
            'MatrixInput': 6
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
            'module': 'avoip_virtual_matrix',
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
                    {'Output': 3, 'Tie Type': 'Video'},
                    {'Output': 3, 'Tie Type': 'Audio'},
                    {'Output': 4, 'Tie Type': 'Video'},
                    {'Output': 4, 'Tie Type': 'Audio'},
                ],
                'callback': VMX_OutputHandler,
            },
            {
                'command': 'InputSignalStatus',
                'qualifier': [
                    {'Input': 1},
                    {'Input': 2},
                    {'Input': 3},
                    {'Input': 4},
                    {'Input': 5},
                    {'Input': 6},
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

# SCN001 - Relay Controlled Screen
SystemDevices.AddNewDevice(
    **{
        'Id': 'SCN001',
        'Name': 'Projector Screen',
        'Manufacturer': 'Da-Lite',
        'Model': '88401L',
        'Interface': 
            {
                'module': 'generic_prj_screen',
                'interface_class': 'LVCScreen',
                'interface_configuration': {
                    'RelayHost': 'CTL001'
                }
            },
        'Subscriptions': None,
        'Polling': None,
        'Options': {
            'Screen': {
                'up': 'RLY1',
                'down': 'RLY2',
                'stop': 'RLY1|RLY2'
            }
        }
    }
)