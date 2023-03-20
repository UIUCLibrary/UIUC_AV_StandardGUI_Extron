import unittest
from typing import Dict, Tuple, List, Callable, Union, cast

## test imports ----------------------------------------------------------------
from uofi_gui import GUIController
from uofi_gui.uiObjects import ExUIDevice
from uofi_gui.pinControl import PINController
import settings

from extronlib.device import UIDevice
from extronlib.ui import Button, Label
from extronlib.system import Timer

## -----------------------------------------------------------------------------

class PINController_TestClass(unittest.TestCase): # rename for module to be tested
    def setUp(self) -> None:
        self.TestCtls = ['CTL001']
        self.TestTPs = ['TP001']
        self.TestGUIController = GUIController(settings, self.TestCtls, self.TestTPs)
        self.TestGUIController.Initialize()
        self.TestUIController = self.TestGUIController.TP_Main
        self.TestPINController = self.TestUIController.TechPINCtl
        return super().setUp()
    
    def test_PINController_Type(self):
        self.assertIsInstance(self.TestPINController, PINController)
        
    def test_PINController_Properties(self):
        # UIHost
        with self.subTest(param='UIHost'):
            self.assertIsInstance(self.TestPINController.UIHost, (UIDevice, ExUIDevice))
        
        # PIN
        with self.subTest(param='PIN'):
            self.assertIsInstance(self.TestPINController.PIN, str)
            self.assertLessEqual(len(self.TestPINController.PIN), 10)
    
    def test_PINController_PRIV_Properties(self):
        # __CurrentPIN
        with self.subTest(param='__CurrentPIN'):
            self.assertIsInstance(self.TestPINController._PINController__CurrentPIN, str)
        
        # __PINPadBtns
        with self.subTest(param='__PINPadBtns'):
            self.assertIsInstance(self.TestPINController._PINController__PINPadBtns, dict)
            for key, value in self.TestPINController._PINController__PINPadBtns.items():
                with self.subTest(key=key, value=value):
                    self.assertIsInstance(key, str)
                    self.assertIsInstance(value, (list, Button))
                    if type(value) is list:
                        for item in value:
                            with self.subTest(item=item):
                                self.assertIsInstance(item, Button)
        
        # __PINLbl
        with self.subTest(param='__PINLbl'):
            self.assertIsInstance(self.TestPINController._PINController__PINLbl, Label)
        
        # __DestPage
        with self.subTest(param='__DestPage'):
            self.assertIsInstance(self.TestPINController._PINController__DestPage, str)
        
        # __DestPageFn
        with self.subTest(param='__DestPageFn'):
            self.assertTrue(callable(self.TestPINController._PINController__DestPageFn))
        
        # __StartBtn
        with self.subTest(param='__StartBtn'):
            self.assertIsInstance(self.TestPINController._PINController__StartBtn, Button)
    
    def test_PINController_EventHandler_UpdatePINHandler(self):
        btnList = self.TestPINController._PINController__PINPadBtns['numPad']
        actList = ['Pressed', 'Released']
        
        for btn in btnList:
            for act in actList:
                with self.subTest(button=btn.Name, action=act):
                    try:
                        self.TestPINController._PINController__UpdatePINHandler(btn, act)
                    except Exception as inst:
                        self.fail('__UpdatePINHandler raised {} unexpectedly!'.format(type(inst)))
    
    def test_PINController_EventHandler_UpdatePINHandler_Success(self):
        preenteredPIN = self.TestGUIController.TechPIN[0:-1]
        lastBtn = self.TestGUIController.TechPIN[-1:]
        self.TestPINController._PINController__CurrentPIN = preenteredPIN
        try:
            self.TestPINController._PINController__UpdatePINHandler(self.TestUIController.Btns['PIN-{}'.format(lastBtn)], 'Released')
        except Exception as inst:
            self.fail('__UpdatePINHandler raised {} unexpectedly!'.format(type(inst)))
    
    def test_PINController_EventHandler_BackspacePINHandler(self):
        btnList = [self.TestPINController._PINController__PINPadBtns['backspace']]
        actList = ['Pressed', 'Released']
        self.TestPINController._PINController__CurrentPIN = '4444'
        for btn in btnList:
            for act in actList:
                with self.subTest(button=btn.Name, action=act):
                    try:
                        self.TestPINController._PINController__BackspacePINHandler(btn, act)
                    except Exception as inst:
                        self.fail('__BackspacePINHandler raised {} unexpectedly!'.format(type(inst)))
                        
                    if act == 'Released':
                        self.assertEqual(self.TestPINController._PINController__CurrentPIN, '444')
    
    def test_PINController_EventHandler_CancelBtnHandler(self):
        btnList = [self.TestPINController._PINController__PINPadBtns['cancel']]
        actList = ['Pressed', 'Released']
        
        for btn in btnList:
            for act in actList:
                with self.subTest(button=btn.Name, action=act):
                    try:
                        self.TestPINController._PINController__CancelBtnHandler(btn, act)
                    except Exception as inst:
                        self.fail('__CancelBtnHandler raised {} unexpectedly!'.format(type(inst)))
    
    def test_PINController_EventHandler_StartBtnHandler(self):
        btnList = [self.TestPINController._PINController__StartBtn]
        actList = ['Held']
        
        for btn in btnList:
            for act in actList:
                with self.subTest(button=btn.Name, action=act):
                    try:
                        self.TestPINController._PINController__StartBtnHandler(btn, act)
                    except Exception as inst:
                        self.fail('__StartBtnHandler raised {} unexpectedly!'.format(type(inst)))
    
    def test_PINController_PRIV_MaskPIN(self):
        self.TestPINController._PINController__CurrentPIN = '4444'
        
        try:
            self.TestPINController._PINController__MaskPIN()
        except Exception as inst:
            self.fail('__MaskPIN raised {} unexpectedly!'.format(type(inst)))
            
        self.assertEqual(self.TestPINController._PINController__PINLbl._text, '****')
    
    def test_PINController_ResetPIN(self):
        self.TestPINController._PINController__CurrentPIN = '4444'
        
        try:
            self.TestPINController.ResetPIN()
        except Exception as inst:
            self.fail('__MaskPIN raised {} unexpectedly!'.format(type(inst)))
            
        self.assertEqual(self.TestPINController._PINController__CurrentPIN, '')
    
    def test_PINController_ShowPINMenu(self):
        try:
            self.TestPINController.ShowPINMenu()
        except Exception as inst:
            self.fail('__MaskPIN raised {} unexpectedly!'.format(type(inst)))
    
    def test_PINController_HidePINMenu(self):
        try:
            self.TestPINController.HidePINMenu()
        except Exception as inst:
            self.fail('__MaskPIN raised {} unexpectedly!'.format(type(inst)))

if __name__ == '__main__':
    unittest.main()