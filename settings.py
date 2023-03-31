
import secrets_hardware

##==============================================================================
## These are per system configuration variables, modify these as required

ctlJSON = '/user/controls.json' # location of controls json file
roomName = 'Test Room'        # Room Name - update for each project
activityMode = 3              # Activity mode popup to display
   # 1 - Share only
   # 2 - Share & Advanced Share
   # 3 - Share, Adv. Share, and Group Work

startupTimer = 5              # Max startup timer duration, seconds
switchTimer = 3               # Max switch timer duration, seconds
shutdownTimer = 5             # Max shutdown timer duration, seconds
shutdownConfTimer = 30        # Shutdown confirmation duration, seconds
activitySplashTimer = 15      # Duration to show activity splash pages for, seconds
initPageTimer = 600           # Inactivity timeout before showing "Splash" page when Activity is Off

defaultSource = "PC001"       # Default source id on activity switch
defaultCamera = 'CAM001'      # Default camera to show on camera control pages
primaryDestination = "PRJ001" # Primary destination
primarySwitcher = 'VMX001'    # Primary Matrix Switcher
primaryTouchPanel = 'TP001'   # Primary Touch Panel
primaryProcessor = 'CTL001'   # Primary Control Processor
techMatrixSize = (8,4)        # (inputs, outputs) - size of the virtual matrix to display in Tech Menu
camSwitcher = 'DEC001'        # ID of hardware device to switch between cameras
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
         "src-ctl": "PC",
         "adv-src-ctl": None
      },
      {
         "id": "PL001-1",
         "name": "HDMI 1",
         "icon": 1,
         "input": 1,
         "alert": "Ensure all cables and adapters to your HDMI device are fully seated.",
         "src-ctl": "HDMI",
         "adv-src-ctl": None
      },
      {
         "id": "PL001-2",
         "name": "HDMI 2",
         "icon": 1,
         "input": 2,
         "alert": "Ensure all cables and adapters to your HDMI device are fully seated",
         "src-ctl": "HDMI",
         "adv-src-ctl": None
      },
      {
         "id": "WPD001",
         "name": "Inst. Wireless",
         "icon": 3,
         "input": 4,
         "alert": "Contact Library IT for Assistance with this Wireless Device",
         "src-ctl": "WPD",
         "adv-src-ctl": "WPD"
      },
      {
         "id": "WPD002",
         "name": "North Wireless",
         "icon": 3,
         "input": 5,
         "alert": "Contact Library IT for Assistance with this Wireless Device",
         "src-ctl": "WPD",
         "adv-src-ctl": "WPD"
      },
      {
         "id": "WPD003",
         "name": "South Wireless",
         "icon": 3,
         "input": 6,
         "alert": "Contact Library IT for Assistance with this Wireless Device",
         "src-ctl": "WPD",
         "adv-src-ctl": "WPD"
      }
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
         'id': 'MON003',
         'name': 'Confidence Monitor',
         'output': 1,
         'type': 'conf',
         'rly': None,
         'group-work-src': 'WPD001',
         'adv-layout': {
            "row": 0,
            "pos": 1
         }
      },
      {
         "id": "PRJ001",
         "name": "Projector",
         "output": 3,
         "type": "proj+scn",
         "rly": [1, 2],
         "group-work-src": "WPD001",
         "adv-layout": {
            "row": 0,
            "pos": 0
         }
      },
      {
         "id": "MON001",
         "name": "North Monitor",
         "output": 2,
         "type": "mon",
         "rly": None,
         "group-work-src": "WPD002",
         "adv-layout": {
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
         "group-work-src": "WPD003",
         "adv-layout": {
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
         "Id": "CAM002",
         "Name": "South Camera",
         "Input": 2
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
         'Name': 'Overhead Mic',
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
               'host': 'libwpdsys01.library.illinois.edu',
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
      'Name': 'North Wireless',
      'Manufacturer': 'Mersive',
      'Model': 'Solstice Pod Gen 3',
      'Interface': 
         {
            'module': 'hardware.mersive_solstice_pod',
            'interface_class': 'RESTClass',
            'interface_configuration': {
               'host': 'wpd002',
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
      'Name': 'South Wireless',
      'Manufacturer': 'Mersive',
      'Model': 'Solstice Pod Gen 3',
      'Interface': 
         {
            'module': 'hardware.mersive_solstice_pod',
            'interface_class': 'RESTClass',
            'interface_configuration': {
               'host': 'wpd003',
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
         }
   },
   {
      'Id': 'DEC001',
      'Name': 'Camera Decoder',
      'Manufacturer': 'Magewell',
      'Model': 'Pro Convert for NDI to HDMI',
      'Interface': 
         {
            'module': 'hardware.mgwl_sm_Pro_Convert_Series_v1_0_1_0',
            'interface_class': 'HTTPClass',
            'interface_configuration': {
               'ipAddress': 'dec001',
               'port': '80',
               'deviceUsername': 'admin',
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
                  'command': 'SourcePresetListSelect',
                  'qualifier': {'NDI Source': 'True'}
               }
         }
   },
   {
      'Id': 'CAM001',
      'Name': 'North Camera',
      'Manufacturer': 'PTZOptics',
      'Model': 'PT12X-NDI-GY',
      'Interface':
         {
            'module': 'hardware.ptz_camera_PT30XNDI_GY_WH_v1_0_0_0',
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
            'Presets': {}
         }
   },
   {
      'Id': 'CAM002',
      'Name': 'South Camera',
      'Manufacturer': 'PTZOptics',
      'Model': 'PT12X-NDI-GY',
      'Interface':
         {
            'module': 'hardware.ptz_camera_PT30XNDI_GY_WH_v1_0_0_0',
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
            'Presets': {}
         }
   },
   {
      'Id': 'DEC002',
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
               'Hostname': 'libavstest08.library.illinois.edu',
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
   # {
   #    'Id': 'DEC003',
   #    'Name': 'North Monitor Decoder',
   #    'Manufacturer': 'AMX',
   #    'Model': 'NMX-DEC-N2322',
   #    'Interface':
   #       {
   #          'module': 'hardware.amx_avoip_n2300_series',
   #          'interface_class': 'EthernetClass',
   #          'ConnectionHandler': {
   #             'keepAliveQuery': 'DeviceStatus',
   #             'DisconnectLimit': 5,
   #             'pollFrequency': 60
   #          },
   #          'interface_configuration': {
   #             'Hostname': 'dec003',
   #             'IPPort': 50002,
   #             'Model': 'NMX-DEC-N2322'
   #          }
   #       },
   #    'Subscriptions': [],
   #    'Polling': [],
   #    'Options': {
   #       'MatrixAssignment': 'VMX001',
   #       'MatrixOutput': 3
   #    }
   # },
   # {
   #    'Id': 'DEC004',
   #    'Name': 'South Monitor Decoder',
   #    'Manufacturer': 'AMX',
   #    'Model': 'NMX-DEC-N2322',
   #    'Interface':
   #       {
   #          'module': 'hardware.amx_avoip_n2300_series',
   #          'interface_class': 'EthernetClass',
   #          'ConnectionHandler': {
   #             'keepAliveQuery': 'DeviceStatus',
   #             'DisconnectLimit': 5,
   #             'pollFrequency': 60
   #          },
   #          'interface_configuration': {
   #             'Hostname': 'dec004',
   #             'IPPort': 50002,
   #             'Model': 'NMX-DEC-N2322'
   #          }
   #       },
   #    'Subscriptions': [],
   #    'Polling': [],
   #    'Options': {
   #       'MatrixAssignment': 'VMX001',
   #       'MatrixOutput': 4
   #    }
   # },
   # {
   #    'Id': 'DEC005',
   #    'Name': 'Confidence Monitor Decoder',
   #    'Manufacturer': 'AMX',
   #    'Model': 'NMX-DEC-N2322',
   #    'Interface':
   #       {
   #          'module': 'hardware.amx_avoip_n2300_series',
   #          'interface_class': 'EthernetClass',
   #          'ConnectionHandler': {
   #             'keepAliveQuery': 'DeviceStatus',
   #             'DisconnectLimit': 5,
   #             'pollFrequency': 60
   #          },
   #          'interface_configuration': {
   #             'Hostname': 'dec005',
   #             'IPPort': 50002,
   #             'Model': 'NMX-DEC-N2322'
   #          }
   #       },
   #    'Subscriptions': [],
   #    'Polling': [],
   #    'Options': {
   #       'MatrixAssignment': 'VMX001',
   #       'MatrixOutput': 1
   #    }
   # },
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
   # {
   #    'Id': 'ENC002',
   #    'Name': 'HDMI 2 Encoder',
   #    'Manufacturer': 'AMX',
   #    'Model': 'NMX-ENC-N2312',
   #    'Interface':
   #       {
   #          'module': 'hardware.amx_avoip_n2300_series',
   #          'interface_class': 'EthernetClass',
   #          'ConnectionHandler': {
   #             'keepAliveQuery': 'DeviceStatus',
   #             'DisconnectLimit': 15,
   #             'pollFrequency': 60
   #          },
   #          'interface_configuration': {
   #             'Hostname': 'enc002',
   #             'IPPort': 50002,
   #             'Model': 'NMX-ENC-N2312'
   #          }
   #       },
   #    'Subscriptions': [],
   #    'Polling': [],
   #    'Options': {
   #       'MatrixAssignment': 'VMX001',
   #       'MatrixInput': 2
   #    }
   # },
   # {
   #    'Id': 'ENC003',
   #    'Name': 'Room PC Encoder',
   #    'Manufacturer': 'AMX',
   #    'Model': 'NMX-ENC-N2312',
   #    'Interface':
   #       {
   #          'module': 'hardware.amx_avoip_n2300_series',
   #          'interface_class': 'EthernetClass',
   #          'ConnectionHandler': {
   #             'keepAliveQuery': 'DeviceStatus',
   #             'DisconnectLimit': 15,
   #             'pollFrequency': 60
   #          },
   #          'interface_configuration': {
   #             'Hostname': 'enc003',
   #             'IPPort': 50002,
   #             'Model': 'NMX-ENC-N2312'
   #          }
   #       },
   #    'Subscriptions': [],
   #    'Polling': [],
   #    'Options': {
   #       'MatrixAssignment': 'VMX001',
   #       'MatrixInput': 3
   #    }
   # },
   # {
   #    'Id': 'ENC004',
   #    'Name': 'Inst. Pod Encoder',
   #    'Manufacturer': 'AMX',
   #    'Model': 'NMX-ENC-N2312',
   #    'Interface':
   #       {
   #          'module': 'hardware.amx_avoip_n2300_series',
   #          'interface_class': 'EthernetClass',
   #          'ConnectionHandler': {
   #             'keepAliveQuery': 'DeviceStatus',
   #             'DisconnectLimit': 15,
   #             'pollFrequency': 60
   #          },
   #          'interface_configuration': {
   #             'Hostname': 'enc004',
   #             'IPPort': 50002,
   #             'Model': 'NMX-ENC-N2312'
   #          }
   #       },
   #    'Subscriptions': [],
   #    'Polling': [],
   #    'Options': {
   #       'MatrixAssignment': 'VMX001',
   #       'MatrixInput': 4
   #    }
   # },
   # {
   #    'Id': 'ENC005',
   #    'Name': 'North Pod Encoder',
   #    'Manufacturer': 'AMX',
   #    'Model': 'NMX-ENC-N2312',
   #    'Interface':
   #       {
   #          'module': 'hardware.amx_avoip_n2300_series',
   #          'interface_class': 'EthernetClass',
   #          'ConnectionHandler': {
   #             'keepAliveQuery': 'DeviceStatus',
   #             'DisconnectLimit': 15,
   #             'pollFrequency': 60
   #          },
   #          'interface_configuration': {
   #             'Hostname': 'enc005',
   #             'IPPort': 50002,
   #             'Model': 'NMX-ENC-N2312'
   #          }
   #       },
   #    'Subscriptions': [],
   #    'Polling': [],
   #    'Options': {
   #       'MatrixAssignment': 'VMX001',
   #       'MatrixInput': 5
   #    }
   # },
   # {
   #    'Id': 'ENC006',
   #    'Name': 'South Pod Encoder',
   #    'Manufacturer': 'AMX',
   #    'Model': 'NMX-ENC-N2312',
   #    'Interface':
   #       {
   #          'module': 'hardware.amx_avoip_n2300_series',
   #          'interface_class': 'EthernetClass',
   #          'ConnectionHandler': {
   #             'keepAliveQuery': 'DeviceStatus',
   #             'DisconnectLimit': 15,
   #             'pollFrequency': 60
   #          },
   #          'interface_configuration': {
   #             'Hostname': 'enc006',
   #             'IPPort': 50002,
   #             'Model': 'NMX-ENC-N2312'
   #          }
   #       },
   #    'Subscriptions': [],
   #    'Polling': [],
   #    'Options': {
   #       'MatrixAssignment': 'VMX001',
   #       'MatrixInput': 6
   #    }
   # },
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
                  {'Input': 6},
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
               }
         }
   },
   {
      'Id': 'MON001',
      'Name': 'North Monitor',
      'Manufacturer': 'SharpNEC',
      'Model': 'V625',
      'Interface': 
         {
            'module': 'hardware.nec_display_P_V_X_Series_v1_4_1_0',
            'interface_class': 'EthernetClass',
            'ConnectionHandler': {
               'keepAliveQuery': 'AmbientCurrentIlluminance',
               'DisconnectLimit': 5,
               'pollFrequency': 60
            },
            'interface_configuration': {
               'Hostname': 'libavstest09.library.illinois.edu',
               'IPPort': 7142,
               'Model': 'V625'
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
            },
            {
               'command': 'AudioMute',
               'callback': 'AudioMuteStatusHandler',
               'active_int': 10,
               'inactive_int': 600
            },
            {
               'command': 'Volume',
               'callback': 'VolumeStatusHandler',
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
            'VolumeRange': (0, 100)
         }
   },
   # {
   #    'Id': 'MON002',
   #    'Name': 'South Monitor',
   #    'Manufacturer': 'SharpNEC',
   #    'Model': 'V625',
   #    'Interface': 
   #       {
   #          'module': 'hardware.nec_display_P_V_X_Series_v1_4_1_0',
   #          'interface_class': 'EthernetClass',
   #          'ConnectionHandler': {
   #             'keepAliveQuery': 'AmbientCurrentIlluminance',
   #             'DisconnectLimit': 5,
   #             'pollFrequency': 60
   #          },
   #          'interface_configuration': {
   #             'Hostname': 'mon002',
   #             'IPPort': 7142,
   #             'Model': 'V625'
   #          }
   #       },
   #    'Subscriptions': [],
   #    'Polling': 
   #       [
   #          {
   #             'command': 'Power',
   #             'callback': 'PowerStatusHandler',
   #             'active_int': 10,
   #             'inactive_int': 30
   #          },
   #          {
   #             'command': 'AudioMute',
   #             'callback': 'AudioMuteStatusHandler',
   #             'active_int': 10,
   #             'inactive_int': 600
   #          },
   #          {
   #             'command': 'Volume',
   #             'callback': 'VolumeStatusHandler',
   #             'active_int': 10,
   #             'inactive_int': 600
   #          }
   #       ],
   #    'Options': 
   #       {
   #          'PowerCommand': 
   #             {
   #                'command': 'Power',
   #             },
   #          'SourceCommand':
   #             {
   #                'command': 'Input',
   #                'value': 'HDMI'
   #             },
   #          'MuteCommand':
   #             {
   #                'command': 'AudioMute',
   #             },
   #          'VolumeCommand':
   #             {
   #                'command': 'Volume'
   #             },
   #          'VolumeRange': (0, 100)
   #       }
   # },
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
   }
]

##==============================================================================
