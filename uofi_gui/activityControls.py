from typing import TYPE_CHECKING, Dict, Tuple, List, Union, Callable
if TYPE_CHECKING:
    from uofi_gui import GUIController
    from uofi_gui.uiObjects import ExUIDevice

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
# import utilityFunctions
from utilityFunctions import Log, RunAsync, TimeIntToStr, debug
#### Extron Global Scripter Modules

## End User Import -------------------------------------------------------------
##
# SOURCE_CONTROLLER = None
##
## Begin Class Definitions -----------------------------------------------------

class ActivityController:
    __activityDict = \
        {
            "share": "Sharing", 
            "adv_share": "Adv. Sharing",
            "group_work": "Group Work"
        }
    def __init__(self, GUIHost: 'GUIController') -> None:
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
        """
        
        self.GUIHost = GUIHost
        self.CurrentActivity = 'off'
        self.startupTime = self.GUIHost.Timers['startup']
        self.switchTime = self.GUIHost.Timers['switch']
        self.shutdownTime = self.GUIHost.Timers['shutdown']
        self.confirmationTime = self.GUIHost.Timers['shutdownConf']
        self.splashTime = self.GUIHost.Timers['activitySplash']
        
        self._activityBtns = \
            {
                "select": [tp.Btn_Grps['Activity-Select'] for tp in self.GUIHost.TPs],
                "indicator": [tp.Btn_Grps['Activity-Indicator'] for tp in self.GUIHost.TPs],
                "end": [tp.Btns['Shutdown-EndNow'] for tp in self.GUIHost.TPs],
                "cancel": [tp.Btns['Shutdown-Cancel'] for tp in self.GUIHost.TPs]
            }
        for set in self._activityBtns['select']:
            @event(set.Objects, 'Pressed')
            def ActivityChange(button: 'Button', action: str):
                Log('Activity Select: {} ({})'.format(button.Name, button))
                self.__ActivityButtonHandler(button, action)
        
        @event(self._activityBtns['end'], 'Pressed')
        def EndNow(button: 'Button', action: str):
            self._confirmationTimer.Stop()
            self.SystemShutdown()
        
        @event(self._activityBtns['cancel'], 'Pressed')
        def CancelShutdown(button: 'Button', action: str):
            self._confirmationTimer.Stop()
            for tp in self.GUIHost.TPs:
                tp.HidePopup("Shutdown-Confirmation")
        
        self._confTimeLbl = [tp.Lbls['ShutdownConf-Count'] for tp in self.GUIHost.TPs]
        self._confTimeLvl = [tp.Lvls['ShutdownConfIndicator'] for tp in self.GUIHost.TPs]
        self._transition = \
            {
                "label": [tp.Lbls['PowerTransLabel-State'] for tp in self.GUIHost.TPs],
                "level": [tp.Lvls['PowerTransIndicator'] for tp in self.GUIHost.TPs],
                "count": [tp.Lbls['PowerTransLabel-Count'] for tp in self.GUIHost.TPs],
                "start": {
                    "init": self.GUIHost.StartupActions,
                    "sync": self.GUIHost.StartupSyncedActions
                },
                "switch": {
                    "init": self.GUIHost.SwitchActions,
                    "sync": self.GUIHost.SwitchSyncedActions
                },
                "shutdown": {
                    "init": self.GUIHost.ShutdownActions,
                    "sync": self.GUIHost.ShutdownSyncedActions
                }
            }
            
        self._all_splashCloseBtns = [tp.Btns['Activity-Splash-Close'] for tp in self.GUIHost.TPs]
        for i in range(len(self._all_splashCloseBtns)):
            self._all_splashCloseBtns[i].TPIndex = i
        self._all_splashBtns = [tp.Btns['Splash'] for tp in self.GUIHost.TPs]
        
        for tp in self.GUIHost.TPs:
            tp.ShowPopup('Menu-Activity-{}'.format(self.GUIHost.ActivityMode))
            tp.ShowPopup('Menu-Activity-open-{}'.format(self.GUIHost.ActivityMode))
        
        self._confirmationTimer = Timer(1, self._ConfimationHandler)
        self._confirmationTimer.Stop()
        
        self._switchTimer = Timer(1, self._SwitchTimerHandler)
        self._switchTimer.Stop()
        
        self._startTimer = Timer(1, self._StartUpTimerHandler)
        self._startTimer.Stop()
        
        self._shutdownTimer = Timer(1, self._ShutdownTimerHandler)
        self._shutdownTimer.Stop()
        
        self._activitySplashTimerList = []
        for i in range(len(self.GUIHost.TPs)):
            self._activitySplashTimerList.insert(i, Timer(1, self._activitySplashWaitHandler))
            self._activitySplashTimerList[i].TPIndex = i
            self._activitySplashTimerList[i].Stop()
        
        self.__StatusTimer = Timer(5, self.__StatusTimerHandler)
        self.__StatusTimer.Stop()
        
        for set in self._activityBtns['select']:
            set.SetCurrent(0)
        for set in self._activityBtns['indicator']:
            set.SetCurrent(0)

        for lvl in self._confTimeLvl:
            lvl.SetRange(0, self.confirmationTime, 1)
            lvl.SetLevel(0)
        
        @event(self._switchTimer, 'StateChanged')        
        def SwitchTimerStateHandler(timer: 'Timer', state: str):
            if state == 'Stopped':
                if self.CurrentActivity == 'share' or self.CurrentActivity == 'group_work':
                    for timer in self._activitySplashTimerList:
                        timer.Restart() 

        @event(self._all_splashBtns, 'Pressed')
        def SplashScreenHandler(button: 'Button', action: str):
            for tp in self.GUIHost.TPs:
                tp.ShowPage('Opening')
        
        @event(self._all_splashCloseBtns, 'Pressed')
        def CloseTipHandler(button: 'Button', action: str):
            self._activitySplashCloseHandler(self._activitySplashTimerList[button.TPIndex])
    
    # Private Methods ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def __ActivityButtonHandler(self, button: 'Button', action: str):
        Log('Activity Select: {} ({})'.format(button.Name, button))
        if button.Name == "ActivitySelect-Off":
            # Log('Off mode selected - show confirmation')
            self.StartShutdownConfirmation()
        elif button.Name == "ActivitySelect-Share":
            # Log('Share mode selected')
            for i in range(len(self.GUIHost.TPs)):
                self._activityBtns['select'][i].SetCurrent(button)
                self._activityBtns['indicator'][i].SetCurrent(1)
            if self.CurrentActivity == 'off':
                self.SystemStart('share')
            else:
                self.SystemSwitch('share')
            self.CurrentActivity = 'share'
        elif button.Name == "ActivitySelect-AdvShare":
            # Log('Adv. Share mode selected')
            for i in range(len(self.GUIHost.TPs)):
                self._activityBtns['select'][i].SetCurrent(button)
                self._activityBtns['indicator'][i].SetCurrent(2)
            if self.CurrentActivity == 'off':
                self.SystemStart('adv_share')
            else:
                self.SystemSwitch('adv_share')
            self.CurrentActivity = 'adv_share'
        elif button.Name == "ActivitySelect-GroupWork":
            # Log('Group Work mode selected')
            for i in range(len(self.GUIHost.TPs)):
                self._activityBtns['select'][i].SetCurrent(button)
                self._activityBtns['indicator'][i].SetCurrent(3)
            if self.CurrentActivity == 'off':
                self.SystemStart('group_work')
            else:
                self.SystemSwitch('group_work')
            self.CurrentActivity = 'group_work'
    
    def __StatusTimerHandler(self, timer: Timer, count: int):
        if self.CurrentActivity == 'share':
            for tp in self.GUIHost.TPs:
                tp.SrcCtl.SourceAlertHandler()
        elif self.CurrentActivity == 'adv_share':
            for tp in self.GUIHost.TPs:
                for dest in tp.SrcCtl.Destinations:
                    dest.AdvSourceAlertHandler()
        elif self.CurrentActivity == 'group_work':
            for tp in self.GUIHost.TPs:
                tp.SrcCtl.SourceAlertHandler()
        
    def _activitySplashWaitHandler(self, timer: Timer, count: int):
        timeTillClose = self.splashTime - count
        self.GUIHost.TPs[timer.TPIndex].Btns['Activity-Splash-Close'].SetText('Close Tip ({})'.format(timeTillClose))
        
        if count > self.splashTime:
            self._activitySplashCloseHandler(timer)
            
    def _activitySplashCloseHandler(self, timer: Timer):
        timer.Stop()
        page = self.GUIHost.TPs[timer.TPIndex].SrcCtl.SelectedSource.SourceControlPage 
        if page == 'PC':
            page = '{p}_{c}'.format(p=page, c=len(self.GUIHost.Cameras))
        self.GUIHost.TPs[timer.TPIndex].ShowPopup("Source-Control-{}".format(page))
    
    def _ConfimationHandler(self, timer: Timer, count: int) -> None:
        timeTillShutdown = self.confirmationTime - count

        for i in range(len(self.GUIHost.TPs)):
            self._confTimeLbl[i].SetText(TimeIntToStr(timeTillShutdown))
            self._confTimeLvl[i].SetLevel(count)
        if count >= self.confirmationTime:
            timer.Stop()
            self.SystemShutdown()
    
    def _StartUpTimerHandler(self, timer: Timer, count: int) -> None:
        timeRemaining = self.startupTime - count

        for i in range(len(self.GUIHost.TPs)):
            self._transition['count'][i].SetText(TimeIntToStr(timeRemaining))
            self._transition['level'][i].SetLevel(count)

        # TIME SYNCED SWITCH ITEMS HERE - function in main
        self._transition['start']['sync'](count)

        # feedback can be used here to jump out of the startup process early

        if count >= self.startupTime:
            timer.Stop()
            # Log('System started in {} mode'.format(self._selectedActivity))
            self.SystemSwitch(self._selectedActivity)
                
    def _SwitchTimerHandler(self, timer: Timer, count: int) -> None:
        timeRemaining = self.switchTime - count

        for i in range(len(self.GUIHost.TPs)):
            self._transition['count'][i].SetText(TimeIntToStr(timeRemaining))
            self._transition['level'][i].SetLevel(count)

        # TIME SYNCED SWITCH ITEMS HERE - function in Main
        self._transition['switch']['sync'](count)

        # feedback can be used here to jump out of the switch process early

        if count >= self.switchTime:
            timer.Stop()
            for tp in self.GUIHost.TPs:
                tp.HidePopup('Power-Transition')
            # Log('System configured in {} mode'.format(self.CurrentActivity))
    
    def _ShutdownTimerHandler(self, timer: Timer, count: int) -> None:
        timeRemaining = self.shutdownTime - count

        for i in range(len(self.GUIHost.TPs)):
            self._transition['count'][i].SetText(TimeIntToStr(timeRemaining))
            self._transition['level'][i].SetLevel(count)

        # TIME SYNCED SHUTDOWN ITEMS HERE - function in main
        self._transition['shutdown']['sync'](count)

        # feedback can be used here to jump out of the shutdown process early

        if count >= self.shutdownTime:
            timer.Stop()
            for tp in self.GUIHost.TPs:
                tp.HidePopup('Power-Transition')
            # Log('System shutdown')
    
    # Public Methods +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    @debug
    def StartShutdownConfirmation(self, click: bool=False):
        if self.CurrentActivity != 'off':
            self._confirmationTimer.Restart()
            for tp in self.GUIHost.TPs:
                Log(self._confTimeLbl)
                Log(self._confTimeLbl[self.GUIHost.TPs.index(tp)])
                self._confTimeLbl[self.GUIHost.TPs.index(tp)].SetText(TimeIntToStr(self.confirmationTime))
                if click:
                    tp.Click(5, 0.2)
                tp.ShowPopup('Shutdown-Confirmation')
            
    def SystemStart(self, activity: str) -> None:
        # Log("System Start function activated", stack=True)
        self._selectedActivity = activity
        
        for tp in self.GUIHost.TPs:
            index = self.GUIHost.TPs.index(tp)
            self._transition['label'][index].SetText('System is switching on. Please Wait...')
            self._transition['level'][index].SetRange(0, self.startupTime, 1)
            self._transition['level'][index].SetLevel(0)
            tp.TechCtl.CloseTechMenu()
            self._transition['count'][index].SetText(TimeIntToStr(self.startupTime))
            tp.ShowPopup('Power-Transition')
            tp.ShowPage('Main')
            
            tp.SrcCtl.SelectSource(self.GUIHost.DefaultSourceId)
            tp.SrcCtl.SwitchSources(tp.SrcCtl.SelectedSource, 'All')

        # Log('Startup Timer Restarting')
        self._startTimer.Restart()

        # STARTUP ONLY ITEMS HERE - function in main
        # Log('Performing unsynced Startup functions')
        self._transition['start']['init']()
        
    def SystemSwitch(self, activity: str) -> None:
        # Log("System Switch function activated", stack=True)
        for timer in self._activitySplashTimerList:
            timer.Stop()
        self._selectedActivity = activity
        
        self.__StatusTimer.Restart()
        
        for tp in self.GUIHost.TPs:
            index = self.GUIHost.TPs.index(tp)
            self._transition['label'][index].SetText('System is switching to {} mode. Please Wait...'.format(self.__activityDict[activity]))
            self._transition['level'][index].SetRange(0, self.switchTime, 1)
            self._transition['level'][index].SetLevel(0)

            self._transition['count'][index].SetText(TimeIntToStr(self.switchTime))
            tp.ShowPopup('Power-Transition')
            tp.ShowPage('Main')

        self.CurrentActivity = self._selectedActivity
        
        # Log('Activity Switch Timer Restarting')
        self._switchTimer.Restart()
        
        # TODO: Figure out a way to reset the activity timer
        #self.UIHost.InactivityTime = 0
        
        self.__StatusTimerHandler(None, None)

        # configure system for current activity
        # Log('Performing unsynced Activity Switch functions')
        # self.UIHost.HidePopupGroup(5) # Source-Controls Group
        
        for tp in self.GUIHost.TPs:
            self.ActivitySwitchTPConfiguration(activity, tp)

        self._transition['switch']['init']()

    def ActivitySwitchTPConfiguration(self, activity, touchPanel: 'ExUIDevice'):
        index = self.GUIHost.TPs.index(touchPanel)
        
        if activity == "share":
            self._activityBtns['select'][index].SetCurrent(1)
            self._activityBtns['indicator'][index].SetCurrent(1)
            # Log('Configuring for Share mode')
            touchPanel.HidePopupGroup(8) # Activity-Controls Group
            touchPanel.ShowPopup("Audio-Control-{}-privacy".format('mic' if len(self.GUIHost.Microphones) > 0 else 'no_mic'))
            
            # get input assigned to the primaryDestination
            curSrc = self.GUIHost.SrcCtl.PrimaryDestination.AssignedSource
            # Log("Pre-Activity Change Source - Name: {}, Id: {}".format(curSrc.Name, curSrc.Id))
            
            if curSrc.Name == 'None':
                # Log('Current Source = None, Setting current source to default, ID = {}'.format(self.UIHost.DefaultSourceID))
                curSrc = touchPanel.SrcCtl.GetSource(id=self.UIHost.DefaultSourceId)
                # Log('New Current Source - Name: {}, ID: {}'.format(curSrc.Name, curSrc.Id))
                touchPanel.SrcCtl.SelectSource(curSrc)
                # Log('Selected Source - Name: {}, Id: {}'.format(self.UIHost.SrcCtl.SelectedSource.Name, self.UIHost.SrcCtl.SelectedSource.Id))
                touchPanel.SrcCtl.SetPrivacyOn()
            
            # update source selection to match primaryDestination
            touchPanel.SrcCtl.SwitchSources(curSrc, 'All')
            
            # show activity splash screen, will be updated config.activitySplash
            # seconds after the activity switch timer stops
            touchPanel.Btns['Activity-Splash-Close'].SetText('Close Tip ({})'.format(self.splashTime))
            touchPanel.ShowPopup("Source-Control-Splash-Share")
            
        elif activity == "adv_share":
            self._activityBtns['select'][index].SetCurrent(2)
            self._activityBtns['indicator'][index].SetCurrent(2)
            # Log('Configuring for Adv Share mode')
            touchPanel.ShowPopup("Activity-Control-AdvShare")
            
            touchPanel.ShowPopup(touchPanel.SrcCtl.GetAdvShareLayout())
            touchPanel.ShowPopup("Audio-Control-{}".format('mic' if len(self.GUIHost.Microphones) > 0 else 'no_mic'))
        
            if self.GUIHost.SrcCtl.Privacy:
                # Log('Handling Privacy reconfigure for Adv Share')
                touchPanel.SrcCtl.SetPrivacyOff()
                destList = []
                for dest in touchPanel.SrcCtl.Destinations:
                    if dest._type != 'conf':
                        # Log('Non-Confidence destination found - {}'.format(dest.Name))
                        destList.append(dest)
                # Log('Count of non-Confidence destinations: {}'.format(len(destList)))
                touchPanel.SrcCtl.SwitchSources(touchPanel.SrcCtl._none_source, destList)
                        
        elif  activity == "group_work":
            self._activityBtns['select'][index].SetCurrent(3)
            self._activityBtns['indicator'][index].SetCurrent(3)
            # Log('Configuring for Group Work mode')
            touchPanel.ShowPopup("Activity-Control-Group")
            touchPanel.ShowPopup("Audio-Control-{}-privacy".format('mic' if len(self.GUIHost.Microphones) > 0 else 'no_mic'))
            
            touchPanel.SrcCtl.SelectSource(touchPanel.SrcCtl.PrimaryDestination.GroupWorkSource)
            for dest in touchPanel.SrcCtl.Destinations:
                touchPanel.SrcCtl.SwitchSources(dest.GroupWorkSource, [dest])
            touchPanel.SrcCtl.SetPrivacyOff()
            
            # show activity splash screen, will be updated config.activitySplash
            # seconds after the activity switch timer stops
            touchPanel.Btns['Activity-Splash-Close'].SetText('Close Tip ({})'.format(self.splashTime))
            touchPanel.ShowPopup("Source-Control-Splash-GrpWrk")

    def SystemShutdown(self) -> None:
        # Log("System Switch function activated", stack=True)
        self.CurrentActivity = 'off'
        self.__StatusTimer.Stop()
        
        for tp in self.GUIHost.TPs:
            index = self.GUIHost.TPs.index(tp)
            self._activityBtns['select'][index].SetCurrent(0)
            self._activityBtns['indicator'][index].SetCurrent(0)
        
            self._transition['label'][index].SetText('System is switching off. Please Wait...')
            self._transition['level'][index].SetRange(0, self.shutdownTime, 1)
            self._transition['level'][index].SetLevel(0)
        
            self._transition['count'][index].SetText(TimeIntToStr(self.shutdownTime))
            tp.ShowPopup('Power-Transition')
            tp.HidePopup("Shutdown-Confirmation")
            tp.ShowPage('Opening')

        # Log('Shutdown timer restarting')
        self._shutdownTimer.Restart()        
        
        # self.UIHost.InactivityTime = 0
        # TODO: Figure out a way to reset the activity timer
        
        # SHUTDOWN ITEMS HERE - function in main
        # Log('Performing unsynced Shutdown functions')
        self._transition['shutdown']['init']()

## End Class Definitions -------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------
# def UpdateSourceContoller(SrcCtl):
#     SOURCE_CONTROLLER = SrcCtl

## End Function Definitions ----------------------------------------------------



