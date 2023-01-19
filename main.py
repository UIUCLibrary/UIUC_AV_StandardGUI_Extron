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
from uofi_gui.sourceControls import SourceController, ACTIVITY_CONTROLLER


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
    pass

def StartupSyncedActions(count: int) -> None:
    pass

def SwitchActions() -> None:
    pass

def SwitchSyncedActions(count: int) -> None:
    pass

def ShutdownActions() -> None:
    pass

def ShutdownSyncedActions(count: int) -> None:
    pass

def Initialize() -> bool:
    #### Set initial page & room name
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
        
    ActModBtns = {"select": vars.TP_Btn_Grps['Activity-Select'],
                       "indicator": vars.TP_Btn_Grps['Activity-Indicator'],
                       "end": vars.TP_Btns['Shutdown-EndNow'],
                       "cancel": vars.TP_Btns['Shutdown-Cancel']}
    
    PinButtons = \
        {
            "numPad": [
                vars.TP_Btns['PIN-0'],
                vars.TP_Btns['PIN-1'],
                vars.TP_Btns['PIN-2'],
                vars.TP_Btns['PIN-3'],
                vars.TP_Btns['PIN-4'],
                vars.TP_Btns['PIN-5'],
                vars.TP_Btns['PIN-6'],
                vars.TP_Btns['PIN-7'],
                vars.TP_Btns['PIN-8'],
                vars.TP_Btns['PIN-9']
              ],
            "backspace": vars.TP_Btns['PIN-Del'],
            "cancel": vars.TP_Btns['PIN-Cancel']
        }
    
    MatrixDict = \
        {
            'btns': 
                [
                    vars.TP_Btns['Tech-Matrix-1,1'],
                    vars.TP_Btns['Tech-Matrix-2,1'],
                    vars.TP_Btns['Tech-Matrix-3,1'],
                    vars.TP_Btns['Tech-Matrix-4,1'],
                    vars.TP_Btns['Tech-Matrix-5,1'],
                    vars.TP_Btns['Tech-Matrix-6,1'],
                    vars.TP_Btns['Tech-Matrix-7,1'],
                    vars.TP_Btns['Tech-Matrix-8,1'],
                    vars.TP_Btns['Tech-Matrix-9,1'],
                    vars.TP_Btns['Tech-Matrix-10,1'],
                    vars.TP_Btns['Tech-Matrix-11,1'],
                    vars.TP_Btns['Tech-Matrix-12,1'],
                    vars.TP_Btns['Tech-Matrix-1,2'],
                    vars.TP_Btns['Tech-Matrix-2,2'],
                    vars.TP_Btns['Tech-Matrix-3,2'],
                    vars.TP_Btns['Tech-Matrix-4,2'],
                    vars.TP_Btns['Tech-Matrix-5,2'],
                    vars.TP_Btns['Tech-Matrix-6,2'],
                    vars.TP_Btns['Tech-Matrix-7,2'],
                    vars.TP_Btns['Tech-Matrix-8,2'],
                    vars.TP_Btns['Tech-Matrix-9,2'],
                    vars.TP_Btns['Tech-Matrix-10,2'],
                    vars.TP_Btns['Tech-Matrix-11,2'],
                    vars.TP_Btns['Tech-Matrix-12,2'],
                    vars.TP_Btns['Tech-Matrix-1,3'],
                    vars.TP_Btns['Tech-Matrix-2,3'],
                    vars.TP_Btns['Tech-Matrix-3,3'],
                    vars.TP_Btns['Tech-Matrix-4,3'],
                    vars.TP_Btns['Tech-Matrix-5,3'],
                    vars.TP_Btns['Tech-Matrix-6,3'],
                    vars.TP_Btns['Tech-Matrix-7,3'],
                    vars.TP_Btns['Tech-Matrix-8,3'],
                    vars.TP_Btns['Tech-Matrix-9,3'],
                    vars.TP_Btns['Tech-Matrix-10,3'],
                    vars.TP_Btns['Tech-Matrix-11,3'],
                    vars.TP_Btns['Tech-Matrix-12,3'],
                    vars.TP_Btns['Tech-Matrix-1,4'],
                    vars.TP_Btns['Tech-Matrix-2,4'],
                    vars.TP_Btns['Tech-Matrix-3,4'],
                    vars.TP_Btns['Tech-Matrix-4,4'],
                    vars.TP_Btns['Tech-Matrix-5,4'],
                    vars.TP_Btns['Tech-Matrix-6,4'],
                    vars.TP_Btns['Tech-Matrix-7,4'],
                    vars.TP_Btns['Tech-Matrix-8,4'],
                    vars.TP_Btns['Tech-Matrix-9,4'],
                    vars.TP_Btns['Tech-Matrix-10,4'],
                    vars.TP_Btns['Tech-Matrix-11,4'],
                    vars.TP_Btns['Tech-Matrix-12,4']
                ],
            'ctls': vars.TP_Btn_Grps['Tech-Matrix-Mode'],
            'del': vars.TP_Btns['Tech-Matrix-DeleteTies'],
            'labels': {
                'input': 
                    [
                        vars.TP_Lbls['MatrixLabel-In-1'],
                        vars.TP_Lbls['MatrixLabel-In-2'],
                        vars.TP_Lbls['MatrixLabel-In-3'],
                        vars.TP_Lbls['MatrixLabel-In-4'],
                        vars.TP_Lbls['MatrixLabel-In-5'],
                        vars.TP_Lbls['MatrixLabel-In-6'],
                        vars.TP_Lbls['MatrixLabel-In-7'],
                        vars.TP_Lbls['MatrixLabel-In-8'],
                        vars.TP_Lbls['MatrixLabel-In-9'],
                        vars.TP_Lbls['MatrixLabel-In-10'],
                        vars.TP_Lbls['MatrixLabel-In-11'],
                        vars.TP_Lbls['MatrixLabel-In-12']
                    ],
                'output': 
                    [
                        vars.TP_Lbls['MatrixLabel-Out-1'],
                        vars.TP_Lbls['MatrixLabel-Out-2'],
                        vars.TP_Lbls['MatrixLabel-Out-3'],
                        vars.TP_Lbls['MatrixLabel-Out-4'],
                        vars.TP_Lbls['MatrixLabel-Out-5'],
                        vars.TP_Lbls['MatrixLabel-Out-6']
                    ]
            }
        }
    
    AdvShareLayout = \
        [
            vars.TP_Btns['Disp-Select-0,0'],
            vars.TP_Btns['Disp-Ctl-0,0'],
            vars.TP_Btns['Disp-Aud-0,0'],
            vars.TP_Btns['Disp-Alert-0,0'],
            vars.TP_Btns['Disp-Scn-0,0'],
            vars.TP_Lbls['DispAdv-0,0'],
            vars.TP_Btns['Disp-Select-1,0'],
            vars.TP_Btns['Disp-Ctl-1,0'],
            vars.TP_Btns['Disp-Aud-1,0'],
            vars.TP_Btns['Disp-Alert-1,0'],
            vars.TP_Btns['Disp-Scn-1,0'],
            vars.TP_Lbls['DispAdv-1,0'],
            vars.TP_Btns['Disp-Select-0,1'],
            vars.TP_Btns['Disp-Ctl-0,1'],
            vars.TP_Btns['Disp-Aud-0,1'],
            vars.TP_Btns['Disp-Alert-0,1'],
            vars.TP_Btns['Disp-Scn-0,1'],
            vars.TP_Lbls['DispAdv-0,1'],
            vars.TP_Btns['Disp-Select-1,1'],
            vars.TP_Btns['Disp-Ctl-1,1'],
            vars.TP_Btns['Disp-Aud-1,1'],
            vars.TP_Btns['Disp-Alert-1,1'],
            vars.TP_Btns['Disp-Scn-1,1'],
            vars.TP_Lbls['DispAdv-1,1'],
            vars.TP_Btns['Disp-Select-2,1'],
            vars.TP_Btns['Disp-Ctl-2,1'],
            vars.TP_Btns['Disp-Aud-2,1'],
            vars.TP_Btns['Disp-Alert-2,1'],
            vars.TP_Btns['Disp-Scn-2,1'],
            vars.TP_Lbls['DispAdv-2,1'],
            vars.TP_Btns['Disp-Select-3,1'],
            vars.TP_Btns['Disp-Ctl-3,1'],
            vars.TP_Btns['Disp-Aud-3,1'],
            vars.TP_Btns['Disp-Alert-3,1'],
            vars.TP_Btns['Disp-Scn-3,1'],
            vars.TP_Lbls['DispAdv-3,1']
        ]
    
    
    #### =======================================================================
    
    #### PIN Code Module
    vars.PINCtl = PINController(vars.TP_Main,
                                vars.TP_Btns['Header-Settings'],
                                PinButtons,
                                vars.TP_Lbls['PIN-Label'],
                                settings.techPIN, 
                                'Tech')
    
    #### Source Control Module
    vars.SrcCtl = SourceController(vars.TP_Main,
                                   SourceButtons,
                                   AdvShareLayout,
                                   MatrixDict,
                                   settings.sources,
                                   settings.destinations)
    SOURCE_CONTROLLER = vars.SrcCtl
    
    #### Activity Control Module
    vars.ActCtl = ActivityController(vars.TP_Main,
                                     ActModBtns,
                                     TransitionDict,
                                     vars.TP_Lbls['ShutdownConf-Count'],
                                     vars.TP_Lvls['ShutdownConfIndicator'])
    ACTIVITY_CONTROLLER = vars.ActCtl
    
    #### Source Control Module
    sourceDict = {'select': vars.SourceButtons['select'],
                  'indicator': vars.SourceButtons['indicator'],
                  'arrows': vars.SourceButtons['arrowBtns']
                 }
    matrixDict = {
                  'btns': vars.MatrixBtns,
                  'ctls': vars.TP_Btn_Grps['Tech-Matrix-Mode'],
                  'del': vars.TP_Btns['Tech-Matrix-DeleteTies']
                 }
    vars.SrcCtl = SourceController(vars.TP_Main,
                                   sourceDict,
                                   matrixDict,
                                   settings.sources,
                                   settings.destinations)
    
    ## DO ADDITIONAL INITIALIZATION ITEMS HERE
    
    ProgramLog('System Initialized', 'info')
    return True

## End Function Definitions ----------------------------------------------------
##
## Event Definitions -----------------------------------------------------------

## End Events Definitions ------------------------------------------------------
##
## Start Program ---------------------------------------------------------------
Initialize()
