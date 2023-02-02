import uofi_gui.feedback
import secrets_hardware

##==============================================================================
## These are per system configuration variables, modify these as required

ctlJSON = '/user/controls.json' # location of controls json file
roomName = 'Test Room'        # Room Name - update for each project
activityMode = 3              # Activity mode popup to display
   # 1 - Share only
   # 2 - Share & Advanced Share
   # 3 - Share, Adv. Share, and Group Work
startupTimer = 10             # Max startup timer duration
switchTimer = 20              # Max switch timer duration
shutdownTimer = 30            # Max shutdown timer duration
shutdownConfTimer = 30        # Shutdown confirmation duration
activitySplashTimer = 15      # Duration to show activity splash pages for
defaultSource = "PC001"       # Default source id on activity switch
primaryDestination = "PRJ001" # Primary destination
micCtl = 1                    # Microphone control
   # 0 - no mic control
   # 1 - mic control
techMatrixSize = (8,4)

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
#  conf     - Instructor confidence monitor
destinations = \
   [
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
         "id": "CAM001",
         "name": "North Camera"
      },
      {
         "id": "CAM002",
         "name": "South Camera"
      }
   ]
   
lights = []

techPIN = "1867"           # PIN Code to access tech pages, must be a string
                           # fewer than 10 characters of 0-9

hardware = [
   {
      'Id': 'WPD001',
      'Name': 'Inst. Wireless',
      'Interface': 
         {
            'module': 'hardware.mersive_solstice_pod',
            'interface_class': 'RESTClass',
            'interface_configuration': {
               'host': 'libwpdsys01.library.illinois.edu',
               'devicePassword': secrets_hardware.mersive_password
            }
         },
      'Subscriptions':
         [
            {
               'command': 'PodStatus',
               'callback': uofi_gui.feedback.WPD_Mersive_StatusHandler
            }
         ],
      'Polling':
         [
            {
               'command': 'PodStatus',
               'active_int': 10,
               'inactive_int': 600
            }
         ]
   },
   {
      'Id': 'WPD002',
      'Name': 'North Wireless',
      'Interface': 
         {
            'module': 'hardware.mersive_solstice_pod',
            'interface_class': 'RESTClass',
            'interface_configuration': {
               'host': '192.17.115.141',
               'devicePassword': secrets_hardware.mersive_password
            }
         },
      'Subscriptions': [],
      'Polling':
         [
            {
               'command': 'PodStatus',
               'callback': uofi_gui.feedback.WPD_Mersive_StatusHandler,
               'active_int': 10,
               'inactive_int': 600
            }
         ]
   },
   {
      'Id': 'WPD003',
      'Name': 'South Wireless',
      'Interface': 
         {
            'module': 'hardware.mersive_solstice_pod',
            'interface_class': 'RESTClass',
            'interface_configuration': {
               'host': '192.17.115.144',
               'devicePassword': secrets_hardware.mersive_password
            }
         },
      'Subscriptions': [],
      'Polling':
         [
            {
               'command': 'PodStatus',
               'callback': uofi_gui.feedback.WPD_Mersive_StatusHandler,
               'active_int': 10,
               'inactive_int': 600
            }
         ]
   },
   {
      'Id': 'DSP001',
      'Name': 'Biamp DSP',
      'Interface':
         {
            'module': 'hardware.biam_dsp_TesiraSeries_uofi',
            'interface_class': 'SSHClass',
            'UseConnectionHandler': True,
            'interface_configuration': {
               'Hostname': 'libavsadm07.library.illinois.edu',
               'IPPort': 22,
               'Credentials': ('admin', secrets_hardware.biamp_password)
            }
         },
      'Subscriptions': [],
      'Polling': 
         [
            {
               'command': 'DeviceFaultList',
               'active_int': 30,
               'inactive_int': 30
            },
            {
               'command': 'LevelControl',
               'qualifier': {'Instance Tag': 'XLRLevel', 'Channel': '1'},
               'callback': uofi_gui.feedback.DSP_BiampTesira_LevelHandler,
               'active_int': 5,
               'inactive_int': 120,
            },
            {
               'command': 'LevelControl',
               'qualifier': {'Instance Tag': 'ProgLevel', 'Channel': '1'},
               'callback': uofi_gui.feedback.DSP_BiampTesira_LevelHandler,
               'active_int': 5,
               'inactive_int': 120,
            },
            {
               'command': 'MuteControl',
               'qualifier': {'Instance Tag': 'XLRLevel', 'Channel': '1'},
               'callback': uofi_gui.feedback.DSP_BiampTesira_MuteHandler,
               'active_int': 5,
               'inactive_int': 120,
            },
            {
               'command': 'MuteControl',
               'qualifier': {'Instance Tag': 'ProgLevel', 'Channel': '1'},
               'callback': uofi_gui.feedback.DSP_BiampTesira_MuteHandler,
               'active_int': 5,
               'inactive_int': 120,
            }
         ]
   }
]

##==============================================================================
