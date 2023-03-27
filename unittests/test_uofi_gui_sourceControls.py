import unittest
from typing import Dict, Tuple, List, Callable, Union, cast

## test imports ----------------------------------------------------------------
from uofi_gui import GUIController
from uofi_gui.activityControls import ActivityController
from uofi_gui.uiObjects import ExUIDevice
from uofi_gui.sourceControls import SourceController, Source, Destination, MatrixController, MatrixRow, LayoutTuple, RelayTuple, MatrixTuple
from uofi_gui.systemHardware import SystemHardwareController
import settings

from extronlib.ui import Button, Label
from extronlib.system import MESet, Timer
## -----------------------------------------------------------------------------
 
class SourceController_TestClass(unittest.TestCase): # rename for module to be tested
    def setUp(self) -> None:
        self.TestCtls = ['CTL001']
        self.TestTPs = ['TP001']
        self.TestGUIController = GUIController(settings, self.TestCtls, self.TestTPs)
        self.TestGUIController.Initialize()
        self.TestUIController = self.TestGUIController.TP_Main
        self.TestSourceController = self.TestUIController.SrcCtl
        return super().setUp()
    
    def test_SourceController_Type(self):
        self.assertIsInstance(self.TestSourceController, SourceController)
    
    def test_SourceController_Properties(self): # configure a test case for each unit in the module
        # UIHost
        with self.subTest(param='UIHost'):
            self.assertIsInstance(self.TestSourceController.UIHost, ExUIDevice)
        
        # GUIHost
        with self.subTest(param='GUIHost'):
            self.assertIsInstance(self.TestSourceController.GUIHost, GUIController)
        
        # Sources
        with self.subTest(param='Sources'):
            self.assertIsInstance(self.TestSourceController.Sources, list)
            for item in self.TestSourceController.Sources:
                with self.subTest(iter=item.Name):
                    self.assertIsInstance(item, Source)
        
        # Destinations
        with self.subTest(param='Destinations'):
            self.assertIsInstance(self.TestSourceController.Destinations, list)
            for item in self.TestSourceController.Destinations:
                with self.subTest(iter=item.Name):
                    self.assertIsInstance(item, Destination)
        
        # PrimaryDestination
        with self.subTest(param='PrimaryDestination'):
            self.assertIsInstance(self.TestSourceController.PrimaryDestination, Destination)
            
        # SelectedSource
        with self.subTest(param='SelectedSource'):
            self.assertIsNone(self.TestSourceController.SelectedSource) # this inits as none
        
        # Privacy
        with self.subTest(param="Privacy"):
            self.assertFalse(self.TestSourceController.Privacy)
        
        # OpenControlPopup
        with self.subTest(param='OpenControlPopup'):
            self.assertIsNone(self.TestSourceController.OpenControlPopup)
            
        # BlankSource
        with self.subTest(param='BlankSource'):
            self.assertIsInstance(self.TestSourceController.BlankSource, Source)
        
    def test_SourceController_PRIV_Properties(self):
        # __SourceBtns
        with self.subTest(param='__SourceBtns'):
            self.assertIsInstance(self.TestSourceController._SourceController__SourceBtns, MESet)
        
        # __SourceInds
        with self.subTest(param='__SourceInds'):
            self.assertIsInstance(self.TestSourceController._SourceController__SourceInds, MESet)
        
        # __ArrowBtns
        with self.subTest(param='__ArrowBtns'):
            self.assertIsInstance(self.TestSourceController._SourceController__ArrowBtns, list)
            for btn in self.TestSourceController._SourceController__ArrowBtns:
                with self.subTest(btn=btn.Name):
                    self.assertIsInstance(btn, Button)
        
        # __PrivacyBtn
        with self.subTest(param='__PrivacyBtn'):
            self.assertIsInstance(self.TestSourceController._SourceController__PrivacyBtn, Button)
        
        # __ReturnToGroupBtn
        with self.subTest(param='__ReturnToGroupBtn'):
            self.assertIsInstance(self.TestSourceController._SourceController__ReturnToGroupBtn, Button)
        
        # __Offset
        with self.subTest(param='__Offset'):
            self.assertIsInstance(self.TestSourceController._SourceController__Offset, int)
        
        # __AdvLayout
        with self.subTest(param='__AdvLayout'):
            self.assertIsInstance(self.TestSourceController._SourceController__AdvLayout, str)
        
        # __DisplaySrcList
        with self.subTest(param='__DisplaySrcList'):
            self.assertIsInstance(self.TestSourceController._SourceController__DisplaySrcList, list)
        
        # __Privacy
        with self.subTest(param='__Privacy'):
            self.assertIsInstance(self.TestSourceController._SourceController__Privacy, bool)
        
        # __Matrix
        with self.subTest(param='__Matrix'):
            self.assertIsInstance(self.TestSourceController._SourceController__Matrix, MatrixController)
    
    def test_SourceController_EventHandler_SourceBtnHandler(self):
        btnList = self.TestSourceController._SourceController__SourceBtns.Objects
        actList = ['Pressed']
        context = ['share', 'adv_share', 'group_work']
        
        for btn in btnList:
            for act in actList:
                for con in context:
                    with self.subTest(button=btn.Name, action=act, context=con):
                        try:
                            self.TestGUIController.ActCtl.CurrentActivity = con
                            self.TestSourceController._SourceController__SourceBtnHandler(btn, act)
                        except Exception as inst:
                            self.fail('__SourceBtnHandler raised {} unexpectedly!'.format(type(inst)))
    
    def test_SourceController_EventHandler_SourcePageHandler(self):
        btnList = self.TestSourceController._SourceController__ArrowBtns
        actList = ['Pressed']
        
        for btn in btnList:
            for act in actList:
                for i in range(len(self.TestSourceController.Sources) - 4):
                    with self.subTest(button=btn.Name, action=act, offset=i):
                        try:
                            self.TestSourceController._SourceController__Offset = i
                            self.TestSourceController._SourceController__SourcePageHandler(btn, act)
                        except Exception as inst:
                            self.fail('__SourcePageHandler raised {} unexpectedly!'.format(type(inst)))
    
    def test_SourceController_EventHandler_ModalCloseHandler(self):
        btnList = [self.TestSourceController._SourceController__ModalCloseBtn]
        actList = ['Pressed']
        
        for btn in btnList:
            for act in actList:
                with self.subTest(button=btn.Name, action=act):
                    try:
                        self.TestSourceController._SourceController__ModalCloseHandler(btn, act)
                    except Exception as inst:
                        self.fail('__ModalCloseHandler raised {} unexpectedly!'.format(type(inst)))
    
    def test_SourceController_EventHandler_SendToAllHandler(self):
        btnList = [self.TestSourceController._SourceController__SendToAllBtn]
        actList = ['Pressed', 'Released']
        
        for btn in btnList:
            for act in actList:
                    with self.subTest(button=btn.Name, action=act):
                        try:
                            self.TestSourceController._SourceController__SendToAllHandler(btn, act)
                        except Exception as inst:
                            self.fail('__SendToAllHandler raised {} unexpectedly!'.format(type(inst)))
    
    def test_SourceController_EventHandler_ReturnToGroupHandler(self):
        btnList = [self.TestSourceController._SourceController__ReturnToGroupBtn]
        actList = ['Pressed', 'Released']
        
        for btn in btnList:
            for act in actList:
                    with self.subTest(button=btn.Name, action=act):
                        try:
                            self.TestSourceController._SourceController__ReturnToGroupHandler(btn, act)
                        except Exception as inst:
                            self.fail('__ReturnToGroupHandler raised {} unexpectedly!'.format(type(inst)))
    
    def test_SourceController_EventHandler_WPDClearPostsHandler(self):
        btnList = [self.TestSourceController._SourceController__WPDClearPostsBtn]
        actList = ['Pressed', 'Released']
        context_act = ['share', 'adv_share', 'group_work']
        context_src = self.TestSourceController.Sources
        
        for btn in btnList:
            for act in actList:
                for con_act in context_act:
                    for con_src in context_src:
                        with self.subTest(button=btn.Name, action=act, context={'activity': con_act, 'source': con_src.Id}):
                            try:
                                self.TestGUIController.ActCtl.CurrentActivity = con_act
                                self.TestSourceController.SelectSource(con_src)
                                if con_act == 'adv_share':
                                    self.TestSourceController.OpenControlPopup = \
                                        {
                                            'page': 'Modal-SrcCtl-{}'.format(con_src.AdvSourceControlPage),
                                            'source': con_src
                                        }
                                self.TestSourceController._SourceController__WPDClearPostsHandler(btn, act)
                            except KeyError:
                                if con_src.Id.startswith('WPD'):
                                    self.fail('__WPDClearPostsHandler raised a key error for a WPD source ({})'.format(con_src.Id))
                            except Exception as inst:
                                self.fail('__WPDClearPostsHandler raised {} unexpectedly!'.format(type(inst)))
    
    def test_SourceController_EventHandler_WPDClearAllHandler(self):
        btnList = [self.TestSourceController._SourceController__WPDClearAllBtn]
        actList = ['Pressed', 'Released']
        context_act = ['share', 'adv_share', 'group_work']
        context_src = self.TestSourceController.Sources
        
        for btn in btnList:
            for act in actList:
                for con_act in context_act:
                    for con_src in context_src:
                        with self.subTest(button=btn.Name, action=act, context={'activity': con_act, 'source': con_src.Id}):
                            try:
                                self.TestGUIController.ActCtl.CurrentActivity = con_act
                                self.TestSourceController.SelectSource(con_src)
                                if con_act == 'adv_share':
                                    self.TestSourceController.OpenControlPopup = \
                                        {
                                            'page': 'Modal-SrcCtl-{}'.format(con_src.AdvSourceControlPage),
                                            'source': con_src
                                        }
                                self.TestSourceController._SourceController__WPDClearAllHandler(btn, act)
                            except KeyError:
                                if con_src.Id.startswith('WPD'):
                                    self.fail('__WPDClearAllHandler raised a key error for a WPD source')
                            except Exception as inst:
                                self.fail('__WPDClearAllHandler raised {} unexpectedly!'.format(type(inst)))
    
    def test_SourceController_PRIV_GetUIForAdvDest(self): 
        destList = self.TestSourceController.Destinations
        
        for dest in destList:
            with self.subTest(destination=dest.Name):
                try:
                    rtnDict = self.TestSourceController._SourceController__GetUIForAdvDest(dest)
                except Exception as inst:
                    self.fail('__GetUIForAdvDest raised {} unexpectedly!'.format(type(inst)))
                    
                self.assertIsInstance(rtnDict, dict)
                for key, value in rtnDict.items():
                    with self.subTest(rtnDictKey=key, rtnDictValue=value):
                        self.assertIsInstance(key, str)
                        self.assertIsInstance(value, (Button, Label))
    
    def test_SourceController_PRIV_GetUIForAdvDest_BadDest(self): 
        destList = [self.TestSourceController.Destinations[0], self.TestSourceController.Destinations[1]]
        
        destList[0].AdvLayoutPosition = None
        destList[1].AdvLayoutPosition = LayoutTuple(4,7)
        
        for dest in destList:
            with self.subTest(destination=dest.AdvLayoutPosition):
                if destList.index(dest) == 0:
                    with self.assertRaises(LookupError):
                        self.TestSourceController._SourceController__GetUIForAdvDest(dest)
                elif destList.index(dest) == 1:
                    with self.assertRaises(KeyError):
                        self.TestSourceController._SourceController__GetUIForAdvDest(dest)
    
    # def test_SourceController_PRIV_GetPositionByName(self):
    #     pass
    
    def test_SourceController_SourceAlertHandler(self):
        context = ['Alert Message', None]
        for src in self.TestSourceController.Sources:
            for con in context:
                with self.subTest(source=src.Name, context=con):
                    try:
                        self.TestSourceController.SelectSource(src)
                        if con is not None:
                            self.TestSourceController.SelectedSource.AppendAlert(con)
                        else:
                            self.TestSourceController.SelectedSource.ResetAlert()
                        self.TestSourceController.SourceAlertHandler()
                    except Exception as inst:
                        self.fail('SourceAlertHandler raised {} unexpectedly!'.format(type(inst)))
                        
    def test_SourceController_TogglePrivacy(self):
        for i in range(2):
            with self.subTest(iteration=i):
                priv0 = bool(self.TestSourceController.Privacy)
                try:
                    self.TestSourceController.TogglePrivacy()
                except Exception as inst:
                    self.fail('TogglePrivacy raised {} unexpectedly!'.format(type(inst)))
                
                priv1 = bool(self.TestSourceController.Privacy)
                self.assertNotEqual(priv0, priv1)
                        
    def test_SourceController_DynProp_Privacy_On(self):
        cmdList = ['on', 'On', 'ON', 1, True, 'Mute', 'mute', 'MUTE']
        for cmd in cmdList:
            with self.subTest(i=cmd):
                try:
                    self.TestSourceController.Privacy = 'On'
                except Exception as inst:
                    self.fail('Setting Privacy On raised {} unexpectedly!'.format(type(inst)))
                self.assertTrue(self.TestSourceController.Privacy)
                        
    def test_SourceController_DynProp_Privacy_Off(self):
        cmdList = ['off', 'Off', 'OFF', 0, False, 'Unmute', 'unmute', 'UNMUTE']
        for cmd in cmdList:
            with self.subTest(i=cmd):
                try:
                    self.TestSourceController.Privacy = 'Off'
                except Exception as inst:
                    self.fail('Setting Privacy Off raised {} unexpectedly!'.format(type(inst)))
                self.assertFalse(self.TestSourceController.Privacy)
                        
    def test_SourceController_GetAdvShareLayout(self):
        try:
            rtnVal = self.TestSourceController.GetAdvShareLayout()
        except Exception as inst:
            self.fail('GetAdvShareLayout raised {} unexpectedly!'.format(type(inst)))
            
        self.assertRegex(rtnVal, r'^Source-Control-Adv_\d+,\d+$')
                        
    def test_SourceController_GetDestination(self):
        context = \
            [
                ('id', 'PRJ001'),
                ('id', 'MON001'),
                ('name', 'Projector'),
                ('name', 'Confidence Monitor'),
                None
            ]
        for con in context:
            with self.subTest(context=con):
                if con is None:
                    with self.assertRaises(ValueError):
                        self.TestSourceController.GetDestination()
                elif con[0] == 'id':
                    try:
                        rtnVal = self.TestSourceController.GetDestination(id = con[1])
                    except Exception as inst:
                        self.fail('GetDestination (id) raised {} unexpectedly!'.format(type(inst)))
                    self.assertIsInstance(rtnVal, Destination)
                elif con[0] == 'name':
                    try:
                        rtnVal = self.TestSourceController.GetDestination(name = con[1])
                    except Exception as inst:
                        self.fail('GetDestination (name) raised {} unexpectedly!'.format(type(inst)))
                    self.assertIsInstance(rtnVal, Destination)
    
    def test_SourceController_GetDestination_BadInput(self):
        context = \
            [
                ('id', 'PC001'),
                ('id', 1),
                ('id', True),
                ('name', 'Room PC'),
                ('name', 1),
                ('name', True),
            ]
        for con in context:
            with self.subTest(context=con):
                with self.assertRaises(LookupError):
                    if con[0] == 'id':
                        self.TestSourceController.GetDestination(id = con[1])
                    elif con[0] == 'name':
                        self.TestSourceController.GetDestination(id = con[1])
                        
    def test_SourceController_GetDestinationByOutput(self):
        for i in range(1, len(self.TestSourceController.Destinations)+1):
            with self.subTest(output=i):
                try:
                    rtnVal = self.TestSourceController.GetDestinationByOutput(i)
                except Exception as inst:
                    self.fail('GetDestinationByOutput raised {} unexpectedly!'.format(type(inst)))
                
                self.assertIsInstance(rtnVal, Destination)
    
    def test_SourceController_GetDestinationByOutput_BadOutput(self):
        with self.assertRaises(LookupError):
            self.TestSourceController.GetDestinationByOutput(100)
    
    def test_SourceController_GetDestinationIndexByID(self):
        context = \
            [
                'PRJ001',
                'MON001'
            ]
        for con in context:
            with self.subTest(id=con):
                try:
                    rtnVal = self.TestSourceController.GetDestinationIndexByID(con)
                except Exception as inst:
                    self.fail('GetDesitinationByID raised {} unexpectedly!'.format(type(inst)))
                self.assertIsInstance(rtnVal, int)
    
    def test_SourceController_GetDestinationIndexByID_BadId(self):
        with self.assertRaises(LookupError):
            self.TestSourceController.GetDestinationIndexByID('PC001')
                        
    def test_SourceController_GetSource(self):
        context = \
            [
                ('id', 'PC001'),
                ('id', 'WPD001'),
                ('name', 'Room PC'),
                ('name', 'HDMI 1'),
                None
            ]
        for con in context:
            with self.subTest(context=con):
                if con is None:
                    with self.assertRaises(ValueError):
                        self.TestSourceController.GetSource()
                elif con[0] == 'id':
                    try:
                        rtnVal = self.TestSourceController.GetSource(id = con[1])
                    except Exception as inst:
                        self.fail('GetSource (id) raised {} unexpectedly!'.format(type(inst)))
                    self.assertIsInstance(rtnVal, Source)
                elif con[0] == 'name':
                    try:
                        rtnVal = self.TestSourceController.GetSource(name = con[1])
                    except Exception as inst:
                        self.fail('GetSource (name) raised {} unexpectedly!'.format(type(inst)))
                    self.assertIsInstance(rtnVal, Source)
    
    def test_SourceController_GetSource_BadInput(self):
        context = \
            [
                ('id', 'PRJ001'),
                ('id', 1),
                ('id', True),
                ('name', 'Projector'),
                ('name', 1),
                ('name', True),
            ]
        for con in context:
            with self.subTest(context=con):
                with self.assertRaises(LookupError):
                    if con[0] == 'id':
                        self.TestSourceController.GetSource(id = con[1])
                    elif con[0] == 'name':
                        self.TestSourceController.GetSource(id = con[1])
                        
    def test_SourceController_GetSourceByInput(self):
        for i in range(1, len(self.TestSourceController.Sources)+1):
            with self.subTest(input=i):
                try:
                    rtnVal = self.TestSourceController.GetSourceByInput(i)
                except Exception as inst:
                    self.fail('GetSourceByInput raised {} unexpectedly!'.format(type(inst)))
                
                self.assertIsInstance(rtnVal, Source)
    
    def test_SourceController_GetSourceByInput_BadInput(self):
        with self.assertRaises(LookupError):
            self.TestSourceController.GetSourceByInput(100)
            
    def test_SourceController_GetSourceIndexByID(self):
        context = \
            [
                'PC001',
                'WPD001'
            ]
        for con in context:
            with self.subTest(id=con):
                try:
                    rtnVal = self.TestSourceController.GetSourceIndexByID(con)
                except Exception as inst:
                    self.fail('GetSourceIndexByID raised {} unexpectedly!'.format(type(inst)))
                self.assertIsInstance(rtnVal, int)
    
    def test_SourceController_GetSourceIndexByID_BadId(self):
        with self.assertRaises(LookupError):
            self.TestSourceController.GetSourceIndexByID('PRJ001')
            
    def test_SourceController_SetPrimaryDestination(self):
        destList = self.TestSourceController.Destinations
        
        for dest in destList:
            with self.subTest(destination=dest):
                try:
                    self.TestSourceController.SetPrimaryDestination(dest)
                except Exception as inst:
                    self.fail('SetPrimaryDestination raised {} unexpectedly!'.format(type(inst)))
                self.assertIs(self.TestSourceController.PrimaryDestination, dest)
                
    def test_SourceController_SetPrimaryDestination_BadInput(self):
        destList = \
            [
                1,
                "PRJ001",
                'other',
                True,
                None
            ]
        for dest in destList:
            with self.subTest(destination=dest):
                with self.assertRaises(TypeError):
                    self.TestSourceController.SetPrimaryDestination(dest)
                
    def test_SourceController_SelectSource_SrcObj(self):
        srcList = self.TestSourceController.Sources
        
        for src in srcList:
            with self.subTest(source=src):
                try:
                    self.TestSourceController.SelectSource(src)
                except Exception as inst:
                    self.fail('SelectSource raised {} unexpectedly!'.format(type(inst)))
                self.assertIs(self.TestSourceController.SelectedSource, src)
                
    def test_SourceController_SelectSource_SrcStr(self):
        srcList = ['PC001', 'WPD001', 'PL001-1', 'Room PC', 'HDMI 1']
        
        for src in srcList:
            with self.subTest(source=src):
                try:
                    self.TestSourceController.SelectSource(src)
                except Exception as inst:
                    self.fail('SelectSource raised {} unexpectedly!'.format(type(inst)))
                self.assertIn(src, [self.TestSourceController.SelectedSource.Id, self.TestSourceController.SelectedSource.Name])
                
    def test_SourceController_SelectSource_BadInput(self):
        srcList = [1, True, None]
        
        for src in srcList:
            with self.subTest(source=src):
                with self.assertRaises(TypeError):
                    self.TestSourceController.SelectSource(src)
                        
    def test_SourceController_UpdateDisplaySourceList(self):
        contextList = ['off', 'share', 'adv_share', 'group_work']
        
        for con in contextList:
            with self.subTest(context=con):
                self.TestGUIController.ActCtl.CurrentActivity = con
                self.TestSourceController._SourceController__DisplaySrcList = []
                len1 = len(self.TestSourceController._SourceController__DisplaySrcList)
                
                try:
                    self.TestSourceController.UpdateDisplaySourceList()
                except Exception as inst:
                    self.fail('UpdateDisplaySourceList raised {} unexpectedly!'.format(type(inst)))
                    
                len2 = len(self.TestSourceController._SourceController__DisplaySrcList)
                
                self.assertGreater(len2, len1)
                        
    def test_SourceController_UpdateSourceMenu(self):
        srcLen = len(self.TestSourceController._SourceController__DisplaySrcList)
        for i in range(srcLen):
            with self.subTest(iteration=i):
                try:
                    self.TestSourceController.UpdateSourceMenu()
                except Exception as inst:
                    self.fail('UpdateDisplaySourceList raised {} unexpectedly!'.format(type(inst)))
                self.TestSourceController.Sources.pop()
                        
    def test_SourceController_ShowSelectedSource(self):
        self.TestSourceController.SelectSource(self.TestGUIController.DefaultSourceId)
        self.TestSourceController.UpdateDisplaySourceList()
        srcLen = len(self.TestSourceController._SourceController__DisplaySrcList)
        for i in range(srcLen):
            for j in range(len(self.TestSourceController.Sources) - 4):
                with self.subTest(iteration=i, offset=j):
                    try:
                        self.TestSourceController._SourceController__Offset = j
                        self.TestSourceController.ShowSelectedSource()
                    except Exception as inst:
                        self.fail('ShowSelectedSource raised {} unexpectedly!'.format(type(inst)))
                    self.TestSourceController.Sources.pop()
    
    # TODO: Figure out a way to test these two functions while the run asynchronously
    # def test_SourceController_SwitchSources(self):
    #     try:
    #         self.TestSourceController.SwitchSources('PC001', 'All')
    #     except Exception as inst:
    #         self.fail('ShowSelectedSource raised {} unexpectedly!'.format(type(inst)))
    
    # def test_SourceController_MatrixSwitch(self):
    #     pass
    
