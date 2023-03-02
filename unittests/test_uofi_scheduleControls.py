import unittest

## test imports ----------------------------------------------------------------
from uofi_gui import GUIController
from uofi_gui.activityControls import ActivityController
from uofi_gui.uiObjects import ExUIDevice
from uofi_gui.scheduleControls import AutoScheduleController
import settings

from extronlib.ui import Button, Label
from extronlib.system import MESet, Clock
## -----------------------------------------------------------------------------

class ScheduleController_TestClass(unittest.TestCase): # rename for module to be tested
    def setUp(self) -> None:
        self.TestCtls = ['CTL001']
        self.TestTPs = ['TP001']
        self.TestGUIController = GUIController(settings, self.TestCtls, self.TestTPs)
        self.TestGUIController.Initialize()
        self.TestUIController = self.TestGUIController.TP_Main
        # self.TestGUIController.ActCtl = ActivityController(self)
        # self.TestUIController.InitializeUIControllers()
        self.TestScheduleController = self.TestUIController.SchedCtl
        return super().setUp()
    
    def test_ScheduleController_Type(self): # configure a test case for each function in the module
        self.assertIs(type(self.TestScheduleController), AutoScheduleController)
        pass
    
    def test_ScheduleController_Properties(self):
        self.assertIsInstance(self.TestScheduleController.UIHost, ExUIDevice)
        self.assertIsInstance(self.TestScheduleController.GUIHost, GUIController)
        self.assertIsInstance(self.TestScheduleController.AutoStart, bool)
        self.assertIsInstance(self.TestScheduleController.AutoShutdown, bool)
        
    def test_ScheduleController_PRIV_Properties(self):
        
        # __default_pattern
        self.assertIsInstance(self.TestScheduleController._AutoScheduleController__default_pattern, dict)
        
        # __inactivityHandlers
        self.assertIsInstance(self.TestScheduleController._AutoScheduleController__inactivityHandlers, dict)
        for key, value in self.TestScheduleController._AutoScheduleController__inactivityHandlers.items():
            self.assertIsInstance(key, int)
            self.assertTrue(callable(value))
        
        # __scheduleFilePath
        self.assertIsInstance(self.TestScheduleController._AutoScheduleController__scheduleFilePath, str)
        self.assertIn('/user/states/', self.TestScheduleController._AutoScheduleController__scheduleFilePath)
        
        # __toggle_start
        self.assertIsInstance(self.TestScheduleController._AutoScheduleController__toggle_start, Button)
        self.assertTrue(hasattr(self.TestScheduleController._AutoScheduleController__toggle_start, 'Value'))
        self.assertIsInstance(self.TestScheduleController._AutoScheduleController__toggle_start.Value, str)
        
        # __toggle_shutdown
        self.assertIsInstance(self.TestScheduleController._AutoScheduleController__toggle_shutdown, Button)
        self.assertTrue(hasattr(self.TestScheduleController._AutoScheduleController__toggle_shutdown, 'Value'))
        self.assertIsInstance(self.TestScheduleController._AutoScheduleController__toggle_shutdown.Value, str)
        
        # __pattern_start
        self.assertIsInstance(self.TestScheduleController._AutoScheduleController__pattern_start, Button)
        self.assertTrue(hasattr(self.TestScheduleController._AutoScheduleController__pattern_start, 'Value'))
        self.assertIsInstance(self.TestScheduleController._AutoScheduleController__pattern_start.Value, str)
        self.assertTrue(hasattr(self.TestScheduleController._AutoScheduleController__pattern_start, 'Pattern'))
        self.assertIsInstance(self.TestScheduleController._AutoScheduleController__pattern_start.Pattern, dict)
        
        # __pattern_shutdown
        self.assertIsInstance(self.TestScheduleController._AutoScheduleController__pattern_shutdown, Button)
        self.assertTrue(hasattr(self.TestScheduleController._AutoScheduleController__pattern_shutdown, 'Value'))
        self.assertIsInstance(self.TestScheduleController._AutoScheduleController__pattern_shutdown.Value, str)
        self.assertTrue(hasattr(self.TestScheduleController._AutoScheduleController__pattern_shutdown, 'Pattern'))
        self.assertIsInstance(self.TestScheduleController._AutoScheduleController__pattern_shutdown.Pattern, dict)
        
        # __activity_start
        self.assertIsInstance(self.TestScheduleController._AutoScheduleController__activity_start, MESet)
        
        # __edit_modal
        self.assertIsInstance(self.TestScheduleController._AutoScheduleController__edit_modal, str)
        
        # __btns_days
        self.assertIsInstance(self.TestScheduleController._AutoScheduleController__btns_days, dict)
        self.assertEqual(len(self.TestScheduleController._AutoScheduleController__btns_days), 7)
        for key, value in self.TestScheduleController._AutoScheduleController__btns_days.items():
            self.assertIsInstance(key, str)
            self.assertIsInstance(value, Button)
            self.assertTrue(hasattr(value, 'Value'))
            self.assertIsInstance(value.Value, str)
            self.assertIn(value.Value, ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
        
        # __btn_sel_all
        self.assertIsInstance(self.TestScheduleController._AutoScheduleController__btn_sel_all, Button)
        
        # __btn_sel_wkdys
        self.assertIsInstance(self.TestScheduleController._AutoScheduleController__btn_sel_wkdys, Button)
        
        # __btns_time
        self.assertIsInstance(self.TestScheduleController._AutoScheduleController__btns_time, list)
        for item in self.TestScheduleController._AutoScheduleController__btns_time:
            self.assertIsInstance(item, Button)
            self.assertTrue(hasattr(item, 'fn'))
            self.assertIsInstance(item.fn, str)
            self.assertIn(item.fn, ['up', 'down'])
            self.assertTrue(hasattr(item, 'mode'))
            self.assertIsInstance(item.mode, str)
            self.assertIn(item.mode, ['hr', 'min'])
            
        # __lbls_time
        self.assertIsInstance(self.TestScheduleController._AutoScheduleController__lbls_time, dict)
        for key, value in self.TestScheduleController._AutoScheduleController__lbls_time.items():
            self.assertIsInstance(key, str)
            self.assertIsInstance(value, Label)
            self.assertTrue(hasattr(value, 'Value'))
            self.assertIsInstance(value.Value, int)
            
        # __btns_ampm
        self.assertIsInstance(self.TestScheduleController._AutoScheduleController__btns_ampm, MESet)
        for item in self.TestScheduleController._AutoScheduleController__btns_ampm.Objects:
            self.assertTrue(hasattr(item, 'Value'))
            self.assertIsInstance(item.Value, str)
            self.assertIn(item.Value, ['AM', 'PM'])
            
        # __btn_save
        self.assertIsInstance(self.TestScheduleController._AutoScheduleController__btn_save, Button)
        
        # __btn_cancel
        self.assertIsInstance(self.TestScheduleController._AutoScheduleController__btn_cancel, Button)
        
        # __editor_pattern
        self.assertIsInstance(self.TestScheduleController._AutoScheduleController__editor_pattern, Label)
        self.assertTrue(hasattr(self.TestScheduleController._AutoScheduleController__editor_pattern, 'Mode'))
        self.assertTrue(hasattr(self.TestScheduleController._AutoScheduleController__editor_pattern, 'Pattern'))
        
        # __AutoStartClock
        self.assertIsInstance(self.TestScheduleController._AutoScheduleController__AutoStartClock, Clock)
        
        # __AutoShutdownClock
        self.assertIsInstance(self.TestScheduleController._AutoScheduleController__AutoShutdownClock, Clock)
        
    def test_ScheduleController_PRIV_UpdatePattern(self):
        # verify callable
        self.assertTrue(callable(self.TestScheduleController._AutoScheduleController__UpdatePattern))
        
        # exec method
        ## test Mode == None
        try:
            self.TestScheduleController._AutoScheduleController__UpdatePattern() # None is default
        except Exception as inst:
            self.fail("__UpdatePatter() raised {} unexpectedly!".format(type(inst)))
            
        ## test Mode == 'start'
        try:
            self.TestScheduleController._AutoScheduleController__UpdatePattern('start')
        except Exception as inst:
            self.fail("__UpdatePattern() raised {} unexpectedly!".format(type(inst)))
        
        ## test Mode == 'shutdown'
        try:
            self.TestScheduleController._AutoScheduleController__UpdatePattern('shutdown')
        except Exception as inst:
            self.fail("__UpdatePattern() raised {} unexpectedly!".format(type(inst)))
            
        self.assertRaises(ValueError, self.TestScheduleController._AutoScheduleController__UpdatePattern, {'Mode', 'garbage input'})
    
    def test_ScheduleController_PRIV_PatternToText(self):
        # verify callable
        self.assertTrue(callable(self.TestScheduleController._AutoScheduleController__PatternToText))
        
        # setup for test
        testPattern = \
            {
                'Days': 
                    [
                        'Monday',
                        'Tuesday',
                        'Thursday',
                        'Friday'
                    ],
                'Time': {
                    'hr': '4',
                    'min': '15',
                    'ampm': 'PM'
                }
            }
        
        # exec method
        rtnVal = None
        try:
            rtnVal = self.TestScheduleController._AutoScheduleController__PatternToText(testPattern)
        except Exception as inst:
            self.fail("__PatternToText() raised {} unexpectedly!".format(type(inst)))
        
        # test outcomes
        self.assertIsNotNone(rtnVal)
        self.assertEqual(rtnVal, 'M,Tu,Th,F 4:15 PM')
    
    def test_ScheduleController_PRIV_SaveSchedule(self):
        # verify callable
        self.assertTrue(callable(self.TestScheduleController._AutoScheduleController__SaveSchedule))
        # TODO: do checks on the output of this function (saved file)
    
    def test_ScheduleController_PRIV_LoadSchedule(self):
        # verify callable
        self.assertTrue(callable(self.TestScheduleController._AutoScheduleController__LoadSchedule))
        # TODO: check that this can ingest a file
     
    def test_ScheduleController_PRIV_UpdateEditor(self):
        # verify callable
        self.assertTrue(callable(self.TestScheduleController._AutoScheduleController__UpdateEditor))
        
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
        # verify callable
        self.assertTrue(callable(self.TestScheduleController._AutoScheduleController__ScheduleShutdownHandler))
        
        # exec method
        try:
            self.TestScheduleController._AutoScheduleController__ScheduleShutdownHandler(Clock=None, Time=None)
        except Exception as inst:
            self.fail("__ScheduleShutdownHandler() raised {} unexpectedly!".format(type(inst)))
    
    def test_ScheduleController_PRIV_ScheduleStartHandler(self):
        # verify callable
        self.assertTrue(callable(self.TestScheduleController._AutoScheduleController__ScheduleStartHandler))
        
        # exec method
        try:
            self.TestScheduleController._AutoScheduleController__ScheduleStartHandler(Clock=None, Time=None)
        except Exception as inst:
            self.fail("__ScheduleStartHandler() raised {} unexpectedly!".format(type(inst)))
    
    def test_ScheduleController_PRIV_SortWeekdays(self):
        # verify callable
        self.assertTrue(callable(self.TestScheduleController._AutoScheduleController__SortWeekdays))
        
        # setup for test
        unsortedList = \
            [
                'Friday',
                'Sunday',
                'Wednesday',
                'Monday',
                'Thursday',
                'Saturday',
                'Tuesday'
            ]
            
        sortedList = \
            [
                'Monday', 
                'Tuesday', 
                'Wednesday', 
                'Thursday', 
                'Friday', 
                'Saturday', 
                'Sunday'
            ]
            
        self.assertNotEqual(unsortedList, sortedList)
        
        # exec method
        try:
            unsortedList.sort(key = self.TestScheduleController._AutoScheduleController__SortWeekdays)
        except Exception as inst:
            self.fail("List sorting raised {} unexpectedly!".format(type(inst)))
        
        # test outcomes 
        self.assertEqual(unsortedList, sortedList)
    
    def test_ScheduleController_PRIV_ClockTime(self):
        # verify callable
        self.assertTrue(callable(self.TestScheduleController._AutoScheduleController__ClockTime))
        
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
        # verify callable
        self.assertTrue(callable(self.TestScheduleController._AutoScheduleController__PopoverInactivityHandler))
        
        # exec method
        try:
            self.TestScheduleController._AutoScheduleController__PopoverInactivityHandler()
        except Exception as inst:
            self.fail("__PopoverInactivityHandler raised {} unexpectedly!".format(type(inst)))
    
    def test_ScheduleController_PRIV_TechPageInactivityHandler(self):
        # verify callable
        self.assertTrue(callable(self.TestScheduleController._AutoScheduleController__TechPageInactivityHandler))
        
        # exec method
        try:
            self.TestScheduleController._AutoScheduleController__TechPageInactivityHandler()
        except Exception as inst:
            self.fail("__TechPageInactivityHandler raised {} unexpectedly!".format(type(inst)))
    
    def test_ScheduleController_PRIV_SplashPageInactivityHandler(self):
        # verify callable
        self.assertTrue(callable(self.TestScheduleController._AutoScheduleController__SplashPageInactivityHandler))
        
        # exec method
        try:
            self.TestScheduleController._AutoScheduleController__SplashPageInactivityHandler()
        except Exception as inst:
            self.fail("__SplashPageInactivityHandler raised {} unexpectedly!".format(type(inst)))
    
    def test_ScheduleController_PRIV_SystemInactivityHandler(self):
        # verify callable
        self.assertTrue(callable(self.TestScheduleController._AutoScheduleController__SystemInactivityHandler))
        
        # exec method
        try:
            self.TestScheduleController._AutoScheduleController__SystemInactivityHandler()
        except Exception as inst:
            self.fail("__SystemInactivityHandler raised {} unexpectedly!".format(type(inst)))
    
if __name__ == '__main__':
    unittest.main()