## Begin ControlScript Import --------------------------------------------------
from extronlib import event, Version
from extronlib.device import eBUSDevice, ProcessorDevice, UIDevice
from extronlib.interface import (CircuitBreakerInterface, ContactInterface,
    DigitalInputInterface, DigitalIOInterface, EthernetClientInterface,
    EthernetServerInterfaceEx, FlexIOInterface, IRInterface, PoEInterface,
    RelayInterface, SerialInterface, SWACReceptacleInterface, SWPowerInterface,
    VolumeInterface)
from extronlib.ui import Button, Knob, Label, Level, Slider
from extronlib.system import (Email, Clock, MESet, Timer, Wait, File, RFile,
    ProgramLog, SaveProgramLog, Ping, WakeOnLan, SetAutomaticTime, SetTimeZone)

print(Version()) ## Sanity check ControlScript Import
## End ControlScript Import ----------------------------------------------------
##
## Begin Python Imports --------------------------------------------------------

'''
Since we can't load modules through Global Scripter directly, we will instead
upload modules to the SFTP path on the controller. Create a new directory at
the root of the SFTP called 'modules' and upload modules there. Modules in this
directory may be imported after the sys.path.import call. 
'''
import sys
sys.path.insert(0, "/var/nortxe/uf/admin/modules/")

## End Python Imports ----------------------------------------------------------
##
## Begin User Import -----------------------------------------------------------
#### Custom Code Modules (SFTP Modules)
from uofi_gui.activityControls import ActivityController
from uofi_gui.pinControl import PINController
from uofi_gui.uiObjects import (BuildButtons, BuildButtonGroups, BuildKnobs,
                                BuildLabels, BuildLevels, BuildSliders)
from uofi_gui.sourceControls import SourceController
from uofi_gui.headerControls import HeaderController
from uofi_gui.techControls import TechMenuController
from uofi_gui.systemHardware import (SystemHardwareController,
                                     SystemPollingController, 
                                     SystemStatusController,
                                     VirtualDeviceInterface)
from uofi_gui.deviceControl import CameraController, DisplayController, AudioController
from uofi_gui.keyboardControl import KeyboardController
from uofi_gui.scheduleControls import AutoScheduleController

import utilityFunctions as utFn

#### System configuration modules (GS Modules)
import settings
import vars

#### Extron Global Scripter Modules

## End User Import -------------------------------------------------------------
##
## Begin Device/Processor Definition -------------------------------------------

vars.CtlProc_Main = ProcessorDevice('CTL001')

## End Device/Processor Definition ---------------------------------------------
##
## Begin Device/User Interface Definition --------------------------------------

vars.TP_Main = UIDevice('TP001')

#### Bezel Lights 
# TODO: Figure out why this button can't be found
vars.TP_Lights = Button(vars.TP_Main, 65533)
vars.TP_Lights.LightIDRed = 16711680
vars.TP_Lights.LightIDGreen = 65280
vars.TP_Lights.LightIDOff = 0
vars.TP_Lights.SetBlinking('Medium', [vars.TP_Lights.LightIDRed, vars.TP_Lights.LightIDOff])


settings.ctlJSON = '/user/controls.json'
#### Build Buttons & Button Groups
vars.TP_Btns = BuildButtons(vars.TP_Main, jsonPath=settings.ctlJSON)
vars.TP_Btn_Grps = BuildButtonGroups(vars.TP_Btns, jsonPath=settings.ctlJSON)

#### Build Knobs
vars.TP_Knobs = BuildKnobs(vars.TP_Main, jsonPath=settings.ctlJSON)

#### Build Levels
vars.TP_Lvls = BuildLevels(vars.TP_Main, jsonPath=settings.ctlJSON)

#### Build Sliders
vars.TP_Slds = BuildSliders(vars.TP_Main, jsonPath=settings.ctlJSON)

#### Build Labels
vars.TP_Lbls = BuildLabels(vars.TP_Main, jsonPath=settings.ctlJSON)

#### System devices
#### Poll Control Module - needs to exist before creating hardware controllers
vars.PollCtl = SystemPollingController()

for hw in settings.hardware:
    vars.Hardware[hw['Id']] = SystemHardwareController(**hw)

## End Device/User Interface Definition ----------------------------------------
##
## Begin Communication Interface Definition ------------------------------------

## End Communication Interface Definition --------------------------------------
##
## Begin Function Definitions --------------------------------------------------

def StartupActions() -> None:
    vars.PollCtl.SetPollingMode('active')
    vars.HdrCtl.ConfigSystemOn()
    vars.SrcCtl.SetPrivacyOff()
    vars.CamCtl.SelectDefaultCamera()
    vars.CamCtl.SendCameraHome()
    vars.AudioCtl.AudioStartUp()

