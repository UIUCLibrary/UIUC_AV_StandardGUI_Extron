import unittest

## test imports ----------------------------------------------------------------
from uofi_gui import GUIController
from uofi_gui.uiObjects import ExUIDevice
from uofi_gui.systemHardware import SystemHardwareController, VirtualDeviceInterface, SystemPollingController, SystemStatusController
import settings
from ConnectionHandler import ConnectionHandler

from extronlib.device import UIDevice
from extronlib.ui import Button, Label
from extronlib.system import Timer
from extronlib.interface import SerialInterface, EthernetClientInterface, ContactInterface, DanteInterface, DigitalInputInterface, DigitalIOInterface, FlexIOInterface, IRInterface, PoEInterface, RelayInterface

from datetime import datetime
from types import ModuleType
## -----------------------------------------------------------------------------

class VirtualDeviceInterface_TestClass(unittest.TestCase):
    def setUp(self) -> None:
        self.TestCtls = ['CTL001']
        self.TestTPs = ['TP001']
        self.TestGUIController = GUIController(settings, self.TestCtls, self.TestTPs)
        self.TestGUIController.Initialize()
        
        self.VirtDevDict = \
            {
                'Id': 'VMX001',
                'Name': 'SVSi Matrix',
                'Manufacturer': 'AMX',
                'Model': 'N2300 Virtual Matrix',
                'Interface': 
                    {
                        'module': 'hardware.avoip_virtual_matrix',
                        'interface_class': 'VirtualDeviceClass',
                        'interface_configuration': {
                            'VirtualDeviceID': 'VMX001',
                            'AssignmentAttribute': 'MatrixAssignment',
                            'Model': 'AMX SVSi N2300'
                        }
                    },
                'Subscriptions': 
                    [
                        {
                        'command': 'OutputTieStatus',
                        'qualifier': [
                            {'Output': 1, 'Tie Type': 'Video'},
                            {'Output': 1, 'Tie Type': 'Audio'},
                            {'Output': 2, 'Tie Type': 'Video'},
                            {'Output': 2, 'Tie Type': 'Audio'},
                            {'Output': 3, 'Tie Type': 'Video'},
                            {'Output': 3, 'Tie Type': 'Audio'},
                            {'Output': 4, 'Tie Type': 'Video'},
                            {'Output': 4, 'Tie Type': 'Audio'},
                        ],
                        'callback': 'FeedbackOutputTieStatusHandler',
                        },
                        {
                        'command': 'InputSignalStatus',
                        'qualifier': [
                            {'Input': 1},
                            {'Input': 2},
                            {'Input': 3},
                            {'Input': 4},
                            {'Input': 5},
                            {'Input': 6},
                        ],
                        'callback': 'FeedbackInputSignalStatusHandler'
                        }
                    ],
                'Polling': 
                    [
                        {
                        'command': 'InputSignalStatus',
                        'active_int': 10,
                        'inactive_int': 600
                        },
                        {
                        'command': 'OutputTieStatus'
                        }
                    ],
                'Options':
                    {
                        'InputSignalStatusCommand': 
                        {
                            'command': 'InputSignalStatus'
                        }
                    }
            }

        return super().setUp()
    
    def test_VirtualDeviceInterface_Init(self):
        try:
            self.TestHardware = SystemHardwareController(self.TestGUIController, **self.VirtDevDict)
        except Exception as inst:
            self.fail('Creating a Virtual Interface Device raised {} unexpectedly!'.format(type(inst)))
    
    def test_VirtualDeviceInterface_FindAssociatedHardware(self):
        self.TestHardware = SystemHardwareController(self.TestGUIController, **self.VirtDevDict)
        self.TestHardware.interface.FindAssociatedHardware()
        for key, assignment in self.TestHardware.interface._VirtualDeviceInterface__AssignmentDict.items():
            with self.subTest(assignment=key):
                self.assertGreater(len(assignment), 0)

