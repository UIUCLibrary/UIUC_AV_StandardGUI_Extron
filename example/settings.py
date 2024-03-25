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
roomName = 'Main Library 314'   # Room Name - update for each project
activityMode = 3                # Activity mode popup to display
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
primaryDestination = "PRJ001" # Primary destination
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
         "input": 3,
         "alert": "Ensure the PC is awake.",
         "srcCtl": "PC",
         "advSrcCtl": None
      },
      {
         "id": "WPD001",
         "name": "Inst. Pod",
         "icon": 3,
         "input": 4,
         "alert": "Contact Library IT for Assistance with this Wireless Device",
         "srcCtl": "WPD",
         "advSrcCtl": "WPD"
      },
      {
         "id": "WPD002",
         "name": "North Pod",
         "icon": 3,
         "input": 5,
         "alert": "Contact Library IT for Assistance with this Wireless Device",
         "srcCtl": "WPD",
         "advSrcCtl": "WPD"
      },
      {
         "id": "WPD003",
         "name": "South Pod",
         "icon": 3,
         "input": 6,
         "alert": "Contact Library IT for Assistance with this Wireless Device",
         "srcCtl": "WPD",
         "advSrcCtl": "WPD"
      },
      {
         "id": "PL001-1",
         "name": "HDMI 1",
         "icon": 1,
         "input": 1,
         "alert": "Ensure all cables and adapters to your HDMI device are fully seated",
         "srcCtl": "HDMI",
         "advSrcCtl": None
      },
      {
         "id": "PL001-2",
         "name": "HDMI 2",
         "icon": 1,
         "input": 2,
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
         'id': 'PRJ001',
         'name': 'Projector',
         'output': 2,
         'type': 'proj+scn',
         'rly': (1,2),
         'groupWrkSrc': 'WPD001',
         'advLayout': {
            'row': 0,
            'pos': 0
         }
      },
      {
         'id': 'MON003',
         'name': 'Confidence Monitor',
         'output': 1,
         'type': 'conf',
         'rly': None,
         'groupWrkSrc': 'WPD001',
         'advLayout': {
            "row": 0,
            "pos": 1
         },
         'confFollow': 'PRJ001'
      },
      {
         "id": "MON001",
         "name": "North Monitor",
         "output": 3,
         "type": "mon",
         "rly": None,
         "groupWrkSrc": "WPD002",
         "advLayout": {
            "row": 1,
            "pos": 0
         }
      },
      {
         "id": "MON002",
         "name": "South Monitor",
         "output": 4,
         "type": "mon",
         "rly": None,
         "groupWrkSrc": "WPD003",
         "advLayout": {
            "row": 1,
            "pos": 1
         }
      }
   ]
   
