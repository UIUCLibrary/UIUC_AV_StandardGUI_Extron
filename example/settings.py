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
roomName = 'Test Room'        # Room Name - update for each project
activityMode = 2              # Activity mode popup to display
   # 1 - Share only
   # 2 - Share & Advanced Share
   # 3 - Share, Adv. Share, and Group Work

startupTimer = 10              # Max startup timer duration, seconds
switchTimer = 5               # Max switch timer duration, seconds
shutdownTimer = 10             # Max shutdown timer duration, seconds
shutdownConfTimer = 30        # Shutdown confirmation duration, seconds
activitySplashTimer = 15      # Duration to show activity splash pages for, seconds
initPageTimer = 600           # Inactivity timeout before showing "Splash" page when Activity is Off

defaultSource = "PC001"       # Default source id on activity switch
defaultCamera = 'CAM001'      # Default camera to show on camera control pages
primaryDestination = "MON001" # Primary destination
primarySwitcher = 'VMX001'    # Primary Matrix Switcher
primaryTouchPanel = 'TP001'   # Primary Touch Panel
primaryProcessor = 'CTL001'   # Primary Control Processor
techMatrixSize = (8,4)        # (inputs, outputs) - size of the virtual matrix to display in Tech Menu
camSwitcher = None            # ID of hardware device to switch between cameras
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
         "input": 1,
         "alert": "Ensure the PC is awake.",
         "srcCtl": "PC",
         "advSrcCtl": None
      },
      {
         "id": "WPD001",
         "name": "Inst. Wireless",
         "icon": 3,
         "input": 2,
         "alert": "Contact Library IT for Assistance with this Wireless Device",
         "srcCtl": "WPD",
         "advSrcCtl": "WPD"
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
         'id': 'MON002',
         'name': 'Confidence Monitor',
         'output': 1,
         'type': 'conf',
         'rly': None,
         'groupWrkSrc': 'WPD001',
         'advLayout': {
            "row": 0,
            "pos": 1
         },
         'confFollow': 'MON001'
      },
      {
         "id": "MON001",
         "name": "Test Monitor",
         "output": 2,
         "type": "mon",
         "rly": None,
         "groupWrkSrc": "WPD001",
         "advLayout": {
            "row": 0,
            "pos": 0
         }
      }
   ]
   
cameras = \
   [
      {
         "Id": "CAM001",
         "Name": "Test Camera",
         "Input": 1
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
      }
   ]

lights = []

techPIN = "1867"           # PIN Code to access tech pages, must be a string
                           # fewer than 10 characters of 0-9

hardware = [
   {
      'Id': 'WPD001',
      'Name': 'Inst. Wireless',
      'Manufacturer': 'Mersive',
      'Model': 'Solstice Pod Gen 3',
      'Interface': 
         {
            'module': 'hardware.mersive_solstice_pod',
            'interface_class': 'RESTClass',
            'interface_configuration': {
               'host': 'libwpdsys02.library.illinois.edu',
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
      'Model': 'TesiraFORTE AI AVB',
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
               'Hostname': 'libavstest10.library.illinois.edu',
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
                  }
               ]
         }
   },
   {
      'Id': 'CAM001',
      'Name': 'Conf Camera',
      'Manufacturer': 'Huddle Cam',
      'Model': 'HCX10X-SV',
      'Interface':
         {
            'module': 'hardware.vsca_camera_Visca_v1_0_1_2',
            'interface_class': 'SerialClass',
            'interface_configuration': {
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
                  'command': 'SavePreset'
               },
            'PresetRecallCommand':
               {
                  'command': 'RecallPreset'
               },
            'Presets': {}
         }
   },
   {
      'Id': 'DEC001',
      'Name': 'Conf Mon Decoder',
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
               'Hostname': 'libavstest08.library.illinois.edu',
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
      'Id': 'DEC002',
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
               'Hostname': 'libavstest12.library.illinois.edu',
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
      'Id': 'ENC001',
      'Name': 'PC Encoder',
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
               'Hostname': 'libavstest07.library.illinois.edu',
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
      'Name': 'Instr WPD Encoder',
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
               'Hostname': 'libavstest11.library.illinois.edu',
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
               ],
               'callback': 'FeedbackOutputTieStatusHandler',
            },
            {
               'command': 'InputSignalStatus',
               'qualifier': [
                  {'Input': 1},
                  {'Input': 2},
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
            'SystemAudioOuput': 1
         }
   },
   {
      'Id': 'MON001',
      'Name': 'Test Monitor',
      'Manufacturer': 'SharpNEC',
      'Model': 'LC-52LE64OU',
      'Interface': 
         {
            'module': 'hardware.shrp_display_LC_xxC6400U_xxLE640U_xxLE633U_v1_0_1_1',
            'interface_class': 'EthernetClass',
            'ConnectionHandler': {
               'keepAliveQuery': 'AspectRatio',
               'DisconnectLimit': 5,
               'pollFrequency': 60
            },
            'interface_configuration': {
               'Hostname': 'libavstest13.library.illinois.edu',
               'IPPort': 10002,
               'Model': 'LC-52LE64OU'
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
            'VolumeRange': (0, 60)
         }
   },
]

##==============================================================================