class Source_TestClass(unittest.TestCase): # rename for module to be tested
    def setUp(self) -> None:
        self.TestCtls = ['CTL001']
        self.TestTPs = ['TP001']
        self.TestGUIController = GUIController(settings, self.TestCtls, self.TestTPs)
        self.TestGUIController.Initialize()
        self.TestUIController = self.TestGUIController.TP_Main
        self.TestSourceController = self.TestUIController.SrcCtl
        self.TestSource = Source(self.TestSourceController, 'TEST001', 'Test Source', 1, 8, 'Test Alert Text', 'WPD', 'WPD')
        return super().setUp()
    
    def test_Source_Type(self):
        self.assertIsInstance(self.TestSource, Source)
    
    def test_Source_Properties(self):
        # SourceController
        with self.subTest(param='SourceController'):
            self.assertIsInstance(self.TestSource.SourceController, SourceController)
        
        # Id
        with self.subTest(param='Id'):
            self.assertIsInstance(self.TestSource.Id, str)
        
        # Name
        with self.subTest(param='Name'):
            self.assertIsInstance(self.TestSource.Name, str)
        
        # Icon
        with self.subTest(param='Icon'):
            self.assertIsInstance(self.TestSource.Icon, int)
        
        # Input
        with self.subTest(param='Input'):
            self.assertIsInstance(self.TestSource.Input, int)
        
        # SourceControlPage
        with self.subTest(param='SourceControlPage'):
            self.assertIsInstance(self.TestSource.SourceControlPage, (str, type(None)))
        
        # AdvSourceControlPage
        with self.subTest(param='AdvSourceControlPage'):
            self.assertIsInstance(self.TestSource.AdvSourceControlPage, (str, type(None)))
        
        # AlertText (Dynamic)
        with self.subTest(param='AlertText'):
            self.assertIsInstance(self.TestSource.AlertText, str)
        
        # AlertBlock (Dynamic)
        with self.subTest(param='AlertBlock'):
            self.assertIsInstance(self.TestSource.AlertBlock, str)
        
        # Alerts (Dynamic)
        with self.subTest(param='Alerts'):
            self.assertIsInstance(self.TestSource.Alerts, int)
        
        # AlertFlag (Dynamic)
        with self.subTest(param='AlertFlag'):
            self.assertIsInstance(self.TestSource.AlertFlag, bool)
    
    def test_Source_DynProp_AlertText(self):
        AlertList = ['Test Alert 1', 'Test Alert 2', 'Test Alert 3']
        for alert in AlertList:
            with self.subTest(alert=alert):
                try:
                    self.TestSource.AppendAlert(alert)
                    rtn1 = self.TestSource.AlertText
                    self.assertIsInstance(rtn1, str)
                    if self.TestSource.Alerts > 1:
                        rtn2 = self.TestSource.AlertText
                        self.assertNotEqual(rtn1, rtn2)
                except Exception as inst:
                    self.fail('AlertText (dynamic property) raised {} unexpectedly!'.format(type(inst)))
    
    def test_Source_DynProp_AlertText_Override(self):
        alerttext = 'Override Source Alert'
        self.TestSource.OverrideAlert(alerttext)
        try:
            rtn = self.TestSource.AlertText
        except Exception as inst:
            self.fail('AlertText (dynamic property) raised {} unexpectedly!'.format(type(inst)))
        self.assertEqual(rtn, alerttext)
    
    def test_Source_DynProp_AlertBlock(self):
        alertList = ['Alert Text 1', 'Alert Text 2', 'Alert Text 3', None]
        for alert in alertList:
            with self.subTest(alert=alert):
                try:
                    if alert is not None:
                        self.TestSource.AppendAlert(alert)
                    else:
                        self.TestSource.OverrideAlert('Override Alert Text')
                        alert = 'Override Alert Text'
                    rtn = self.TestSource.AlertBlock
                except Exception as inst:
                    self.fail('AlertBlock (dynamic property) raised {} unexpectedly!'.format(type(inst)))
                self.assertIn(alert, rtn)
                    
    
    def test_Source_DynProp_Alerts(self):
        alertList = ['Alert Text 1', 'Alert Text 2', 'Alert Text 3', None]
        for alert in alertList:
            with self.subTest(alert=alert):
                try:
                    if alert is not None:
                        self.TestSource.AppendAlert(alert)
                    else:
                        self.TestSource.OverrideAlert('Override Alert Text')
                    test = alertList.index(alert) + 1
                    rtn = self.TestSource.Alerts
                except Exception as inst:
                    self.fail('Alerts (dynamic property) raised {} unexpectedly!'.format(type(inst)))
                self.assertEqual(rtn, test)
    
    def test_Source_DynProp_AlertFlag(self):
        self.assertFalse(self.TestSource.AlertFlag)
        
        self.TestSource.AppendAlert('Test Alert')
        self.assertTrue(self.TestSource.AlertFlag)
        
        self.TestSource.ResetAlert()
        self.assertFalse(self.TestSource.AlertFlag)
        
        self.TestSource.OverrideAlert("Test Override Alert")
        self.assertTrue(self.TestSource.AlertFlag)
        
        self.TestSource.ClearOverride()
        self.assertFalse(self.TestSource.AlertFlag)
    
    def test_Source_PRIV_Properties(self):
        # __AlertText
        with self.subTest(param='__AlertText'):
            self.assertIsInstance(self.TestSource._Source__AlertText, dict)
        
        # __AlertIndex
        with self.subTest(param='__AlertIndex'):
            self.assertIsInstance(self.TestSource._Source__AlertIndex, int)
        
        # __OverrideAlert
        with self.subTest(param='__OverrideAlert'):
            self.assertIsInstance(self.TestSource._Source__OverrideAlert, (str, type(None)))
        
        # __OverrideState
        with self.subTest(param='__OverrideState'):
            self.assertIsInstance(self.TestSource._Source__OverrideState, bool)
        
        # __DefaultAlert
        with self.subTest(param='__DefaultAlert'):
            self.assertIsInstance(self.TestSource._Source__DefaultAlert, str)
        
        # __AlertTimer
        with self.subTest(param='__AlertTimer'):
            self.assertIsInstance(self.TestSource._Source__AlertTimer, Timer)
    
    def test_Source_PRIV_AlertTimerHandler(self):
        class testTimer:
            def __init__(self):
                self.Running = True
            def Stop(self):
                self.Running = False
            
        timer = testTimer()
        
        alertList = \
            [
                ('Alert Text 1', 5),
                ('Alert Text 2', 15),
                ('Alert Text 3', 25),
                ('Alert Text 4', 0)
            ]
        for alert in alertList:
            self.TestSource.AppendAlert(alert[0], alert[1])
            
        for i in range(1,31):
            with self.subTest(count=i):
                try:
                    self.TestSource._Source__AlertTimerHandler(timer, i)
                except Exception as inst:
                    self.fail('__AlertTimerHandler (dynamic property) raised {} unexpectedly!'.format(type(inst)))
                
                if i <= 5:
                    self.assertEqual(self.TestSource.Alerts, 4)
                elif i > 5 and i <= 15:
                    self.assertEqual(self.TestSource.Alerts, 3)
                elif i > 15 and i <= 25:
                    self.assertEqual(self.TestSource.Alerts, 2)
                elif i > 25:
                    self.assertEqual(self.TestSource.Alerts, 1)
        
        with self.subTest(count='clear'):
            self.TestSource.ResetAlert()
            self.TestSource._Source__AlertTimerHandler(timer, 31)
            self.assertFalse(timer.Running)
    
    def test_Source_CycleAlert(self):
        alertList = \
            [
                ('Alert Text 1', 5),
                ('Alert Text 2', 15),
                ('Alert Text 3', 25),
                ('Alert Text 4', 0)
            ]
        for alert in alertList:
            self.TestSource.AppendAlert(alert[0], alert[1])
        
        for i in range(6):
            with self.subTest(iter=i):
                try:
                    self.TestSource.CycleAlert()
                except Exception as inst:
                    self.fail('CycleAlert raised {} unexpectedly!'.format(type(inst)))

                test = (i+1)%self.TestSource.Alerts
                self.assertEqual(self.TestSource._Source__AlertIndex, test)
        
    
    def test_Source_AppendAlert(self):
        alertList = \
            [
                ("Alert Message 1", -1),
                ("Alert Message 2", 0),
                ("alert message 3", 1)
            ]
        i=1
        for alert in alertList:
            with self.subTest(alert=alert[0]):
                try:
                    self.TestSource.AppendAlert(alert[0], alert[1])
                except Exception as inst:
                    self.fail('AppendAlert raised {} unexpectedly!'.format(type(inst)))
                    
                self.assertIn(alert[0], list(self.TestSource._Source__AlertText.keys()))
                self.assertEqual(self.TestSource.Alerts, i)
                i += 1
    
    def test_Source_OverrideAlert(self):
        self.assertFalse(self.TestSource._Source__OverrideState)
        
        try:
            self.TestSource.OverrideAlert('Override Alert')
        except Exception as inst:
            self.fail('OverrideAlert raised {} unexpectedly!'.format(type(inst)))
            
        self.assertIsInstance(self.TestSource._Source__OverrideAlert, str)
        self.assertEqual(self.TestSource._Source__OverrideAlert, 'Override Alert')
        self.assertTrue(self.TestSource._Source__OverrideState)
    
    def test_Source_ClearOverride(self):
        self.TestSource.OverrideAlert('Override Alert')
        self.assertEqual(self.TestSource._Source__OverrideAlert, 'Override Alert')
        self.assertTrue(self.TestSource._Source__OverrideState)
        
        try:
            self.TestSource.ClearOverride()
        except Exception as inst:
            self.fail('ClearOverride raised {} unexpectedly!'.format(type(inst)))
            
        self.assertIsNone(self.TestSource._Source__OverrideAlert)
        self.assertFalse(self.TestSource._Source__OverrideState)
    
    def test_Source_ClearAlert(self):
        alertList = [None, 'Alert Message']
        
        for alert in alertList:
            self.TestSource.AppendAlert(alert)
            
        for alert in alertList:
            len1 = self.TestSource.Alerts
            try:
                self.TestSource.ClearAlert(alert)
            except Exception as inst:
                self.fail('ClearAlert raised {} unexpectedly!'.format(type(inst)))
            len2 = self.TestSource.Alerts
            self.assertNotEqual(len1, len2)
    
    def test_Source_ResetAlert(self):
        alertList = \
            [
                ('Alert Text 1', 5),
                ('Alert Text 2', 15),
                ('Alert Text 3', 25),
                ('Alert Text 4', 0)
            ]
        for alert in alertList:
            self.TestSource.AppendAlert(alert[0], alert[1])
            
        try:
            self.TestSource.ResetAlert()
        except Exception as inst:
            self.fail('ResetAlert raised {} unexpectedly!'.format(type(inst)))
            
        self.assertEqual(self.TestSource.Alerts, 0)