cameras = \
   [
      {
         "Id": "CAM001",
         "Name": "North Camera",
         "Input": 1
      },
      {
         'Id': 'CAM002',
         'Name': 'Sourth Camera',
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
                     'HwId': 'MIC001',
                     'HwCmd': 'MuteCommand'
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
      'Name': 'Inst. Pod',
      'Manufacturer': 'Mersive',
      'Model': 'Solstice Pod Gen 3',
      'Interface': 
         {
            'module': 'hardware.mersive_solstice_pod',
            'interface_class': 'RESTClass',
            'interface_configuration': {
               'host': 'mainlib314-wpd001.library.illinois.edu',
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
      'Id': 'WPD002',
      'Name': 'North Pod',
      'Manufacturer': 'Mersive',
      'Model': 'Solstice Pod Gen 3',
      'Interface': 
         {
            'module': 'hardware.mersive_solstice_pod',
            'interface_class': 'RESTClass',
            'interface_configuration': {
               'host': 'mainlib314-wpd002.library.illinois.edu',
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
      'Id': 'WPD003',
      'Name': 'South Pod',
      'Manufacturer': 'Mersive',
      'Model': 'Solstice Pod Gen 3',
      'Interface': 
         {
            'module': 'hardware.mersive_solstice_pod',
            'interface_class': 'RESTClass',
            'interface_configuration': {
               'host': 'mainlib314-wpd003.library.illinois.edu',
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
               'Hostname': 'mainlib314-dsp001.library.illinois.edu',
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
               'qualifier': {'Instance Tag': 'Mic2Level', 'Channel': '1'},
               'callback': 'FeedbackLevelHandler',
               'tag': ('mics', '2'),
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
                  {'Instance Tag': 'AecInput1', 'Channel': '4'},
                  {'Instance Tag': 'AecInput1', 'Channel': '5'},
                  {'Instance Tag': 'AecInput1', 'Channel': '6'},
                  {'Instance Tag': 'AecInput1', 'Channel': '7'},
                  {'Instance Tag': 'AecInput1', 'Channel': '8'},
                  {'Instance Tag': 'AecInput1', 'Channel': '9'},
                  {'Instance Tag': 'AecInput1', 'Channel': '10'},
                  {'Instance Tag': 'AecInput1', 'Channel': '11'},
                  {'Instance Tag': 'AecInput1', 'Channel': '12'}
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
                  {'Instance Tag': 'AecInput1', 'Channel': '4'},
                  {'Instance Tag': 'AecInput1', 'Channel': '5'},
                  {'Instance Tag': 'AecInput1', 'Channel': '6'},
                  {'Instance Tag': 'AecInput1', 'Channel': '7'},
                  {'Instance Tag': 'AecInput1', 'Channel': '8'},
                  {'Instance Tag': 'AecInput1', 'Channel': '9'},
                  {'Instance Tag': 'AecInput1', 'Channel': '10'},
                  {'Instance Tag': 'AecInput1', 'Channel': '11'},
                  {'Instance Tag': 'AecInput1', 'Channel': '12'}
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
                  {
                     'Name': 'Unused Input',
                     'Block': 'AecInput1',
                     'Channel': '5',
                     'GainCommand': 'AECGain',
                     'PhantomCommand': 'AECPhantomPower'
                  },
                  {
                     'Name': 'Unused Input',
                     'Block': 'AecInput1',
                     'Channel': '6',
                     'GainCommand': 'AECGain',
                     'PhantomCommand': 'AECPhantomPower'
                  },
                  {
                     'Name': 'Unused Input',
                     'Block': 'AecInput1',
                     'Channel': '7',
                     'GainCommand': 'AECGain',
                     'PhantomCommand': 'AECPhantomPower'
                  },
                  {
                     'Name': 'Unused Input',
                     'Block': 'AecInput1',
                     'Channel': '8',
                     'GainCommand': 'AECGain',
                     'PhantomCommand': 'AECPhantomPower'
                  },
                  {
                     'Name': 'Unused Input',
                     'Block': 'AecInput1',
                     'Channel': '9',
                     'GainCommand': 'AECGain',
                     'PhantomCommand': 'AECPhantomPower'
                  },
                  {
                     'Name': 'Unused Input',
                     'Block': 'AecInput1',
                     'Channel': '10',
                     'GainCommand': 'AECGain',
                     'PhantomCommand': 'AECPhantomPower'
                  },
                  {
                     'Name': 'Unused Input',
                     'Block': 'AecInput1',
                     'Channel': '11',
                     'GainCommand': 'AECGain',
                     'PhantomCommand': 'AECPhantomPower'
                  },
                  {
                     'Name': 'Unused Input',
                     'Block': 'AecInput1',
                     'Channel': '12',
                     'GainCommand': 'AECGain',
                     'PhantomCommand': 'AECPhantomPower'
                  }
               ]
         }
   },
   {
      'Id': 'CAM001',
      'Name': 'North Camera',
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
               'Hostname': 'mainlib314-cam001.library.illinois.edu',
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
      'Name': 'South Camera',
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
               'Hostname': 'mainlib314-cam002.library.illinois.edu',
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
               'ipAddress': 'mainlib314-dec001.library.illinois.edu',
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
                  'qualifier': {'NDI Source': 'False'}
               }
         }
   },
   {
      'Id': 'DEC002',
      'Name': 'Confidence Monitor Decoder',
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
               'Hostname': 'mainlib314-dec002.library.illinois.edu',
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
      'Name': 'Projector Decoder',
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
               'Hostname': 'mainlib314-dec003.library.illinois.edu',
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
               'Hostname': 'mainlib314-dec004.library.illinois.edu',
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
      'Id': 'DEC005',
      'Name': 'South Monitor Decoder',
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
               'Hostname': 'mainlib314-dec005.library.illinois.edu',
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
   },
   {
      'Id': 'ENC001',
      'Name': 'HDMI 1 Encoder',
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
               'Hostname': 'mainlib314-enc001.library.illinois.edu',
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
      'Name': 'HDMI 2 Encoder',
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
               'Hostname': 'mainlib314-enc002.library.illinois.edu',
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
               'Hostname': 'mainlib314-enc003.library.illinois.edu',
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
      'Name': 'Instr. Pod Encoder',
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
               'Hostname': 'mainlib314-enc004.library.illinois.edu',
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
      'Name': 'North Pod Encoder',
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
               'Hostname': 'mainlib314-enc005.library.illinois.edu',
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
      'Id': 'ENC006',
      'Name': 'South Pod Encoder',
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
               'Hostname': 'mainlib314-enc006.library.illinois.edu',
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
                  {'Output': 4, 'Tie Type': 'Video'},
                  {'Output': 4, 'Tie Type': 'Audio'},
                  {'Output': 5, 'Tie Type': 'Video'},
                  {'Output': 5, 'Tie Type': 'Audio'},
                  {'Output': 6, 'Tie Type': 'Video'},
                  {'Output': 6, 'Tie Type': 'Audio'},
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
            'SystemAudioOuput': 2
         }
   },
   {
      'Id': 'MON001',
      'Name': 'North Monitor',
      'Manufacturer': 'SharpNEC',
      'Model': 'C860Q',
      'Interface': 
         {
            'module': 'hardware.nec_display_C750Q_C860Q_v1_2_0_0',
            'interface_class': 'EthernetClass',
            'ConnectionHandler': {
               'keepAliveQuery': 'AspectRatio',
               'DisconnectLimit': 5,
               'pollFrequency': 60
            },
            'interface_configuration': {
               'Hostname': 'mainlib314-mon001.library.illinois.edu',
               'IPPort': 7142,
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
      'Name': 'South Monitor',
      'Manufacturer': 'SharpNEC',
      'Model': 'C860Q',
      'Interface': 
         {
            'module': 'hardware.nec_display_C750Q_C860Q_v1_2_0_0',
            'interface_class': 'EthernetClass',
            'ConnectionHandler': {
               'keepAliveQuery': 'AspectRatio',
               'DisconnectLimit': 5,
               'pollFrequency': 60
            },
            'interface_configuration': {
               'Hostname': 'mainlib314-mon002.library.illinois.edu',
               'IPPort': 7142,
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
      'Id': 'MIC001',
      'Name': 'Overhead Mic',
      'Manufacturer': 'Shure',
      'Model': 'MXA920',
      'Interface':
         {
            'module': 'hardware.shur_dsp_MXA_Series_v1_3_0_0',
            'interface_class': 'EthernetClass',
            'ConnectionHandler': {
               'keepAliveQuery': 'ActiveMicChannels',
               'DisconnectLimit': 5,
               'pollFrequency': 60
            },
            'interface_configuration': {
               'Hostname': 'mainlib314-mic001.library.illinois.edu',
               'IPPort': 2202,
               'Model': 'MXA920'
            }
         },
      'Subscriptions': [],
      'Polling': 
         [
            {
               'command': 'DeviceAudioMute',
               'callback': 'FeedbackMuteHandler',
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
               }
         }
   },
   {
      'Id': 'PRJ001',
      'Name': 'Projector',
      'Manufacturer': 'SharpNEC',
      'Model': 'NP-PV710UL',
      'Interface':
         {
            'module': 'hardware.nec_vp_NPPA_803UL_653UL_v1_1_1_0',
            'interface_class': 'EthernetClass',
            'ConnectionHandler': {
               'keepAliveQuery': 'LampUsage',
               'DisconnectLimit': 5,
               'pollFrequency': 60
            },
            'interface_configuration': {
               'Hostname': 'mainlib314-prj001.library.illinois.edu',
               'IPPort': 7142
            }
         },
      'Subscriptions': [],
      'Polling':
         [
            {
               'command': 'Power',
               'callback': 'PowerStatusHandler',
               'active_int': 10,
               'inactive_int': 30
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
   },
   {
      'Id': 'RF001',
      'Name': 'Lav Mic Receiver',
      'Manufacturer': 'Shure',
      'Model': 'QLXD4-G50',
      'Interface':
         {
            'module': 'hardware.shur_other_QLX_D_ULX_D_Series_v1_1_5_0',
            'interface_class': 'EthernetClass',
            'ConnectionHandler': {
               'keepAliveQuery': 'AntennaStatus',
               'DisconnectLimit': 5,
               'pollFrequency': 60
            },
            'interface_configuration': {
               'Hostname': 'mainlib314-rf001.library.illinois.edu',
               'IPPort': 2202,
               'Model': 'QLX-D',
            }
         },
      'Subscriptions': [],
      'Polling': 
         [
            {
               'command': 'InterferenceDetection',
               'qualifier': {'Channel': '1'},
               'callback': 'FeedbackInterferenceHandler',
               'active_int': 10,
               'inactive_in': 600,
            }
         ],
      'Options': []
   }
]

##==============================================================================