class SystemHardwareController_TestClass(unittest.TestCase): 
    def setUp(self) -> None:
        self.TestCtls = ['CTL001']
        self.TestTPs = ['TP001']
        self.TestGUIController = GUIController(settings, self.TestCtls, self.TestTPs)
        self.TestGUIController.Initialize()
        self.TestUIController = self.TestGUIController.TP_Main
        return super().setUp()
    
    # TODO: test creating system hardware devices
    def test_SystemHardwareController_Init(self):
        self.HardwareDict = \
            {
                'Id': 'MON001',
                'Name': 'North Monitor',
                'Manufacturer': 'SharpNEC',
                'Model': 'V625',
                'Interface': 
                    {
                        'module': 'hardware.nec_display_P_V_X_Series_v1_4_1_0',
                        'interface_class': 'EthernetClass',
                        'ConnectionHandler': {
                        'keepAliveQuery': 'AmbientCurrentIlluminance',
                        'DisconnectLimit': 5,
                        'pollFrequency': 60
                        },
                        'interface_configuration': {
                            'Hostname': 'libavstest09.library.illinois.edu',
                            'IPPort': 7142,
                            'Model': 'V625'
                        }
                    },
                'Subscriptions': [],
                'Polling': 
                    [
                        {
                        'command': 'Power',
                        'callback': 'PowerStatusHandler',
                        'active_int': 10,
                        'inactive_int': 30
                        },
                        {
                        'command': 'AudioMute',
                        'callback': 'AudioMuteStatusHandler',
                        'active_int': 10,
                        'inactive_int': 600
                        },
                        {
                        'command': 'Volume',
                        'callback': 'VolumeStatusHandler',
                        'active_int': None,
                        'inactive_int': None
                        }
                    ],
                'Options': 
                    {
                        'PowerCommand': 
                        {
                            'command': 'Power',
                        },
                        'SourceCommand':
                        {
                            'command': 'Input',
                            'value': 'HDMI'
                        },
                        'MuteCommand':
                        {
                            'command': 'AudioMute',
                        },
                        'VolumeCommand':
                        {
                            'command': 'Volume'
                        },
                        'VolumeRange': (0, 100)
                    }
            }
        
        try:
            self.TestHardware = SystemHardwareController(self.TestGUIController, **self.HardwareDict)
        except Exception as inst:
            self.fail('Initializing of test hardware rasied {} unexpectedly!'.format(type(inst)))
        
    def test_SystemHardwareController_Type(self):
        self.test_SystemHardwareController_Init()
        
        self.assertIsInstance(self.TestHardware, SystemHardwareController)
        
    def test_SystemHardwareController_Properties(self):
        self.test_SystemHardwareController_Init()
        
        # GUIHost
        with self.subTest(param='GUIHost'):
            self.assertIsInstance(self.TestHardware.GUIHost, GUIController)
        
        # Id
        with self.subTest(param='Id'):
            self.assertIsInstance(self.TestHardware.Id, str)
        
        # Name
        with self.subTest(param='Name'):
            self.assertIsInstance(self.TestHardware.Name, str)
        
        # Manufacturer
        with self.subTest(param='Manufacturer'):
            self.assertIsInstance(self.TestHardware.Manufacturer, str)
        
        # Model
        with self.subTest(param='Model'):
            self.assertIsInstance(self.TestHardware.Model, str)
        
        # ConnectionStatus
        with self.subTest(param='ConnectionStatus'):
            self.assertIsInstance(self.TestHardware.ConnectionStatus, str)
        
        # LastStatusChange
        with self.subTest(param='LastStatusChange'):
            self.assertIsInstance(self.TestHardware.LastStatusChange, (datetime, type(None)))
        
        # interface
        with self.subTest(param='interface'):
            self.assertIsInstance(self.TestHardware.interface, (ConnectionHandler, SerialInterface, EthernetClientInterface, ContactInterface, DanteInterface, DigitalInputInterface, DigitalIOInterface, FlexIOInterface, IRInterface, PoEInterface, RelayInterface))
        
        # Options
        for option in self.HardwareDict['Options'].keys():
            with self.subTest(param='Options', option=option):
                self.assertTrue(hasattr(self.TestHardware, option))
    
    def test_SystemHardwareController_PRIV_Properties(self):
        self.test_SystemHardwareController_Init()
        
        # __Module
        with self.subTest(param='__Module'):
            self.assertIsInstance(self.TestHardware._SystemHardwareController__Module, ModuleType)
        
        # __Constructor
        with self.subTest(param='__Constructor'):
            self.assertTrue(callable(self.TestHardware._SystemHardwareController__Constructor))
    
    def test_SystemHardwareController_PRIV_ConnectionStatus(self):
        self.test_SystemHardwareController_Init()
        
        try:
            self.TestHardware._SystemHardwareController__ConnectionStatus('Power', 'On', None)
        except Exception as inst:
            self.fail('__ConnectionStatus raised {} unexpectedly!'.format(type(inst)))
    
    def test_SystemHardwareController_GetQualifierList(self):
        self.test_SystemHardwareController_Init()
        
        contextList = ['subscription', 'polling']
        expectedList = \
            [
                [
                    {'Input': 1},
                    {'Input': 2},
                    {'Input': 3},
                    {'Input': 4},
                    {'Input': 5},
                    {'Input': 6},
                ],
                [{'Pan Speed': 5, 'Tilt Speed': 5}],
                [None]
            ]
        
        for con in contextList:
            testList = \
            [
                {
                    'command': 'Power',
                    'callback': 'PowerStatusHandler',
                    'active_int': 10,
                    'inactive_int': 30,
                    'qualifier': [
                        {'Input': 1},
                        {'Input': 2},
                        {'Input': 3},
                        {'Input': 4},
                        {'Input': 5},
                        {'Input': 6},
                    ]
                },
                {
                    'command': 'AudioMute',
                    'callback': 'AudioMuteStatusHandler',
                    'active_int': 10,
                    'inactive_int': 600,
                    'qualifier': {'Pan Speed': 5, 'Tilt Speed': 5}
                },
                {
                    'command': 'Volume',
                    'callback': 'VolumeStatusHandler',
                    'active_int': 10,
                    'inactive_int': 600
                }
            ]
            for item in testList:
                with self.subTest(context=con, item=item['command']):
                    if con == 'subscription':
                        item.pop('active_int')
                        item.pop('inactive_int')
                    
                    try:
                        qualifier = self.TestHardware.GetQualifierList(item)
                    except Exception as inst:
                        self.fail('GetQualifierList raised {} unexpectedly!'.format(type(inst)))
                        
                    self.assertEqual(qualifier, expectedList[testList.index(item)])
    
    def test_SystemHardwareController_GetQualifierList_BadQualList(self):
        self.test_SystemHardwareController_Init()
        
        contextList = ['subscription', 'polling']
        
        for con in contextList:
            testList = \
            [
                {
                    'command': 'Power',
                    'callback': 'PowerStatusHandler',
                    'active_int': 10,
                    'inactive_int': 30,
                    'qualifier': [
                        'not a dict',
                        1,
                        2.5,
                        True,
                        ['more nonsesne']
                    ]
                },
                {
                    'command': 'AudioMute',
                    'callback': 'AudioMuteStatusHandler',
                    'active_int': 10,
                    'inactive_int': 600,
                    'qualifier': 'this is a string not a dict'
                }
            ]
            for item in testList:
                with self.subTest(context=con, item=item['command']):
                    if con == 'subscription':
                        item.pop('active_int')
                        item.pop('inactive_int')
                    
                    with self.assertRaises(TypeError):
                        self.TestHardware.GetQualifierList(item)
    
    def test_SystemHardwareController_AddSubscription(self):
        self.test_SystemHardwareController_Init()
        
        def TestCallable(*args, **kwargs):
            pass
        
        testList = \
            [
                {
                    'command': 'Power',
                    'callback': 'PowerStatusHandler',
                    'active_int': 10,
                    'inactive_int': 30,
                },
                {
                    'command': 'AudioMute',
                    'callback': 'AudioMuteStatusHandler',
                    'active_int': 10,
                    'inactive_int': 600,
                    'tag': 'tag here'
                },
                {
                    'command': 'Volume',
                    'callback': TestCallable,
                    'active_int': 10,
                    'inactive_int': 600
                },
                {
                    'command': 'AutoImage',
                    'callback': TestCallable,
                    'active_int': 10,
                    'inactive_int': 600,
                    'tag': 'tag here'
                }
            ]
            
        for item in testList:
            qualifier = self.TestHardware.GetQualifierList(item)
            for qual in qualifier:
                with self.subTest(item=item['command'], qualifier=qual):
                    try:
                        self.TestHardware.AddSubscription(item, qual)
                    except Exception as inst:
                        self.fail('AddSubscription raised {} unexpetedly!'.format(type(inst)))
                        
                    print(self.TestHardware.interface._Subscriptions)
    
    def test_SystemHardwareController_AddSubscription_BadCallback(self):
        self.test_SystemHardwareController_Init()
        
        testItem = {
                        'command': 'Power',
                        'callback': 'CallbackToNothing'
                    }

        with self.assertRaises(TypeError):
            self.TestHardware.AddSubscription(testItem, None)
    