class Destination_TestClass(unittest.TestCase):
    def setUp(self) -> None:
        self.TestCtls = ['CTL001']
        self.TestTPs = ['TP001']
        self.TestGUIController = GUIController(settings, self.TestCtls, self.TestTPs)
        self.TestGUIController.Initialize()
        self.TestUIController = self.TestGUIController.TP_Main
        self.TestSourceController = self.TestUIController.SrcCtl
        self.TestDestination = Destination(self.TestSourceController, 'TEST001', 'Test Destination', 4, 'proj', RelayTuple(1, 2), 'WPD001', LayoutTuple(0,0))
        return super().setUp()

    def test_Destination_Type(self):
        self.assertIsInstance(self.TestDestination, Destination)
        
    def test_Destination_Properties(self):
        # SourceController
        with self.subTest(param='SourceController'):
            self.assertIsInstance(self.TestDestination.SourceController, SourceController)
        
        # Id
        with self.subTest(param='Id'):
            self.assertIsInstance(self.TestDestination.Id, str)
        
        # Name
        with self.subTest(param='Name'):
            self.assertIsInstance(self.TestDestination.Name, str)
        
        # Output
        with self.subTest(param='Output'):
            self.assertIsInstance(self.TestDestination.Output, int)
        
        # AdvLayoutPosition
        with self.subTest(param='AdvLayoutPosition'):
            self.assertIsInstance(self.TestDestination.AdvLayoutPosition, LayoutTuple)
        
        # GroupWorkSource
        with self.subTest(param='GroupWorkSource'):
            self.assertIsInstance(self.TestDestination.GroupWorkSource, Source)
        
        # Type
        with self.subTest(param='Type'):
            self.assertIsInstance(self.TestDestination.Type, str)
        
        # AssignedSource
        with self.subTest(param='AssignedSource'):
            self.assertIsInstance(self.TestDestination.AssignedSource, MatrixTuple)
            self.assertIsInstance(self.TestDestination.AssignedSource.Vid, Source)
            self.assertIsInstance(self.TestDestination.AssignedSource.Aud, Source)
            
        
        # AssignedInput
        with self.subTest(param='AssignedInput'):
            self.assertIsInstance(self.TestDestination.AssignedInput, MatrixTuple)
            self.assertIsInstance(self.TestDestination.AssignedInput.Vid, int)
            self.assertIsInstance(self.TestDestination.AssignedInput.Aud, int)
        
        # Mute
        with self.subTest(param='Mute'):
            self.assertIsInstance(self.TestDestination.Mute, bool)
    
    def test_Destination_PRIV_Properties(self):
        # __Mute
        with self.subTest(param='__Mute'):
            self.assertIsInstance(self.TestDestination._Destination__Mute, bool)
        
        # __Relay
        with self.subTest(param='__Relay'):
            self.assertIsInstance(self.TestDestination._Destination__Relay, RelayTuple)
        
        # __AssignedVidSource
        with self.subTest(param='__AssignedVidSource'):
            self.assertIsInstance(self.TestDestination._Destination__AssignedVidSource, Source)
        
        # __AssignedAudSource
        with self.subTest(param='__AssignedAudSource'):
            self.assertIsInstance(self.TestDestination._Destination__AssignedAudSource, Source)
        
        # __AdvSelectBtn
        with self.subTest(param='__AdvSelectBtn'):
            self.assertIsInstance(self.TestDestination._Destination__AdvSelectBtn, (Button, type(None)))
        
        # __AdvCtlBtn
        with self.subTest(param='__AdvCtlBtn'):
            self.assertIsInstance(self.TestDestination._Destination__AdvCtlBtn, (Button, type(None)))
        
        # __AdvAudBtn
        with self.subTest(param='__AdvAudBtn'):
            self.assertIsInstance(self.TestDestination._Destination__AdvAudBtn, (Button, type(None)))
        
        # __AdvAlertBtn
        with self.subTest(param='__AdvAlertBtn'):
            self.assertIsInstance(self.TestDestination._Destination__AdvAlertBtn, (Button, type(None)))
        
        # __AdvScnBtn
        with self.subTest(param='__AdvScnBtn'):
            self.assertIsInstance(self.TestDestination._Destination__AdvScnBtn, (Button, type(None)))
        
        # __AdvLabel
        with self.subTest(param='__AdvLabel'):
            self.assertIsInstance(self.TestDestination._Destination__AdvLabel, (Label, type(None)))
        
        # __MatrixRow
        with self.subTest(param='__MatrixRow'):
            self.assertIsInstance(self.TestDestination._Destination__MatrixRow, (MatrixRow, type(None)))
        
        # __AssignedVidInput
        with self.subTest(param='__AssignedVidInput'):
            self.assertIsInstance(self.TestDestination._Destination__AssignedVidInput, int)
        
        # __AssignedAudInput
        with self.subTest(param='__AssignedAudInput'):
            self.assertIsInstance(self.TestDestination._Destination__AssignedAudInput, int)
    
    def test_Destination_EventHandler_SelectHandler(self):
        self.TestDestination.AssignAdvUI(self.TestSourceController._SourceController__GetUIForAdvDest(self.TestDestination))
        
        btnList = [self.TestDestination._Destination__AdvSelectBtn]
        actList = ['Pressed']
        
        contextList = self.TestSourceController.Sources
        
        for btn in btnList:
            for act in actList:
                for con in contextList:
                    with self.subTest(button=btn.Name, action=act, context=con.Name):
                        try:
                            self.TestSourceController.SelectSource(con)
                            self.TestDestination._Destination__SelectHandler(btn, act)
                        except Exception as inst:
                            self.fail('__SelectHandler raised {} unexpectedly!'.format(type(inst)))
    
    def test_Destination_EventHandler_SourceControlHandler(self):
        # this needs a fully instanciated destination
        self.TestDestination = self.TestSourceController.Destinations[0]
        self.TestDestination = cast(Destination, self.TestDestination)
        
        btnList = [self.TestDestination._Destination__AdvCtlBtn]
        srcList = self.TestSourceController.Sources
        actList = ['Pressed']
        
        for btn in btnList:
            for act in actList:
                for src in srcList:
                    with self.subTest(button=btn.Name, action=act, source=src.Name):
                        try:
                            self.TestDestination.AssignSource(src)
                            self.TestDestination._Destination__SourceControlHandler(btn, act)
                        except Exception as inst:
                            self.fail('__SourceControlHandler raised {} unexpectedly!'.format(type(inst)))
    
    def test_Destination_EventHandler_AudioHandler(self):
        self.TestDestination.AssignAdvUI(self.TestSourceController._SourceController__GetUIForAdvDest(self.TestDestination))
        
        btnList = [self.TestDestination._Destination__AdvAudBtn]
        actList = ['Tapped', 'Released']
        
        contextList = [0, 1, 2, 3]
        
        for btn in btnList:
            for act in actList:
                for con in contextList:
                    with self.subTest(button=btn.Name, action=act, context=con):
                        try:
                            btn.SetState(con)
                            self.TestDestination._Destination__AudioHandler(btn, act)
                        except Exception as inst:
                            self.fail('__AudioHandler raised {} unexpectedly!'.format(type(inst)))
                        # TODO: test changes after handler processes
    
    def test_Destination_EventHandler_AlertHandler(self):
        self.TestDestination.AssignAdvUI(self.TestSourceController._SourceController__GetUIForAdvDest(self.TestDestination))
        
        btnList = [self.TestDestination._Destination__AdvAlertBtn]
        actList = ['Pressed']
        
        for btn in btnList:
            for act in actList:
                with self.subTest(button=btn.Name, action=act):
                    try:
                        self.TestDestination._Destination__AlertHandler(btn, act)
                    except Exception as inst:
                        self.fail('__AlertHandler raised {} unexpectedly!'.format(type(inst)))
    
    def test_Destination_EventHandler_ScreenHandler(self):
        self.TestDestination.AssignAdvUI(self.TestSourceController._SourceController__GetUIForAdvDest(self.TestDestination))
        
        btnList = [self.TestDestination._Destination__AdvScnBtn]
        actList = ['Pressed']
        
        for btn in btnList:
            for act in actList:
                with self.subTest(button=btn.Name, action=act):
                    try:
                        self.TestDestination._Destination__ScreenHandler(btn, act)
                    except Exception as inst:
                        self.fail('__ScreenHandler raised {} unexpectedly!'.format(type(inst)))
    
    def test_Destination_ToggleMute(self):
        state1 = self.TestDestination._Destination__Mute
        
        try:
            self.TestDestination.ToggleMute()
        except Exception as inst:
            self.fail('ToggleMute raised {} unexpectedly!'.format(type(inst)))
        
        state2 = self.TestDestination._Destination__Mute
        self.assertNotEqual(state1, state2)
    
    def test_Destination_DynProp_Mute_On(self):
        cmdList = ['on', 'On', 'ON', 1, True, 'Mute', 'mute', 'MUTE']
        
        for cmd in cmdList:
            with self.subTest(i=cmd):
                try:
                    self.TestDestination.Mute = cmd
                except Exception as inst:
                    self.fail('Mute (On) raised {} unexpectedly!'.format(type(inst)))
                self.assertTrue(self.TestDestination.Mute)
    
    def test_Destination_DynProp_Mute_Off(self):
        cmdList = ['off', 'Off', 'OFF', 0, False, 'Unmute', 'unmute', 'UNMUTE']
        
        for cmd in cmdList:
            with self.subTest(i=cmd):
                try:
                    self.TestDestination.Mute = cmd
                except Exception as inst:
                    self.fail('Mute (Off) raised {} unexpectedly!'.format(type(inst)))
                self.assertFalse(self.TestDestination.Mute)
    
    def test_Destination_AssignInput(self):
        # this needs a fully instanciated destination
        self.TestDestination = self.TestSourceController.Destinations[0]
        self.TestDestination = cast(Destination, self.TestDestination)
        
        srcList = self.TestSourceController.Sources
        
        for src in srcList:
            with self.subTest(source=src.Name):
                try:
                    self.TestDestination.AssignInput(src.Input)
                except Exception as inst:
                    self.fail('AssignInput raised {} unexpectedly!'.format(type(inst)))
                    
                self.assertEqual(MatrixTuple(src, src), self.TestDestination.AssignedSource)
    
    def test_Destination_AssignSource(self):
        # this needs a fully instanciated destination
        self.TestDestination = self.TestSourceController.Destinations[0]
        self.TestDestination = cast(Destination, self.TestDestination)
        
        srcList = self.TestSourceController.Sources
        
        for src in srcList:
            with self.subTest(source=src.Name):
                try:
                    self.TestDestination.AssignSource(src)
                except Exception as inst:
                    self.fail('AssignSource raised {} unexpectedly!'.format(type(inst)))
                    
                self.assertEqual(MatrixTuple(src, src), self.TestDestination.AssignedSource)
    
    def test_Destination_AssignMatrixByInput(self):
        # this needs a fully instanciated destination
        self.TestDestination = self.TestSourceController.Destinations[0]
        self.TestDestination = cast(Destination, self.TestDestination)
        
        srcList = self.TestSourceController.Sources
        tieList = ['Vid', 'Aud', 'AV', 'untie']
        defSrc = self.TestSourceController.BlankSource
        
        for src in srcList:
            for tie in tieList:
                with self.subTest(source=src.Name, tie=tie):
                    self.TestDestination.AssignSource(self.TestSourceController.BlankSource)
                    try:
                        self.TestDestination.AssignMatrixByInput(src.Input, tie)
                    except Exception as inst:
                        self.fail('AssignMatrixByInput raised {} unexpectedly!'.format(type(inst)))
                    
                    if tie == 'Vid':
                        self.assertEqual(MatrixTuple(src, defSrc), self.TestDestination.AssignedSource)
                    if tie == 'Aud':
                        self.assertEqual(MatrixTuple(defSrc, src), self.TestDestination.AssignedSource)
                    if tie == 'AV':
                        self.assertEqual(MatrixTuple(src, src), self.TestDestination.AssignedSource)
                    if tie == 'untie':
                        self.assertEqual(MatrixTuple(defSrc, defSrc), self.TestDestination.AssignedSource)
    
    def test_Destination_AssignMatrixBySource(self):
        # this needs a fully instanciated destination
        self.TestDestination = self.TestSourceController.Destinations[0]
        self.TestDestination = cast(Destination, self.TestDestination)
        
        srcList = self.TestSourceController.Sources
        tieList = ['Vid', 'Aud', 'AV', 'untie']
        defSrc = self.TestSourceController.BlankSource
        
        for src in srcList:
            for tie in tieList:
                with self.subTest(source=src.Name, tie=tie):
                    self.TestDestination.AssignSource(self.TestSourceController.BlankSource)
                    try:
                        self.TestDestination.AssignMatrixBySource(src, tie)
                    except Exception as inst:
                        self.fail('AssignMatrixBySource raised {} unexpectedly!'.format(type(inst)))
                    
                    if tie == 'Vid':
                        self.assertEqual(MatrixTuple(src, defSrc), self.TestDestination.AssignedSource)
                    if tie == 'Aud':
                        self.assertEqual(MatrixTuple(defSrc, src), self.TestDestination.AssignedSource)
                    if tie == 'AV':
                        self.assertEqual(MatrixTuple(src, src), self.TestDestination.AssignedSource)
                    if tie == 'untie':
                        self.assertEqual(MatrixTuple(defSrc, defSrc), self.TestDestination.AssignedSource)
    
    def test_Destination_AssignInput_BadInput(self):
        # this needs a fully instanciated destination
        self.TestDestination = self.TestSourceController.Destinations[0]
        self.TestDestination = cast(Destination, self.TestDestination)
        
        inputList = ['str', ['list'], {'dict': 1}, 1.0, True]
        
        for input in inputList:
            with self.subTest(input=input):
                with self.assertRaises(ValueError):
                    self.TestDestination.AssignInput(input)
                    
    def test_Destination_AssignSource_BadSource(self):
        # this needs a fully instanciated destination
        self.TestDestination = self.TestSourceController.Destinations[0]
        self.TestDestination = cast(Destination, self.TestDestination)
        
        inputList = [2, 'str', ['list'], {'dict': 1}, 1.0, True]
        
        for input in inputList:
            with self.subTest(input=input):
                with self.assertRaises(ValueError):
                    self.TestDestination.AssignSource(input)
                    
    def test_Destination_AssignMatrix_BadTie(self):
        # this needs a fully instanciated destination
        self.TestDestination = self.TestSourceController.Destinations[0]
        self.TestDestination = cast(Destination, self.TestDestination)
        
        inputList = ['str', ['list'], {'dict': 1}, 1.0, True]
        
        for input in inputList:
            with self.subTest(input=input):
                with self.assertRaises(ValueError):
                    self.TestDestination.AssignMatrixBySource(self.TestSourceController.Sources[0], input)
    
    def test_Destination_AssignAdvUI(self):
        try:
            self.TestDestination.AssignAdvUI(self.TestSourceController._SourceController__GetUIForAdvDest(self.TestDestination))
        except Exception as inst:
            self.fail('AssignAdvUI raised {} unexpectedly!'.format(type(inst)))
    
    def test_Destination_UpdateAdvUI(self):
        self.TestDestination.AssignAdvUI(self.TestSourceController._SourceController__GetUIForAdvDest(self.TestDestination))
        try:
            self.TestDestination.UpdateAdvUI()
        except Exception as inst:
            self.fail('UpdateAdvUI raised {} unexpectedly!'.format(type(inst)))
            
    def test_Destination_AdvSourceAlertHandler(self):
        # this needs a fully instanciated destination
        self.TestDestination = self.TestSourceController.Destinations[0]
        self.TestDestination = cast(Destination, self.TestDestination)
        
        srcList = self.TestSourceController.Sources
        
        for src in srcList:
            with self.subTest(source=src):
                try:
                    self.TestDestination.AssignSource(src)
                    
                    self.TestDestination.AssignedSource.Vid.AppendAlert('Alert Message')
                    
                    self.TestDestination.AdvSourceAlertHandler()
                    self.assertTrue(self.TestDestination._Destination__AdvAlertBtn.Visible)
                    self.assertTrue(self.TestDestination._Destination__AdvAlertBtn.Enabled)
                    self.assertEqual(self.TestDestination._Destination__AdvAlertBtn.BlinkState, 'Blinking')
                    
                    self.TestDestination.AssignedSource.Vid.ResetAlert()
                    
                    self.TestDestination.AdvSourceAlertHandler()
                    self.assertFalse(self.TestDestination._Destination__AdvAlertBtn.Visible)
                    self.assertFalse(self.TestDestination._Destination__AdvAlertBtn.Enabled)
                    self.assertEqual(self.TestDestination._Destination__AdvAlertBtn.BlinkState, 'Not blinking')
                
                except Exception as inst:
                    self.fail('AdvSourceAlertHandler raised {} unexpectedly!'.format(type(inst)))
    
