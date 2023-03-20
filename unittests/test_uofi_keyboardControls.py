import unittest
from typing import Dict, Tuple, List, Callable, Union, cast

## test imports ----------------------------------------------------------------
from uofi_gui import GUIController
from uofi_gui.uiObjects import ExUIDevice
from uofi_gui.keyboardControl import KeyboardController
import settings

from extronlib.device import UIDevice
from extronlib.ui import Button, Label
from extronlib.system import Timer

## -----------------------------------------------------------------------------

class KeyboardController_TestClass(unittest.TestCase): # rename for module to be tested
    def setUp(self) -> None:
        self.TestCtls = ['CTL001']
        self.TestTPs = ['TP001']
        self.TestGUIController = GUIController(settings, self.TestCtls, self.TestTPs)
        self.TestGUIController.Initialize()
        self.TestUIController = self.TestGUIController.TP_Main
        self.TestKeyboardController = self.TestUIController.KBCtl
        return super().setUp()
    
    def test_KeyboardController_Type(self):
        self.assertIsInstance(self.TestKeyboardController, KeyboardController)
    
    def test_KeyboardController_Properties(self):
        # UIHost
        with self.subTest(param='UIHost'):
            self.assertIsInstance(self.TestKeyboardController.UIHost, (UIDevice, ExUIDevice))
        
        # CapsLock
        with self.subTest(param='CapsLock'):
            self.assertIsInstance(self.TestKeyboardController.CapsLock, bool)
        
        # Shift
        with self.subTest(param='Shift'):
            self.assertIsInstance(self.TestKeyboardController.Shift, bool)
        
        # Text
        with self.subTest(param='Text'):
            self.assertIsInstance(self.TestKeyboardController.Text, str)
        
        # Callback
        with self.subTest(param='Callback'):
            self.assertIsInstance(self.TestKeyboardController.Callback, (Callable, type(None)))
    
    def test_KeyboardController_PRIV_Properties(self):
        # __KBDict
        with self.subTest(param='__KBDict'):
            self.assertIsInstance(self.TestKeyboardController._KeyboardController__KBDict, dict)
            for key, value in self.TestKeyboardController._KeyboardController__KBDict.items():
                with self.subTest(item=key):
                    self.assertIsInstance(key, str)
                    self.assertIsInstance(value, tuple)
                    self.assertIsInstance(value[0], str)
                    self.assertIsInstance(value[1], str)
        
        # __CharBtns
        with self.subTest(param='__CharBtns'):
            self.assertIsInstance(self.TestKeyboardController._KeyboardController__CharBtns, list)
            for item in self.TestKeyboardController._KeyboardController:
                with self.subTest(item=item.Name):
                    self.assertIsInstance(item, Button)
        
        # __SaveBtn
        with self.subTest(param='__SaveBtn'):
            self.assertIsInstance(self.TestKeyboardController._KeyboardController__SaveBtn, Button)
        
        # __CancelBtn
        with self.subTest(param='__SaveBtn'):
            self.assertIsInstance(self.TestKeyboardController._KeyboardController__SaveBtn, Button)
        
        # __LeftBtn
        with self.subTest(param='__LeftBtn'):
            self.assertIsInstance(self.TestKeyboardController._KeyboardController__LeftBtn, Button)
        
        # __RightBtn
        with self.subTest(param='__RightBtn'):
            self.assertIsInstance(self.TestKeyboardController._KeyboardController__RightBtn, Button)
        
        # __ShiftBtn
        with self.subTest(param='__ShiftBtn'):
            self.assertIsInstance(self.TestKeyboardController._KeyboardController__ShiftBtn, Button)
        
        # __CapsBtn
        with self.subTest(param='__CapsBtn'):
            self.assertIsInstance(self.TestKeyboardController._KeyboardController__CapsBtn, Button)
        
        # __BSBtn
        with self.subTest(param='__BSBtn'):
            self.assertIsInstance(self.TestKeyboardController._KeyboardController__BSBtn, Button)
        
        # __DelBtn
        with self.subTest(param='__DelBtn'):
            self.assertIsInstance(self.TestKeyboardController._KeyboardController__DelBtn, Button)
        
        # __TextLbl
        with self.subTest(param='__TextLbl'):
            self.assertIsInstance(self.TestKeyboardController._KeyboardController__TextLbl, Label)
        
        # __Cursor
        with self.subTest(param='__Cursor'):
            self.assertIsInstance(self.TestKeyboardController._KeyboardController__Cursor, tuple)
            self.assertIsInstance(self.TestKeyboardController._KeyboardController__Curson[0], str)
            self.assertIsInstance(self.TestKeyboardController._KeyboardController__Curson[1], str)
        
        # __Pos
        with self.subTest(param='__Pos'):
            self.assertIsInstance(self.TestKeyboardController._KeyboardController__Pos, int)
        
        # __CursorTimer
        with self.subTest(param='__CursorTimer'):
            self.assertIsInstance(self.TestKeyboardController._KeyboardController__CursorTimer, Timer)
    
    def test_KeyboardController_EventHandler_CharBtnHandler(self):
        btnList = [self.TestKeyboardController._KeyboardController__CharBtns]
        actList = ['Pressed', 'Released']
        contextList = [True, False]
        for btn in btnList:
            for act in actList:
                for con in contextList:
                    with self.subTest(button=btn, action=act, context=con):
                        try:
                            self.TestKeyboardController.Shift = con
                            self.TestKeyboardController._KeyboardController__CharBtnHandler(btn, act)
                        except Exception as inst:
                            self.fail('__CharBtnHandler raised {} unexpectedly!'.format(type(inst)))
    
    def test_KeyboardController_EventHandler_ShiftBtnHandler(self):
        btnList = [self.TestKeyboardController._KeyboardController__ShiftBtn]
        actList = ['Pressed', 'Released']
        contextList = [True, False]
        
        for btn in btnList:
            for act in actList:
                for con in contextList:
                    with self.subTest(button=btn, action=act, context=con):
                        try:
                            self.TestKeyboardController.Shift = con
                            self.TestKeyboardController._KeyboardController__ShiftBtnHandler(btn, act)
                        except Exception as inst:
                            self.fail('__ShiftBtnHandler raised {} unexpectedly!'.format(type(inst)))
    
    def test_KeyboardController_EventHandler_CapsLockBtnHandler(self):
        btnList = [self.TestKeyboardController._KeyboardController__CapsBtn]
        actList = ['Pressed', 'Released']
        contextList = [True, False]
        
        for btn in btnList:
            for act in actList:
                for con in contextList:
                    with self.subTest(button=btn, action=act, context=con):
                        try:
                            self.TestKeyboardController.CapsLock = con
                            self.TestKeyboardController._KeyboardController__CapsLockBtnHandler(btn, act)
                        except Exception as inst:
                            self.fail('__CapsLockBtnHandler raised {} unexpectedly!'.format(type(inst)))
    
    def test_KeyboardController_EventHandler_ArrowBtnHandler(self):
        btnList = [self.TestKeyboardController._KeyboardController__LeftBtn, self.TestKeyboardController._KeyboardController__RightBtn]
        actList = ['Pressed', 'Released']
        textList = ['Text String 1', 'More text goes in here']
        
        for text in textList:
            self.TestKeyboardController.Text = text
            for i in range(len(text)):
                self.TestKeyboardController._KeyboardController_Pos = i
                for btn in btnList:
                    for act in actList:
                        with self.subTest(button=btn, action=act, text=text, pos=i):
                            try:
                                self.TestKeyboardController._KeyboardController__ArrowBtnHandler(btn, act)
                            except Exception as inst:
                                self.fail('__ArrowBtnHandler raised {} unexpectedly!'.format(type(inst)))
    
    def test_KeyboardController_EventHandler_BackspaceBtnHandler(self):
        btnList = [self.TestKeyboardController._KeyboardController__BSBtn]
        actList = ['Pressed', 'Released']
        
        self.TestKeyboardController.Text = 'Text'
        self.TestKeyboardController._KeyboardController_Pos = 2
        for btn in btnList:
            for act in actList:
                with self.subTest(button=btn, action=act):
                    try:
                        self.TestKeyboardController._KeyboardController__BackspaceBtnHandler(btn, act)
                    except Exception as inst:
                        self.fail('__BackspaceBtnHandler raised {} unexpectedly!'.format(type(inst)))
    
    def test_KeyboardController_EventHandler_DeleteBtnHandler(self):
        btnList = [self.TestKeyboardController._KeyboardController__DelBtn]
        actList = ['Pressed', 'Released']
        
        self.TestKeyboardController.Text = 'Text'
        self.TestKeyboardController._KeyboardController_Pos = 2
        for btn in btnList:
            for act in actList:
                with self.subTest(button=btn, action=act):
                    try:
                        self.TestKeyboardController._KeyboardController__DeleteBtnHandler(btn, act)
                    except Exception as inst:
                        self.fail('__DeleteBtnHandler raised {} unexpectedly!'.format(type(inst)))
    
    def test_KeyboardController_EventHandler_SaveBtnHandler(self):
        btnList = [self.TestKeyboardController._KeyboardController__SaveBtn]
        actList = ['Pressed', 'Released']
        
        for btn in btnList:
            for act in actList:
                with self.subTest(button=btn, action=act):
                    try:
                        self.TestKeyboardController._KeyboardController__SaveBtnHandler(btn, act)
                    except Exception as inst:
                        self.fail('__SaveBtnHandler raised {} unexpectedly!'.format(type(inst)))
    
    def test_KeyboardController_EventHandler_CancelBtnHandler(self):
        btnList = [self.TestKeyboardController._KeyboardController__CancelBtn]
        actList = ['Pressed', 'Released']
        
        for btn in btnList:
            for act in actList:
                with self.subTest(button=btn, action=act):
                    try:
                        self.TestKeyboardController._KeyboardController__CancelBtnHandler(btn, act)
                    except Exception as inst:
                        self.fail('__CancelBtnHandler raised {} unexpectedly!'.format(type(inst)))
    
    def test_KeyboardController_EventHandler_CursorTimerHandler(self):
        for i in range(31):
            with self.subTest(count=i):
                try:
                    self.TestKeyboardController._KeyboardController__CursorTimerHandler(self.TestKeyboardController._KeyboardController__CursorTimer, i)
                except Exception as inst:
                    self.fail('__CursorTimerHandler raised {} unexpectedly!'.format(type(inst)))
    
    def test_KeyboardController_PRIV_CharIndex(self):
        testList = [True, False]
        
        for cap in testList:
            for shift in testList:
                with self.subTest(capslock=cap, shift=shift):
                    self.TestKeyboardController.CapsLock = cap
                    self.TestKeyboardController.Shift = shift
                    try:
                        i = self.TestKeyboardController._KeyboardController__CharIndex()
                    except Exception as inst:
                        self.fail('__CharIndex raised {} unexpectedly!'.format(type(inst)))
                        
                    if (cap and shift) or (not cap and not shift):
                        self.assertEqual(i, 0)
                    elif (cap and not shift) or (not cap and shift):
                        self.assertEqual(i, 1)
    
    def test_KeyboardController_PRIV_CursorString(self):
        text = "Text string"
        self.TestKeyboardController.Text = text
        for i in range(len(text)+1):
            with self.subTest(pos=i):
                self.TestKeyboardController._KeyboardController__Pos = i
                try:
                    displayStr = self.TestKeyboardController._KeyboardController__CursorString(0)
                    self.assertIn('\u2502', displayStr)
                    self.assertEqual(self.TestKeyboardController._KeyboardController__Pos, displayStr.index('\u2502'))
                    
                    displayStr = self.TestKeyboardController._KeyboardController__CursorString(1)
                    self.assertIn('\u2588', displayStr)
                    self.assertEqual(self.TestKeyboardController._KeyboardController__Pos, displayStr.index('\u2588'))
                except Exception as inst:
                    self.fail('__CursorString raised {} unexpectedly!'.format(type(inst)))
    
    def test_KeyboardController_PRIV_InsertChar(self):
        text = "Text string"
        expectedList = \
            [
                ".Text string",
                "T.ext string",
                "Te.xt string",
                "Tex.t string",
                "Text. string",
                "Text .string",
                "Text s.tring",
                "Text st.ring",
                "Text str.ing",
                "Text stri.ng",
                "Text strin.g",
                "Text string."
            ]
        for i in range(len(text)+1):
            with self.subTest(pos = i):
                self.TestKeyboardController.Text = text
                self.TestKeyboardController._KeyboardController__Pos = i
                try:
                    self.TestKeyboardController._KeyboardController__InsertChar('.')
                except Exception as inst:
                    self.fail('__InsertChar raised {} unexpectedly!'.format(type(inst)))
                    
                self.assertEqual(self.TestKeyboardController.Text, expectedList[i])
    
    def test_KeyboardController_PRIV_RemoveChar(self):
        text = 'Text String'
        expectedLists = \
            {
                '-1':
                    [
                        'Text String',
                        'ext String',
                        'Txt String',
                        'Tet String',
                        'Tex String',
                        'TextString',
                        'Text tring',
                        'Text Sring',
                        'Text Sting',
                        'Text Strng',
                        'Text Strig',
                        'Text Strin',
                    ],
                '1':
                    [
                        'ext String',
                        'Txt String',
                        'Tet String',
                        'Tex String',
                        'TextString',
                        'Text tring',
                        'Text Sring',
                        'Text Sting',
                        'Text Strng',
                        'Text Strig',
                        'Text Strin',
                        'Text String'
                    ]
            }
        removeList = [1, -1]
        
        for dir in removeList:
            for i in range(len(text)+1):
                with self.subTest(direction=str(dir), pos=i):
                    self.TestKeyboardController.Text = text
                    self.TestKeyboardController._KeyboardController__Pos = i
                    try:
                        self.TestKeyboardController._KeyboardController__RemoveChar(dir)
                    except Exception as inst:
                        self.fail('__RemoveChar raised {} unexpectedly!'.format(type(inst)))
                    self.assertEqual(self.TestKeyboardController.Text, expectedLists[str(dir)][i])
    
    def test_KeyboardController_PRIV_UpdateKeyboardState(self):
        try:
            self.TestKeyboardController._KeyboardController__UpdateKeyboardState()
        except Exception as inst:
            self.fail('__UpdateKeyboardState raised {} unexpectedly!'.format(type(inst)))
    
    def test_KeyboardController_Open(self):
        def testCallable(value):
            self.assertTrue(True)
            self.assertIsNotNone(value)
        
        try:
            self.TestKeyboardController.Open('Text String', testCallable)
        except Exception as inst:
            self.fail('__UpdateKeyboardState raised {} unexpectedly!'.format(type(inst)))
            
        self.assertEqual(self.TestKeyboardController.Text, 'Text String')
        self.assertTrue(callable(self.TestKeyboardController.Callback))
        self.assertIs(self.TestKeyboardController.Callback, testCallable)
        self.assertEqual(self.TestKeyboardController._KeyboardController__Pos, len('Text String'))
    
    def test_KeyboardController_Save(self):
        def testCallable(value):
            self.assertTrue(True)
            self.assertIsNotNone(value)
        
        try:
            self.TestKeyboardController.Open('Text String', testCallable)
            self.TestKeyboardController.Save()
        except Exception as inst:
            self.fail('__UpdateKeyboardState raised {} unexpectedly!'.format(type(inst)))
    
    def test_KeyboardController_Close(self):
        def testCallable(value):
            self.assertTrue(True)
            self.assertIsNotNone(value)
        
        try:
            self.TestKeyboardController.Open('Text String', testCallable)
            self.TestKeyboardController.Close()
        except Exception as inst:
            self.fail('__UpdateKeyboardState raised {} unexpectedly!'.format(type(inst)))
        
        self.assertIsNone(self.TestKeyboardController.Callback)
    
if __name__ == '__main__':
    unittest.main()