class SystemPollingController_TestClass(unittest.TestCase):
    def setUp(self) -> None:
        self.TestCtls = ['CTL001']
        self.TestTPs = ['TP001']
        self.TestGUIController = GUIController(settings, self.TestCtls, self.TestTPs)
        self.TestGUIController.Initialize()
        self.TestUIController = self.TestGUIController.TP_Main
        self.TestPollController = self.TestGUIController.PollCtl
        return super().setUp()
    
    def test_SystemPollingController_Type(self):
        self.assertIsInstance(self.TestPollController, SystemPollingController)
    
    def test_SystemPollingController_Properties(self):
        # Polling
        with self.subTest(param='Polling'):
            self.assertIsInstance(self.TestPollController.Polling, list)
    
    def test_SystemPollingController_PRIV_Properties(self):
        # __PollingState
        with self.subTest(param='__PollingState'):
            self.assertIsInstance(self.TestPollController._SystemPollingController__PollingState, str)
        
        # __DefaultActiveDur
        with self.subTest(param='__DefaultActiveDur'):
            self.assertIsInstance(self.TestPollController._SystemPollingController__DefaultActiveDur, int)
        
        # __DefaultInactiveDur
        with self.subTest(param='__DefaultInactiveDur'):
            self.assertIsInstance(self.TestPollController._SystemPollingController__DefaultInactiveDur, int)
        
        # __InactivePolling
        with self.subTest(param='__InactivePolling'):
            self.assertIsInstance(self.TestPollController._SystemPollingController__InactivePolling, Timer)
        
        # __ActivePolling
        with self.subTest(param='__ActivePolling'):
            self.assertIsInstance(self.TestPollController._SystemPollingController__ActivePolling, Timer)
    
    def test_SystemPollingController_EventHandler_ActivePollingHandler(self):
        for i in range(121):
            with self.subTest(iter=i):
                try:
                    self.TestPollController._SystemPollingController__ActivePollingHandler(self.TestPollController._SystemPollingController__ActivePolling, i)
                except Exception as inst:
                    self.fail("ActivePollingHandler raised {} unexpectedly!".format(type(inst)))
    
    def test_SystemPollingController_EventHandler_InactivePollingHandler(self):
        for i in range(601):
            with self.subTest(iter=i):
                try:
                    self.TestPollController._SystemPollingController__InactivePollingHandler(self.TestPollController._SystemPollingController__InactivePolling, i)
                except Exception as inst:
                    self.fail("ActivePollingHandler raised {} unexpectedly!".format(type(inst)))
    
    # def test_SystemPollingController_PRIV_PollInterface(self):
    #     # this is going to be a difficult one to properly simulate in testing
    #     pass
    
    def test_SystemPollingController_PollEverything(self):
        try:
            self.TestPollController.PollEverything()
        except Exception as inst:
            self.fail('PollEverything raised {} unexpectedly!'.format(type(inst)))
    
    def test_SystemPollingController_StartPolling(self):
        contextList = ['inactive', 'active']
        for con in contextList:
            with self.subTest(context=con):
                try:
                    self.TestPollController.StartPolling(con)
                except Exception as inst:
                    self.fail('StartPolling raised {} unexpectedly!'.format(type(inst)))
            
                self.assertEqual(self.TestPollController._SystemPollingController__PollingState, con)
                
    def test_SystemPollingController_StartPolling_BadMode(self):
        testList = \
            [
                'foo',
                1,
                2.5,
                True,
                {'dict': 1},
                ['list']
            ]
        for test in testList:
            with self.subTest(value=test):
                with self.assertRaises(ValueError):
                    self.TestPollController.StartPolling(test)
        
    def test_SystemPollingController_StopPolling(self):
        self.TestPollController.StartPolling()
        try:
            self.TestPollController.StopPolling()
        except Exception as inst:
            self.fail('StopPolling raised {} unexpectedly!'.format(type(inst)))
            
        self.assertEqual(self.TestPollController._SystemPollingController__PollingState, 'stopped')
    
    def test_SystemPollingController_TogglePollingMode(self):
        self.TestPollController.StartPolling()
        self.assertEqual(self.TestPollController._SystemPollingController__PollingState, 'inactive')
        
        try:
            self.TestPollController.TogglePollingMode()
        except Exception as inst:
            self.fail('TogglePollingMode raised {} unexpectedly!'.format(type(inst)))
            
        self.assertEqual(self.TestPollController._SystemPollingController__PollingState, 'active')
        
        try:
            self.TestPollController.TogglePollingMode()
        except Exception as inst:
            self.fail('TogglePollingMode raised {} unexpectedly!'.format(type(inst)))
            
        self.assertEqual(self.TestPollController._SystemPollingController__PollingState, 'inactive')
    
    def test_SystemPollingController_SetPollingMode(self):
        contextList = ['inactive', 'active']
        for con1 in contextList:
            for con2 in contextList:
                with self.subTest(contextCur=con1, contextSet=con2):
                    self.TestPollController.StartPolling(con1)
                    try:
                        self.TestPollController.SetPollingMode(con2)
                    except Exception as inst:
                        self.fail('SetPollingMode raised {} unexpectedly!'.format(type(inst)))
                        
                    self.assertEqual(self.TestPollController._SystemPollingController__PollingState, con2)
    
    def test_SystemPollingController_SetPollingMode_BadMode(self):
        contextList = ['string', 1, 2.5, True, {'key': 'val'}, ['stuff']]
        
        for con in contextList:
            with self.subTest(context=con):
                with self.assertRaises(ValueError):
                    self.TestPollController.SetPollingMode(con)
    
    def test_SystemPollingController_AddPolling(self):
        self.TestGUIController.Initialize()
        TestHardware = self.TestGUIController.Hardware['MON001']
        contextList = \
            [
                {
                    'qualifier': None,
                    'active_duration': 5,
                    'inactive_duration': 10
                },
                {
                    'qualifier': None,
                    'active_duration': None,
                    'inactive_duration': None
                }
            ]
        
        for con in contextList:
            with self.subTest(context=con):
                self.TestPollController.Polling = []
                try:
                    self.TestPollController.AddPolling(TestHardware.interface,
                                                        'AutoImage',
                                                        **con)
                except Exception as inst:
                    self.fail('AddPolling raised {} unexpectedly!'.format(type(inst)))
                    
                self.assertEqual(self.TestPollController.Polling[0], {'interface': TestHardware.interface, 'command': 'AutoImage', 'qualifier': None, 'active_duration': 5, 'inactive_duration': 10})
        
    
    def test_SystemPollingController_RemovePolling(self):
        self.TestGUIController.Initialize()
        TestHardware = self.TestGUIController.Hardware['MON001']
        self.TestPollController.Polling = []
        self.TestPollController.AddPolling(TestHardware.interface,
                                            'AutoImage',
                                            qualifier=None,
                                            active_duration=5,
                                            inactive_duration=10)
        self.assertEqual(len(self.TestPollController.Polling), 1)
        try:
            self.TestPollController.RemovePolling(TestHardware.interface, 'AutoImage')
        except Exception as inst:
            self.fail('RemovePolling raised {} unexpectedly!'.format(type(inst)))
        self.assertEqual(len(self.TestPollController.Polling), 0)
    
    def test_SystemPollingController_UpdatePolling(self):
        self.TestGUIController.Initialize()
        TestHardware = self.TestGUIController.Hardware['MON001']
        self.TestPollController.Polling = []
        self.TestPollController.AddPolling(TestHardware.interface,
                                            'AutoImage',
                                            qualifier=None,
                                            active_duration=5,
                                            inactive_duration=10)
        
        try:
            self.TestPollController.UpdatePolling(TestHardware.interface, 'AutoImage', {'Input': 1}, 10, 15)
        except Exception as inst:
            self.fail('RemovePolling raised {} unexpectedly!'.format(type(inst)))
            
        self.assertEqual(self.TestPollController.Polling[0], {'interface': TestHardware.interface, 'command': 'AutoImage', 'qualifier': {'Input': 1}, 'active_duration': 10, 'inactive_duration': 15})