def StartupSyncedActions(count: int) -> None:
    pass

def SwitchActions() -> None:
    # utFn.Log('Update Source Menu')
    vars.SrcCtl.UpdateSourceMenu()
    
    # utFn.Log('Show selected source')
    vars.SrcCtl.ShowSelectedSource()

def SwitchSyncedActions(count: int) -> None:
    pass

def ShutdownActions() -> None:
    vars.PollCtl.SetPollingMode('inactive')
    vars.HdrCtl.ConfigSystemOff()
    vars.SrcCtl.MatrixSwitch(0, 'All', 'untie')
    vars.AudioCtl.AudioShutdown()
    
    # for id, hw in vars.Hardware:
    #     if id.startswith('WPD'):
    #         hw.interface.Set('BootUsers', value=None, qualifier=None)

def ShutdownSyncedActions(count: int) -> None:
    pass

def Initialize() -> bool:
    #### Set initial page & room name
    vars.TP_Main.HideAllPopups()
    vars.TP_Main.ShowPage('Splash')
    vars.TP_Btns['Room-Label'].SetText(settings.roomName)
    
    #### Build Common Use UI Dictionaries ======================================
    TransitionDict = \
        {
            "label": vars.TP_Lbls['PowerTransLabel-State'],
            "level": vars.TP_Lvls['PowerTransIndicator'],
            "count": vars.TP_Lbls['PowerTransLabel-Count'],
            "start": {
                "init": StartupActions,
                "sync": StartupSyncedActions
              },
            "switch": {
                "init": SwitchActions,
                "sync": SwitchSyncedActions
              },
            "shutdown": {
                "init": ShutdownActions,
                "sync": ShutdownSyncedActions
              }
        }
        
    SourceButtons = \
        {
            "select": vars.TP_Btn_Grps['Source-Select'],
            "indicator": vars.TP_Btn_Grps['Source-Indicator'],
            "arrows": [
                vars.TP_Btns['SourceMenu-Prev'],
                vars.TP_Btns['SourceMenu-Next']
              ]
        }
        
    ActModBtns = \
        {
            "select": vars.TP_Btn_Grps['Activity-Select'],
            "indicator": vars.TP_Btn_Grps['Activity-Indicator'],
            "end": vars.TP_Btns['Shutdown-EndNow'],
            "cancel": vars.TP_Btns['Shutdown-Cancel']
        }
    
    PinButtons = \
        {
            "numPad": utFn.DictValueSearchByKey(vars.TP_Btns, r'PIN-\d', regex=True),
            "backspace": vars.TP_Btns['PIN-Del'],
            "cancel": vars.TP_Btns['PIN-Cancel']
        }
    
    MatrixDict = \
        {
            'btns': utFn.DictValueSearchByKey(vars.TP_Btns, r'Tech-Matrix-\d+,\d+', regex=True),
            'ctls': vars.TP_Btn_Grps['Tech-Matrix-Mode'],
            'del': vars.TP_Btns['Tech-Matrix-DeleteTies'],
            'labels': {
                'input': utFn.DictValueSearchByKey(vars.TP_Lbls, r'MatrixLabel-In-\d+', regex=True),
                'output': utFn.DictValueSearchByKey(vars.TP_Lbls, r'MatrixLabel-Out-\d+', regex=True)
            }
        }
        
    HeaderDict = \
        {
            'alert': {
                'btn': vars.TP_Btns['Header-Alert'],
                'popover': 'Popover-Ctl-Alert'
            },
            'camera': {
                'btn': vars.TP_Btns['Header-Camera'],
                'popover': 'Popover-Ctl-Camera_{}'.format(len(settings.cameras))
            },
            'lights': {
                'btn': vars.TP_Btns['Header-Lights'],
                'popover': 'Popover-Ctl-Lights_{}'.format(len(settings.lights))
            },
            'settings': {
                'btn': vars.TP_Btns['Header-Settings'],
                'popover': 'Popover-Ctl-Audio_{}'.format(len(settings.microphones))
            },
            'help': {
                'btn': vars.TP_Btns['Header-Help'],
                'popover': 'Popover-Ctl-Help'
            },
            'room': {
                'btn': vars.TP_Btns['Room-Label'],
                'popover': 'Popover-Room'
            },
            'popover-close': vars.TP_Btns['Popover-Close']
        }
        
    TechMenuControlDict = \
        {
            'prev': vars.TP_Btns['Tech-Menu-Previous'],
            'next': vars.TP_Btns['Tech-Menu-Next'],
            'exit': vars.TP_Btns['Tech-Menu-Exit'],
            'menu-pages': [
                'Menu-Tech-1',
                'Menu-Tech-2'
            ]
        }
                
    #### =======================================================================
        
    #### Activity Control Module
    vars.ActCtl = ActivityController(vars.TP_Main,
                                     ActModBtns,
                                     TransitionDict,
                                     vars.TP_Lbls['ShutdownConf-Count'],
                                     vars.TP_Lvls['ShutdownConfIndicator'])
    
    #### Source Control Module
    vars.SrcCtl = SourceController(vars.TP_Main,
                                   SourceButtons,
                                   MatrixDict,
                                   settings.sources,
                                   settings.destinations)
    
    #### Header Control Module
    vars.HdrCtl = HeaderController(vars.TP_Main,
                                   HeaderDict)
    
    #### Tech Menu Control Module
    vars.TechCtl = TechMenuController(vars.TP_Main,
                                      TechMenuControlDict,
                                      utFn.DictValueSearchByKey(vars.TP_Btns, r'Tech-\w+$', regex=True))
    
    #### PIN Code Module
    vars.PINCtl = PINController(vars.TP_Main,
                                vars.TP_Btns['Header-Settings'],
                                PinButtons,
                                vars.TP_Lbls['PIN-Label'],
                                settings.techPIN, 
                                'Tech',
                                vars.TechCtl.OpenTechMenu)
    
    #### System Status Module
    vars.StatusCtl = SystemStatusController(vars.Hardware,
                                            {
                                                'icons': utFn.DictValueSearchByKey(vars.TP_Btns, r'DeviceStatusIcon-\d+', regex=True),
                                                'labels': utFn.DictValueSearchByKey(vars.TP_Lbls, r'DeviceStatusLabel-\d+', regex=True),
                                                'arrows': {
                                                    'prev': vars.TP_Btns['DeviceStatus-PageDown'],
                                                    'next': vars.TP_Btns['DeviceStatus-PageUp']
                                                },
                                                'pages': {
                                                    'current': vars.TP_Lbls['DeviceStatusPage-Current'],
                                                    'total': vars.TP_Lbls['DeviceStatusPage-Total'],
                                                    'div': vars.TP_Lbls['PaginationSlash']
                                                }
                                            })
    
    #### Camera Controller Module
    if settings.camSwitcher is not None:
        vars.CamCtl = CameraController(vars.TP_Main,
                                       vars.TP_Btn_Grps['Camera-Select'],
                                       utFn.DictValueSearchByKey(vars.TP_Btns,
                                                                 r'Ctl-Camera-Preset-\d+',
                                                                 regex=True),
                                       utFn.DictValueSearchByKey(vars.TP_Btns,
                                                                 r'Ctl-Camera-[TPZ]-(?:Up|Dn|L|R|In|Out)',
                                                                 regex=True),
                                       {
                                           'Title': vars.TP_Lbls['CameraPreset-Title'],
                                           'DisplayName': vars.TP_Btns['CamPreset-Name'],
                                           'Home': vars.TP_Btns['CamPreset-Home'],
                                           'Save': vars.TP_Btns['CamPreset-Save'],
                                           'Cancel': vars.TP_Btns['CamPreset-Cancel']
                                       },
                                       settings.camSwitcher
                                       )
    
    #### Keyboard Module
    vars.KBCtl = KeyboardController(vars.TP_Main)
    
    #### Schedule Module
    vars.SchedCtl = AutoScheduleController(vars.TP_Main)
    
    #### Display Control Module
    vars.DispCtl = DisplayController(vars.TP_Main)
    
    #### Audio Control Module
    vars.AudioCtl = AudioController(vars.TP_Main, settings.primaryDSP)
    
    ## DO ADDITIONAL INITIALIZATION ITEMS HERE
    
    # Associate Virtual Hardware
    # utFn.Log('Looking for Virtual Device Interfaces')
    for Hw in vars.Hardware.values():
        # utFn.Log('Hardware ({}) - Interface Class: {}'.format(id, type(Hw.interface)))
        if issubclass(type(Hw.interface), VirtualDeviceInterface):
            Hw.interface.FindAssociatedHardware()
            # utFn.Log('Hardware Found for {}. New IO Size: {}'.format(Hw.Name, Hw.interface.MatrixSize))
    
    #### Start Polling
    vars.PollCtl.PollEverything()
    vars.PollCtl.StartPolling()
    
    utFn.Log('System Initialized')
    vars.TP_Lights.SetBlinking('Fast', [vars.TP_Lights.LightIDGreen, vars.TP_Lights.LightIDRed])
    vars.TP_Main.Click(5, 0.2)
    @Wait(3)
    def StopTPLight():
        vars.TP_Lights.SetState(vars.TP_Lights.LightIDOff)
    return True

## End Function Definitions ----------------------------------------------------
##
## Event Definitions -----------------------------------------------------------

## End Events Definitions ------------------------------------------------------
##
## Start Program ---------------------------------------------------------------
Initialize()
