################################################################################
# Copyright © 2023 The Board of Trustees of the University of Illinois
#
# Licensed under the MIT License (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://opensource.org/licenses/MIT
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
################################################################################


## Begin Imports ---------------------------------------------------------------

#### Type Checking
from typing import TYPE_CHECKING, Dict, Tuple, List, Union, Callable
if TYPE_CHECKING: # pragma: no cover
    pass

#### Python imports

#### Extron Library Imports
from extronlib.device import ProcessorDevice, UIDevice, SPDevice, eBUSDevice
from extronlib.system import Wait

#### Project imports
from modules.helper.CommonUtilities import Logger, DictValueSearchByKey, RunAsync, debug
from modules.helper.Collections import DictObj
from ui.interface.TouchPanel import TouchPanelInterface
from ui.interface.ButtonPanel import ButtonPanelInterface
from ui.utilties.PinPad import PINController
from modules.helper.PrimitiveObjects import Alias, classproperty
import System

## End Imports -----------------------------------------------------------------
##
## Begin Class Definitions -----------------------------------------------------

class ExProcessorDevice(ProcessorDevice):
    ipcp_pro_xi_part_list = ['60-1911-01', '60-1911-01A', # IPCP Pro 250 xi
                             '60-1914-01', '60-1914-01A', # IPCP Pro 250Q xi
                             '60-1912-01', '60-1912-01A', # IPCP Pro 350 xi
                             '60-1915-01', '60-1915-01A', # IPCP Pro 355DRQ xi
                             '60-1916-01', '60-1916-01A', # IPCP Pro 360Q xi
                             '60-1913-01', '60-1913-01A', # IPCP Pro 550 xi
                             '60-1917-01', '60-1917-01A', # IPCP Pro 555Q xi
                             '60-1979-01', '60-1979-01A', # IPCP Pro S1 xi
                             ]
    ipcp_pro_part_list = ['60-1429-01', '60-1429-01A', # IPCP Pro 250
                          '60-1431-01', '60-1431-01A', # IPCP Pro 255
                          '60-1417-01', '60-1417-01A', # IPCP Pro 350
                          '60-1433-01', '60-1433-01A', # IPCP Pro 355DR
                          '60-1432-01', '60-1432-01A', # IPCP Pro 360
                          '60-1418-01', '60-1418-01A', # IPCP Pro 550
                          '60-1434-01', '60-1434-01A', # IPCP Pro 555
                          ]
    
    def __init__(self, DeviceAlias: str, PartNumber: str = None) -> object:
        super().__init__(DeviceAlias, PartNumber)
        self.Id = DeviceAlias
    
    def __repr__(self) -> str:
        return 'ExProcessorDevice: {} ({}|{})'.format(self.ModelName, self.DeviceAlias, self.IPAddress)
    
    @classproperty
    def validation_part_list(cls) -> list:
        valid_list = []
        valid_list.extend(cls.ipcp_pro_part_list)
        valid_list.extend(cls.ipcp_pro_xi_part_list)
        return valid_list

