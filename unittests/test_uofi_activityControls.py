import unittest

## test imports ----------------------------------------------------------------
from uofi_gui import GUIController
from uofi_gui.activityControls import ActivityController
from uofi_gui.uiObjects import ExUIDevice
from uofi_gui.scheduleControls import AutoScheduleController
import settings

from extronlib.ui import Button, Label, Level
from extronlib.system import MESet, Clock, Timer
## -----------------------------------------------------------------------------

class ActivityController_TestClass(unittest.TestCase): # rename for module to be tested
    def setUp(self) -> None:
        self.TestCtls = ['CTL001']
        self.TestTPs = ['TP001']
        self.TestGUIController = GUIController(settings, self.TestCtls, self.TestTPs)
    
    def init_ActCtl(self):
        self.TestGUIController.Initialize()
        self.TestUIController = self.TestGUIController.TP_Main
        self.TestActivityController = self.TestGUIController.ActCtl
    
    def test_ActivityController_Init(self): # configure a test case for each function in the module
        try:
            ActCtl = ActivityController(self.TestGUIController)
        except Exception as inst:
            self.fail("Creating GUIController raised {} unexpectedly!".format(type(inst)))
            
        self.assertIsInstance(ActCtl, ActivityController)
        
    def test_ActivityController_Properties(self):
        self.init_ActCtl()
        
        # GUIHost
        with self.subTest(param='GUIHost'):
            self.assertIsInstance(self.TestActivityController.GUIHost, GUIController)
            
        # CurrentActivity
        with self.subTest(param='CurrentActivity'):
            self.assertIsInstance(self.TestActivityController.CurrentActivity, str)
            self.assertTrue(self.TestActivityController.CurrentActivity in ['off', 'share', 'adv_share', 'group_work'])
    
    def test_ActivityController_PRIV_Properties(self):
        self.init_ActCtl()
        
        # __StartupTime
        with self.subTest(param='__StartupTime'):
            self.assertIsInstance(self.TestActivityController._ActivityController__StartupTime, int)
            self.assertTrue(self.TestActivityController._ActivityController__StartupTime > 0)
        
        # __SwitchTime
        with self.subTest(param='__SwitchTime'):
            self.assertIsInstance(self.TestActivityController._ActivityController__SwitchTime, int)
            self.assertTrue(self.TestActivityController._ActivityController__SwitchTime > 0)
        
        # __ShutdownTime
        with self.subTest(param='__ShutdownTime'):
            self.assertIsInstance(self.TestActivityController._ActivityController__ShutdownTime, int)
            self.assertTrue(self.TestActivityController._ActivityController__ShutdownTime > 0)
        
        # __ConfirmationTime
        with self.subTest(param='__ConfirmationTime'):
            self.assertIsInstance(self.TestActivityController._ActivityController__ConfirmationTime, int)
            self.assertTrue(self.TestActivityController._ActivityController__ConfirmationTime > 0)
        
        # __SplashTime
        with self.subTest(param='__SplashTime'):
            self.assertIsInstance(self.TestActivityController._ActivityController__SplashTime, int)
            self.assertTrue(self.TestActivityController._ActivityController__SplashTime > 0)
        
        # __ActivityBtns
        with self.subTest(param='__ActivityBtns'):
            self.assertIsInstance(self.TestActivityController._ActivityController__ActivityBtns, dict)
            for key, value in self.TestActivityController._ActivityController__ActivityBtns.items():
                with self.subTest(iter=key):
                    self.assertIsInstance(value, list)
                    for item in value:
                        self.assertIsInstance(item, (MESet, Button))
        
        # __ConfTimeLbl
        with self.subTest(param='__ConfTimeLbl'):
            self.assertIsInstance(self.TestActivityController._ActivityController__ConfTimeLbl, list)
            for item in self.TestActivityController._ActivityController__ConfTimeLbl:
                with self.subTest(iter=item):
                    self.assertIsInstance(item, Label)
        
        # __ConfTimeLvl
        with self.subTest(param='__ConfTimeLvl'):
            self.assertIsInstance(self.TestActivityController._ActivityController__ConfTimeLvl, list)
            for item in self.TestActivityController._ActivityController__ConfTimeLvl:
                with self.subTest(iter=item):
                    self.assertIsInstance(item, Level)
        
        # __Transition
        with self.subTest(param='__Transition'):
            self.assertIsInstance(self.TestActivityController._ActivityController__Transition, dict)
            
            self.assertIsInstance(self.TestActivityController._ActivityController__Transition['label'], list)
            for item in self.TestActivityController._ActivityController__Transition['label']:
                with self.subTest(key='label', iter=self.TestActivityController._ActivityController__Transition['label'].index(item)):
                    self.assertIsInstance(item, Label)
                    
            self.assertIsInstance(self.TestActivityController._ActivityController__Transition['level'], list)
            for item in self.TestActivityController._ActivityController__Transition['level']:
                with self.subTest(key='level', iter=self.TestActivityController._ActivityController__Transition['level'].index(item)):
                    self.assertIsInstance(item, Level)
            
            with self.subTest(key='start'):
                self.assertIsInstance(self.TestActivityController._ActivityController__Transition['start'], dict)
                self.assertTrue(callable(self.TestActivityController._ActivityController__Transition['start']['init']))
                self.assertTrue(callable(self.TestActivityController._ActivityController__Transition['start']['sync']))
            
            with self.subTest(key='switch'):
                self.assertIsInstance(self.TestActivityController._ActivityController__Transition['switch'], dict)
                self.assertTrue(callable(self.TestActivityController._ActivityController__Transition['switch']['init']))
                self.assertTrue(callable(self.TestActivityController._ActivityController__Transition['switch']['sync']))
            
            with self.subTest(key='shutdown'):
                self.assertIsInstance(self.TestActivityController._ActivityController__Transition['shutdown'], dict)
                self.assertTrue(callable(self.TestActivityController._ActivityController__Transition['shutdown']['init']))
                self.assertTrue(callable(self.TestActivityController._ActivityController__Transition['shutdown']['sync']))
        
        # __AllSplashCloseBtns
        with self.subTest(param='__AllSplashCloseBtns'):
            self.assertIsInstance(self.TestActivityController._ActivityController__AllSplashCloseBtns, list)
            for item in self.TestActivityController._ActivityController__AllSplashCloseBtns:
                with self.subTest(iter=item):
                    self.assertIsInstance(item, Button)
        
        # __AllSplashBtns
        with self.subTest(param='__AllSplashBtns'):
            self.assertIsInstance(self.TestActivityController._ActivityController__AllSplashBtns, list)
            for item in self.TestActivityController._ActivityController__AllSplashBtns:
                with self.subTest(iter=item):
                    self.assertIsInstance(item, Button)
        
        # __ConfirmationTimer
        with self.subTest(param='__ConfirmationTimer'):
            self.assertIsInstance(self.TestActivityController._ActivityController__ConfirmationTimer, Timer)
        
        # __SwitchTimer
        with self.subTest(param='__SwitchTimer'):
            self.assertIsInstance(self.TestActivityController._ActivityController__SwitchTimer, Timer)
        
        # __StartTimer
        with self.subTest(param='__StartTimer'):
            self.assertIsInstance(self.TestActivityController._ActivityController__StartTimer, Timer)
        
        # __ActivitySplashTimerList
        with self.subTest(param='__ActivitySplashTimerList'):
            self.assertIsInstance(self.TestActivityController._ActivityController__ActivitySplashTimerList, list)
            for item in self.TestActivityController._ActivityController__ActivitySplashTimerList:
                with self.subTest(iter=item):
                    self.assertIsInstance(item, Timer)
        
        # __StatusTimer
        with self.subTest(param='__StatusTimer'):
            self.assertIsInstance(self.TestActivityController._ActivityController__StatusTimer, Timer)
        
    
    def test_ActivityController_EventHandler_ActivityButtonHandler(self):
        self.init_ActCtl()
        context = ['off', 'share', 'adv_share', 'group_work']
        btns = []
        for set in self.TestActivityController._ActivityController__ActivityBtns['select']:
            btns.extend(set.Objects)
        
        for con in context:
            for btn in btns:
                with self.subTest(btn=btn.Name, act='Pressed'):
                    try:
                        self.TestActivityController.CurrentActivity = con
                        for tp in self.TestGUIController.TPs:
                            tp.SrcCtl.PrimaryDestination.AssignSource(self.TestGUIController.SrcCtl.Sources[0])
                        self.TestActivityController._ActivityController__ActivityButtonHandler(btn, 'Pressed')
                    except Exception as inst:
                        self.fail('__ActivityButtonHandler raised {} unexpectedly!'.format(type(inst)))
    
    def test_ActivityController_EventHandler_EndNow(self):
        self.init_ActCtl()
        
        for btn in self.TestActivityController._ActivityController__ActivityBtns['end']:
            with self.subTest(btn=btn.Name, act='Pressed'):
                try:
                    self.TestActivityController._ActivityController__EndNow(btn, 'Pressed')
                except Exception as inst:
                    self.fail('__EndNow raised {} unexpectedly!'.format(type(inst)))
    
    def test_ActivityController_EventHandler_CancelShutdown(self):
        self.init_ActCtl()
        
        for btn in self.TestActivityController._ActivityController__ActivityBtns['cancel']:
            with self.subTest(btn=btn.Name, act='Pressed'):
                try:
                    self.TestActivityController._ActivityController__CancelShutdown(btn, 'Pressed')
                except Exception as inst:
                    self.fail('__CancelShutdown raised {} unexpectedly!'.format(type(inst)))
    
    def test_ActivityController_EventHandler_SwitchTimerStateHandler(self):
        self.init_ActCtl()
        context = ['share', 'adv_share', 'group_work']
        for con in context:
            with self.subTest(context=con):
                self.TestActivityController.CurrentActivity = con
                try:
                    self.TestActivityController._ActivityController__SwitchTimerStateHandler(self.TestActivityController._ActivityController__SwitchTimer, 'Stopped')
                except Exception as inst:
                    self.fail('__SwitchTimerStateHandler raised {} unexpectedly!'.format(type(inst)))
    
    def test_ActivityController_EventHandler_SplashScreenHandler(self):
        self.init_ActCtl()
        
        for btn in self.TestActivityController._ActivityController__AllSplashBtns:
            with self.subTest(btn=btn.Name, act='Pressed'):
                try: 
                    self.TestActivityController._ActivityController__SplashScreenHandler(btn, 'Pressed')
                except Exception as inst:
                    self.fail('__SplashScreenHandler raised {} unexpectedly!'.format(type(inst)))
    
    def test_ActivityController_EventHandler_CloseTipHandler(self):
        self.init_ActCtl()
        srcList = ['PC001', 'WPD001', 'PL001-1']
        for src in srcList:
            for btn in self.TestActivityController._ActivityController__AllSplashCloseBtns:
                with self.subTest(src=src, btn=btn.Name):
                    try: 
                        self.TestActivityController.GUIHost.TPs[btn.TPIndex].SrcCtl.SelectSource(src)
                        print()
                        self.TestActivityController._ActivityController__CloseTipHandler(self.TestActivityController._ActivityController__ActivitySplashTimerList[btn.TPIndex])
                    except Exception as inst:
                        self.fail('__CloseTipHandler raised {} unexpectedly!'.format(type(inst)))
    
    def test_ActivityController_EventHandler_StatusTimerHandler(self):
        self.init_ActCtl()
        
        context = ['share', 'adv_share', 'group_work']
        
        for con in context:
            for i in range(0, 5):
                with self.subTest(context=con, i=i):
                    try:
                        self.TestActivityController._ActivityController__StatusTimerHandler(self.TestActivityController._ActivityController__StatusTimer, i*5)
                    except Exception as inst:
                        self.fail('__StatusTimerHandler raised {} unexpectedly!'.format(type(inst)))
    
    def test_ActivityController_EventHandler_ActivitySplashWaitHandler(self):
        self.init_ActCtl()
        
        for timer in self.TestActivityController._ActivityController__ActivitySplashTimerList:
            self.TestActivityController.GUIHost.TPs[timer.TPIndex].SrcCtl.SelectSource(self.TestGUIController.DefaultSourceId)
            for i in range(self.TestActivityController._ActivityController__SplashTime + 2):
                with self.subTest(timer=timer, i=i):
                    try:
                        self.TestActivityController._ActivityController__ActivitySplashWaitHandler(timer, i)
                    except Exception as inst:
                        self.fail('__ActivitySplashWaitHandler raised {} unexpectedly!'.format(type(inst)))
    
    def test_ActivityController_EventHandler_ConfirmationHandler(self):
        self.init_ActCtl()
        
        for i in range(self.TestActivityController._ActivityController__ConfirmationTime + 1):
            with self.subTest(i=i):
                try:
                    self.TestActivityController._ActivityController__ConfirmationHandler(self.TestActivityController._ActivityController__ConfirmationTimer, i)
                except Exception as inst:
                    self.fail('__ConfirmationHandler raised {} unexpectedly!'.format(type(inst)))
    
    def test_ActivityController_EventHandler_StartUpTimerHandler(self):
        self.init_ActCtl()
        context = ['share', 'adv_share', 'group_work']
        for con in context:
            self.TestActivityController.CurrentActivity = con
            for i in range(self.TestActivityController._ActivityController__StartupTime + 1):
                with self.subTest(context=con, i=i):
                    try:
                        for tp in self.TestGUIController.TPs:
                            tp.SrcCtl.PrimaryDestination.AssignSource(self.TestGUIController.SrcCtl.Sources[0])
                        self.TestActivityController._ActivityController__StartUpTimerHandler(self.TestActivityController._ActivityController__StartTimer, i)
                    except Exception as inst:
                        self.fail('__StartUpTimerHandler raised {} unexpectedly!'.format(type(inst)))
    
    def test_ActivityController_EventHandler_SwitchTimerHandler(self):
        self.init_ActCtl()
        
        for i in range(self.TestActivityController._ActivityController__SwitchTime + 1):
            with self.subTest(i=i):
                try:
                    self.TestActivityController._ActivityController__SwitchTimerHandler(self.TestActivityController._ActivityController__SwitchTimer, i)
                except Exception as inst:
                    self.fail('__SwitchTimerHandler raised {} unexpectedly!'.format(type(inst)))
    
    def test_ActivityController_EventHandler_ShutdownTimerHandler(self):
        self.init_ActCtl()
        
        for i in range(self.TestActivityController._ActivityController__ShutdownTime + 1):
            with self.subTest(i=i):
                try:
                    self.TestActivityController._ActivityController__ShutdownTimerHandler(self.TestActivityController._ActivityController__ShutdownTimer, i)
                except Exception as inst:
                    self.fail('__ShutdownTimerHandler raised {} unexpectedly!'.format(type(inst)))
    
    def test_ActivityController_PRIV_ActivitySwitchTPConfiguration(self):
        self.init_ActCtl()
        
        context = ['share', 'adv_share', 'adv_share|privacy', 'group_work']
        sourceList = \
            [
                self.TestGUIController.SrcCtl.Sources[0],
                self.TestGUIController.SrcCtl.BlankSource
            ]
        
        for src in sourceList:
            for con in context:
                for tp in self.TestActivityController.GUIHost.TPs:
                    with self.subTest(src=src.Name, context=con, tp=tp.Id):
                        try: 
                            if con == 'adv_share|privacy':
                                con = 'adv_share'
                                tp.SrcCtl.SetPrivacyOn()
                            for tp in self.TestGUIController.TPs:
                                tp.SrcCtl.PrimaryDestination.AssignSource(src)
                            self.TestActivityController._ActivityController__ActivitySwitchTPConfiguration(con, tp)
                        except Exception as inst:
                            self.fail('__ActivitySwitchTPConfiguration raised {} unexpectedly!'.format(type(inst)))
    
    def test_ActivityController_StartShutdownConfirmation(self):
        self.init_ActCtl()
        
        context = ['off', 'share', 'adv_share', 'group_work']
        click = [True, False]
        for clk in click:
            for con in context:
                with self.subTest(click=clk, context=con):
                    try:
                        self.TestActivityController.CurrentActivity = con
                        self.TestActivityController.StartShutdownConfirmation(clk)
                    except Exception as inst:
                        self.fail('StartShutdownConfirmation raised {} unexpectedly!'.format(type(inst)))
    
    def test_ActivityController_SystemStart(self):
        self.init_ActCtl()
        
        context = ['share', 'adv_share', 'group_work']
        for con in context:
            with self.subTest(context=con):
                try:
                    self.TestActivityController.SystemStart(con)
                except Exception as inst:
                    self.fail('SystemStart raised {} unexpectedly!'.format(type(inst)))
    
    def test_ActivityController_SystemSwitch(self):
        self.init_ActCtl()
        
        context = ['share', 'adv_share', 'group_work']
        for con in context:
            with self.subTest(context=con):
                try:
                    for tp in self.TestGUIController.TPs:
                            tp.SrcCtl.PrimaryDestination.AssignSource(self.TestGUIController.SrcCtl.Sources[0])
                    self.TestActivityController.SystemSwitch(con)
                except Exception as inst:
                    self.fail('SystemSwitch raised {} unexpectedly!'.format(type(inst)))
    
    def test_ActivityController_SystemShutdown(self):
        self.init_ActCtl()
        
        try:
            self.TestActivityController.SystemShutdown()
        except Exception as inst:
            self.fail('SystemShutdown raised {} unexpectedly!'.format(type(inst)))
    
if __name__ == '__main__':
    unittest.main()