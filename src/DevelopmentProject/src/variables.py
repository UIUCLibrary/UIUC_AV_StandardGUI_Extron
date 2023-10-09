"""
The variables file is for data that will be used throughout the project.  This could be static or
dynamic data.  After being initial loaded by main.py, it can be imported and used in any module
throughout the system.
"""

TESTING = True

## PROJECT CONSTANTS -----------------------------------------------------------
##     Edit values below to configure the project

#### Common Settings 
ROOM_NAME = 'Test Room'             # Room Name - update for each project
PROJECT_FILE = "VSCodeProject.json" # Extron project file name, ex VSCodeProject.json
UI_LAYOUT = "UofI_Library"          # The file name used for the layout & button files, do not include a file extension
SYSTEM_ACTIVITIES = (0, 1, 2, 3)    # Include valid ActivityModes to SYSTEM_ACTIVITIES
                                        # this must include 0 and at least one other mode
PIN_SYSTEM = '0000'                 # PIN Code to access system, must be a string fewer than 10 characters of 0-9
                                        # Set to None to allow system access without pin
PIN_TECH = '1867'                   # PIN Code to access tech pages, must be a string fewer than 10 characters of 0-9
                                        # Set to None to allow tech page access without pin

#### Timer Settings
STARTUP_TIMER_DUR = 5               # Max startup timer duration, seconds
SWITCH_TIMER_DUR = 3                # Max switch timer duration, seconds
SHUTDOWN_TIMER_DUR = 5              # Max shutdown timer duration, seconds
SHUTDOWN_CONF_TIMER_DUR = 30        # Shutdown confirmation duration, seconds
TIP_TIMER_DUR = 15                  # Duration to show activity tip pages for, seconds
SPLASH_INACTIVITY_TIMER_DUR = 600   # Inactivity timeout before showing "Splash" page when Activity is Off, seconds

#### Defaults & Primary Device Settings
DEFAULT_SOURCE = 'PC001'    # Default source id on activity switch
DEFAULT_CAMERA = 'CAM001'   # Default camera to show on camera control pages
PRIMARY_DEST = 'PRJ001'     # Primary destination
PRIMARY_SW = 'VMX001'       # Primary Matrix Switcher
PRIMARY_UI = 'TP001'        # Primary User Interface Device
PRIMARY_PROC = 'CTL001'     # Primary Control Processor
PRIMARY_DSP = 'DSP001'      # Primary DSP for audio control
CAMERA_SW = 'DEC001'        # ID of hardware device to switch between cameras