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

from typing import TYPE_CHECKING, Dict, Tuple, List, Union, Callable
if TYPE_CHECKING: # pragma: no cover
    pass

## Begin ControlScript Import --------------------------------------------------

from extronlib.device import ProcessorDevice, UIDevice, SPDevice

## End ControlScript Import ----------------------------------------------------
##
## Begin Python Imports --------------------------------------------------------

## End Python Imports ----------------------------------------------------------
##
## Begin User Import -----------------------------------------------------------
#### Custom Code Modules
from modules.helper.UtilityFunctions import DictValueSearchByKey, RunAsync, debug
from variables import PROG, TRACE

## End User Import -------------------------------------------------------------
##
## Begin Class Definitions -----------------------------------------------------

class ExProcessorDevice(ProcessorDevice):
    def __init__(self, DeviceAlias: str, PartNumber: str = None) -> object:
        super().__init__(DeviceAlias, PartNumber)
        self.Id = DeviceAlias
        
class ExUIDevice(UIDevice):
    def __init__(self, DeviceAlias: str, UI: str, PartNumber: str = None) -> object:
        super().__init__(DeviceAlias, PartNumber)
        self.Id = DeviceAlias
        
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
        cp_part_list = ['60-1559-13' # 3.5" Cable Cubble Touch & Button Panel
                        ]
        
        if self.PartNumber in tp_part_list:
            self.Class = 'TouchPanel'
        elif self.PartNumber in bp_part_list:
            self.Class = 'ButtonPanel'
        elif self.PartNumber in cp_part_list:
            self.Class = 'ComboPanel'
        else:
            self.Class = 'Unknown'
            
        if type(UI) is str:
            self.UI = UI
        else:
            raise ValueError('Layout must be a string')
        
class ExSPDevice(SPDevice):
    def __init__(self, DeviceAlias: str, PartNumber: str = None) -> None:
        super().__init__(DeviceAlias, PartNumber)
        self.Id = DeviceAlias

## End Class Definitions -------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------

## End Function Definitions ----------------------------------------------------
