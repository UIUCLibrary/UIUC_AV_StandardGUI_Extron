import unittest
import importlib

## test imports ----------------------------------------------------------------
import os
from uofi_gui import GUIController
from uofi_gui.activityControls import ActivityController
from uofi_gui.uiObjects import ExUIDevice
from uofi_gui.scheduleControls import AutoScheduleController
import test_settings as settings

from extronlib.ui import Button, Label
from extronlib.system import MESet, Clock, File
## -----------------------------------------------------------------------------

class ScheduleController_TestClass(unittest.TestCase): # rename for module to be tested
    def setUp(self) -> None:
        self.TestCtls = ['CTL001']
        self.TestTPs = ['TP001']
        importlib.reload(settings)
        self.TestGUIController = GUIController(settings, self.TestCtls, self.TestTPs)
        self.TestGUIController.Initialize()
        self.TestUIController = self.TestGUIController.TP_Main
        self.TestScheduleController = self.TestUIController.SchedCtl
        return super().setUp()
    
    def tearDown(self):
        if os.path.exists('./emulatedFileSystem/SFTP/user/states/room_schedule.json'):
            os.remove('./emulatedFileSystem/SFTP/user/states/room_schedule.json')
    
    def test_ScheduleController_Type(self): # configure a test case for each function in the module
        self.assertIsInstance(self.TestScheduleController, AutoScheduleController)
    
    def test_ScheduleController_Properties(self):
        # UIHost
        with self.subTest(prop='UIHost'):
            self.assertIsInstance(self.TestScheduleController.UIHost, ExUIDevice)
            
        # GUIHost
        with self.subTest(prop='GUIHost'):
            self.assertIsInstance(self.TestScheduleController.GUIHost, GUIController)
            
        # AutoStart
        with self.subTest(prop='AutoStart'):
            self.assertIsInstance(self.TestScheduleController.AutoStart, bool)
            
        # AutoShutdown
        with self.subTest(prop='AutoShutdown'):
            self.assertIsInstance(self.TestScheduleController.AutoShutdown, bool)
        
    def test_ScheduleController_PRIV_Properties(self):
        
        # __default_pattern
        with self.subTest(prop='__default_pattern'):
            self.assertIsInstance(self.TestScheduleController._AutoScheduleController__default_pattern, dict)
        
        # __inactivityHandlers
        with self.subTest(prop='__inactivityHandlers'):
            self.assertIsInstance(self.TestScheduleController._AutoScheduleController__inactivityHandlers, dict)
            for key, value in self.TestScheduleController._AutoScheduleController__inactivityHandlers.items():
                with self.subTest(i=key):
                    self.assertIsInstance(key, int)
                    self.assertTrue(callable(value))
        
        # __scheduleFilePath
        with self.subTest(prop='__scheduleFilePath'):
            self.assertIsInstance(self.TestScheduleController._AutoScheduleController__scheduleFilePath, str)
            self.assertIn('/user/states/', self.TestScheduleController._AutoScheduleController__scheduleFilePath)
        
        # __toggle_start
        with self.subTest(prop='__toggle_start'):
            self.assertIsInstance(self.TestScheduleController._AutoScheduleController__toggle_start, Button)
            self.assertTrue(hasattr(self.TestScheduleController._AutoScheduleController__toggle_start, 'Value'))
            self.assertIsInstance(self.TestScheduleController._AutoScheduleController__toggle_start.Value, str)
        
        # __toggle_shutdown
        with self.subTest(prop='__toggle_shutdown'):
            self.assertIsInstance(self.TestScheduleController._AutoScheduleController__toggle_shutdown, Button)
            self.assertTrue(hasattr(self.TestScheduleController._AutoScheduleController__toggle_shutdown, 'Value'))
            self.assertIsInstance(self.TestScheduleController._AutoScheduleController__toggle_shutdown.Value, str)
        
        # __pattern_start
        with self.subTest(prop='__pattern_start'):
            self.assertIsInstance(self.TestScheduleController._AutoScheduleController__pattern_start, Button)
            self.assertTrue(hasattr(self.TestScheduleController._AutoScheduleController__pattern_start, 'Value'))
            self.assertIsInstance(self.TestScheduleController._AutoScheduleController__pattern_start.Value, str)
            self.assertTrue(hasattr(self.TestScheduleController._AutoScheduleController__pattern_start, 'Pattern'))
            self.assertIsInstance(self.TestScheduleController._AutoScheduleController__pattern_start.Pattern, dict)
        
        # __pattern_shutdown
        with self.subTest(prop='__pattern_shutdown'):
            self.assertIsInstance(self.TestScheduleController._AutoScheduleController__pattern_shutdown, Button)
            self.assertTrue(hasattr(self.TestScheduleController._AutoScheduleController__pattern_shutdown, 'Value'))
            self.assertIsInstance(self.TestScheduleController._AutoScheduleController__pattern_shutdown.Value, str)
            self.assertTrue(hasattr(self.TestScheduleController._AutoScheduleController__pattern_shutdown, 'Pattern'))
            self.assertIsInstance(self.TestScheduleController._AutoScheduleController__pattern_shutdown.Pattern, dict)
        
        # __activity_start
        with self.subTest(prop='__activity_start'):
            self.assertIsInstance(self.TestScheduleController._AutoScheduleController__activity_start, MESet)
        
        # __edit_modal
        with self.subTest(prop='__edit_modal'):
            self.assertIsInstance(self.TestScheduleController._AutoScheduleController__edit_modal, str)
                
        # __btns_days
        with self.subTest(prop='__btns_days'):
            self.assertIsInstance(self.TestScheduleController._AutoScheduleController__btns_days, dict)
            self.assertEqual(len(self.TestScheduleController._AutoScheduleController__btns_days), 7)
            for key, value in self.TestScheduleController._AutoScheduleController__btns_days.items():
                with self.subTest(i=key):
                    self.assertIsInstance(key, str)
                    self.assertIsInstance(value, Button)
                    self.assertTrue(hasattr(value, 'Value'))
                    self.assertIsInstance(value.Value, str)
                    self.assertIn(value.Value, ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
        
        # __btn_sel_all
        with self.subTest(prop='__btn_sel_all'):
            self.assertIsInstance(self.TestScheduleController._AutoScheduleController__btn_sel_all, Button)
            
        # __btn_sel_wkdys
        with self.subTest(prop='__btn_sel_wkdys'):
            self.assertIsInstance(self.TestScheduleController._AutoScheduleController__btn_sel_wkdys, Button)
        
        # __btns_time
        with self.subTest(prop='__btns_time'):
            self.assertIsInstance(self.TestScheduleController._AutoScheduleController__btns_time, list)
            for item in self.TestScheduleController._AutoScheduleController__btns_time:
                with self.subTest(i=item):
                    self.assertIsInstance(item, Button)
                    self.assertTrue(hasattr(item, 'fn'))
                    self.assertIsInstance(item.fn, str)
                    self.assertIn(item.fn, ['up', 'down'])
                    self.assertTrue(hasattr(item, 'mode'))
                    self.assertIsInstance(item.mode, str)
                    self.assertIn(item.mode, ['hr', 'min'])
            
        # __lbls_time
        with self.subTest(prop='__lbls_time'):
            self.assertIsInstance(self.TestScheduleController._AutoScheduleController__lbls_time, dict)
            for key, value in self.TestScheduleController._AutoScheduleController__lbls_time.items():
                with self.subTest(i=key):
                    self.assertIsInstance(key, str)
                    self.assertIsInstance(value, Label)
                    self.assertTrue(hasattr(value, 'Value'))
                    self.assertIsInstance(value.Value, int)
            
        # __btns_ampm
        with self.subTest(prop='__btns_ampm'):
            self.assertIsInstance(self.TestScheduleController._AutoScheduleController__btns_ampm, MESet)
            for item in self.TestScheduleController._AutoScheduleController__btns_ampm.Objects:
                with self.subTest(i=item):
                    self.assertTrue(hasattr(item, 'Value'))
                    self.assertIsInstance(item.Value, str)
                    self.assertIn(item.Value, ['AM', 'PM'])
            
        # __btn_save
        with self.subTest(prop='__btn_save'):
            self.assertIsInstance(self.TestScheduleController._AutoScheduleController__btn_save, Button)
        
        # __btn_cancel
        with self.subTest(prop='__btn_cancel'):
            self.assertIsInstance(self.TestScheduleController._AutoScheduleController__btn_cancel, Button)
        
        # __editor_pattern
        with self.subTest(prop='__editor_pattern'):
            self.assertIsInstance(self.TestScheduleController._AutoScheduleController__editor_pattern, Label)
            self.assertTrue(hasattr(self.TestScheduleController._AutoScheduleController__editor_pattern, 'Mode'))
            self.assertTrue(hasattr(self.TestScheduleController._AutoScheduleController__editor_pattern, 'Pattern'))
        
        # __AutoStartClock
        with self.subTest(prop='__AutoStartClock'):
            self.assertIsInstance(self.TestScheduleController._AutoScheduleController__AutoStartClock, Clock)
        
        # __AutoShutdownClock
        with self.subTest(prop='__AutoShutdownClock'):
            self.assertIsInstance(self.TestScheduleController._AutoScheduleController__AutoShutdownClock, Clock)
        
    def test_ScheduleController_PRIV_UpdatePattern(self):
        self.TestScheduleController._AutoScheduleController__pattern_start.Pattern = self.TestScheduleController._AutoScheduleController__default_pattern
        self.TestScheduleController._AutoScheduleController__pattern_shutdown.Pattern = self.TestScheduleController._AutoScheduleController__default_pattern

        # exec method
        ## test Mode == None
        with self.subTest(mode='None'):
            try:
                self.TestScheduleController._AutoScheduleController__UpdatePattern() # None is default
            except Exception as inst:
                self.fail("__UpdatePatter() raised {} unexpectedly!".format(type(inst)))
            
        ## test Mode == 'start'
        with self.subTest(mode='start'):
            try:
                self.TestScheduleController._AutoScheduleController__UpdatePattern('start')
            except Exception as inst:
                self.fail("__UpdatePattern() raised {} unexpectedly!".format(type(inst)))
        
        ## test Mode == 'shutdown'
        with self.subTest(mode='None'):
            try:
                self.TestScheduleController._AutoScheduleController__UpdatePattern('shutdown')
            except Exception as inst:
                self.fail("__UpdatePattern() raised {} unexpectedly!".format(type(inst)))
        
        ## test no patterns
        with self.subTest(mode='patternless'):
            self.TestScheduleController._AutoScheduleController__pattern_start.Pattern = None
            self.TestScheduleController._AutoScheduleController__pattern_shutdown.Pattern = None
            
            try:
                self.TestScheduleController._AutoScheduleController__UpdatePattern('start')
                self.TestScheduleController._AutoScheduleController__UpdatePattern('shutdown')
            except Exception as inst:
                self.fail("__UpdatePattern() raised {} unexpectedly!".format(type(inst)))
        
        with self.subTest(mode='garbage'):
            self.assertRaises(ValueError, self.TestScheduleController._AutoScheduleController__UpdatePattern, {'Mode', 'garbage input'})
    
    def test_ScheduleController_PRIV_PatternToText(self):
        
        # setup for test
        testPatternList = \
            [
                {
                    'Days': 
                        [
                            'Monday',
                            'Tuesday',
                            'Thursday',
                            'Friday'
                        ],
                    'Time': 
                        {
                            'hr': '4',
                            'min': '15',
                            'ampm': 'PM'
                        }
                },
                {
                    'Days': [],
                    'Time': 
                        {
                            'hr': '12',
                            'min': '00',
                            'ampm': 'AM'
                        }
                },
                {
                    'Days': 
                        [
                            'Monday',
                            'Tuesday',
                            'Wednesday',
                            'Thursday',
                            'Friday',
                            'Saturday',
                            'Sunday'
                        ],
                    'Time': 
                        {
                            'hr': '12',
                            'min': '00',
                            'ampm': 'PM'
                        }
                }
            ]
        
        # exec method
        expectedValList = \
            [
                'M,Tu,Th,F 4:15 PM',
                'None',
                'M,Tu,W,Th,F,Sa,Su 12:00 PM'
            ]
        for i in range(len(testPatternList)):
            with self.subTest(i=testPatternList[i]):
                try:
                    rtnVal = self.TestScheduleController._AutoScheduleController__PatternToText(testPatternList[i])
                except Exception as inst:
                    self.fail("__PatternToText() raised {} unexpectedly!".format(type(inst)))
                
                # test outcomes
                self.assertIsNotNone(rtnVal)
                self.assertEqual(rtnVal, expectedValList[i])
    
    def test_ScheduleController_PRIV_SaveSchedule(self):
        import shutil
        
        with self.subTest(con='Save - No Existing Schedule'):
            if File.Exists(self.TestScheduleController._AutoScheduleController__scheduleFilePath):
                File.DeleteFile(self.TestScheduleController._AutoScheduleController__scheduleFilePath)
            try:
                self.TestScheduleController._AutoScheduleController__SaveSchedule()
            except Exception as inst:
                self.fail("__SaveSchedule() raised {} unexpectedly!".format(type(inst)))
                
        with self.subTest(con='Save - Existing Schedule'):
            shutil.copyfile('./emulatedFileSystem/SFTP/user/states/test_states/test_room_schedule.json', './emulatedFileSystem/SFTP/user/states/test_room_schedule_write.json')
            self.TestScheduleController._AutoScheduleController__scheduleFilePath = '/user/states/test_room_schedule_write.json'
            try:
                self.TestScheduleController._AutoScheduleController__SaveSchedule()
            except Exception as inst:
                self.fail("__SaveSchedule() raised {} unexpectedly!".format(type(inst)))
            os.remove('./emulatedFileSystem/SFTP/user/states/test_room_schedule_write.json')
    
    def test_ScheduleController_PRIV_LoadSchedule_NoFile(self):
        try:
            self.TestScheduleController._AutoScheduleController__LoadSchedule()
        except Exception as inst:
            self.fail("__LoadSchedule() raised {} unexpectedly!".format(type(inst)))
    
    def test_ScheduleController_PRIV_LoadSchedule_TestFile(self):
        context = \
            [
                {
                    'AutoStart': True,
                    'AutoShutdown': True
                },
                {
                    'AutoStart': False,
                    'AutoShutdown': True
                },
                {
                    'AutoStart': True,
                    'AutoShutdown': False
                },
                {
                    'AutoStart': False,
                    'AutoShutdown': False
                }
            ]
        
        self.TestScheduleController._AutoScheduleController__scheduleFilePath = '/user/states/test_states/test_room_schedule.json'
        
        for con in context:
            with self.subTest(i=con):
                self.TestScheduleController.AutoStart = con['AutoStart']
                self.TestScheduleController.AutoShutdown = con['AutoShutdown']
                self.TestScheduleController._AutoScheduleController__LoadSchedule()
        
     
    def test_ScheduleController_PRIV_UpdateEditor(self):
        # setup for test
        testPattern = \
            {
                'Days': 
                    [
                        'Monday',
                        'Wednesday',
                        'Friday'
                    ],
                'Time': {
                    'hr': '4',
                    'min': '15',
                    'ampm': 'PM'
                }
            }
        
        # exec method
        try:
            self.TestScheduleController._AutoScheduleController__UpdateEditor(testPattern)
        except Exception as inst:
            self.fail("__UpdateEditor() raised {} unexpectedly!".format(type(inst)))
        
        # test outcomes
        for key, value in self.TestScheduleController._AutoScheduleController__btns_days.items():
            expectedState = 1 if key in testPattern['Days'] else 0
            self.assertEqual(value.State, expectedState)
            
        self.assertEqual(self.TestScheduleController._AutoScheduleController__lbls_time['hr'].Value, int(testPattern['Time']['hr']))
        self.assertEqual(self.TestScheduleController._AutoScheduleController__lbls_time['min'].Value, int(testPattern['Time']['min']))
        
        self.assertEqual(self.TestScheduleController._AutoScheduleController__btns_ampm.GetCurrent().Value, testPattern['Time']['ampm'])
    
    def test_ScheduleController_PRIV_ScheduleShutdownHandler(self):
        context = ['off', 'share', 'adv_share', 'group_work']
        
        # exec method
        for con in context:
            with self.subTest(i=con):
                self.TestScheduleController.GUIHost.ActCtl.CurrentActivity = con
                try:
                    self.TestScheduleController._AutoScheduleController__ScheduleShutdownHandler(Clock=None, Time=None)
                except Exception as inst:
                    self.fail("__ScheduleShutdownHandler() raised {} unexpectedly!".format(type(inst)))
    
    def test_ScheduleController_PRIV_ScheduleStartHandler(self):
        context = ['off', 'share', 'adv_share', 'group_work']
        
        # exec method
        for con in context:
            with self.subTest(i=con):
                self.TestScheduleController.GUIHost.ActCtl.CurrentActivity = con
                for tp in self.TestGUIController.TPs:
                    tp.SrcCtl.PrimaryDestination.AssignSource(self.TestGUIController.SrcCtl.Sources[0])
                try:
                    self.TestScheduleController._AutoScheduleController__ScheduleStartHandler(Clock=None, Time=None)
                except Exception as inst:
                    self.fail("__ScheduleStartHandler() raised {} unexpectedly!".format(type(inst)))
    
    def test_ScheduleController_PRIV_ClockTime(self):
        # setup for test
        testTimes = \
            [
                {
                    'hr': '4',
                    'min': '15',
                    'ampm': 'PM'
                },
                {
                    'hr': '12',
                    'min': '00',
                    'ampm': 'PM'
                },
                {
                    'hr': '12',
                    'min': '00',
                    'ampm': 'AM'
                },
                {
                    'hr': '6',
                    'min': '37',
                    'ampm': 'AM'
                }
            ]
        
        expectedValues = \
            [
                '16:15:00',
                '12:00:00',
                '00:00:00',
                '06:37:00'
            ]
            
        # exec method
        for i in range(len(testTimes)):
            with self.subTest(i=i):
                clockTime = None
                try:
                    clockTime = self.TestScheduleController._AutoScheduleController__ClockTime(testTimes[i])
                except Exception as inst:
                    self.fail("List sorting ({}) raised {} unexpectedly!".format(testTimes[i], type(inst)))
                    
                # test outcomes
                self.assertIsNotNone(clockTime)
                
                self.assertEqual(clockTime, expectedValues[i])
    
    def test_ScheduleController_PRIV_PopoverInactivityHandler(self):
        # exec method
        try:
            self.TestScheduleController._AutoScheduleController__PopoverInactivityHandler()
        except Exception as inst:
            self.fail("__PopoverInactivityHandler raised {} unexpectedly!".format(type(inst)))
    
    def test_ScheduleController_PRIV_TechPageInactivityHandler(self):
        context = [True, False]
        
        # exec method
        for con in context:
            with self.subTest(i=con):
                self.TestScheduleController.UIHost.TechCtl.TechMenuOpen = con
                try:
                    self.TestScheduleController._AutoScheduleController__TechPageInactivityHandler()
                except Exception as inst:
                    self.fail("__TechPageInactivityHandler raised {} unexpectedly!".format(type(inst)))
    
    # def test_ScheduleController_PRIV_SplashPageInactivityHandler(self):
    #     # exec method
    #     try:
    #         self.TestScheduleController._AutoScheduleController__SplashPageInactivityHandler()
    #     except Exception as inst:
    #         self.fail("__SplashPageInactivityHandler raised {} unexpectedly!".format(type(inst)))
    
    def test_ScheduleController_PRIV_SystemInactivityHandler(self):
        # exec method
        try:
            self.TestScheduleController._AutoScheduleController__SystemInactivityHandler()
        except Exception as inst:
            self.fail("__SystemInactivityHandler raised {} unexpectedly!".format(type(inst)))
            
    def test_ScheduleController_EventHandlers_InactivityMethodHandler(self):
        # exec method
        for key in self.TestScheduleController._AutoScheduleController__inactivityHandlers.keys():
            with self.subTest(i=key):
                try:
                    self.TestScheduleController._AutoScheduleController__InactivityMethodHandler(self.TestUIController, key)
                except Exception as inst:
                    self.fail("__EventHandlers InactivityMethodHandler raised {} unexpectedly!".format(type(inst)))
            
    def test_ScheduleController_EventHandlers_ToggleHandler(self):
        # gather context
        context = \
            [
                {
                    'button': self.TestScheduleController._AutoScheduleController__toggle_start,
                    'action': 'Released'
                },
                {
                    'button': self.TestScheduleController._AutoScheduleController__toggle_shutdown,
                    'action': 'Released'
                }
            ]
        
        # exec method
        self.TestScheduleController.AutoStart = True
        self.TestScheduleController.AutoShutdown = True
        for item in context:
            with self.subTest(parentTest='test_ScheduleController_EventHandlers_ToggleHandler', auto='True', i=item):
                try:
                    self.TestScheduleController._AutoScheduleController__ToggleHandler(item['button'], item['action'])
                except Exception as inst:
                    self.fail("__EventHandlers ToggleHandler raised {} unexpectedly!".format(type(inst)))
        
        self.TestScheduleController.AutoStart = False
        self.TestScheduleController.AutoShutdown = False
        for item in context:
            with self.subTest(parentTest='test_ScheduleController_EventHandlers_ToggleHandler', auto='False', i=item):
                try:
                    self.TestScheduleController._AutoScheduleController__ToggleHandler(item['button'], item['action'])
                except Exception as inst:
                    self.fail("__EventHandlers ToggleHandler raised {} unexpectedly!".format(type(inst)))
            
    def test_ScheduleController_EventHandlers_PatternEditHandler(self):
        # gather context
        context = \
            [
                {
                    'button': self.TestScheduleController._AutoScheduleController__pattern_start,
                    'action': 'Pressed'
                },
                {
                    'button': self.TestScheduleController._AutoScheduleController__pattern_shutdown,
                    'action': 'Pressed'
                },
                {
                    'button': self.TestScheduleController._AutoScheduleController__pattern_start,
                    'action': 'Released'
                },
                {
                    'button': self.TestScheduleController._AutoScheduleController__pattern_shutdown,
                    'action': 'Released'
                }
            ]
        
        # exec method
        for item in context:
            with self.subTest(i=item):
                try:
                    self.TestScheduleController._AutoScheduleController__PatternEditHandler(item['button'], item['action'])
                except Exception as inst:
                    self.fail("__EventHandlers PatternEditHandler raised {} unexpectedly!".format(type(inst)))
            
    def test_ScheduleController_EventHandlers_ActivitySelectHandler(self):
        # gather context
        context = [{'button': obj, 'action': 'Pressed'} for obj in self.TestScheduleController._AutoScheduleController__activity_start.Objects]
        
        # exec method
        for item in context:
            with self.subTest(i=item):
                try:
                    self.TestScheduleController._AutoScheduleController__ActivitySelectHandler(item['button'], item['action'])
                except Exception as inst:
                    self.fail("__EventHandlers ActivitySelectHandler raised {} unexpectedly!".format(type(inst)))
            
    def test_ScheduleController_EventHandlers_DayOfWeekSelectHandler(self):
        # gather context
        context = [{'button': obj, 'action': 'Pressed'} for obj in self.TestScheduleController._AutoScheduleController__btns_days.values()]
        
        self.TestScheduleController._AutoScheduleController__editor_pattern.Pattern = self.TestScheduleController._AutoScheduleController__default_pattern
        
        # exec method
        for item in context:
            with self.subTest(i=item):
                item['button'].SetState(0)
                try:
                    self.TestScheduleController._AutoScheduleController__DayOfWeekSelectHandler(item['button'], item['action'])
                except Exception as inst:
                    self.fail("__EventHandlers DayOfWeekSelectHandler (button state 0) raised {} unexpectedly!".format(type(inst)))
                item['button'].SetState(1)
                try:
                    self.TestScheduleController._AutoScheduleController__DayOfWeekSelectHandler(item['button'], item['action'])
                except Exception as inst:
                    self.fail("__EventHandlers DayOfWeekSelectHandler (button state 1) raised {} unexpectedly!".format(type(inst)))
                
            
    def test_ScheduleController_EventHandlers_SelectAllHandler(self):
        # gather context
        context = \
            [
                {
                    'button': self.TestScheduleController._AutoScheduleController__btn_sel_all,
                    'action': 'Pressed'
                },
                {
                    'button': self.TestScheduleController._AutoScheduleController__btn_sel_all,
                    'action': 'Released'
                }
            ]
        
        self.TestScheduleController._AutoScheduleController__editor_pattern.Pattern = self.TestScheduleController._AutoScheduleController__default_pattern
        
        # exec method
        for item in context:
            with self.subTest(i=item):
                try:
                    self.TestScheduleController._AutoScheduleController__SelectAllHandler(item['button'], item['action'])
                except Exception as inst:
                    self.fail("__EventHandlers SelectAllHandler raised {} unexpectedly!".format(type(inst)))
            
    def test_ScheduleController_EventHandlers_SelectWeekdaysHandler(self):
        # gather context
        context = \
            [
                {
                    'button': self.TestScheduleController._AutoScheduleController__btn_sel_wkdys,
                    'action': 'Pressed'
                },
                {
                    'button': self.TestScheduleController._AutoScheduleController__btn_sel_wkdys,
                    'action': 'Released'
                }
            ]
        
        self.TestScheduleController._AutoScheduleController__editor_pattern.Pattern = self.TestScheduleController._AutoScheduleController__default_pattern
        
        # exec method
        for item in context:
            with self.subTest(i=item):
                try:
                    self.TestScheduleController._AutoScheduleController__SelectWeekdaysHandler(item['button'], item['action'])
                except Exception as inst:
                    self.fail("__EventHandlers SelectWeekdaysHandler raised {} unexpectedly!".format(type(inst)))
            
    def test_ScheduleController_EventHandlers_TimeEditHandler(self):
        # gather context
        context = [{'button': obj, 'action': 'Pressed'} for obj in self.TestScheduleController._AutoScheduleController__btns_time]
        context.extend([{'button': obj, 'action': 'Released'} for obj in self.TestScheduleController._AutoScheduleController__btns_time])
        print(context)
        self.TestScheduleController._AutoScheduleController__editor_pattern.Pattern = self.TestScheduleController._AutoScheduleController__default_pattern
        
        # exec method
        for item in context:
            with self.subTest(con=item):
                timesList = [
                    {
                        'hr': 12,
                        'min': 00
                    },
                    {
                        'hr': 1,
                        'min': 30
                    },
                    {
                        'hr': 6,
                        'min': 59
                    },
                ]
                for time in timesList:
                    with self.subTest(i=time):
                        self.TestScheduleController._AutoScheduleController__lbls_time['hr'].Value = time['hr']
                        self.TestScheduleController._AutoScheduleController__lbls_time['min'].Value = time['min']
                        try:
                            self.TestScheduleController._AutoScheduleController__TimeEditHandler(item['button'], item['action'])
                        except Exception as inst:
                            self.fail("__EventHandlers TimeEditHandler raised {} unexpectedly!".format(type(inst)))
            
    def test_ScheduleController_EventHandlers_AMPMEditHandler(self):
        # gather context
        context = [{'button': obj, 'action': 'Pressed'} for obj in self.TestScheduleController._AutoScheduleController__btns_ampm.Objects]
        
        self.TestScheduleController._AutoScheduleController__editor_pattern.Pattern = self.TestScheduleController._AutoScheduleController__default_pattern
        
        # exec method
        for item in context:
            with self.subTest(i=item):
                try:
                    self.TestScheduleController._AutoScheduleController__AMPMEditHandler(item['button'], item['action'])
                except Exception as inst:
                    self.fail("__EventHandlers AMPMEditHandler raised {} unexpectedly!".format(type(inst)))
            
    def test_ScheduleController_EventHandlers_EditorSaveHandler(self):
        # gather context
        context = \
            [
                {
                    'button': self.TestScheduleController._AutoScheduleController__btn_save,
                    'action': 'Pressed'
                },
                {
                    'button': self.TestScheduleController._AutoScheduleController__btn_save,
                    'action': 'Released'
                }
            ]
            
        self.TestScheduleController._AutoScheduleController__editor_pattern.Pattern = self.TestScheduleController._AutoScheduleController__default_pattern
        
        # exec method
        for item in context:
            with self.subTest(i=item):
                self.TestScheduleController._AutoScheduleController__editor_pattern.Mode = 'start'
                try:
                    self.TestScheduleController._AutoScheduleController__EditorSaveHandler(item['button'], item['action'])
                except Exception as inst:
                    self.fail("__EventHandlers EditorSaveHandler raised {} unexpectedly!".format(type(inst)))
                
                self.TestScheduleController._AutoScheduleController__editor_pattern.Mode = 'shutdown'
                try:
                    self.TestScheduleController._AutoScheduleController__EditorSaveHandler(item['button'], item['action'])
                except Exception as inst:
                    self.fail("__EventHandlers EditorSaveHandler raised {} unexpectedly!".format(type(inst)))
            
    def test_ScheduleController_EventHandlers_EditorCancelHandler(self):
        # gather context
        context = \
            [
                {
                    'button': self.TestScheduleController._AutoScheduleController__btn_cancel,
                    'action': 'Pressed'
                },
                {
                    'button': self.TestScheduleController._AutoScheduleController__btn_cancel,
                    'action': 'Released'
                }
            ]
        
        # exec method
        for item in context:
            with self.subTest(i=item):
                try:
                    self.TestScheduleController._AutoScheduleController__EditorCancelHandler(item['button'], item['action'])
                except Exception as inst:
                    self.fail("__EventHandlers EditorCancelHandler raised {} unexpectedly!".format(type(inst)))
    
if __name__ == '__main__':
    unittest.main()