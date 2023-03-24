import unittest

## test imports ----------------------------------------------------------------
from uofi_gui import GUIController
from uofi_gui.uiObjects import ExUIDevice
from uofi_gui.techControls import TechMenuController
import settings

from extronlib.device import UIDevice
from extronlib.ui import Button, Label
from extronlib.system import Timer, MESet
## -----------------------------------------------------------------------------

class TechMenuController_TestClass(unittest.TestCase):
    def setUp(self) -> None:
        self.TestCtls = ['CTL001']
        self.TestTPs = ['TP001']
        self.TestGUIController = GUIController(settings, self.TestCtls, self.TestTPs)
        self.TestGUIController.Initialize()
        self.TestUIController = self.TestGUIController.TP_Main
        self.TestTechController = self.TestUIController.TechCtl
        return super().setUp()
    
    def test_TechMenuController_Type(self):
        self.assertIsInstance(self.TestTechController, TechMenuController)
        
    def test_TechMenuController_Properties(self):
        # UIHost
        with self.subTest(param='UIHost'):
            self.assertIsInstance(self.TestTechController.UIHost, (UIDevice, ExUIDevice))
        
        # GUIHost
        with self.subTest(param='GUIHost'):
            self.assertIsInstance(self.TestTechController.GUIHost, GUIController)
        
        # TechMenuOpen
        with self.subTest(param='TechMenuOpen'):
            self.assertIsInstance(self.TestTechController.TechMenuOpen, bool)
    
    def test_TechMenuController_PRIV_Properties(self):
        # __PageSelects
        with self.subTest(param='__PageSelects'):
            self.assertIsInstance(self.TestTechController._TechMenuController__PageSelects, dict)
            for key, value in self.TestTechController._TechMenuController__PageSelects.items():
                with self.subTest(key=key, value=value):
                    self.assertIsInstance(key, str)
                    self.assertTrue(callable(value))
        
        # __PageUpdates
        with self.subTest(param='__PageUpdates'):
            self.assertIsInstance(self.TestTechController._TechMenuController__PageUpdates, dict)
            for key, value in self.TestTechController._TechMenuController__PageUpdates.items():
                with self.subTest(key=key, value=value):
                    self.assertIsInstance(key, str)
                    self.assertTrue(callable(value))
                    
        # __MenuBtns
        with self.subTest(param='__MenuBtns'):
            self.assertIsInstance(self.TestTechController._TechMenuController__MenuBtns, MESet)
        
        # __DefaultPage
        with self.subTest(param='__DefaultPage'):
            self.assertIsInstance(self.TestTechController._TechMenuController__DefaultPage, str)
        
        # __DefaultBtn
        with self.subTest(param='__DefaultBtn'):
            self.assertIsInstance(self.TestTechController._TechMenuController__DefaultBtn, Button)
        
        # __CtlBtns
        with self.subTest(param='__CtlBtns'):
            self.assertIsInstance(self.TestTechController._TechMenuController__CtlBtns, dict)
            for key, value in self.TestTechController._TechMenuController__CtlBtns.items():
                with self.subTest(key=key, value=value):
                    self.assertIsInstance(key, str)
                    if key == 'menu-pages':
                        self.assertIsInstance(value, list)
                        for item in value:
                            self.assertIsInstance(item, str)
                    else:
                        self.assertIsInstance(value, Button)
        
        # __PageIndex
        with self.subTest(param='__PageIndex'):
            self.assertIsInstance(self.TestTechController._TechMenuController__PageIndex, int)
    
    def test_TechMenuController_EventHandler_TechMenuBtnHandler(self):
        btnList = self.TestTechController._TechMenuController__MenuBtns.Objects
        actList = ['Pressed']
        
        for btn in btnList:
            for act in actList:
                with self.subTest(button=btn, action=act):
                    try:
                        self.TestTechController._TechMenuController__TechMenuBtnHandler(btn, act)
                    except Exception as inst:
                        self.fail('__TechMenuBtnHandler raised {} unexpectedly!'.format(type(inst)))
    
    def test_TechMenuController_EventHandler_TechMenuPrevHandler(self):
        btnList = [self.TestTechController._TechMenuController__CtlBtns['prev']]
        actList = ['Pressed', 'Released']
        
        for btn in btnList:
            for act in actList:
                for i in range(len(self.TestTechController._TechMenuController__CtlBtns['menu-pages'])):
                    with self.subTest(button=btn, action=act, pageIndex=i):
                        self.TestTechController._TechMenuController__PageIndex = i
                        try:
                            self.TestTechController._TechMenuController__TechMenuPrevHandler(btn, act)
                        except Exception as inst:
                            self.fail('__TechMenuPrevHandler raised {} unexpectedly!'.format(type(inst)))

    
    def test_TechMenuController_EventHandler_TechMenuNextHandler(self):
        btnList = [self.TestTechController._TechMenuController__CtlBtns['next']]
        actList = ['Pressed', 'Released']
        
        for btn in btnList:
            for act in actList:
                for i in range(len(self.TestTechController._TechMenuController__CtlBtns['menu-pages'])):
                    with self.subTest(button=btn, action=act, pageIndex=i):
                        self.TestTechController._TechMenuController__PageIndex = i
                        try:
                            self.TestTechController._TechMenuController__TechMenuNextHandler(btn, act)
                        except Exception as inst:
                            self.fail('__TechMenuNextHandler raised {} unexpectedly!'.format(type(inst)))

    
    def test_TechMenuController_EventHandler_TechMenuExitHandler(self):
        btnList = [self.TestTechController._TechMenuController__CtlBtns['exit']]
        actList = ['Pressed', 'Released']
        
        for btn in btnList:
            for act in actList:
                with self.subTest(button=btn, action=act):
                    try:
                        self.TestTechController._TechMenuController__TechMenuExitHandler(btn, act)
                    except Exception as inst:
                        self.fail('__TechMenuExitHandler raised {} unexpectedly!'.format(type(inst)))

    
    def test_TechMenuController_PRIV_AdvVolPage(self):
        try:
            self.TestTechController._TechMenuController__AdvVolPage()
        except Exception as inst:
            self.fail('__AdvVolPage raised {} unexpectedly!'.format(type(inst)))
    
    def test_TechMenuController_PRIV_CamCtlsPage(self):
        try:
            self.TestTechController._TechMenuController__CamCtlsPage()
        except Exception as inst:
            self.fail('__CamCtlsPage raised {} unexpectedly!'.format(type(inst)))
    
    def test_TechMenuController_PRIV_DispCtlPage(self):
        try:
            self.TestTechController._TechMenuController__DispCtlPage()
        except Exception as inst:
            self.fail('__DispCtlPage raised {} unexpectedly!'.format(type(inst)))
    
    def test_TechMenuController_PRIV_ManMtxPage(self):
        try:
            self.TestTechController._TechMenuController__ManMtxPage()
        except Exception as inst:
            self.fail('__ManMtxPage raised {} unexpectedly!'.format(type(inst)))
    
    def test_TechMenuController_PRIV_RmCfgPage(self):
        try:
            self.TestTechController._TechMenuController__RmCfgPage()
        except Exception as inst:
            self.fail('__RmCfgPage raised {} unexpectedly!'.format(type(inst)))
    
    def test_TechMenuController_PRIV_StatusPage(self):
        contextList = [True, False]
        for con in contextList:
            with self.subTest(context=con):
                try:
                    self.TestTechController._TechMenuController__StatusPage(con)
                except Exception as inst:
                    self.fail('__StatusPage raised {} unexpectedly!'.format(type(inst)))
    
    def test_TechMenuController_OpenTechMenu(self):
        try:
            self.TestTechController.OpenTechMenu()
        except Exception as inst:
            self.fail('OpenTechMenu raised {} unexpectedly!'.format(type(inst)))
            
        self.assertTrue(self.TestTechController.TechMenuOpen)
    
    def test_TechMenuController_CloseTechMenu(self):
        contextList = ['off', 'share', 'adv_share', 'group_work']
        for con in contextList:
            with self.subTest(context=con):
                try:
                    self.TestGUIController.ActCtl.CurrentActivity = con
                    self.TestTechController.CloseTechMenu()
                except Exception as inst:
                    self.fail('CloseTechMenu raised {} unexpectedly!'.format(type(inst)))
                
                self.assertFalse(self.TestTechController.TechMenuOpen)
    
if __name__ == '__main__':
    unittest.main()