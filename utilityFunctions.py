## Begin ControlScript Import --------------------------------------------------
# from extronlib import event, Version
# from extronlib.device import eBUSDevice, ProcessorDevice, UIDevice
# from extronlib.interface import (CircuitBreakerInterface, ContactInterface,
#     DigitalInputInterface, DigitalIOInterface, EthernetClientInterface,
#     EthernetServerInterfaceEx, FlexIOInterface, IRInterface, PoEInterface,
#     RelayInterface, SerialInterface, SWACReceptacleInterface, SWPowerInterface,
#     VolumeInterface)
# from extronlib.ui import Button, Knob, Label, Level, Slider
# from extronlib.system import (Email, Clock, MESet, Timer, Wait, File, RFile,
#     ProgramLog, SaveProgramLog, Ping, WakeOnLan, SetAutomaticTime, SetTimeZone)
#
#print(Version()) ## Sanity check ControlScript Import
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

#### Extron Global Scripter Modules

## End User Import -------------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------

def TimeIntToStr(time: int, units: bool = True) -> str:
    """Converts integer seconds to human readable string

    Args:
        time (int): integer time in seconds
        units (bool, optional): True to display units (m minutes s seconds) or
            false to return a unitless string (DD:HH:MM:SS). Defaults to True.

    Returns:
        str: Time string
    """    
    returnStr = ''
    seconds = 0
    minutes = 0
    hours = 0
    days = 0

    if time < 60:
        seconds = time
    elif time > 60:
        seconds = time % 60
        minutes = time // 60
        if minutes > 60:
            hours = minutes // 60
            minutes = minutes % 60
            if hours > 24:
                days = hours // 24
                hours = hours % 24

    if units:
        uS = "seconds"
        uM = "minutes"
        uH = "hours"
        uD = "days"
        if seconds == 1:
            uS = 'second'
        if minutes == 1:
            uM = 'minute'
        if hours == 1:
            uH = 'hour'
        if days == 1:
            uD = 'day'
        if days != 0:
            returnStr = "{d} {unitD}, {hr} {unitH}, {min} {unitM}, {sec} {unitS}"\
                .format(d=days,
                        unitD=uD,
                        hr=hours,
                        unitH=uH,
                        min=minutes,
                        unitM=uM,
                        sec=seconds,
                        unitS=uS)
        elif days == 0 and hours != 0:
            returnStr = "{hr} {unitH}, {min} {unitM}, {sec} {unitS}"\
                .format(hr=hours,
                        unitH=uH,
                        min=minutes,
                        unitM=uM,
                        sec=seconds,
                        unitS=uS)
        elif days == 0 and hours == 0 and minutes != 0:
            returnStr = "{min} {unitM}, {sec} {unitS}"\
                .format(min=minutes,
                        unitM=uM,
                        sec=seconds,
                        unitS=uS)
        elif days == 0 and hours == 0 and minutes == 0:
            returnStr = "{sec} {unitS}".format(sec=seconds, unitS=uS)
    else:
        returnStr = "{d}:{hr}:{min}:{sec}".format(d=days,
                                                  hr=str(hours).zfill(2),
                                                  min=str(minutes).zfill(2),
                                                  sec=str(seconds).zfill(2))

    return returnStr

## End Function Definitions ----------------------------------------------------
##
## Begin Script Definition -----------------------------------------------------
if __name__ == "__main__": ## this module does not run as a script
    pass
## End Script Definition -------------------------------------------------------


