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

import secrets_hardware

##==============================================================================
## These are per system configuration variables, modify these as required

ctlJSON = '/user/controls.json' # location of controls json file
roomName = 'Main Library 106'   # Room Name - update for each project
activityMode = 2                # Activity mode popup to display
   # 1 - Share only
   # 2 - Share & Advanced Share
   # 3 - Share, Adv. Share, and Group Work

startupTimer = 30             # Max startup timer duration, seconds
startupMin = 20               # Minium startup timer duration, seconds
switchTimer = 3               # Max switch timer duration, seconds
shutdownTimer = 45            # Max shutdown timer duration, seconds
shutdownMin = 30              # Minium shutdown timer duration, seconds
shutdownConfTimer = 30        # Shutdown confirmation duration, seconds
activitySplashTimer = 60      # Duration to show activity splash pages for, seconds
initPageTimer = 600           # Inactivity timeout before showing "Splash" page when Activity is Off

defaultSource = "PC001"       # Default source id on activity switch
defaultCamera = 'CAM001'      # Default camera to show on camera control pages
primaryDestination = "MON002" # Primary destination
primarySwitcher = 'VMX001'    # Primary Matrix Switcher
primaryTouchPanel = 'TP001'   # Primary Touch Panel
primaryProcessor = 'CTL001'   # Primary Control Processor
techMatrixSize = (8,4)        # (inputs, outputs) - size of the virtual matrix to display in Tech Menu
camSwitcher = "DEC001"        # ID of hardware device to switch between cameras
primaryDSP = 'DSP001'         # Primary DSP for audio control

# Icon Map
#     0 - no source
#     1 - HDMI
#     2 - PC
#     3 - Wireless
#     4 - Camera
#     5 - Document Camera
#     6 - BluRay
sources = \
   [
      {
         "id": "PC001",
         "name": "Room PC",
         "icon": 2,
         "input": 4,
         "alert": "Ensure the PC is awake.",
         "srcCtl": "PC",
         "advSrcCtl": None
      },
      {
         "id": "WPD001",
         "name": "Wireless Pod",
         "icon": 3,
         "input": 5,
         "alert": "Contact Library IT for Assistance with this Wireless Device",
         "srcCtl": "WPD",
         "advSrcCtl": "WPD"
      },
      {
         "id": "PL001",
         "name": "Lectern HDMI",
         "icon": 1,
         "input": 1,
         "alert": "Ensure all cables and adapters to your HDMI device are fully seated",
         "srcCtl": "HDMI",
         "advSrcCtl": None
      },
      {
         "id": "ENC002",
         "name": "West HDMI",
         "icon": 1,
         "input": 2,
         "alert": "Ensure all cables and adapters to your HDMI device are fully seated",
         "srcCtl": "HDMI",
         "advSrcCtl": None
      },
      {
         "id": "ENC003",
         "name": "East HDMI",
         "icon": 1,
         "input": 3,
         "alert": "Ensure all cables and adapters to your HDMI device are fully seated",
         "srcCtl": "HDMI",
         "advSrcCtl": None
      },
   ]

# Destination Types
#  proj     - Projector with uncontrolled screen
#  proj+scn - Projector with controlled screen
#  mon      - Large format monitor
#  conf     - Instructor confidence monitor (no power control)
#  c-conf   - Instructor confidence monitor (with display control)
destinations = \
   [
      {
         "id": "MON001",
         "name": "West Monitor",
         "output": 1,
         "type": "mon",
         "rly": None,
         "groupWrkSrc": "WPD001",
         "advLayout": {
            "row": 1,
            "pos": 0
         }
      },
      {
         "id": "MON002",
         "name": "North Monitor",
         "output": 2,
         "type": "mon",
         "rly": None,
         "groupWrkSrc": "WPD001",
         "advLayout": {
            "row": 1,
            "pos": 1
         }
      },
      {
         'id': 'MON003',
         'name': 'East Monitor',
         'output': 1,
         'type': 'mon',
         'rly': None,
         'groupWrkSrc': 'WPD001',
         'advLayout': {
            "row": 0,
            "pos": 1
         }
      },
   ]
   
