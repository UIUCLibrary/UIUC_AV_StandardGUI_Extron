from typing import TYPE_CHECKING, Dict, Tuple, List, Union, Callable, cast
if TYPE_CHECKING: # pragma: no cover
    from uofi_gui import GUIController
    from uofi_gui.uiObjects import ExUIDevice
    from uofi_gui.sourceControls import MatrixTuple, Destination

## Begin ControlScript Import --------------------------------------------------
from extronlib import event
from extronlib.ui import Button
from extronlib.system import Timer

## End ControlScript Import ----------------------------------------------------
##
## Begin Python Imports --------------------------------------------------------

## End Python Imports ----------------------------------------------------------
##
## Begin User Import -----------------------------------------------------------
#### Custom Code Modules
from utilityFunctions import Log, RunAsync, TimeIntToStr, debug
#### Extron Global Scripter Modules

## End User Import -------------------------------------------------------------
##
# SOURCE_CONTROLLER = None
##
## Begin Class Definitions -----------------------------------------------------

class ActivityController:
    __ActivityDict = \
        {
            "share": "Sharing", 
            "adv_share": "Adv. Sharing",
            "group_work": "Group Work"
        }
    def __init__(self, GUIHost: 'GUIController') -> None:
        
        self.GUIHost = GUIHost
        self.CurrentActivity = 'off'
        self.__StartupTime = self.GUIHost.Timers['startup']
        self.__SwitchTime = self.GUIHost.Timers['switch']
        self.__ShutdownTime = self.GUIHost.Timers['shutdown']
        self.__ConfirmationTime = self.GUIHost.Timers['shutdownConf']
        self.__SplashTime = self.GUIHost.Timers['activitySplash']
        
        self.__ActivityBtns = \
            {
                "select": [tp.Btn_Grps['Activity-Select'] for tp in self.GUIHost.TPs],
                "indicator": [tp.Btn_Grps['Activity-Indicator'] for tp in self.GUIHost.TPs],
                "end": [tp.Btns['Shutdown-EndNow'] for tp in self.GUIHost.TPs],
                "cancel": [tp.Btns['Shutdown-Cancel'] for tp in self.GUIHost.TPs]
            }
        for set in self.__ActivityBtns['select']:
            set.SetCurrent(0)
        for set in self.__ActivityBtns['indicator']:
            set.SetCurrent(0)

        for lvl in self.__ConfTimeLvl:
            lvl.SetRange(0, self.__ConfirmationTime, 1)
            lvl.SetLevel(0)
        
        self.__ConfTimeLbl = [tp.Lbls['ShutdownConf-Count'] for tp in self.GUIHost.TPs]
        self.__ConfTimeLvl = [tp.Lvls['ShutdownConfIndicator'] for tp in self.GUIHost.TPs]
        self.__Transition = \
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
            
        self.__AllSplashCloseBtns = [tp.Btns['Activity-Splash-Close'] for tp in self.GUIHost.TPs]
        for i in range(len(self.__AllSplashCloseBtns)):
            self.__AllSplashCloseBtns[i].TPIndex = i
            
        self.__AllSplashBtns = [tp.Btns['Splash'] for tp in self.GUIHost.TPs]
        
        for tp in self.GUIHost.TPs:
            tp.ShowPopup('Menu-Activity-{}'.format(self.GUIHost.ActivityMode))
            tp.ShowPopup('Menu-Activity-open-{}'.format(self.GUIHost.ActivityMode))
        
        self.__ConfirmationTimer = Timer(1, self.__ConfirmationHandler)
        self.__ConfirmationTimer.Stop()
        
        self.__SwitchTimer = Timer(1, self.__SwitchTimerHandler)
        self.__SwitchTimer.Stop()
        
        self.__StartTimer = Timer(1, self.__StartUpTimerHandler)
        self.__StartTimer.Stop()
        
        self.__ShutdownTimer = Timer(1, self.__ShutdownTimerHandler)
        self.__ShutdownTimer.Stop()
        
        self.__InitPageTimer = Timer(60, self.__InitPageTimerHandler)
        self.__InitPageTimer.TriggerTime = self.GUIHost.Timers['initPage']
        self.__InitPageTimer.LastInactivity = {}
        self.__InitPageTimer.PanelInactivity = {}
        for tp in self.GUIHost.TPs:
            self.__InitPageTimer.LastInactivity[tp.Id] = 0
            self.__InitPageTimer.PanelInactivity[tp.Id] = 0
        self.__InitPageTimer.Restart()
        
        self.__ActivitySplashTimerList = []
        for i in range(len(self.GUIHost.TPs)):
            self.__ActivitySplashTimerList.insert(i, Timer(1, self.__ActivitySplashWaitHandler))
            self.__ActivitySplashTimerList[i].TPIndex = i
            self.__ActivitySplashTimerList[i].Stop()
        
        self.__StatusTimer = Timer(5, self.__StatusTimerHandler)
        self.__StatusTimer.Stop()
        
        for set in self.__ActivityBtns['select']:
            @event(set.Objects, 'Pressed') # pragma: no cover
            def ActivityButtonHandler(button: 'Button', action: str):
                self.__ActivityButtonHandler(button, action)
        
        @event(self.__ActivityBtns['end'], 'Pressed') # pragma: no cover
        def EndNow(button: 'Button', action: str):
            self.__EndNow(button, action)
        
        @event(self.__ActivityBtns['cancel'], 'Pressed') # pragma: no cover
        def CancelShutdown(button: 'Button', action: str):
            self.__CancelShutdown(button, action)
        
        @event(self.__SwitchTimer, 'StateChanged') # pragma: no cover
        def SwitchTimerStateHandler(timer: 'Timer', state: str):
            self.__SwitchTimerStateHandler(timer, state)

        @event(self.__AllSplashBtns, 'Pressed') # pragma: no cover
        def SplashScreenHandler(button: 'Button', action: str):
            self.__SplashScreenHandler(button, action)
        
        @event(self.__AllSplashCloseBtns, 'Pressed') # pragma: no cover
        def CloseTipHandler(button: 'Button', action: str):
            self.__CloseTipHandler(self.__ActivitySplashTimerList[button.TPIndex])
    
    # Event Handlers +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    def __ActivityButtonHandler(self, button: 'Button', action: str):
        Log('Activity Select: {} ({})'.format(button.Name, button))
        if button.Name == "ActivitySelect-Off":
            # Log('Off mode selected - show confirmation')
            self.StartShutdownConfirmation()
        elif button.Name == "ActivitySelect-Share":
            # Log('Share mode selected')
            for i in range(len(self.GUIHost.TPs)):
                self.__ActivityBtns['select'][i].SetCurrent(button)
                self.__ActivityBtns['indicator'][i].SetCurrent(1)
            if self.CurrentActivity == 'off':
                self.SystemStart('share')
            else:
                self.SystemSwitch('share')
            self.CurrentActivity = 'share'
        elif button.Name == "ActivitySelect-AdvShare":
            # Log('Adv. Share mode selected')
            for i in range(len(self.GUIHost.TPs)):
                self.__ActivityBtns['select'][i].SetCurrent(button)
                self.__ActivityBtns['indicator'][i].SetCurrent(2)
            if self.CurrentActivity == 'off':
                self.SystemStart('adv_share')
            else:
                self.SystemSwitch('adv_share')
            self.CurrentActivity = 'adv_share'
        elif button.Name == "ActivitySelect-GroupWork":
            # Log('Group Work mode selected')
            for i in range(len(self.GUIHost.TPs)):
                self.__ActivityBtns['select'][i].SetCurrent(button)
                self.__ActivityBtns['indicator'][i].SetCurrent(3)
            if self.CurrentActivity == 'off':
                self.SystemStart('group_work')
            else:
                self.SystemSwitch('group_work')
            self.CurrentActivity = 'group_work'
    
    def __EndNow(self, button: 'Button', action: str):
        self.__ConfirmationTimer.Stop()
        self.SystemShutdown()
            
    def __CancelShutdown(self, button: 'Button', action: str):
        self.__ConfirmationTimer.Stop()
        for tp in self.GUIHost.TPs:
            tp.HidePopup("Shutdown-Confirmation")
    
    def __SwitchTimerStateHandler(self, timer: 'Timer', state: str):
        if state == 'Stopped':
            if self.CurrentActivity == 'share' or self.CurrentActivity == 'group_work':
                for timer in self.__ActivitySplashTimerList:
                    timer.Restart() 
    
    def __SplashScreenHandler(self, button: 'Button', action: str):
        for tp in self.GUIHost.TPs:
            tp.ShowPage('Opening')
        
    def __CloseTipHandler(self, timer: Timer):
        timer.Stop()
        page = self.GUIHost.TPs[timer.TPIndex].SrcCtl.SelectedSource.SourceControlPage 
        if page == 'PC':
            page = '{p}_{c}'.format(p=page, c=len(self.GUIHost.Cameras))
        self.GUIHost.TPs[timer.TPIndex].ShowPopup("Source-Control-{}".format(page))
    
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
    
    def __ActivitySplashWaitHandler(self, timer: Timer, count: int):
        timeTillClose = self.__SplashTime - count
        self.GUIHost.TPs[timer.TPIndex].Btns['Activity-Splash-Close'].SetText('Close Tip ({})'.format(timeTillClose))
        
        if count > self.__SplashTime:
            self.__CloseTipHandler(timer)
    
    def __ConfirmationHandler(self, timer: Timer, count: int) -> None:
        timeTillShutdown = self.__ConfirmationTime - count

        for i in range(len(self.GUIHost.TPs)):
            self.__ConfTimeLbl[i].SetText(TimeIntToStr(timeTillShutdown))
            self.__ConfTimeLvl[i].SetLevel(count)
        if count >= self.__ConfirmationTime:
            timer.Stop()
            self.SystemShutdown()
    
    def __StartUpTimerHandler(self, timer: Timer, count: int) -> None:
        timeRemaining = self.__StartupTime - count

        for i in range(len(self.GUIHost.TPs)):
            self.__Transition['count'][i].SetText(TimeIntToStr(timeRemaining))
            self.__Transition['level'][i].SetLevel(count)

        # TIME SYNCED SWITCH ITEMS HERE - function in main
        self.__Transition['start']['sync'](count)

        # feedback can be used here to jump out of the startup process early

        if count >= self.__StartupTime:
            timer.Stop()
            # Log('System started in {} mode'.format(self.CurrentActivity))
            self.SystemSwitch(self.CurrentActivity)
                
    def __SwitchTimerHandler(self, timer: Timer, count: int) -> None:
        timeRemaining = self.__SwitchTime - count

        for i in range(len(self.GUIHost.TPs)):
            self.__Transition['count'][i].SetText(TimeIntToStr(timeRemaining))
            self.__Transition['level'][i].SetLevel(count)

        # TIME SYNCED SWITCH ITEMS HERE - function in Main
        self.__Transition['switch']['sync'](count)

        # feedback can be used here to jump out of the switch process early

        if count >= self.__SwitchTime:
            timer.Stop()
            for tp in self.GUIHost.TPs:
                tp.HidePopup('Power-Transition')
            # Log('System configured in {} mode'.format(self.CurrentActivity))
    
    def __ShutdownTimerHandler(self, timer: Timer, count: int) -> None:
        timeRemaining = self.__ShutdownTime - count

        for i in range(len(self.GUIHost.TPs)):
            self.__Transition['count'][i].SetText(TimeIntToStr(timeRemaining))
            self.__Transition['level'][i].SetLevel(count)

        # TIME SYNCED SHUTDOWN ITEMS HERE - function in main
        self.__Transition['shutdown']['sync'](count)

        # feedback can be used here to jump out of the shutdown process early

        if count >= self.__ShutdownTime:
            timer.Stop()
            for tp in self.GUIHost.TPs:
                tp.HidePopup('Power-Transition')
            # Log('System shutdown')
    
    def __InitPageTimerHandler(self, timer: Timer, count: int) -> None:
        for tp in self.GUIHost.TPs:
            if self.CurrentActivity == 'off':
                if tp.InactivityTime > timer.LastInactivity[tp.Id]:
                    timer.PanelInactivity[tp.Id] += tp.InactivityTime - timer.LastInactivity[tp.Id]
                else:
                    timer.PanelInactivity[tp.Id] = 0
                timer.LastInactivity[tp.Id] = tp.InactivityTime
                
                if timer.PanelInactivity[tp.Id] >= timer.TriggerTime:
                    tp.ShowPage('Splash')
            else:
                timer.LastInactivity[tp.Id] = 0
                timer.PanelInactivity[tp.Id] = 0
    
    # Private Methods ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    def __ActivitySwitchTPConfiguration(self, activity, touchPanel: 'ExUIDevice'):
        index = self.GUIHost.TPs.index(touchPanel)
        
        if activity == "share":
            self.__ActivityBtns['select'][index].SetCurrent(1)
            self.__ActivityBtns['indicator'][index].SetCurrent(1)
            # Log('Configuring for Share mode')
            touchPanel.HidePopupGroup(8) # Activity-Controls Group
            touchPanel.ShowPopup("Audio-Control-{}-privacy".format('mic' if len(self.GUIHost.Microphones) > 0 else 'no_mic'))
            
            # get video source assigned to the primaryDestination
            curSrc = self.GUIHost.SrcCtl.PrimaryDestination.AssignedSource.Vid
            # Log("Pre-Activity Change Source - Name: {}, Id: {}".format(curSrc.Name, curSrc.Id))
            
            if curSrc.Name == 'None':
                # Log('Current Source = None, Setting current source to default, ID = {}'.format(self.UIHost.DefaultSourceID))
                curSrc = touchPanel.SrcCtl.GetSource(id=self.GUIHost.DefaultSourceId)
                # Log('New Current Source - Name: {}, ID: {}'.format(curSrc.Name, curSrc.Id))
                touchPanel.SrcCtl.SelectSource(curSrc)
                # Log('Selected Source - Name: {}, Id: {}'.format(self.UIHost.SrcCtl.SelectedSource.Name, self.UIHost.SrcCtl.SelectedSource.Id))
                touchPanel.SrcCtl.Privacy = 'on'
            
            # update source selection to match primaryDestination
            touchPanel.SrcCtl.SwitchSources(curSrc, 'All')
            
            # show activity splash screen, will be updated config.activitySplash
            # seconds after the activity switch timer stops
            touchPanel.Btns['Activity-Splash-Close'].SetText('Close Tip ({})'.format(self.__SplashTime))
            touchPanel.ShowPopup("Source-Control-Splash-Share")
            
        elif activity == "adv_share":
            self.__ActivityBtns['select'][index].SetCurrent(2)
            self.__ActivityBtns['indicator'][index].SetCurrent(2)
            # Log('Configuring for Adv Share mode')
            touchPanel.ShowPopup("Activity-Control-AdvShare")
            
            touchPanel.ShowPopup(touchPanel.SrcCtl.GetAdvShareLayout())
            touchPanel.ShowPopup("Audio-Control-{}".format('mic' if len(self.GUIHost.Microphones) > 0 else 'no_mic'))
        
            if self.GUIHost.SrcCtl.Privacy:
                # Log('Handling Privacy reconfigure for Adv Share')
                touchPanel.SrcCtl.Privacy = 'off'
                destList = []
                for dest in touchPanel.SrcCtl.Destinations:
                    dest = cast('Destination', dest)
                    if dest.Type != 'conf':
                        # Log('Non-Confidence destination found - {}'.format(dest.Name))
                        destList.append(dest)
                # Log('Count of non-Confidence destinations: {}'.format(len(destList)))
                touchPanel.SrcCtl.SwitchSources(touchPanel.SrcCtl.BlankSource, destList)
                        
        elif  activity == "group_work":
            self.__ActivityBtns['select'][index].SetCurrent(3)
            self.__ActivityBtns['indicator'][index].SetCurrent(3)
            # Log('Configuring for Group Work mode')
            touchPanel.ShowPopup("Activity-Control-Group")
            touchPanel.ShowPopup("Audio-Control-{}-privacy".format('mic' if len(self.GUIHost.Microphones) > 0 else 'no_mic'))
            
            touchPanel.SrcCtl.SelectSource(touchPanel.SrcCtl.PrimaryDestination.GroupWorkSource)
            for dest in touchPanel.SrcCtl.Destinations:
                dest = cast('Destination', dest)
                touchPanel.SrcCtl.SwitchSources(dest.GroupWorkSource, [dest])
            touchPanel.SrcCtl.Privacy = 'off'
            
            # show activity splash screen, will be updated config.activitySplash
            # seconds after the activity switch timer stops
            touchPanel.Btns['Activity-Splash-Close'].SetText('Close Tip ({})'.format(self.__SplashTime))
            touchPanel.ShowPopup("Source-Control-Splash-GrpWrk")
    
    # Public Methods +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    def StartShutdownConfirmation(self, click: bool=False):
        if self.CurrentActivity != 'off':
            self.__ConfirmationTimer.Restart()
            for tp in self.GUIHost.TPs:
                Log(self.__ConfTimeLbl)
                Log(self.__ConfTimeLbl[self.GUIHost.TPs.index(tp)])
                self.__ConfTimeLbl[self.GUIHost.TPs.index(tp)].SetText(TimeIntToStr(self.__ConfirmationTime))
                if click:
                    tp.Click(5, 0.2)
                tp.ShowPopup('Shutdown-Confirmation')
            
    def SystemStart(self, activity: str) -> None:
        # Log("System Start function activated", stack=True)
        self.CurrentActivity = activity
        
        for tp in self.GUIHost.TPs:
            index = self.GUIHost.TPs.index(tp)
            self.__Transition['label'][index].SetText('System is switching on. Please Wait...')
            self.__Transition['level'][index].SetRange(0, self.__StartupTime, 1)
            self.__Transition['level'][index].SetLevel(0)
            tp.TechCtl.CloseTechMenu()
            self.__Transition['count'][index].SetText(TimeIntToStr(self.__StartupTime))
            tp.ShowPopup('Power-Transition')
            tp.ShowPage('Main')
            
            tp.SrcCtl.SelectSource(self.GUIHost.DefaultSourceId)
            tp.SrcCtl.SwitchSources(tp.SrcCtl.SelectedSource, 'All')

        # Log('Startup Timer Restarting')
        self.__StartTimer.Restart()

        # STARTUP ONLY ITEMS HERE - function in main
        # Log('Performing unsynced Startup functions')
        self.__Transition['start']['init']()
        
    def SystemSwitch(self, activity: str) -> None:
        # Log("System Switch function activated", stack=True)
        for timer in self.__ActivitySplashTimerList:
            timer.Stop()
        self.CurrentActivity = activity
        
        self.__StatusTimer.Restart()
        
        for tp in self.GUIHost.TPs:
            index = self.GUIHost.TPs.index(tp)
            self.__Transition['label'][index].SetText('System is switching to {} mode. Please Wait...'.format(self.__ActivityDict[activity]))
            self.__Transition['level'][index].SetRange(0, self.__SwitchTime, 1)
            self.__Transition['level'][index].SetLevel(0)

            self.__Transition['count'][index].SetText(TimeIntToStr(self.__SwitchTime))
            tp.ShowPopup('Power-Transition')
            tp.ShowPage('Main')
        
        # Log('Activity Switch Timer Restarting')
        self.__SwitchTimer.Restart()
        
        # TODO: Figure out a way to reset the activity timer
        #self.UIHost.InactivityTime = 0
        
        self.__StatusTimerHandler(None, None)

        # configure system for current activity
        # Log('Performing unsynced Activity Switch functions')
        # self.UIHost.HidePopupGroup(5) # Source-Controls Group
        
        for tp in self.GUIHost.TPs:
            self.__ActivitySwitchTPConfiguration(activity, tp)

        self.__Transition['switch']['init']()

    def SystemShutdown(self) -> None:
        # Log("System Switch function activated", stack=True)
        self.CurrentActivity = 'off'
        self.__StatusTimer.Stop()
        
        for tp in self.GUIHost.TPs:
            index = self.GUIHost.TPs.index(tp)
            self.__ActivityBtns['select'][index].SetCurrent(0)
            self.__ActivityBtns['indicator'][index].SetCurrent(0)
        
            self.__Transition['label'][index].SetText('System is switching off. Please Wait...')
            self.__Transition['level'][index].SetRange(0, self.__ShutdownTime, 1)
            self.__Transition['level'][index].SetLevel(0)
        
            self.__Transition['count'][index].SetText(TimeIntToStr(self.__ShutdownTime))
            tp.ShowPopup('Power-Transition')
            tp.HidePopup("Shutdown-Confirmation")
            tp.ShowPage('Opening')

        # Log('Shutdown timer restarting')
        self.__ShutdownTimer.Restart()        
        
        # self.UIHost.InactivityTime = 0
        # TODO: Figure out a way to reset the activity timer
        
        # SHUTDOWN ITEMS HERE - function in main
        # Log('Performing unsynced Shutdown functions')
        self.__Transition['shutdown']['init']()

## End Class Definitions -------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------

## End Function Definitions ----------------------------------------------------



