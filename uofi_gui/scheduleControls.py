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
import re
from typing import Dict, Tuple, List

## End Python Imports ----------------------------------------------------------
##
## Begin User Import -----------------------------------------------------------
#### Custom Code Modules
import utilityFunctions
import settings
import vars

#### Extron Global Scripter Modules

## End User Import -------------------------------------------------------------
##
## Begin Class Definitions -----------------------------------------------------

class AutoScheduleController:
    def __init__(self, UIHost: UIDevice) -> None:
        self.UIHost = UIHost
        self.AutoStart = False
        self.AutoShutdown = False
        
        self.__inactivityHandlers = \
            {
                300: self.__TechPageInactivityHandler,
                600: self.__SplashPageInactivityHandler,
                10800: self.__SystemInactivityHandler
            }
            
        self.UIHost.SetInactivityTime(list(self.__inactivityHandlers.keys()))
        @event(self.UIHost, 'InactivityChanged')
        def inactivityMethodHandler(tlp, time):
            if time in self.__inactivityHandlers:
                self.__inactivityHandlers[time]()
        
        self.__default_pattern = \
            {
                'days': 
                    [
                        'Monday',
                        'Tuesday',
                        'Wednesday',
                        'Thursday',
                        'Friday'
                    ],
                'time': {
                    'hr': '12',
                    'min': '00',
                    'ampm': 'AM'
                }
            }
        self.__scheduleFilePath = '/user/states/room_schedule.json'
        
        self.__toggle_start = vars.TP_Btns['Schedule-Start-Toggle']
        self.__toggle_start.Value = 'start'
        self.__toggle_shutdown = vars.TP_Btns['Schedule-Shutdown-Toggle']
        self.__toggle_shutdown.Value = 'shutdown'
        
        self.__pattern_start = vars.TP_Btns['Schedule-Start-Pattern']
        self.__pattern_start.Value = 'start'
        self.__pattern_start.Pattern = None
        self.__pattern_shutdown = vars.TP_Btns['Schedule-Shutdown-Pattern']
        self.__pattern_shutdown.Value = 'shutdown'
        self.__pattern_shutdown.Pattern = None
        
        self.__activity_start = vars.TP_Btn_Grps['Schedule-Start-Activity-Mode']
        
        self.__edit_modal = 'Modal-Scheduler'
        
        self.__btns_days = \
            {
                'Monday': vars.TP_Btns['Schedule-Mon'],
                'Tuesday': vars.TP_Btns['Schedule-Tue'],
                'Wednesday': vars.TP_Btns['Schedule-Wed'],
                'Thursday': vars.TP_Btns['Schedule-Thu'],
                'Friday': vars.TP_Btns['Schedule-Fri'],
                'Saturday': vars.TP_Btns['Schedule-Sat'],
                'Sunday': vars.TP_Btns['Schedule-Sun']
            }
            
        for dow, btn in self.__btns_days.items():
            btn.Value = dow
            
        self.__btn_sel_all = vars.TP_Btns['Schedule-All']
        self.__btn_sel_wkdys = vars.TP_Btns['Schedule-Weekdays']
        
        vars.TP_Btns['Schedule-Hr-Up'].fn = 'up'
        vars.TP_Btns['Schedule-Hr-Dn'].fn = 'down'
        vars.TP_Btns['Schedule-Min-Up'].fn = 'up'
        vars.TP_Btns['Schedule-Min-Dn'].fn = 'down'
        vars.TP_Btns['Schedule-Hr-Up'].mode = 'hr'
        vars.TP_Btns['Schedule-Hr-Dn'].mode = 'hr'
        vars.TP_Btns['Schedule-Min-Up'].mode = 'min'
        vars.TP_Btns['Schedule-Min-Dn'].mode = 'min'
        self.__btns_time = [
            vars.TP_Btns['Schedule-Hr-Up'],
            vars.TP_Btns['Schedule-Hr-Dn'],
            vars.TP_Btns['Schedule-Min-Up'],
            vars.TP_Btns['Schedule-Min-Dn']
        ]
        self.__lbls_time = \
            {
                'hr': vars.TP_Lbls['Schedule-Hr'],
                'min': vars.TP_Lbls['Schedule-Min']
            }
        self.__lbls_time['hr'].Value = 12
        self.__lbls_time['min'].Value = 0
            
        vars.TP_Btns['Schedule-AM'].Value = 'AM'
        vars.TP_Btns['Schedule-PM'].Value = 'PM'
        self.__btns_ampm = vars.TP_Btn_Grps['Schedule-AMPM']
        utilityFunctions.Log('AM/PM MESet - Len: {}, Obj: {}'.format(len(self.__btns_ampm.Objects), self.__btns_ampm.Objects))
        
        self.__btn_save = vars.TP_Btns['Schedule-Save']
        self.__btn_cancel = vars.TP_Btns['Schedule-Cancel']
        
        self.__editor_pattern = vars.TP_Lbls['Schedule-Calc']
        self.__editor_pattern.Mode = None
        self.__editor_pattern.Pattern = None
        
        self.__AutoStartClock = Clock(['12:00:00'], None, self.__ScheduleStartHandler)
        self.__AutoShutdownClock = Clock(['12:00:00'], None, self.__ScheduleShutdownHandler)
        
        self.__LoadSchedule()
        
        @event([self.__toggle_start, self.__toggle_shutdown], ['Released'])
        def toggleHandler(button, action):
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
                
        @event([self.__pattern_start, self.__pattern_shutdown], ['Pressed', 'Released'])
        def patternEditHandler(button, action):
            if action == 'Pressed':
                button.SetState(1)
            elif action == 'Released':
                self.__editor_pattern.Mode = button.Value
                self.__editor_pattern.Pattern = button.Pattern
                self.__UpdateEditor(button.Pattern)
                self.UIHost.ShowPopup(self.__edit_modal)
                button.SetState(0)
                
        @event(self.__activity_start.Objects, ['Pressed'])
        def activitySelectHandler(button, action):
            self.__activity_start.SetCurrent(button)
            re_match = re.match(r'Schedule-Start-Act-(\w+)', button.Name)
            self.__pattern_start.Activity = re_match.group(1)
            self.__SaveSchedule()
            
        @event(list(self.__btns_days.values()), ['Pressed'])
        def DayOfWeekSelectHandler(button, action):
            if button.State == 0:
                button.SetState(1)
                self.__editor_pattern.Pattern['Days'].append(button.Value)
            elif button.State == 1:
                button.SetState(0)
                self.__editor_pattern.Pattern['Days'].remove(button.Value)
            self.__editor_pattern.SetText(self.__PatternToText(self.__editor_pattern.Pattern))
                
        @event(self.__btn_sel_all, ['Pressed', 'Released'])
        def SelectAllHandler(button, action):
            if action == 'Pressed':
                button.SetState(1)
            elif action == 'Released':
                self.__editor_pattern.Pattern['Days'] = list(self.__btns_days.keys())
                for dayBtn in self.__btns_days.values():
                    dayBtn.SetState(1)
                self.__editor_pattern.SetText(self.__PatternToText(self.__editor_pattern.Pattern))
                button.SetState(0)
        
        @event(self.__btn_sel_wkdys, ['Pressed', 'Released'])
        def SelectWeekdaysHandler(button, action):
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
        
        @event(self.__btns_time, ['Pressed', 'Released'])
        def TimeEditHandler(button, action):
            if action == 'Pressesd':
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
                
        @event(self.__btns_ampm.Objects, ['Pressed'])
        def AMPMEditHandler(button, action):
            self.__btns_ampm.SetCurrent(button)
            self.__editor_pattern.Pattern['Time']['ampm'] = button.Value
            self.__editor_pattern.SetText(self.__PatternToText(self.__editor_pattern.Pattern))
            
        @event(self.__btn_save, ['Pressed', 'Released'])
        def EditorSaveHandler(button, action):
            if action == 'Pressed':
                button.SetState(1)
            elif action == 'Released':
                pat = self.__editor_pattern.Pattern
                pat['Days'].sort(key = self.__SortWeekdays)
                if self.__editor_pattern.Mode == 'start':
                    self.__pattern_start.Pattern = pat
                    self.__UpdatePattern('start')
                elif self.__editor_pattern.Mode == 'shutdown':
                    self.__pattern_shutdown.Pattern = pat
                    self.__UpdatePattern('shutdown')
                self.__SaveSchedule()
                self.UIHost.HidePopup(self.__edit_modal)
                button.SetState(0)
                
        @event(self.__btn_cancel, ['Pressed', 'Released'])
        def EditorCancelHandler(button, action):
            if action == 'Pressed':
                button.SetState(1)
            elif action == 'Released':
                self.UIHost.HidePopup(self.__edit_modal)
                button.SetState(0)
                
    def __UpdatePattern(self, Mode: str=None):
        if Mode == 'start' or Mode is None:
            if self.__pattern_start.Pattern is not None:
                self.__pattern_start.SetText(self.__PatternToText(self.__pattern_start.Pattern))
            else:
                self.__pattern_start.SetText('')
        if Mode == 'shutdown' or Mode is None:
            if self.__pattern_shutdown.Pattern is not None:
                self.__pattern_shutdown.SetText(self.__PatternToText(self.__pattern_shutdown.Pattern))
            else:
                self.__pattern_shutdown.SetText('')
                
    def __PatternToText(self, Pattern: Dict):
        DoW = ''
        Pattern['Days'].sort(key = self.__SortWeekdays)
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
            utilityFunctions.Log('JSON Obj: {}'.format(scheduleObj))
            scheduleFile.close()
            
            #### iterate over objects and load presets
            self.AutoStart = bool(scheduleObj['auto_start']['enabled'])
            self.__pattern_start.Pattern = scheduleObj['auto_start']['pattern']
            self.__pattern_start.Activity = scheduleObj['auto_start']['mode']
            self.AutoShutdown =  bool(scheduleObj['auto_shutdown']['enabled'])
            self.__pattern_shutdown.Pattern = scheduleObj['auto_shutdown']['pattern']

        else:
            utilityFunctions.Log('No presets file exists')
            
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
            
        self.__activity_start.SetCurrent(vars.TP_Btns['Schedule-Start-Act-{}'.format(self.__pattern_start.Activity)])

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
        self.__btns_ampm.SetCurrent(vars.TP_Btns['Schedule-{}'.format(Pattern['Time']['ampm'])])
        
        # Update Pattern
        self.__editor_pattern.SetText(self.__PatternToText(Pattern))
        
    def __ScheduleShutdownHandler(self, Clock, Time):
        if vars.ActCtl.CurrentActivity != 'off':
            vars.ActCtl.SystemShutdown()
        
    def __ScheduleStartHandler(self, Clock, Time):
        if vars.ActCtl.CurrentActivity == 'off':
            vars.ActCtl.SystemStart(self.__pattern_start.Activity)
        elif vars.ActCtl.CurrentActivity != self.__pattern_start.Activity:
            vars.ActCtl.SystemSwitch(self.__pattern_start.Activity)
    
    def __SortWeekdays(self, Day):
        if Day == 'Monday':
            return 0
        elif Day == 'Tuesday':
            return 1
        elif Day == 'Wednesday':
            return 2
        elif Day == 'Thursday':
            return 3
        elif Day == 'Friday':
            return 4
        elif Day == 'Saturday':
            return 5
        elif Day == 'Sunday':
            return 6
        
    def __ClockTime(self, Time):
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
    
    def __TechPageInactivityHandler(self):
        if vars.TechCtl.TechMenuOpen:
            vars.TechCtl.CloseTechMenu()
    
    def __SplashPageInactivityHandler(self):
        if vars.ActCtl.CurrentActivity == 'off':
            self.UIHost.Click()
            self.UIHost.ShowPage('Splash')
    
    def __SystemInactivityHandler(self):
        vars.ActCtl.StartShutdownConfirmation(click=True)

## End Class Definitions -------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------

## End Function Definitions ----------------------------------------------------