class MatrixController_TestClass(unittest.TestCase):
    def setUp(self) -> None:
        self.TestCtls = ['CTL001']
        self.TestTPs = ['TP001']
        self.TestGUIController = GUIController(settings, self.TestCtls, self.TestTPs)
        self.TestGUIController.Initialize()
        self.TestUIController = self.TestGUIController.TP_Main
        self.TestSourceController = self.TestUIController.SrcCtl
        self.TestMatrix = self.TestSourceController._SourceController__Matrix
        self.TestMatrix = cast(MatrixController, self.TestMatrix)
        return super().setUp()
    
    def test_MatrixController_Type(self):
        self.assertIsInstance(self.TestMatrix, MatrixController)
        
    def test_MatrixController_Properties(self):
        # SourceController
        with self.subTest(param='SourceController'):
            self.assertIsInstance(self.TestMatrix.SourceController, SourceController)
        
        # Mode
        with self.subTest(param='Mode'):
            self.assertIsInstance(self.TestMatrix.Mode, str)
        
        # Hardware
        with self.subTest(param='Hardware'):
            self.assertIsInstance(self.TestMatrix.Hardware, SystemHardwareController)
            
        # StateDict
        with self.subTest(param='StateDict'):
            self.assertIsInstance(self.TestMatrix.StateDict, dict)
            for key, value in self.TestMatrix.StateDict.items():
                with self.subTest(key=key, value=value):
                    self.assertIsInstance(key, str)
                    self.assertIsInstance(value, int)
    
    def test_MatrixController_PRIV_Properties(self):
        # __Rows
        with self.subTest(param='__Rows'):
            self.assertIsInstance(self.TestMatrix._MatrixController__Rows, dict)
            print(self.TestMatrix._MatrixController__Rows)
            for key, value in self.TestMatrix._MatrixController__Rows.items():
                with self.subTest(key=key, value=value):
                    self.assertIsInstance(key, int)
                    self.assertIsInstance(value, MatrixRow)
        
        # __CtlsSet
        with self.subTest(param='__CtlsSet'):
            self.assertIsInstance(self.TestMatrix._MatrixController__CtlsSet, MESet)
        
        # __DelBtn
        with self.subTest(param='__DelBtn'):
            self.assertIsInstance(self.TestMatrix._MatrixController__DelBtn, Button)
        
        # __InputLbls
        with self.subTest(param='__InputLbls'):
            self.assertIsInstance(self.TestMatrix._MatrixController__InputLbls, list)
            for value in self.TestMatrix._MatrixController__InputLbls:
                with self.subTest(value=value.Name):
                    self.assertIsInstance(value, Label)
        
        # __OutputLbls
        with self.subTest(param='__OutputLbls'):
            self.assertIsInstance(self.TestMatrix._MatrixController__OutputLbls, list)
            for value in self.TestMatrix._MatrixController__OutputLbls:
                with self.subTest(value=value.Name):
                    self.assertIsInstance(value, Label)
        
    def test_MatrixController_EventHandler_ModeHandler(self):
        btnList = self.TestMatrix._MatrixController__CtlsSet.Objects
        actList = ['Pressed']
        
        for btn in btnList:
            for act in actList:
                with self.subTest(button=btn.Name, action=act):
                    try:
                        self.TestMatrix._MatrixController__ModeHandler(btn, act)
                    except Exception as inst:
                        self.fail('__ModeHander raised {} unexpectedly!'.format(type(inst)))
                    self.assertIn(self.TestMatrix.Mode.upper(), btn.Name.upper())
    
    def test_MatrixController_EventHandler_DeleteAllTiesHandler(self):
        btn = self.TestMatrix._MatrixController__DelBtn
        actList = ['Pressed', 'Released']
        
        for act in actList:
            with self.subTest(button=btn.Name, action=act):
                try:
                    self.TestMatrix._MatrixController__DeleteAllTiesHandler(btn, act)
                except Exception as inst:
                    self.fail('__DeleteAllTiesHandler raise {} unexpectedly!'.format(type(inst)))