cameras = \
   [
      {
         "Id": "CAM001",
         "Name": "Presenter Camera",
         "Input": 1
      },
      {
         'Id': 'CAM002',
         'Name': 'Audience Camera',
         'Input': 2
      }
   ]
   
microphones = \
   [
      {
         'Id': 'RF001',
         'Name': 'Wireless Lav',
         'Number': 1,
         'Control': 
            {
               'level': 
                  {
                     'HwId': 'DSP001',
                     'HwCmd': 'Mic1LevelCommand',
                     'Range': (-36, 12),
                     'Step': 1,
                     'StartUp': 0
                  },
               'mute':
                  {
                     'HwId': 'DSP001',
                     'HwCmd': 'Mic1MuteCommand'
                  }
            }
      },
      {
         'Id': 'MIC001',
         'Name': 'Audience Mic',
         'Number': 2,
         'Control': 
            {
               'level': 
                  {
                     'HwId': 'DSP001',
                     'HwCmd': 'Mic2LevelCommand',
                     'Range': (-36, 12),
                     'Step': 1,
                     'StartUp': 0
                  },
               'mute':
                  {
                     'HwId': 'DSP001',
                     'HwCmd': 'Mic2MuteCommand'
                  }
            }
      },
      {
         'Id': 'MIC002',
         'Name': 'Lectern XLR',
         'Number': 3,
         'Control':
            {
               'level':
                  {
                     'HwId': 'DSP001',
                     'HwCmd': 'Mic3LevelCommand',
                     'Range': (-36, 12),
                     'Step': 1,
                     'StartUp': 0
                  },
               'mute':
                  {
                     'HwId': 'DSP001',
                     'HwCmd': 'Mic3MuteCommand'
                  }
            }
      }
   ]

lights = []

techPIN = "1408"           # PIN Code to access tech pages, must be a string
                           # fewer than 10 characters of 0-9