class SystemStatusController_TestClass(unittest.TestCase):
    def setUp(self) -> None:
        self.TestCtls = ['CTL001']
        self.TestTPs = ['TP001']
        self.TestGUIController = GUIController(settings, self.TestCtls, self.TestTPs)
        self.TestGUIController.Initialize()
        self.TestUIController = self.TestGUIController.TP_Main
        self.TestStatusController = self.TestUIController.StatusCtl
        return super().setUp()
    
    def test_SystemStatusController_Type(self):
        self.assertIsInstance(self.TestStatusController, SystemStatusController)
    
    def test_SystemStatusController_Properties(self):
        # UIHost
        with self.subTest(param='UIHost'):
            self.assertIsInstance(self.TestStatusController.UIHost, (UIDevice, ExUIDevice))
        
        # GUIHost
        with self.subTest(param='GUIHost'):
            self.assertIsInstance(self.TestStatusController.GUIHost, GUIController)
        
        # Hardware
        with self.subTest(param='Hardware'):
            self.assertIsInstance(self.TestStatusController.Hardware, list)
            for item in self.TestStatusController.Hardware:
                with self.subTest(hardware=item):
                    self.assertIsInstance(item, SystemHardwareController)
        
        # UpdateTimer
        with self.subTest(param='UpdateTimer'):
            self.assertIsInstance(self.TestStatusController.UpdateTimer, Timer)
    
    def test_SystemStatusController_PRIV_Properties(self):
        # __StatusIcons
        with self.subTest(param='__StatusIcons'):
            self.assertIsInstance(self.TestStatusController._SystemStatusController__StatusIcons, list)
            for item in self.TestStatusController._SystemStatusController__StatusIcons:
                with self.subTest(item=item.Name):
                    self.assertIsInstance(item, Button)
        
        # __StatusLabels
        with self.subTest(param='__StatusLabels'):
            self.assertIsInstance(self.TestStatusController._SystemStatusController__StatusLabels, list)
            for item in self.TestStatusController._SystemStatusController__StatusLabels:
                with self.subTest(item=item.Name):
                    self.assertIsInstance(item, Label)
        
        # __Arrows
        with self.subTest(param='__Arrows'):
            self.assertIsInstance(self.TestStatusController._SystemStatusController__Arrows, dict)
            for key, item in self.TestStatusController._SystemStatusController__Arrows.items():
                with self.subTest(item=key):
                    self.assertIsInstance(key, str)
                    self.assertIsInstance(item, Button)
        
        # __PageLabels
        with self.subTest(param='__PageLabels'):
            self.assertIsInstance(self.TestStatusController._SystemStatusController__PageLabels, dict)
            for key, item in self.TestStatusController._SystemStatusController__PageLabels.items():
                with self.subTest(item=key):
                    self.assertIsInstance(key, str)
                    self.assertIsInstance(item, Label)
        
        # __HardwareCount
        with self.subTest(param='__HardwareCount'):
            self.assertIsInstance(self.TestStatusController._SystemStatusController__HardwareCount, int)
        
        # __DisplayPages
        with self.subTest(param='__DisplayPages'):
            self.assertIsInstance(self.TestStatusController._SystemStatusController__DisplayPages, int)
        
        # __CurrentPageIndex
        with self.subTest(param='__CurrentPageIndex'):
            self.assertIsInstance(self.TestStatusController._SystemStatusController__CurrentPageIndex, int)
    
    def test_SystemStatusController_EventHandler_PaginationHandler(self):
        btnList = list(self.TestStatusController._SystemStatusController__Arrows.values())
        actList = ['Pressed', 'Released']
        conList = range(self.TestStatusController._SystemStatusController__DisplayPages)
        
        for con in conList:
            for btn in btnList:
                for act in actList:
                    with self.subTest(button=btn.Name, action=act, context=con):
                        try:
                            self.TestStatusController._SystemStatusController__CurrentPageIndex = con
                            self.TestStatusController._SystemStatusController__PaginationHandler(btn, act)
                        except Exception as inst:
                            self.fail('__PaginationHandler raised {} unexpectedly!'.format(type(inst)))
    
    def test_SystemStatusController_EventHandler_UpdateHandler(self):
        try:
            self.TestStatusController._SystemStatusController__UpdateHandler(self.TestStatusController.UpdateTimer, 1)
        except Exception as inst:
            self.fail('__UpdateHandler raised {} unexpectedly!'.format(type(inst)))
    
    def test_SystemStatusController_PRIV_ClearStatusIcons(self):
        try:
            self.TestStatusController._SystemStatusController__ClearStatusIcons()
        except Exception as inst:
            self.fail('__ClearStatusIcon raised {} unexpectedly!'.format(type(inst)))
    
    def test_SystemStatusController_PRIV_ShowStatusIcons(self):
        while self.TestStatusController._SystemStatusController__DisplayPages < 3:
            self.TestStatusController.Hardware.extend(self.TestStatusController.Hardware)
        for i in range(self.TestStatusController._SystemStatusController__DisplayPages):
            with self.subTest(pageIndex=i):
                try:
                    self.TestStatusController._SystemStatusController__CurrentPageIndex = i
                    self.TestStatusController._SystemStatusController__ShowStatusIcons()
                except Exception as inst:
                    self.fail('__ShowStatusIcons raised {} unexpectedly!'.format(type(inst)))
    
    # This is very difficult to test
    # def test_SystemStatusController_PRIV_GetStatusState(self):
    #     for hw in self.TestStatusController.Hardware:
    #         with self.subTest(hardware=hw.Name):
    #             try:
    #                 state = self.TestStatusController._SystemStatusController__GetStatusState(hw)
    #             except Exception as inst:
    #                 self.fail('__GetStatusState raised {} unexpectedly!'.format(type(inst)))
    #             self.assertIn(state, [0, 1, 2, 3])
    
    def test_SystemStatusController_PRIV_UpdatePagination_MultiPage(self):
        while self.TestStatusController._SystemStatusController__DisplayPages < 3:
            self.TestStatusController.Hardware.extend(self.TestStatusController.Hardware)
        for i in range(self.TestStatusController._SystemStatusController__DisplayPages):
            with self.subTest(pageindex=i):
                try:
                    self.TestStatusController._SystemStatusController__CurrentPageIndex = i
                    self.TestStatusController._SystemStatusController__UpdatePagination()
                except Exception as inst:
                    self.fail('__UpdatePagination raised {} unexpectedly!'.format(type(inst)))
                    
    def test_SystemStatusController_PRIV_UpdatePagination_SinglePage(self):
        while self.TestStatusController._SystemStatusController__DisplayPages > 1:
            self.TestStatusController.Hardware.pop()
        try:
            self.TestStatusController._SystemStatusController__CurrentPageIndex = 0
            self.TestStatusController._SystemStatusController__UpdatePagination()
        except Exception as inst:
            self.fail('__UpdatePagination raised {} unexpectedly!'.format(type(inst)))
    
    def test_SystemStatusController_ResetPages(self):
        try:
            self.TestStatusController.ResetPages()
        except Exception as inst:
            self.fail('ResetPages raised {} unexpectedly!'.format(type(inst)))
    
    def test_SystemStatusController_UpdateStatusIcons(self):
        self.TestStatusController._SystemStatusController__ShowStatusIcons()
        
        try:
            self.TestStatusController.UpdateStatusIcons()
        except Exception as inst:
            self.fail('UpdateStatusIcons raised {} unexpectedly!'.format(type(inst)))

if __name__ == '__main__':
    unittest.main()