class ExUIDevice(UIDevice):
    tp_part_list = ['60-1791-02', '60-1791-12', '60-1792-02', '60-1792-12', # 17" panels
                    '60-1789-02', '60-1789-12', '60-1790-02', '60-1790-12', # 15" panels
                    '60-1668-02', '60-1668-03', '60-1340-02', '60-1787-02', '60-1787-12', '60-1788-02', '60-1788-12', # 12" panels
                    '60-1566-02', '60-1566-03', '60-1566-12', '60-1566-13', '60-1565-02', '60-1565-03', '60-1565-12', '60-1565-13' # 10" panels
                    '60-1564-02', '60-1564-12', '60-1563-02', '60-1563-03', '60-1563-12', '60-1563-13', '60-1562-02', '60-1562-03', '60-1562-12', '60-1562-13' # 7" panels
                    '60-1560-02', '60-1560-12', '60-1561-02', '60-1561-03', '60-1561-12', '60-1561-13', '60-1559-02', '60-1559-03', '60-1559-12', '60-1559-13' # 5" panles
                    '60-1667-02', '60-1667-03' # 3.5" panels
                    ]
    bp_part_list = ['60-1953-01', # NBP 50
                    '60-1794-01', # NBP 100
                    '60-1795-01', # NBP 200
                    '60-1688-01', '60-1817-01', '60-1818-01', '60-1689-01', # NBP Decora Panels
                    '60-1835-01', '60-1835-08' # Cable Cubby NBP panel
                    ]
    
    def __init__(self, DeviceAlias: str, UI: str, PartNumber: str = None, Name: str=None, WebControlId: str=None) -> object:
        super().__init__(DeviceAlias, PartNumber)
        self.Id = DeviceAlias
        self.Name = Name
        self.WebControlId = WebControlId
        self.Initialized = False
        if type(UI) is str:
            self.UI = UI
        else:
            raise ValueError('Layout must be a string')
        
        if self.PartNumber in self.tp_part_list:
            self.Class = 'TouchPanel'
            self.Interface = TouchPanelInterface(self, self.UI)
        elif self.PartNumber in self.bp_part_list:
            self.Class = 'ButtonPanel'
            self.Interface = ButtonPanelInterface(self, self.UI)
        else:
            self.Class = 'Unknown'
            
        self.BlinkLights(Rate='Slow', StateList=['Red'])
    
    def __repr__(self) -> str:
        return 'ExUIDevice: {} ({}|{})'.format(self.ModelName, self.DeviceAlias, self.IPAddress)
        
    @classproperty
    def validation_part_list(cls) -> list:
        valid_list = []
        valid_list.extend(cls.tp_part_list)
        valid_list.extend(cls.bp_part_list)
        return valid_list
    
    def Initialize(self) -> None:
        ## Hide any popups from previous program loads
        self.HideAllPopups()
        
        ## initialize interface
        self.Interface.Initialize()
        
        ## show control group popups
        self.Interface.Objects.ControlGroups.ShowPopups()
        
        ## initialize PIN Controllers
        if self.Class == 'TouchPanel':
            self.SecureAccess = DictObj({
                    "System": PINController(self),
                    "Tech": PINController(self)
                })
        
        ## set Room Label to system Room Name
        RoomLabelBtn = self.Interface.Objects.Buttons['Room-Label']
        RoomLabelBtn.SetText(System.CONTROLLER.RoomName)
        RoomLabelBtn.SetEnable(False)
        
        ## show initial page
        self.ShowPage('Splash')
        
        self.Initialized = True
    
    def BlinkLights(self, Rate: str='Medium', StateList: List=None, Timeout: Union[int, float]=0):
        if StateList is None:
            StateList = ['Off', 'Red']
        
        for State in StateList:
            if State not in ['Off', 'Green', 'Red']:
                raise ValueError('State must be one of "Off", "Red", or "Green"')
        
        allowedRates = ['Slow', 'Medium', 'Fast']
        if Rate not in allowedRates:
            raise ValueError('Rate must be one of {}'.format(allowedRates))
        
        # self.TP_Lights.SetBlinking(Rate, StateList) 
        self.SetLEDBlinking(65533, Rate, StateList)
        
        if Timeout > 0:
            Wait(float(Timeout), self.LightsOff())
    
    def SetLights(self, State, Timeout: Union[int, float]=0):
        if State not in ['Off', 'Green', 'Red']:
            raise ValueError('State must be one of "Off", "Red", or "Green"')
        self.SetLEDState(65533, State)
        
        if Timeout > 0:
            Wait(float(Timeout), self.LightsOff())
    
    def LightsOff(self):
        # self.TP_Lights.SetState(self.TP_Lights.StateIds['off'])
        self.SetLEDState(65533, 'Off')

class ExSPDevice(SPDevice):
    def __init__(self, DeviceAlias: str, PartNumber: str = None) -> None:
        super().__init__(DeviceAlias, PartNumber)
        self.Id = DeviceAlias

class ExEBUSDevice(eBUSDevice):
    us_ebus_part_list = ["60-1388-01", # EBP 100
                         "60-1389-01", # EPB 200
                         "60-1670-01", # EBP 50
                        ]
    decora_ebus_part_list = ["60-1671-01", # EBP 103 D
                             "60-1084-01", # EBP 106 D
                             "60-1093-01", # EBP 106P D
                             "60-1189-01", # EBP 108 D
                             "60-1190-01", # EBP 110 D
                             "60-1087-01", # EBP 111 D
                             "60-1086-01", # EBP NAV D
                             "60-1184-01", # EBP VC1
                             ]
    def __init__(self, Host: Union[ProcessorDevice, ExProcessorDevice], UI: str, DeviceAlias: str, Name: str=None, WebControlId: str=None):
        super().__init__(Host, DeviceAlias)
        # The super object has an ID prop for eBUS ID, unclear how that is populated
        self.Id = DeviceAlias
        self.eBUSID = Alias('ID')
        self.WebControlId = WebControlId
        if type(UI) is str:
            self.UI = UI
        else:
            raise ValueError('Layout must be a string')
        self.Class = 'ButtonPanel'
        self.Interface = ButtonPanelInterface(self, self.UI)
        
    @classproperty
    def validation_part_list(cls) -> list:
        valid_list = []
        valid_list.extend(cls.us_ebus_part_list)
        valid_list.extend(cls.decora_ebus_part_list)
        return valid_list

## End Class Definitions -------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------

## End Function Definitions ----------------------------------------------------