hardware = [
   {
      'Id': 'WPD001',
      'Name': 'Wireless Pod',
      'Manufacturer': 'Mersive',
      'Model': 'Solstice Pod Gen 3',
      'Interface': 
         {
            'module': 'hardware.mersive_solstice_pod',
            'interface_class': 'RESTClass',
            'interface_configuration': {
               'host': 'mainlib106-wpd001.library.illinois.edu',
               'devicePassword': secrets_hardware.mersive_password
            }
         },
      'Subscriptions': [],
      'Polling':
         [
            {
               'command': 'PodStatus',
               'callback': 'FeedbackStatusHandler',
               'active_int': 10,
               'inactive_int': 600
            }
         ]
   },
   {
      'Id': 'DSP001',
      'Name': 'DSP',
      'Manufacturer': 'Biamp',
      'Model': 'TesiraFORTE AVB VT4',
      'Interface':
         {
            'module': 'hardware.biam_dsp_TesiraSeries_uofi',
            'interface_class': 'SSHClass',
            'ConnectionHandler': {
               'keepAliveQuery': 'VerboseMode',
               'DisconnectLimit': 5,
               'pollFrequency': 20
            },
            'interface_configuration': {
               'Hostname': 'mainlib106-dsp001.library.illinois.edu',
               'IPPort': 22,
               'Credentials': ('admin', secrets_hardware.biamp_password)
            }
         },
      'Subscriptions': [],
      'Polling':
         [
            {
               'command': 'LevelControl',
               'qualifier': {'Instance Tag': 'ProgLevel', 'Channel': '1'},
               'callback': 'FeedbackLevelHandler',
               'tag': ('prog',),
               'active_int': 30,
               'inactive_int': 120,
            },
            {
               'command': 'LevelControl',
               'qualifier': {'Instance Tag': 'Mic1Level', 'Channel': '1'},
               'callback': 'FeedbackLevelHandler',
               'tag': ('mics', '1'),
               'active_int': 30,
               'inactive_int': 120,
            },
            {
               'command': 'LevelControl',
               'qualifier': {'Instance Tag': 'CeilingMicLevel', 'Channel': '1'},
               'callback': 'FeedbackLevelHandler',
               'tag': ('mics', '2'),
               'active_int': 30,
               'inactive_int': 120,
            },
            {
               'command': 'LevelControl',
               'qualifier': {'Instance Tag': 'XLRLevel', 'Channel': '1'},
               'callback': 'FeedbackLevelHandler',
               'tag': ('mics', '3'),
               'active_int': 30,
               'inactive_int': 120,
            },
            {
               'command': 'MuteControl',
               'qualifier': {'Instance Tag': 'ProgLevel', 'Channel': '1'},
               'callback': 'FeedbackMuteHandler',
               'tag': ('prog',),
               'active_int': 30,
               'inactive_int': 120,
            },
            {
               'command': 'MuteControl',
               'qualifier': {'Instance Tag': 'Mic1Level', 'Channel': '1'},
               'callback': 'FeedbackMuteHandler',
               'tag': ('mics', '1'),
               'active_int': 30,
               'inactive_int': 120,
            },
            {
               'command': 'MuteControl',
               'qualifier': {'Instance Tag': 'CeilingMicMute', 'Channel': '1'},
               'callback': 'FeedbackMuteHandler',
               'tag': ('mics', '2'),
               'active_int': 30,
               'inactive_int': 120,
            },
            {
               'command': 'MuteControl',
               'qualifier': {'Instance Tag': 'XLRLevel', 'Channel': '1'},
               'callback': 'FeedbackMuteHandler',
               'tag': ('mics', '3'),
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
               'callback': 'FeedbackGainHandler',
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
               'callback': 'FeedbackPhantomHandler',
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
            'Mic2MuteCommand': 
               {
                  'command': 'LogicState',
                  'qualifier': {'Instance Tag': 'CeilingMicLogic', 'Channel': '1'}
               },
            'Mic2LevelCommand':
               {
                  'command': 'LevelControl',
                  'qualifier': {'Instance Tag': 'CeilingMicLevel', 'Channel': '1'}
               },
            'Mic3MuteCommand': 
               {
                  'command': 'MuteControl',
                  'qualifier': {'Instance Tag': 'XLRLevel', 'Channel': '1'}
               },
            'Mic3LevelCommand':
               {
                  'command': 'LevelControl',
                  'qualifier': {'Instance Tag': 'XLRLevel', 'Channel': '1'}
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
                     'Name': 'Mic - MIC002',
                     'Block': 'AecInput1',
                     'Channel': '3',
                     'GainCommand': 'AECGain',
                     'PhantomCommand': 'AECPhantomPower'
                  },
                  {
                     'Name': 'Mic - RF001',
                     'Block': 'AecInput1',
                     'Channel': '4',
                     'GainCommand': 'AECGain',
                     'PhantomCommand': 'AECPhantomPower'
                  }
               ]
         }
   },
   {
      'Id': 'CAM001',
      'Name': 'Presenter Camera',
      'Manufacturer': 'PTZOptics',
      'Model': 'PT12X-NDI',
      'Interface':
         {
            'module': 'hardware.ptz_camera_12X_SDI_USB_G2_20X_SDI_USB_G2_v1_0_0_0',
            'interface_class': 'EthernetClass',
            'ConnectionHandler': {
               'keepAliveQuery': 'Power',
               'DisconnectLimit': 5,
               'pollFrequency': 20
            },
            'interface_configuration': {
               'Hostname': 'mainlib106-cam001.library.illinois.edu',
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
            'Presets': {}
         }
   },
   {
      'Id': 'CAM002',
      'Name': 'Audience Camera',
      'Manufacturer': 'PTZOptics',
      'Model': 'PT12X-NDI',
      'Interface':
         {
            'module': 'hardware.ptz_camera_12X_SDI_USB_G2_20X_SDI_USB_G2_v1_0_0_0',
            'interface_class': 'EthernetClass',
            'ConnectionHandler': {
               'keepAliveQuery': 'Power',
               'DisconnectLimit': 5,
               'pollFrequency': 20
            },
            'interface_configuration': {
               'Hostname': 'mainlib106-cam002.library.illinois.edu',
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
            'Presets': {}
         }
   },
   {
      'Id': 'DEC001',
      'Name': 'Camera Decoder',
      'Manufacturer': 'Magewell',
      'Model': 'ProConvert for NDI to HDMI',
      'Interface':
         {
            'module': 'hardware.mgwl_sm_Pro_Convert_Series_v1_0_1_0',
            'interface_class': 'HTTPClass',
            'interface_configuration': {
               'ipAddress': 'mainlib106-dec001.library.illinois.edu',
               'port': 80,
               'deviceUsername': 'Admin',
               'devicePassword': secrets_hardware.magewell_password
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
                  'command': 'SourcePresetCommand',
                  'qualifier': {'NDI Source': 'True'}
               }
         }
   },
   {
      'Id': 'DEC002',
      'Name': 'West Monitor Decoder',
      'Manufacturer': 'AMX',
      'Model': 'NMX-DEC-N2322',
      'Interface':
         {
            'module': 'hardware.amx_avoip_n2300_series',
            'interface_class': 'EthernetClass',
            'ConnectionHandler': {
               'keepAliveQuery': 'DeviceStatus',
               'DisconnectLimit': 5,
               'pollFrequency': 60
            },
            'interface_configuration': {
               'Hostname': 'mainlib106-dec002.library.illinois.edu',
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
   },
   {
      'Id': 'DEC003',
      'Name': 'North Monitor Decoder',
      'Manufacturer': 'AMX',
      'Model': 'NMX-DEC-N2322',
      'Interface':
         {
            'module': 'hardware.amx_avoip_n2300_series',
            'interface_class': 'EthernetClass',
            'ConnectionHandler': {
               'keepAliveQuery': 'DeviceStatus',
               'DisconnectLimit': 5,
               'pollFrequency': 60
            },
            'interface_configuration': {
               'Hostname': 'mainlib106-dec003.library.illinois.edu',
               'IPPort': 50002,
               'Model': 'NMX-DEC-N2322'
            }
         },
      'Subscriptions': [],
      'Polling': [],
      'Options': {
         'MatrixAssignment': 'VMX001',
         'MatrixOutput': 2
      }
   },
   {
      'Id': 'DEC004',
      'Name': 'East Monitor Decoder',
      'Manufacturer': 'AMX',
      'Model': 'NMX-DEC-N2322',
      'Interface':
         {
            'module': 'hardware.amx_avoip_n2300_series',
            'interface_class': 'EthernetClass',
            'ConnectionHandler': {
               'keepAliveQuery': 'DeviceStatus',
               'DisconnectLimit': 5,
               'pollFrequency': 60
            },
            'interface_configuration': {
               'Hostname': 'mainlib106-dec004.library.illinois.edu',
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
   },
   {
      'Id': 'ENC001',
      'Name': 'Lectern HDMI Encoder',
      'Manufacturer': 'AMX',
      'Model': 'NMX-ENC-N2312',
      'Interface':
         {
            'module': 'hardware.amx_avoip_n2300_series',
            'interface_class': 'EthernetClass',
            'ConnectionHandler': {
               'keepAliveQuery': 'DeviceStatus',
               'DisconnectLimit': 15,
               'pollFrequency': 60
            },
            'interface_configuration': {
               'Hostname': 'mainlib106-enc001.library.illinois.edu',
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
   },
   {
      'Id': 'ENC002',
      'Name': 'West HDMI Encoder',
      'Manufacturer': 'AMX',
      'Model': 'NMX-ENC-N2315-WP',
      'Interface':
         {
            'module': 'hardware.amx_avoip_n2300_series',
            'interface_class': 'EthernetClass',
            'ConnectionHandler': {
               'keepAliveQuery': 'DeviceStatus',
               'DisconnectLimit': 15,
               'pollFrequency': 60
            },
            'interface_configuration': {
               'Hostname': 'mainlib106-enc002.library.illinois.edu',
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
   },
   {
      'Id': 'ENC003',
      'Name': 'East HDMI Encoder',
      'Manufacturer': 'AMX',
      'Model': 'NMX-ENC-N2315-WP',
      'Interface':
         {
            'module': 'hardware.amx_avoip_n2300_series',
            'interface_class': 'EthernetClass',
            'ConnectionHandler': {
               'keepAliveQuery': 'DeviceStatus',
               'DisconnectLimit': 15,
               'pollFrequency': 60
            },
            'interface_configuration': {
               'Hostname': 'mainlib106-enc003.library.illinois.edu',
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
   },
   {
      'Id': 'ENC004',
      'Name': 'Room PC Encoder',
      'Manufacturer': 'AMX',
      'Model': 'NMX-ENC-N2312',
      'Interface':
         {
            'module': 'hardware.amx_avoip_n2300_series',
            'interface_class': 'EthernetClass',
            'ConnectionHandler': {
               'keepAliveQuery': 'DeviceStatus',
               'DisconnectLimit': 15,
               'pollFrequency': 60
            },
            'interface_configuration': {
               'Hostname': 'mainlib106-enc004.library.illinois.edu',
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
   },
   {
      'Id': 'ENC005',
      'Name': 'Wireless Pod Encoder',
      'Manufacturer': 'AMX',
      'Model': 'NMX-ENC-N2312',
      'Interface':
         {
            'module': 'hardware.amx_avoip_n2300_series',
            'interface_class': 'EthernetClass',
            'ConnectionHandler': {
               'keepAliveQuery': 'DeviceStatus',
               'DisconnectLimit': 15,
               'pollFrequency': 60
            },
            'interface_configuration': {
               'Hostname': 'mainlib106-enc005.library.illinois.edu',
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
   },
   {
      'Id': 'ATC001',
      'Name': 'Audio Transceiver',
      'Manufacturer': 'AMX',
      'Model': 'NMX-ATC-N4321',
      'Interface':
         {
            'module': 'hardware.amx_avoip_n4321_atc',
            'interface_class': 'EthernetClass',
            'ConnectionHandler': {
               'keepAliveQuery': 'DeviceStatus',
               'DisconnectLimit': 15,
               'pollFrequency': 60
            },
            'interface_configuration': {
               'Hostname': 'mainlib106-atc001.library.illinois.edu',
               'IPPort': 50002,
               'Model': 'NMX-ATC-N4321'
            }
         },
      'Subscriptions': [],
      'Polling': [],
      'Options': {
         'MatrixAssignment': 'VMX001',
         'MatrixInput': 6,
         'MatrixOutput': 4
      }
   },
   {
      'Id': 'VMX001',
      'Name': 'SVSi Matrix',
      'Manufacturer': 'AMX',
      'Model': 'N2300 Virtual Matrix',
      'Interface': 
         {
            'module': 'hardware.avoip_virtual_matrix',
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
                  {'Output': 4, 'Tie Type': 'Audio'},
               ],
               'callback': 'FeedbackOutputTieStatusHandler',
            },
            {
               'command': 'InputSignalStatus',
               'qualifier': [
                  {'Input': 1},
                  {'Input': 2},
                  {'Input': 3},
                  {'Input': 4},
                  {'Input': 5},
                  {'Input': 6}
               ],
               'callback': 'FeedbackInputSignalStatusHandler'
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
            'SystemAudioOuput': 4
         }
   },
   {
      'Id': 'MON001',
      'Name': 'West Monitor',
      'Manufacturer': 'SharpNEC',
      'Model': 'LC-80LE650U',
      'Interface': 
         {
            'module': 'hardware.shrp_display_LC_60C_xxLExxxU_Series_v1_0_7_0',
            'interface_class': 'SerialOverEthernetClass',
            'ConnectionHandler': {
               'keepAliveQuery': 'AspectRatio',
               'DisconnectLimit': 5,
               'pollFrequency': 60
            },
            'interface_configuration': {
               'Hostname': 'mainlib106-dec002.library.illinois.edu',
               'IPPort': 50004,
               'Model': 'LC-80LE650U'
            }
         },
      'Subscriptions': [],
      'Polling': 
         [
            {
               'command': 'Power',
               'callback': 'PowerStatusHandler',
               'active_int': 11,
               'inactive_int': 30
            },
            {
               'command': 'AudioMute',
               'callback': 'AudioMuteStatusHandler',
               'active_int': 22,
               'inactive_int': 600
            },
            {
               'command': 'Volume',
               'callback': 'VolumeStatusHandler',
               'active_int': 33,
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
            'VolumeRange': (0, 100)
         }
   },
   {
      'Id': 'MON002',
      'Name': 'North Monitor',
      'Manufacturer': 'SharpNEC',
      'Model': 'LC-80LE650U',
      'Interface': 
         {
            'module': 'hardware.shrp_display_LC_60C_xxLExxxU_Series_v1_0_7_0',
            'interface_class': 'SerialOverEthernetClass',
            'ConnectionHandler': {
               'keepAliveQuery': 'AspectRatio',
               'DisconnectLimit': 5,
               'pollFrequency': 60
            },
            'interface_configuration': {
               'Hostname': 'mainlib106-dec003.library.illinois.edu',
               'IPPort': 50004,
               'Model': 'LC-80LE650U'
            }
         },
      'Subscriptions': [],
      'Polling': 
         [
            {
               'command': 'Power',
               'callback': 'PowerStatusHandler',
               'active_int': 11,
               'inactive_int': 30
            },
            {
               'command': 'AudioMute',
               'callback': 'AudioMuteStatusHandler',
               'active_int': 22,
               'inactive_int': 600
            },
            {
               'command': 'Volume',
               'callback': 'VolumeStatusHandler',
               'active_int': 33,
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
            'VolumeRange': (0, 100)
         }
   },
   {
      'Id': 'MON003',
      'Name': 'East Monitor',
      'Manufacturer': 'SharpNEC',
      'Model': 'LC-80LE650U',
      'Interface': 
         {
            'module': 'hardware.shrp_display_LC_60C_xxLExxxU_Series_v1_0_7_0',
            'interface_class': 'SerialOverEthernetClass',
            'ConnectionHandler': {
               'keepAliveQuery': 'AspectRatio',
               'DisconnectLimit': 5,
               'pollFrequency': 60
            },
            'interface_configuration': {
               'Hostname': 'mainlib106-dec004.library.illinois.edu',
               'IPPort': 50004,
               'Model': 'LC-80LE650U'
            }
         },
      'Subscriptions': [],
      'Polling': 
         [
            {
               'command': 'Power',
               'callback': 'PowerStatusHandler',
               'active_int': 11,
               'inactive_int': 30
            },
            {
               'command': 'AudioMute',
               'callback': 'AudioMuteStatusHandler',
               'active_int': 22,
               'inactive_int': 600
            },
            {
               'command': 'Volume',
               'callback': 'VolumeStatusHandler',
               'active_int': 33,
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
         }
   }
]

##==============================================================================
