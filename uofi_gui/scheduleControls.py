from typing import TYPE_CHECKING, Dict, Tuple, List, Union, Callable
if TYPE_CHECKING: # pragma: no cover
    from uofi_gui import GUIController
    from uofi_gui.uiObjects import ExUIDevice
    from extronlib.device import UIDevice
    from extronlib.ui import Button, Knob, Label, Level, Slider

## Begin ControlScript Import --------------------------------------------------
from extronlib import event
from extronlib.system import Clock, File

## End ControlScript Import ----------------------------------------------------
##
## Begin Python Imports --------------------------------------------------------
import json
import re

## End Python Imports ----------------------------------------------------------
##
## Begin User Import -----------------------------------------------------------
#### Custom Code Modules
from utilityFunctions import DictValueSearchByKey, Log, RunAsync, debug, SortKeys

#### Extron Global Scripter Modules

## End User Import -------------------------------------------------------------
##
## Begin Class Definitions -----------------------------------------------------

# TODO: need to make sure that schedule changes properly propigate across all UIHosts
class AutoScheduleController:
    def __init__(self, UIHost: 'ExUIDevice') -> None:
        self.UIHost = UIHost
        self.GUIHost = self.UIHost.GUIHost
        self.AutoStart = False
        self.AutoShutdown = False
        
        self.__inactivityHandlers = \
            {
                180: self.__PopoverInactivityHandler,
                300: self.__TechPageInactivityHandler,
                10800: self.__SystemInactivityHandler
            }
            
        self.UIHost.SetInactivityTime(list(self.__inactivityHandlers.keys()))
        @event(self.UIHost, 'InactivityChanged') # pragma: no cover
        def InactivityMethodHandler(tlp: Union['UIDevice', 'ExUIDevice'], time):
            self.__InactivityMethodHandler(tlp, time)
        
        self.__default_pattern = \
            {
                'Days': 
                    [
                        'Monday',
                        'Tuesday',
                        'Wednesday',
                        'Thursday',
                        'Friday'
                    ],
                'Time': {
                    'hr': '12',
                    'min': '00',
                    'ampm': 'AM'
                }
            }
        self.__scheduleFilePath = '/user/states/room_schedule.json'
        
        self.__toggle_start = self.UIHost.Btns['Schedule-Start-Toggle']
        self.__toggle_start.Value = 'start'
        self.__toggle_shutdown = self.UIHost.Btns['Schedule-Shutdown-Toggle']
        self.__toggle_shutdown.Value = 'shutdown'
        
        self.__pattern_start = self.UIHost.Btns['Schedule-Start-Pattern']
        self.__pattern_start.Value = 'start'
        self.__pattern_start.Pattern = None
        self.__pattern_shutdown = self.UIHost.Btns['Schedule-Shutdown-Pattern']
        self.__pattern_shutdown.Value = 'shutdown'
        self.__pattern_shutdown.Pattern = None
        
        self.__activity_start = self.UIHost.Btn_Grps['Schedule-Start-Activity-Mode']
        
        self.__edit_modal = 'Modal-Scheduler'
        
        self.__btns_days = \
            {
                'Monday': self.UIHost.Btns['Schedule-Mon'],
                'Tuesday': self.UIHost.Btns['Schedule-Tue'],
                'Wednesday': self.UIHost.Btns['Schedule-Wed'],
                'Thursday': self.UIHost.Btns['Schedule-Thu'],
                'Friday': self.UIHost.Btns['Schedule-Fri'],
                'Saturday': self.UIHost.Btns['Schedule-Sat'],
                'Sunday': self.UIHost.Btns['Schedule-Sun']
            }
            
        for dow, btn in self.__btns_days.items():
            btn.Value = dow
            
        self.__btn_sel_all = self.UIHost.Btns['Schedule-All']
        self.__btn_sel_wkdys = self.UIHost.Btns['Schedule-Weekdays']
        
        self.UIHost.Btns['Schedule-Hr-Up'].fn = 'up'
        self.UIHost.Btns['Schedule-Hr-Dn'].fn = 'down'
        self.UIHost.Btns['Schedule-Min-Up'].fn = 'up'
        self.UIHost.Btns['Schedule-Min-Dn'].fn = 'down'
        self.UIHost.Btns['Schedule-Hr-Up'].mode = 'hr'
        self.UIHost.Btns['Schedule-Hr-Dn'].mode = 'hr'
        self.UIHost.Btns['Schedule-Min-Up'].mode = 'min'
        self.UIHost.Btns['Schedule-Min-Dn'].mode = 'min'
        self.__btns_time = [
            self.UIHost.Btns['Schedule-Hr-Up'],
            self.UIHost.Btns['Schedule-Hr-Dn'],
            self.UIHost.Btns['Schedule-Min-Up'],
            self.UIHost.Btns['Schedule-Min-Dn']
        ]
        self.__lbls_time = \
            {
                'hr': self.UIHost.Lbls['Schedule-Hr'],
                'min': self.UIHost.Lbls['Schedule-Min']
            }
        self.__lbls_time['hr'].Value = 12
        self.__lbls_time['min'].Value = 0
            
        self.UIHost.Btns['Schedule-AM'].Value = 'AM'
        self.UIHost.Btns['Schedule-PM'].Value = 'PM'
        self.__btns_ampm = self.UIHost.Btn_Grps['Schedule-AMPM']
        
        self.__btn_save = self.UIHost.Btns['Schedule-Save']
        self.__btn_cancel = self.UIHost.Btns['Schedule-Cancel']
        
        self.__editor_pattern = self.UIHost.Lbls['Schedule-Calc']
        self.__editor_pattern.Mode = None
        self.__editor_pattern.Pattern = None
        
        self.__AutoStartClock = Clock(['12:00:00'], None, self.__ScheduleStartHandler)
        self.__AutoShutdownClock = Clock(['12:00:00'], None, self.__ScheduleShutdownHandler)
        
        self.__LoadSchedule()
        
        @event([self.__toggle_start, self.__toggle_shutdown], ['Released']) # pragma: no cover
        def ToggleHandler(button: 'Button', action: str):
            self.__ToggleHandler(button, action)
                
        @event([self.__pattern_start, self.__pattern_shutdown], ['Pressed', 'Released']) # pragma: no cover
        def PatternEditHandler(button: 'Button', action: str):
            self.__PatternEditHandler(button, action)
                
        @event(self.__activity_start.Objects, ['Pressed']) # pragma: no cover
        def ActivitySelectHandler(button: 'Button', action: str):
            self.__ActivitySelectHandler(button, action)
            
        @event(list(self.__btns_days.values()), ['Pressed']) # pragma: no cover
        def DayOfWeekSelectHandler(button: 'Button', action: str):
            self.__DayOfWeekSelectHandler(button, action)
        
        @event(self.__btn_sel_all, ['Pressed', 'Released']) # pragma: no cover
        def SelectAllHandler(button: 'Button', action: str):
            self.__SelectAllHandler(button, action)
        
        @event(self.__btn_sel_wkdys, ['Pressed', 'Released']) # pragma: no cover
        def SelectWeekdaysHandler(button: 'Button', action: str):
            self.__SelectWeekdaysHandler(button, action)
        
        @event(self.__btns_time, ['Pressed', 'Released']) # pragma: no cover
        def TimeEditHandler(button: 'Button', action: str):
            self.__TimeEditHandler(button, action)
                
        @event(self.__btns_ampm.Objects, ['Pressed']) # pragma: no cover
        def AMPMEditHandler(button: 'Button', action: str):
            self.__AMPMEditHandler(button, action)
        
        @event(self.__btn_save, ['Pressed', 'Released']) # pragma: no cover
        def EditorSaveHandler(button: 'Button', action: str):
            self.__EditorSaveHandler(button, action)
                
        @event(self.__btn_cancel, ['Pressed', 'Released']) # pragma: no cover
        def EditorCancelHandler(button: 'Button', action: str):
            self.__EditorCancelHandler(button, action)
            
    ## Event Handlers (Private) ------------------------------------------------
    def __InactivityMethodHandler(self, tlp: Union['UIDevice', 'ExUIDevice'], time):
        if time in self.__inactivityHandlers:
            self.__inactivityHandlers[time]()
    
    def __ToggleHandler(self, button: 'Button', action: str):
        if button.Value == 'start' and self.AutoStart is True:
            self.AutoStart = False
            button.SetState(0)
        elif button.Value == 'start' and self.AutoStart is False:
            self.AutoStart = True
            button.SetState(1)
        elif button.Value == 'shutdown' and self.AutoShutdown is True:
            self.AutoShutdown = False
            button.SetState(0)
        elif button.Value == 'shutdown' and self.AutoShutdown is False:
            self.AutoShutdown = True
            button.SetState(1)
        self.__SaveSchedule()
    
    def __PatternEditHandler(self, button: 'Button', action: str):
        if action == 'Pressed':
            button.SetState(1)
        elif action == 'Released':
            self.__editor_pattern.Mode = button.Value
            self.__editor_pattern.Pattern = button.Pattern
            self.__UpdateEditor(button.Pattern)
            self.UIHost.ShowPopup(self.__edit_modal)
            button.SetState(0)
    
    def __ActivitySelectHandler(self, button: 'Button', action: str):
        self.__activity_start.SetCurrent(button)
        re_match = re.match(r'Schedule-Start-Act-(\w+)', button.Name)
        self.__pattern_start.Activity = re_match.group(1)
        self.__SaveSchedule()
    
    def __DayOfWeekSelectHandler(self, button: 'Button', action: str):
        if button.State == 0:
            button.SetState(1)
            self.__editor_pattern.Pattern['Days'].append(button.Value)
        elif button.State == 1:
            button.SetState(0)
            if button.Value in self.__editor_pattern.Pattern['Days']:
                self.__editor_pattern.Pattern['Days'].remove(button.Value)
        self.__editor_pattern.SetText(self.__PatternToText(self.__editor_pattern.Pattern))

        
    def __SelectAllHandler(self, button: 'Button', action: str):
        if action == 'Pressed':
            button.SetState(1)
        elif action == 'Released':
            self.__editor_pattern.Pattern['Days'] = list(self.__btns_days.keys())
            for dayBtn in self.__btns_days.values():
                dayBtn.SetState(1)
            self.__editor_pattern.SetText(self.__PatternToText(self.__editor_pattern.Pattern))
            button.SetState(0)
    
    def __SelectWeekdaysHandler(self, button: 'Button', action: str):
        if action == 'Pressed':
            button.SetState(1)
        elif action == 'Released':
            self.__editor_pattern.Pattern['Days'] = \
                [
                    'Monday',
                    'Tuesday',
                    'Wednesday',
                    'Thursday',
                    'Friday'
                ]
            for d in self.__btns_days:
                if d in self.__editor_pattern.Pattern['Days']:
                    self.__btns_days[d].SetState(1)
                else: 
                    self.__btns_days[d].SetState(0)
            self.__editor_pattern.SetText(self.__PatternToText(self.__editor_pattern.Pattern))
            button.SetState(0)
    
    def __TimeEditHandler(self, button: 'Button', action: str):
        if action == 'Pressed':
            button.SetState(1)
        elif action == 'Released':
            if button.mode == 'hr':
                currentVal = self.__lbls_time['hr'].Value
                if button.fn == 'up':
                    if currentVal >= 12:
                        self.__lbls_time['hr'].Value = 1
                    else:
                        self.__lbls_time['hr'].Value = currentVal + 1
                elif button.fn == 'down':
                    if currentVal <= 1:
                        self.__lbls_time['hr'].Value = 12
                    else:
                        self.__lbls_time['hr'].Value = currentVal - 1
                strVal = '{:02d}'.format(self.__lbls_time['hr'].Value)
                self.__lbls_time['hr'].SetText(strVal)
                self.__editor_pattern.Pattern['Time']['hr'] = strVal
            elif button.mode == 'min':
                currentVal = self.__lbls_time['min'].Value
                if button.fn == 'up':
                    if currentVal >= 59:
                        self.__lbls_time['min'].Value = 1
                    else:
                        self.__lbls_time['min'].Value = currentVal + 1
                elif button.fn == 'down':
                    if currentVal <= 0:
                        self.__lbls_time['min'].Value = 59
                    else:
                        self.__lbls_time['min'].Value = currentVal - 1
                strVal = '{:02d}'.format(self.__lbls_time['min'].Value)
                self.__lbls_time['min'].SetText(strVal)
                self.__editor_pattern.Pattern['Time']['min'] = strVal
            self.__editor_pattern.SetText(self.__PatternToText(self.__editor_pattern.Pattern))
            button.SetState(0)
                
    def __AMPMEditHandler(self, button: 'Button', action: str):
        self.__btns_ampm.SetCurrent(button)
        self.__editor_pattern.Pattern['Time']['ampm'] = button.Value
        self.__editor_pattern.SetText(self.__PatternToText(self.__editor_pattern.Pattern))

    def __EditorSaveHandler(self, button: 'Button', action: str):
        if action == 'Pressed':
            button.SetState(1)
        elif action == 'Released':
            pat = self.__editor_pattern.Pattern
            pat['Days'].sort(key = SortKeys.SortDaysOfWeek)
            if self.__editor_pattern.Mode == 'start':
                self.__pattern_start.Pattern = pat
                self.__UpdatePattern('start')
            elif self.__editor_pattern.Mode == 'shutdown':
                self.__pattern_shutdown.Pattern = pat
                self.__UpdatePattern('shutdown')
            self.__SaveSchedule()
            self.UIHost.HidePopup(self.__edit_modal)
            button.SetState(0)
        
    def __EditorCancelHandler(self, button: 'Button', action: str):
        if action == 'Pressed':
            button.SetState(1)
        elif action == 'Released':
            self.UIHost.HidePopup(self.__edit_modal)
            button.SetState(0)
    
    ## Private Methods ---------------------------------------------------------
    def __UpdatePattern(self, Mode: str=None):
        if Mode == 'start' or Mode is None:
            if self.__pattern_start.Pattern is not None:
                self.__pattern_start.SetText(self.__PatternToText(self.__pattern_start.Pattern))
            else:
                self.__pattern_start.SetText('')
        elif Mode == 'shutdown' or Mode is None:
            if self.__pattern_shutdown.Pattern is not None:
                self.__pattern_shutdown.SetText(self.__PatternToText(self.__pattern_shutdown.Pattern))
            else:
                self.__pattern_shutdown.SetText('')
        else:
            raise ValueError('Mode must be "start", "shutdown", or None.')
                
    def __PatternToText(self, Pattern: Dict):
        DoW = ''
        Pattern['Days'].sort(key = SortKeys.SortDaysOfWeek)
        if len(Pattern['Days']) == 0:
            return 'None'
        for d in Pattern['Days']:
            if len(DoW) > 0:
                DoW = DoW + ','
            if d[0] == 'S' or d[0] == 'T':
                DoW = DoW + d[0:2]
            else:
                DoW = DoW + d[0]
            
        text = '{dow} {h}:{m} {a}'.format(dow = DoW, 
                                          h = Pattern['Time']['hr'],
                                          m = Pattern['Time']['min'],
                                          a = Pattern['Time']['ampm'])
        
        return text
    
    def __SaveSchedule(self):
        # only need to save the preset names, presets are stored presistently on camera
        if File.Exists(self.__scheduleFilePath):
            # file exists -> read file to object, modify object, save object to file
            #### read file to object
            scheduleFile = File(self.__scheduleFilePath, 'rt')
            scheduleString = scheduleFile.read()
            scheduleObj = json.loads(scheduleString)
            scheduleFile.close()
            
            #### modify object
            scheduleObj['auto_start']['enabled'] = int(self.AutoStart)
            scheduleObj['auto_start']['pattern'] = self.__pattern_start.Pattern
            scheduleObj['auto_start']['mode'] = self.__pattern_start.Activity
            scheduleObj['auto_shutdown']['enabled'] = int(self.AutoShutdown)
            scheduleObj['auto_shutdown']['pattern'] = self.__pattern_shutdown.Pattern
            
            #### save object to file
            scheduleFile = File(self.__scheduleFilePath, 'wt')
            scheduleFile.write(json.dumps(scheduleObj))
            scheduleFile.close()
            
        else:
            # file does not exist -> create object, save object to file
            #### create object
            scheduleObj = \
                {
                    'auto_start': 
                        {
                            'enabled': 0,
                            'pattern': {},
                            'mode': ''
                        },
                    'auto_shutdown':
                        {
                            'enabled': 0,
                            'pattern': {}
                        }
                }
            scheduleObj['auto_start']['enabled'] = int(self.AutoStart)
            scheduleObj['auto_start']['pattern'] = self.__pattern_start.Pattern
            scheduleObj['auto_start']['mode'] = self.__pattern_start.Activity
            scheduleObj['auto_shutdown']['enabled'] = int(self.AutoShutdown)
            scheduleObj['auto_shutdown']['pattern'] = self.__pattern_shutdown.Pattern
            
            #### save object to file
            scheduleFile = File(self.__scheduleFilePath, 'xt')
            scheduleFile.write(json.dumps(scheduleObj))
            scheduleFile.close()
            
        if bool(scheduleObj['auto_start']['enabled']):
            self.__AutoStartClock.Enable()
        else:
            self.__AutoStartClock.Disable()
            
        self.__AutoStartClock.SetDays(scheduleObj['auto_start']['pattern']['Days'])
        self.__AutoStartClock.SetTimes([self.__ClockTime(scheduleObj['auto_start']['pattern']['Time'])])
        
        if bool(scheduleObj['auto_shutdown']['enabled']):
            self.__AutoShutdownClock.Enable()
        else:
            self.__AutoShutdownClock.Disable()
            
        self.__AutoShutdownClock.SetDays(scheduleObj['auto_shutdown']['pattern']['Days'])
        self.__AutoShutdownClock.SetTimes([self.__ClockTime(scheduleObj['auto_shutdown']['pattern']['Time'])])
        
    
    def __LoadSchedule(self):
        # only need to load the preset names, presets are stored presistently on camera
        if File.Exists(self.__scheduleFilePath):
            #### read file to object
            scheduleFile = File(self.__scheduleFilePath, 'rt')
            scheduleString = scheduleFile.read()
            scheduleObj = json.loads(scheduleString)
            # Log('JSON Obj: {}'.format(scheduleObj))
            scheduleFile.close()
            
            #### iterate over objects and load presets
            self.AutoStart = bool(scheduleObj['auto_start']['enabled'])
            self.__pattern_start.Pattern = scheduleObj['auto_start']['pattern']
            self.__pattern_start.Activity = scheduleObj['auto_start']['mode']
            self.AutoShutdown =  bool(scheduleObj['auto_shutdown']['enabled'])
            self.__pattern_shutdown.Pattern = scheduleObj['auto_shutdown']['pattern']

        else:
            Log('No presets file exists')
            
            # load defaults
            self.AutoStart = False
            self.__pattern_start.Pattern = self.__default_pattern
            self.__pattern_start.Activity = 'share'
            self.AutoShutdown =  False
            self.__pattern_shutdown.Pattern = self.__default_pattern
            
        if self.AutoStart:
            self.__toggle_start.SetState(1)
            self.__AutoStartClock.Enable()
        else:
            self.__toggle_start.SetState(0)
            self.__AutoStartClock.Disable()
            
        if self.AutoShutdown:
            self.__toggle_shutdown.SetState(1)
            self.__AutoShutdownClock.Enable()
        else:
            self.__toggle_shutdown.SetState(0)
            self.__AutoShutdownClock.Disable()
        
        self.__activity_start.SetCurrent(self.UIHost.Btns['Schedule-Start-Act-{}'.format(self.__pattern_start.Activity)])
        
        self.__AutoStartClock.SetDays(self.__pattern_start.Pattern['Days'])
        self.__AutoStartClock.SetTimes([self.__ClockTime(self.__pattern_start.Pattern['Time'])])
            
        self.__AutoShutdownClock.SetDays(self.__pattern_shutdown.Pattern['Days'])
        self.__AutoShutdownClock.SetTimes([self.__ClockTime(self.__pattern_shutdown.Pattern['Time'])])
        
        self.__UpdatePattern()
    
    def __UpdateEditor(self, Pattern):
        # Update Days of Week
        for d in self.__btns_days:
            if d in Pattern['Days']:
                self.__btns_days[d].SetState(1)
            else:
                self.__btns_days[d].SetState(0)
            
        # Update Hr
        self.__lbls_time['hr'].SetText(Pattern['Time']['hr'])
        self.__lbls_time['hr'].Value = int(Pattern['Time']['hr'])
        
        # Update Min
        self.__lbls_time['min'].SetText(Pattern['Time']['min'])
        self.__lbls_time['min'].Value = int(Pattern['Time']['min'])
        
        # Update AM/PM
        self.__btns_ampm.SetCurrent(self.UIHost.Btns['Schedule-{}'.format(Pattern['Time']['ampm'])])
        
        # Update Pattern
        self.__editor_pattern.SetText(self.__PatternToText(Pattern))
        
    def __ScheduleShutdownHandler(self, Clock, Time):
        if self.GUIHost.ActCtl.CurrentActivity != 'off':
            self.GUIHost.ActCtl.SystemShutdown()
        else:
            Log('System already off at scheduled shutdown.')
        
    def __ScheduleStartHandler(self, Clock, Time):
        if self.GUIHost.ActCtl.CurrentActivity == 'off':
            self.GUIHost.ActCtl.SystemStart(self.__pattern_start.Activity)
        elif self.GUIHost.ActCtl.CurrentActivity != self.__pattern_start.Activity:
            self.GUIHost.ActCtl.SystemSwitch(self.__pattern_start.Activity)
        else:
            pass # The system is already configured in the desired state
        
    def __ClockTime(self, Time: Dict):
        if Time['ampm'] == 'PM':
            if int(Time['hr']) == 12:
                hrs = 12
            else:
                hrs = int(Time['hr']) + 12
        else:
            if int(Time['hr']) == 12:
                hrs = 0
            else:
                hrs = int(Time['hr'])
        
        return '{:02d}:{}:00'.format(hrs, Time['min'])
    
    def __PopoverInactivityHandler(self):
        for p in self.UIHost.PopoverPageList:
            self.UIHost.HidePopup(p)
    
    def __TechPageInactivityHandler(self):
        if self.UIHost.TechCtl.TechMenuOpen:
            self.UIHost.TechCtl.CloseTechMenu()
    
    # def __SplashPageInactivityHandler(self):
    #     if self.GUIHost.ActCtl.CurrentActivity == 'off':
    #         self.UIHost.Click()
    #         self.UIHost.ShowPage('Splash')
    
    def __SystemInactivityHandler(self):
        self.GUIHost.ActCtl.StartShutdownConfirmation(click=True)

## End Class Definitions -------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------

## End Function Definitions ----------------------------------------------------