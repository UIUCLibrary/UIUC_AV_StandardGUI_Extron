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

# Python imports
from enum import Enum

# Project imports
from modules.device.classes.Sources import Source

class ActivityMode(Enum):
    Standby = 0
    Share = 1
    AdvShare = 2
    GroupWork = 3
    
    def GetNameByValue(cls, val) -> str:
        for data in cls:
            if data.value == val:
                return data.name

BLANK_SOURCE = Source(None, 0, 0, 'blank', 'None')

OFF = ['off', 'Off', 'OFF', False, 0]
ON = ['on', 'On', 'ON', True, 1]

STANDBY = ['off', 'Off', 'OFF', 'standby', 'Standby', 'StandBy', 'STANDBY', ActivityMode.Standby, 0]
SHARE = ['share', 'Share', ActivityMode.Share, 1]
ADVSHARE = ['advshare', 'advShare', 'AdvShare', 'Adv.Share', 'Adv Share', 'Adv. Share', 'adv_share', 'ADV_SHARE', 'ADVSHARE', ActivityMode.AdvShare, 2]
GROUPWORK = ['groupwork', 'groupWork', 'GroupWork', 'GROUPWORK', 'grpwrk', 'grp_work', 'grp_wrk', 'grp_work', 'group work', 'Group Work', 'GROUP WORK', ActivityMode.GroupWork, 3]