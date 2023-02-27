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
# SOURCE_CONTROLLER = None
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
        # utilityFunctions.Log('Set Public Properties')
        self.UIHost = UIHost
        self.CurrentActivity = 'off'
        self.startupTime = settings.startupTimer
        self.switchTime = settings.switchTimer
        self.shutdownTime = settings.shutdownTimer
        self.confirmationTime = settings.shutdownConfTimer
        self.splashTime = settings.activitySplashTimer
        
        # Private Properties ===================================================
        # utilityFunctions.Log('Set Private Properties')
        self._activityBtns = activityBtns
        self._confTimeLbl = confTimeLbl
        self._confTimeLvl = confTimeLvl
        self._transition = transitionDict
        
        # Inital Class Setup ===================================================
        # utilityFunctions.Log('Show Activity Popups, Mode: {}'.format(settings.activityMode))
        self.UIHost.ShowPopup('Menu-Activity-{}'.format(settings.activityMode))
        self.UIHost.ShowPopup('Menu-Activity-open-{}'.format(settings.activityMode))
        
        # utilityFunctions.Log("Create Timers")
        self._confirmationTimer = Timer(1, self._ConfimationHandler)
        self._confirmationTimer.Stop()
        
        self._switchTimer = Timer(1, self._SwitchTimerHandler)
        self._switchTimer.Stop()
        
        self._startTimer = Timer(1, self._StartUpTimerHandler)
        self._startTimer.Stop()
        
        self._shutdownTimer = Timer(1, self._ShutdownTimerHandler)
        self._shutdownTimer.Stop()
        
        self._activitySplashTimer = Timer(1, self._activitySplashWaitHandler)
        self._activitySplashTimer.Stop()
        
        self.__StatusTimer = Timer(5, self.__StatusTimerHandler)
        self.__StatusTimer.Stop()
        
        self._activityBtns['select'].SetCurrent(0)
        self._activityBtns['indicator'].SetCurrent(0)

        self._confTimeLvl.SetRange(0, self.confirmationTime, 1)
        self._confTimeLvl.SetLevel(0)

        # Class Event Definitions ==============================================
        # utilityFunctions.Log("Create Class Events")
        @event(self._activityBtns['select'].Objects, 'Pressed')
        def ActivityChange(button, action):
            if button.Name == "ActivitySelect-Off":
                # utilityFunctions.Log('Off mode selected - show confirmation')
                self.StartShutdownConfirmation()
            elif button.Name == "ActivitySelect-Share":
                # utilityFunctions.Log('Share mode selected')
                self._activityBtns['select'].SetCurrent(button)
                self._activityBtns['indicator'].SetCurrent(1)
                if self.CurrentActivity == 'off':
                    self.SystemStart('share')
                else:
                    self.SystemSwitch('share')
                self.CurrentActivity = 'share'
            elif button.Name == "ActivitySelect-AdvShare":
                # utilityFunctions.Log('Adv. Share mode selected')
                self._activityBtns['select'].SetCurrent(button)
                self._activityBtns['indicator'].SetCurrent(2)
                if self.CurrentActivity == 'off':
                    self.SystemStart('adv_share')
                else:
                    self.SystemSwitch('adv_share')
                self.CurrentActivity = 'adv_share'
            elif button.Name == "ActivitySelect-GroupWork":
                # utilityFunctions.Log('Group Work mode selected')
                self._activityBtns['select'].SetCurrent(button)
                self._activityBtns['indicator'].SetCurrent(3)
                if self.CurrentActivity == 'off':
                    self.SystemStart('group_work')
                else:
                    self.SystemSwitch('group_work')
                self.CurrentActivity = 'group_work'

        
        
        @event(self._activityBtns['end'], 'Pressed')
        def EndNow(button, action):
            # utilityFunctions.Log("Ending Session Now")
            self._confirmationTimer.Stop()
            self.SystemShutdown()
        
        @event(self._activityBtns['cancel'], 'Pressed')
        def CancelShutdown(button, action):
            self._confirmationTimer.Stop()
            self.UIHost.HidePopup("Shutdown-Confirmation")
        
        @event(self._switchTimer, 'StateChanged')        
        def SwitchTimerStateHandler(timer, state):
            if state == 'Stopped':
                if self.CurrentActivity == 'share' or self.CurrentActivity == 'group_work':
                    self._activitySplashTimer.Restart() 

        @event(vars.TP_Btns['Splash'], 'Pressed')
        def SplashScreenHandler(button, action):
            self.UIHost.ShowPage('Opening')
        
        @event(vars.TP_Btns['Activity-Splash-Close'], 'Pressed')
        def CloseTipHandler(button, action):
            self._activitySplashCloseHandler(self._activitySplashTimer)
    
    # Private Methods ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def __StatusTimerHandler(self, timer: Timer, count: int):
        if self.CurrentActivity == 'share':
            vars.SrcCtl.SourceAlertHandler()
        elif self.CurrentActivity == 'adv_share':
            for dest in vars.SrcCtl.Destinations:
                dest.AdvSourceAlertHandler()
        elif self.CurrentActivity == 'group_work':
            vars.SrcCtl.SourceAlertHandler()
        
    def _activitySplashWaitHandler(self, timer: Timer, count: int):
        timeTillClose = self.splashTime - count
        vars.TP_Btns['Activity-Splash-Close'].SetText('Close Tip ({})'.format(timeTillClose))
        
        if count > self.splashTime:
            self._activitySplashCloseHandler(timer)
            
    def _activitySplashCloseHandler(self, timer: Timer):
        timer.Stop()
        page = vars.SrcCtl.SelectedSource.SourceControlPage 
        if page == 'PC':
            page = '{p}_{c}'.format(p=page, c=len(settings.cameras))
        self.UIHost.ShowPopup("Source-Control-{}".format(page))
    
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
                # utilityFunctions.Log('System started in {} mode'.format(self._selectedActivity))
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
            # utilityFunctions.Log('System configured in {} mode'.format(self.CurrentActivity),
            #         'info')
    
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
            # utilityFunctions.Log('System shutdown', 'info')
    
    # Public Methods +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def StartShutdownConfirmation(self, click: bool=False):
        if self.CurrentActivity != 'off':
            if click:
                self.UIHost.Click(5, 0.2)
            self._confirmationTimer.Restart()
            self._confTimeLbl.SetText(utilityFunctions.TimeIntToStr(self.confirmationTime))
            self.UIHost.ShowPopup('Shutdown-Confirmation')
            
    def SystemStart(self, activity: str) -> None:
        # utilityFunctions.Log("System Start function activated", stack=True)
        self._selectedActivity = activity
        
        self._transition['label'].SetText(
            'System is switching on. Please Wait...')
        self._transition['level'].SetRange(0, self.startupTime, 1)
        self._transition['level'].SetLevel(0)

        self._transition['count'].SetText(
                utilityFunctions.TimeIntToStr(self.startupTime))
        self.UIHost.ShowPopup('Power-Transition')
        self.UIHost.ShowPage('Main')

        # utilityFunctions.Log('Startup Timer Restarting')
        self._startTimer.Restart()

        # STARTUP ONLY ITEMS HERE - function in main
        # utilityFunctions.Log('Performing unsynced Startup functions')
        vars.SrcCtl.SelectSource(settings.defaultSource)
        vars.SrcCtl.SwitchSources(vars.SrcCtl.SelectedSource, 'All')
        self._transition['start']['init']()
        
    def SystemSwitch(self, activity: str) -> None:
        # utilityFunctions.Log("System Switch function activated", stack=True)
        self._activitySplashTimer.Stop()
        self._selectedActivity = activity
        
        self.__StatusTimer.Restart()
        
        self._transition['label'].SetText(
            'System is switching to {} mode. Please Wait...'
            .format(self._activityDict[activity]))
        self._transition['level'].SetRange(0, self.switchTime, 1)
        self._transition['level'].SetLevel(0)

        self._transition['count'].SetText(
                utilityFunctions.TimeIntToStr(self.switchTime))
        self.UIHost.ShowPopup('Power-Transition')
        self.UIHost.ShowPage('Main')

        self.CurrentActivity = self._selectedActivity
        
        # utilityFunctions.Log('Activity Switch Timer Restarting')
        self._switchTimer.Restart()
        
        # TODO: Figure out a way to reset the activity timer
        #self.UIHost.InactivityTime = 0
        
        self.__StatusTimerHandler(None, None)

        # configure system for current activity
        # utilityFunctions.Log('Performing unsynced Activity Switch functions')
        # self.UIHost.HidePopupGroup(5) # Source-Controls Group
        if activity == "share":
            self._activityBtns['select'].SetCurrent(1)
            self._activityBtns['indicator'].SetCurrent(1)
            # utilityFunctions.Log('Configuring for Share mode')
            self.UIHost.HidePopupGroup(8) # Activity-Controls Group
            self.UIHost.ShowPopup("Audio-Control-{}-privacy".format('mic' if len(settings.microphones) > 0 else 'no_mic'))
            
            # get input assigned to the primaryDestination
            curSrc = vars.SrcCtl.PrimaryDestination.AssignedSource
            # utilityFunctions.Log("Pre-Activity Change Source - Name: {}, Id: {}".format(curSrc.Name, curSrc.Id))
            
            if curSrc.Name == 'None':
                # utilityFunctions.Log('Current Source = None, Setting current source to default, ID = {}'.format(settings.defaultSource))
                curSrc = vars.SrcCtl.GetSource(id=settings.defaultSource)
                # utilityFunctions.Log('New Current Source - Name: {}, ID: {}'.format(curSrc.Name, curSrc.Id))
                vars.SrcCtl.SelectSource(curSrc)
                # utilityFunctions.Log('Selected Source - Name: {}, Id: {}'.format(vars.SrcCtl.SelectedSource.Name, vars.SrcCtl.SelectedSource.Id))
                vars.SrcCtl.SetPrivacyOn()
            
            # update source selection to match primaryDestination
            vars.SrcCtl.SwitchSources(curSrc, 'All')
            
            # show activity splash screen, will be updated config.activitySplash
            # seconds after the activity switch timer stops
            vars.TP_Btns['Activity-Splash-Close'].SetText('Close Tip ({})'.format(self.splashTime))
            self.UIHost.ShowPopup("Source-Control-Splash-Share")
            
        elif activity == "adv_share":
            self._activityBtns['select'].SetCurrent(2)
            self._activityBtns['indicator'].SetCurrent(2)
            # utilityFunctions.Log('Configuring for Adv Share mode')
            self.UIHost.ShowPopup("Activity-Control-AdvShare")
            
            self.UIHost.ShowPopup(vars.SrcCtl.GetAdvShareLayout())
            self.UIHost.ShowPopup("Audio-Control-{}".format('mic' if len(settings.microphones) > 0 else 'no_mic'))
        
            if vars.SrcCtl.Privacy:
                # utilityFunctions.Log('Handling Privacy reconfigure for Adv Share')
                vars.SrcCtl.SetPrivacyOff()
                destList = []
                for dest in vars.SrcCtl.Destinations:
                    if dest._type != 'conf':
                        # utilityFunctions.Log('Non-Confidence destination found - {}'.format(dest.Name))
                        destList.append(dest)
                # utilityFunctions.Log('Count of non-Confidence destinations: {}'.format(len(destList)))
                vars.SrcCtl.SwitchSources(vars.SrcCtl._none_source, destList)
                        
        elif  activity == "group_work":
            self._activityBtns['select'].SetCurrent(3)
            self._activityBtns['indicator'].SetCurrent(3)
            # utilityFunctions.Log('Configuring for Group Work mode')
            self.UIHost.ShowPopup("Activity-Control-Group")
            self.UIHost.ShowPopup("Audio-Control-{}-privacy".format('mic' if len(settings.microphones) > 0 else 'no_mic'))
            
            vars.SrcCtl.SelectSource(vars.SrcCtl.PrimaryDestination.GroupWorkSource)
            for dest in vars.SrcCtl.Destinations:
                vars.SrcCtl.SwitchSources(dest.GroupWorkSource, [dest])
            vars.SrcCtl.SetPrivacyOff()
            
            # show activity splash screen, will be updated config.activitySplash
            # seconds after the activity switch timer stops
            vars.TP_Btns['Activity-Splash-Close'].SetText('Close Tip ({})'.format(self.splashTime))
            self.UIHost.ShowPopup("Source-Control-Splash-GrpWrk")

        self._transition['switch']['init']()

    def SystemShutdown(self) -> None:
        # utilityFunctions.Log("System Switch function activated", stack=True)
        self._activityBtns['select'].SetCurrent(0)
        self._activityBtns['indicator'].SetCurrent(0)
        self.CurrentActivity = 'off'
        
        self.__StatusTimer.Stop()

        self._transition['label']\
            .SetText('System is switching off. Please Wait...')
        self._transition['level'].SetRange(0, self.shutdownTime, 1)
        self._transition['level'].SetLevel(0)
        
        self._transition['count'].SetText(
                utilityFunctions.TimeIntToStr(self.shutdownTime))
        self.UIHost.ShowPopup('Power-Transition')
        self.UIHost.HidePopup("Shutdown-Confirmation")
        self.UIHost.ShowPage('Opening')

        # utilityFunctions.Log('Shutdown timer restarting')
        self._shutdownTimer.Restart()        
        
        # self.UIHost.InactivityTime = 0
        # TODO: Figure out a way to reset the activity timer
        
        # SHUTDOWN ITEMS HERE - function in main
        # utilityFunctions.Log('Performing unsynced Shutdown functions')
        self._transition['shutdown']['init']()

## End Class Definitions -------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------
# def UpdateSourceContoller(SrcCtl):
#     SOURCE_CONTROLLER = SrcCtl

## End Function Definitions ----------------------------------------------------