class MatrixRow_TestClass(unittest.TestCase):
    def setUp(self) -> None:
        self.TestCtls = ['CTL001']
        self.TestTPs = ['TP001']
        self.TestGUIController = GUIController(settings, self.TestCtls, self.TestTPs)
        self.TestGUIController.Initialize()
        self.TestUIController = self.TestGUIController.TP_Main
        self.TestSourceController = self.TestUIController.SrcCtl
        self.TestMatrix = self.TestSourceController._SourceController__Matrix
        self.TestMatrixRow = self.TestMatrix._MatrixController__Rows[1]
        self.TestMatrixRow = cast(MatrixRow, self.TestMatrixRow)
        return super().setUp()
    
    def test_MatrixRow_Type(self):
        self.assertIsInstance(self.TestMatrixRow, MatrixRow)
    
    def test_MatrixRow_Properties(self):
        # Matrix
        with self.subTest(param='Matrix'):
            self.assertIsInstance(self.TestMatrixRow.Matrix, MatrixController)
        
        # MatrixOutput
        with self.subTest(param='MatrixOutput'):
            self.assertIsInstance(self.TestMatrixRow.MatrixOutput, int)
        
        # VidSelect
        with self.subTest(param='VidSelect'):
            self.assertIsInstance(self.TestMatrixRow.VidSelect, int)
        
        # AudSelect
        with self.subTest(param='AudSelect'):
            self.assertIsInstance(self.TestMatrixRow.AudSelect, int)
        
        # Objects
        with self.subTest(param='Objects'):
            self.assertIsInstance(self.TestMatrixRow.Objects, list)
            for value in self.TestMatrixRow.Objects:
                with self.subTest(value=value.Name):
                    self.assertIsInstance(value, Button)
    
    def test_MatrixRow_EventHandler_MatrixSelectHandler(self):
        btnList = self.TestMatrixRow.Objects
        actList = ['Pressed']
        modeList = ['AV', 'Vid', 'Aud', 'untie']
        
        for btn in btnList:
            for act in actList:
                for mode in modeList:
                    with self.subTest(button=btn, action=act, mode=mode):
                        self.TestMatrix.Mode = mode
                        try:
                            self.TestMatrixRow._MatrixRow__MatrixSelectHandler(btn, act)
                        except Exception as inst:
                            self.fail('__MatrixSelectHandler raised {} unexpectedly!'.format(type(inst)))
    
    def test_MatrixRow_PRIV_UpdateRowBtns(self):
        btnList = self.TestMatrixRow.Objects
        modeList = ['AV', 'Vid', 'Aud']
        stateList = [0, 1, 2, 3]
        
        for btn in btnList:
            for mode in modeList:
                for state in stateList:
                    with self.subTest(modButton=btn, mode=mode, initalState=state):
                        try:
                            btn.SetState(state)
                            self.TestMatrixRow._MatrixRow__UpdateRowBtns(btn, mode)
                        except Exception as inst:
                            self.fail('__UpdateRowBtns raised {} unexpectedly!'.format(type(inst)))
    
    def test_MatrixRow_MakeTie_Sources(self):
        modeList = ['AV', 'Vid', 'Aud', 'untie']
        srcList = self.TestSourceController.Sources
        srcList.append(self.TestSourceController.BlankSource)
        
        for src in srcList:
            for mode in modeList:
                with self.subTest(source=src.Name, mode=mode):
                    try:
                        self.TestMatrixRow.MakeTie(src.Input, mode)
                    except Exception as inst:
                        self.fail('MakeTie raised {} unexpectedly!'.format(type(inst)))
    
    def test_MatrixRow_MakeTie_Btns(self):
        modeList = ['AV', 'Vid', 'Aud', 'untie']
        srcList = self.TestMatrixRow.Objects
        
        for src in srcList:
            for mode in modeList:
                with self.subTest(source=src.Name, mode=mode):
                    try:
                        self.TestMatrixRow.MakeTie(src, mode)
                    except Exception as inst:
                        self.fail('MakeTie raised {} unexpectedly!'.format(type(inst)))
    
    def test_MatrixRow_MakeTie_BadTie(self):
        modeList = [1, True, 2.5, ['test'], {'test': 2}, 'other string']
        
        for mode in modeList:
            with self.subTest(mode=mode):
                with self.assertRaises(ValueError):
                    self.TestMatrixRow.MakeTie(1, mode)
    
    def test_MatrixRow_MakeTie_BadInput(self):
        modeList = ['AV', 'Vid', 'Aud', 'untie']
        srcList = ['one', 2.5, True, ['list'], {'dict': 2}]
        
        for mode in modeList:
            for src in srcList:
                with self.subTest(mode=mode, input=type(src)):
                    with self.assertRaises(TypeError):
                        self.TestMatrixRow.MakeTie(src, mode)


if __name__ == '__main__':
    unittest.main()