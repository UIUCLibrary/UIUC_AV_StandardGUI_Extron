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
from typing import Dict, Tuple, List, Union, Callable
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
#### Custom Code Modules
import utilityFunctions
import vars
import settings

#### Extron Global Scripter Modules

## End User Import -------------------------------------------------------------
##
SOURCE_CONTROLLER = None
##
## Begin Class Definitions -----------------------------------------------------

class ActivityController:
    _activityDict = \
        {
            "share": "Sharing", 
            "adv_share": "Adv. Sharing",
            "group_work": "Group Work"
        }
    def __init__(self,
                 UIHost: UIDevice,
                 activityBtns: Dict[str, Union[MESet, Button]],
                 transitionDict: Dict[str, Union[Label, Level, Dict[str, Callable]]],
                 confTimeLbl: Label,
                 confTimeLvl: Level) -> None:
        """Initializes the Activity Selection Controller
    
        Args:
            UIHost (extronlib.device): UIHost to which the buttons are assigned
            activityBtns (Dict[str, Union[extronlib.system.MESet, extronlib.system.MESet, extronlib.ui.Button, extronlib.ui.Button]]): a dictionary of activity buttons. Should contain the following keys/value pairs:
                select: MESet of selection buttons
                indicator: MESet of indicator buttons
                end: Shutdown Confirmation End Now button
                cancel: Shutdown confirmation cancel shutdown button
            transitionDict (Dict[str, Union[extronlib.ui.Label, extronlib.ui.Level, Dict[str, Callable]]]): a dictionary of transition items. Should contain the following keys/value pairs:
                label: Power transition state label
                level: Power transition progress bar
                count: Power transition count label
                start: Dict containing the following key/value pairs:
                    init: Callback when start begins, takes no arguments
                    sync: Callback synced to statup progress, take a count argument corresponding to the startup progress
                switch: Dict containing the following key/value pairs:
                    init: Callback when switch begins, takes no arguments
                    sync: Callback synced to switch progress, take a count argument corresponding to the startup progress
                shutdown: Dict containing the following key/value pairs:
                    init: Callback when shutdown begins, takes no arguments
                    sync: Callback synced to shutdown progress, take a count argument corresponding to the startup progress
            confTimeLbl (extronlib.ui.Label): Shutdown confirmation text label
            confTimeLvl (extronlib.ui.Level): Shutdown confirmation level indicator

        Returns:
            bool: True on success or False on failure
        """
        # Public Properties ====================================================
        self.UIHost = UIHost
        self.CurrentActivity = 'off'
        self.startupTime = settings.startupTimer
        self.switchTime = settings.switchTimer
        self.shutdownTime = settings.shutdownTimer
        self.confirmationTime = settings.shutdownConfTimer
        self.splashTime = settings.activitySplashTimer
        
        # Private Properties ===================================================
        self._activityBtns = activityBtns
        self._confTimeLbl = confTimeLbl
        self._confTimeLvl = confTimeLvl
        self._transition = transitionDict
        
        # Inital Class Setup ===================================================
        self.UIHost.ShowPopup('Menu-Activity-{}'.format(settings.activityMode))
        self.UIHost.ShowPopup('Menu-Activity-open-{}'.format(settings.activityMode))
        
        self._confirmationTimer = Timer(1, self._ConfimationHandler)
        self._confirmationTimer.Stop()
        
        self._switchTimer = Timer(1, self._SwitchTimerHandler)
        self._switchTimer.Stop()
        
        self._startTimer = Timer(1, self._StartUpTimerHandler)
        self._startTimer.Stop()
        
        self._shutdownTimer = Timer(1, self._ShutdownTimerHandler)
        self._shutdownTimer.Stop()
        
        self._activityBtns['select'].SetCurrent(0)
        self._activityBtns['indicator'].SetCurrent(0)

        self._confTimeLvl.SetRange(0, self.confirmationTime, 1)
        self._confTimeLvl.SetLevel(0)

        # Class Event Definitions ==============================================
        @event(self._activityBtns['select'].Objects, 'Pressed')
        def ActivityChange(button, action):
            if button.Name == "ActivitySelect-Off":
                self._activityBtns['indicator'].SetCurrent(0)
                if self.CurrentActivity != 'off':
                    self._confirmationTimer.Restart()
                    self.UIHost.ShowPopup('Shutdown-Confirmation')
                self.CurrentActivity = 'off'
            elif button.Name == "ActivitySelect-Share":
                self._activityBtns['indicator'].SetCurrent(1)
                if self.CurrentActivity == 'off':
                    self.SystemStart('share')
                else:
                    self.SystemSwitch('share')
                self.CurrentActivity = 'share'
            elif button.Name == "ActivitySelect-AdvShare":
                self._activityBtns['indicator'].SetCurrent(2)
                if self.CurrentActivity == 'off':
                    self.SystemStart('adv_share')
                else:
                    self.SystemSwitch('adv_share')
                self.CurrentActivity = 'adv_share'
            elif button.Name == "ActivitySelect-GroupWork":
                self._activityBtns['indicator'].SetCurrent(3)
                if self.CurrentActivity == 'off':
                    self.SystemStart('group_work')
                else:
                    self.SystemSwitch('group_work')
                self.CurrentActivity = 'group_work'
        
        @event(self._activityBtns['end'], 'Pressed')
        def EndNow(button, action):
            self._confirmationTimer.Stop()
            self.SystemShutdown()
        
        @event(self._activityBtns['cancel'], 'Pressed')
        def CancelShutdown(button, action):
            self._confirmationTimer.Stop()
            self.UIHost.HidePopup("Shutdown-Confirmation")
        
        @event(self._switchTimer, 'StateChanged')        
        def SwitchTimerStateHandler(timer, state):
            if state == 'Stopped':
                if self.CurrentActivity == 'share' or self.CurrentActivity == 'group-work':
                    @Wait(self.splashTime) 
                    def activitySplash():
                        page = SOURCE_CONTROLLER.SelectedSource._sourceControlPage 
                        if page == 'PC':
                            page = '{p}_{c}'.format(p=page, c=len(settings.cameras))
                        self.UIHost.ShowPopup("Source-Control-{}".format(page))
    
    # Private Methods ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    def _ConfimationHandler(self, timer: Timer, count: int) -> None:
        timeTillShutdown = self.confirmationTime - count

        self._confTimeLbl.SetText(utilityFunctions.TimeIntToStr(timeTillShutdown))
        self._confTimeLvl.SetLevel(count)
        if count >= self.confirmationTime:
            timer.Stop()
            self.SystemShutdown()
            
    def _StartUpTimerHandler(self, timer: Timer, count: int) -> None:
            timeRemaining = self.startupTime - count

            self._transition['count'].SetText(
                utilityFunctions.TimeIntToStr(timeRemaining))
            self._transition['level'].SetLevel(count)

            # TIME SYNCED SWITCH ITEMS HERE - function in main
            self._transition['start']['sync'](count)

            # feedback can be used here to jump out of the startup process early

            if count >= self.startupTime:
                timer.Stop()
                print('System started in {} mode'.format(self._selectedActivity))
                ProgramLog('System started in {} mode'.format(self._selectedActivity), 'info')
                self.SystemSwitch(self._selectedActivity)
                
    def _SwitchTimerHandler(self, timer: Timer, count: int) -> None:
        timeRemaining = self.switchTime - count

        self._transition['count'].SetText(
            utilityFunctions.TimeIntToStr(timeRemaining))
        self._transition['level'].SetLevel(count)

        # TIME SYNCED SWITCH ITEMS HERE - function in Main
        self._transition['switch']['sync'](count)

        # feedback can be used here to jump out of the switch process early

        if count >= self.switchTime:
            timer.Stop()
            self.UIHost.HidePopup('Power-Transition')
            print('System configured in {} mode'.format(self.CurrentActivity))
            ProgramLog('System configured in {} mode'.format(self.CurrentActivity),
                    'info')
    
    def _ShutdownTimerHandler(self, timer: Timer, count: int) -> None:
        timeRemaining = self.shutdownTime - count

        self._transition['count'].SetText(utilityFunctions.TimeIntToStr(timeRemaining))
        self._transition['level'].SetLevel(count)

        # TIME SYNCED SHUTDOWN ITEMS HERE - function in main
        self._transition['shutdown']['sync'](count)

        # feedback can be used here to jump out of the shutdown process early

        if count >= self.shutdownTime:
            timer.Stop()
            self.UIHost.HidePopup('Power-Transition')
            print('System shutdown')
            ProgramLog('System shutdown', 'info')
    
    # Public Methods +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    def SystemStart(self, activity: str) -> None:
        self._selectedActivity = activity
        
        self._transition['label'].SetText(
            'System is switching on. Please Wait...')
        self._transition['level'].SetRange(0, self.startupTime, 1)
        self._transition['level'].SetLevel(0)

        self.UIHost.ShowPopup('Power-Transition')
        self.UIHost.ShowPage('Main')

        self._startTimer.Restart()

        # STARTUP ONLY ITEMS HERE - function in main
        SOURCE_CONTROLLER.SelectSource(settings.defaultSource)
        SOURCE_CONTROLLER.SwitchSources(SOURCE_CONTROLLER.SelectedSource, 'All')
        self._transition['start']['init']()
        
    def SystemSwitch(self, activity: str) -> None:
        self._selectedActivity = activity
        
        self._transition['label'].SetText(
            'System is switching to {} mode. Please Wait...'
            .format(self._activityDict[activity]))
        self._transition['level'].SetRange(0, self.switchTime, 1)
        self._transition['level'].SetLevel(0)

        self.UIHost.ShowPopup('Power-Transition')
        self.UIHost.ShowPage('Main')

        self.CurrentActivity = self._selectedActivity
        self._switchTimer.Restart()

        # configure system for current activity
        self.UIHost.HidePopupGroup('Source-Controls')
        if activity == "share":
            self.UIHost.HidePopupGroup('Activity-Controls')
            # get input assigned to the primaryDestination
            curSrc = SOURCE_CONTROLLER.PrimaryDestination.AssignedSource
            
            # update source selection to match primaryDestination
            for dest in SOURCE_CONTROLLER.Destinations:
                if dest.AssignedSource != curSrc:
                    dest.AssignSource(curSrc)
            
            self.UIHost.ShowPopup("Audio-Control-{},P".format(settings.micCtl))
            
            # show activity splash screen, will be updated config.activitySplash
            # seconds after the activity switch timer stops
            self.UIHost.ShowPopup("Source-Control-Splash-Share")
            
        elif activity == "adv_share":
            self.UIHost.ShowPopup("Activity-Control-AdvShare")
            
            self.UIHost.ShowPopup(SOURCE_CONTROLLER.GetAdvShareLayout())
            # TODO: get inputs assigned to destination outputs, update destination
            # buttons for these assignments
            self.UIHost.ShowPopup("Audio-Control-{}".format(settings.micCtl))
        
        elif  activity == "group_work":
            self.UIHost.ShowPopup("Activity-Control-Group")
            self.UIHost.ShowPopup("Audio-Control-{},P".format(settings.micCtl))
            for dest in SOURCE_CONTROLLER.Destinations:
                SOURCE_CONTROLLER.SwitchSources(dest.GroupWorkSource, [dest])
            
        SOURCE_CONTROLLER.ShowSelectedSource()

    def SystemShutdown(self) -> None:
        self.CurrentActivity = 'off'

        self._transition['label']\
            .SetText('System is switching off. Please Wait...')
        self._transition['level'].SetRange(0, self.shutdownTime, 1)
        self._transition['level'].SetLevel(0)
        
        self.UIHost.ShowPopup('Power-Transition')
        self.UIHost.ShowPage('Opening')

        self._shutdownTimer.Restart()        
        
        # SHUTDOWN ITEMS HERE - function in main
        self._transition['shutdown']['init']()

## End Class Definitions -------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------
def UpdateSourceContoller(SrcCtl):
    SOURCE_CONTROLLER = SrcCtl

## End Function Definitions ----------------------------------------------------



