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
## End Python Imports ----------------------------------------------------------
##
## Begin User Import -----------------------------------------------------------
#### Custom Code Modules
from uofi_gui.activityControls import ActivityController
from uofi_gui.pinControl import PINController
from uofi_gui.uiObjects import (BuildButtons, BuildButtonGroups, BuildKnobs,
                                BuildLabels, BuildLevels, BuildSliders)
from uofi_gui.sourceControls import SourceController


import utilityFunctions as utFn
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

#### Build Buttons & Button Groups
vars.TP_Btns = BuildButtons(vars.TP_Main, jsonPath='controls.json')
vars.TP_Btn_Grps = BuildButtonGroups(vars.TP_Btns, jsonPath="controls.json")

#### Build Knobs
vars.TP_Knobs = BuildKnobs(vars.TP_Main, jsonPath='controls.json')

#### Build Levels
vars.TP_Lvls = BuildLevels(vars.TP_Main, jsonPath='controls.json')

#### Build Sliders
vars.TP_Slds = BuildSliders(vars.TP_Main, jsonPath='controls.json')

#### Build Labels
vars.TP_Lbls = BuildLabels(vars.TP_Main, jsonPath='controls.json')

## End Device/User Interface Definition ----------------------------------------
##
## Begin Communication Interface Definition ------------------------------------

## End Communication Interface Definition --------------------------------------
##
## Begin Function Definitions --------------------------------------------------

def StartupActions() -> None:
    pass

def StartUpSyncedActions(count: int) -> None:
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
    vars.TransitionDict = \
        {
            "label": vars.TP_Lbls['PowerTransLabel-State'],
            "level": vars.TP_Lvls['PowerTransIndicator'],
            "count": vars.TP_Lbls['PowerTransLabel-Count'],
            "start": {
                "init": StartupActions,
                "sync": StartUpSyncedActions
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
        
    vars.SourceButtons = \
        {
            "select": vars.TP_Btn_Grps['Source-Select'],
            "indicator": vars.TP_Btn_Grps['Source-Indicator'],
            "arrows": [
                vars.TP_Btns['SourceMenu-Prev'],
                vars.TP_Btns['SourceMenu-Next']
              ]
        }
        
    vars.ActModBtns = {"select": vars.TP_Btn_Grps['Activity-Select'],
                       "indicator": vars.TP_Btn_Grps['Activity-Indicator'],
                       "end": vars.TP_Btns['Shutdown-EndNow'],
                       "cancel": vars.TP_Btns['Shutdown-Cancel']}
    
    vars.PinButtons = \
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
        
    vars.MatrixBtns = \
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
        ]
    
    #### =======================================================================
    
    #### PIN Code Module
    vars.PINCtl = PINController(vars.TP_Main,
                                vars.TP_Btns['Header-Settings'],
                                vars.PinButtons,
                                vars.TP_Lbls['PIN-Label'],
                                settings.techPIN, 
                                'Tech')

    #### Activity Control Module
    vars.ActCtl = ActivityController(vars.TP_Main,
                                     vars.ActModBtns,
                                     vars.TransitionDict,
                                     vars.TP_Lbls['ShutdownConf-Count'],
                                     vars.TP_Lvls['ShutdownConfIndicator'])

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
    
    print('System Initialized')
    return True

## End Function Definitions ----------------------------------------------------
##
## Event Definitions -----------------------------------------------------------

## End Events Definitions ------------------------------------------------------
##
## Start Program ---------------------------------------------------------------
Initialize()
