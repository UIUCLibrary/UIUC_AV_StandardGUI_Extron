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
from typing import Dict, Tuple, List

## End Python Imports ----------------------------------------------------------
##
## Begin User Import -----------------------------------------------------------
#### Custom Code Modules
import utilityFunctions
import settings
import vars

import uofi_gui.systemHardware as SysHW

#### Extron Global Scripter Modules

## End User Import -------------------------------------------------------------
##
## Begin Class Definitions -----------------------------------------------------

## End Class Definitions -------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------

def WPD_Mersive_Feedback(hardware, blank_on_fail = True) -> None:
    podIdLabel = vars.TP_Lbls['WPD-PodIDs']
    podKeyLabel = vars.TP_Lbls['WPD-Key']
    
    podHW = None
    
    if type(hardware) is str:
        utilityFunctions.Log('Hardware ID String Submitted - {}'.format(hardware))
        podHW = vars.Hardware.get(hardware, None)
    elif type(hardware) is SysHW.SystemHardwareController:
        podHW = hardware
    
    if podHW is not None:
        podStatus = podHW.interface.ReadStatus('PodStatus')
        podName = podStatus['m_displayInformation']['m_displayName']
        podIP = podStatus['m_displayInformation']['m_ipv4']
        podKey = podStatus['m_authenticationCuration']['sessionKey']

        podIdLabel.SetText('{} ({})'.format(podName, podIP))
        podKeyLabel.SetText('Key: {}'.format(podKey))
    elif blank_on_fail:
        utilityFunctions.Log('Pod HW not found')
        podIdLabel.SetText('')
        podKeyLabel.SetText('')
        
def WPD_Mersive_StatusHandler(command, value, qualifier, hardware=None):
    utilityFunctions.Log('{} Callback; Value: {}; Qualifier {}'.format(hardware.Name, command, value, qualifier))
    
    if vars.ActCtl.CurrentActivity != 'adv_share':
        if vars.SrcCtl.SelectedSource.Id == hardware.Id:
            WPD_Mersive_Feedback(hardware, blank_on_fail=False)
    else:
        if (vars.SrcCtl.OpenControlPopup is not None and
            vars.SrcCtl.OpenControlPopup['page'] == 'Modal-SrcCtl-WPD' and 
            vars.SrcCtl.OpenControlPopup['source'].Id == hardware.Id):
                WPD_Mersive_Feedback(hardware, blank_on_fail=False)

def DSP_BiampTesira_MuteHandler(command, value, qualifier, hardware=None):
    utilityFunctions.Log('{} Callback; Value: {}; Qualifier {}'.format(hardware.Name, command, value, qualifier))
    
def DSP_BiampTesira_LevelHandler(command, value, qualifier, hardware=None):
    utilityFunctions.Log('{} Callback; Value: {}; Qualifier {}'.format(hardware.Name, command, value, qualifier))
    
    
## End Function Definitions ----------------------------------------------------



