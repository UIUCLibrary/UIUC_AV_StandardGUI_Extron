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
from datetime import datetime
import json

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

## End Device/User Interface Definition ----------------------------------------
##
## Begin Communication Interface Definition ------------------------------------

## End Communication Interface Definition --------------------------------------
##
## Begin Function Definitions --------------------------------------------------

def StartupActions() -> None:
    vars.HdrCtl.ConfigSystemOn()
    pass

def StartupSyncedActions(count: int) -> None:
    pass

def SwitchActions() -> None:
    pass

def SwitchSyncedActions(count: int) -> None:
    pass

def ShutdownActions() -> None:
    vars.HdrCtl.ConfigSystemOff()
    pass

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
                'popover': 'Popover-Ctl-Audio_{}'.format(settings.micCtl)
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
    
    ## DO ADDITIONAL INITIALIZATION ITEMS HERE
    
    utFn.Log('System Initialized')
    return True

## End Function Definitions ----------------------------------------------------
##
## Event Definitions -----------------------------------------------------------

## End Events Definitions ------------------------------------------------------
##
## Start Program ---------------------------------------------------------------
Initialize()
