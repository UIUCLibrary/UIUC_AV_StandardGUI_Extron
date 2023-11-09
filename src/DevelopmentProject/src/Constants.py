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

#### Type Checking
from typing import TYPE_CHECKING, Union

if TYPE_CHECKING: # pragma: no cover
    from modules.helper.ExtendedUIClasses \
        import (RefButton, 
                ExButton, 
                ExLabel, 
                ExLevel, 
                ExSlider, 
                ExKnob)
    from modules.helper.ExtendedDeviceClasses \
        import (ExProcessorDevice,
                ExUIDevice,
                ExSPDevice,
                ExEBUSDevice)
    from modules.helper.ExtendedUIClasses.UISets \
        import (RadioSet, 
                SelectSet, 
                VariableRadioSet, 
                ScrollingRadioSet, 
                VolumeControlGroup,
                HeaderControlGroup,
                PINPadControlGroup,
                KeyboardControlGroup,
                SystemStatusControlGroup,
                AboutPageGroup,
                PanelSetupGroup)

# Python imports
from enum import Enum

# Project imports
from modules.device.classes.Sources import Source
from modules.helper.CommonUtilities import MergeLists

class ActivityMode(Enum):
    Standby = 0
    Share = 1
    AdvShare = 2
    GroupWork = 3

class SystemState(Enum):
    Standby = 0
    Active = 1

BLANK_SOURCE = Source(None, 0, 0, 'blank', 'None')

OFF =  ('off', 
        'Off', 
        'OFF', 
        False, 
        0)
ON =   ('on', 
        'On', 
        'ON', 
        True, 
        1)

STANDBY =      ('off', 
                'Off', 
                'OFF', 
                'standby', 
                'Standby', 
                'StandBy', 
                'STANDBY', 
                ActivityMode.Standby, 
                SystemState.Standby, 
                0)
SHARE =        ('share', 
                'Share', 
                ActivityMode.Share, 
                1)
ADVSHARE =     ('advshare', 
                'advShare', 
                'AdvShare', 
                'Adv.Share', 
                'Adv Share', 
                'Adv. Share', 
                'adv_share', 
                'ADV_SHARE', 
                'ADVSHARE', 
                ActivityMode.AdvShare, 
                2)
GROUPWORK =    ('groupwork', 
                'groupWork', 
                'GroupWork', 
                'GROUPWORK', 
                'grpwrk', 
                'grp_work', 
                'grp_wrk', 
                'grp_work', 
                'group work', 
                'Group Work', 
                'GROUP WORK', 
                ActivityMode.GroupWork, 
                3)

ACTIVE = tuple(MergeLists([SystemState.Active], SHARE, ADVSHARE, GROUPWORK))

EVENTS_BUTTON = ('Pressed', 'Released', 'Held', 'Repeated', 'Tapped')
EVENTS_SLIDER = ('Pressed', 'Released', 'Changed')

UI_SETS =     Union['RadioSet', 
                    'SelectSet', 
                    'VariableRadioSet', 
                    'ScrollingRadioSet',
                    'VolumeControlGroup',
                    'HeaderControlGroup',
                    'PINPadControlGroup',
                    'KeyboardControlGroup',
                    'SystemStatusControlGroup',
                    'AboutPageGroup',
                    'PanelSetupGroup']
UI_SETS_MATCH =    ('RadioSet', 
                    'SelectSet', 
                    'VariableRadioSet', 
                    'ScrollingRadioSet',
                    'VolumeControlGroup',
                    'HeaderControlGroup',
                    'PINPadControlGroup',
                    'KeyboardControlGroup',
                    'SystemStatusControlGroup',
                    'AboutPageGroup',
                    'PanelSetupGroup')

UI_OBJECTS =  Union['RefButton', 
                    'ExButton', 
                    'ExLabel', 
                    'ExLevel', 
                    'ExSlider', 
                    'ExKnob']
UI_OBJECTS_MATCH = ('RefButton', 
                    'ExButton', 
                    'ExLabel', 
                    'ExLevel', 
                    'ExSlider', 
                    'ExKnob')

UI_ALL =  Union['RadioSet', 
                'SelectSet', 
                'VariableRadioSet', 
                'ScrollingRadioSet',
                'VolumeControlGroup',
                'HeaderControlGroup',
                'PINPadControlGroup',
                'KeyboardControlGroup',
                'SystemStatusControlGroup',
                'AboutPageGroup',
                'PanelSetupGroup',
                'RefButton', 
                'ExButton', 
                'ExLabel', 
                'ExLevel', 
                'ExSlider', 
                'ExKnob']
UI_ALL_MATCH = ('RadioSet', 
                'SelectSet', 
                'VariableRadioSet', 
                'ScrollingRadioSet',
                'VolumeControlGroup',
                'HeaderControlGroup',
                'PINPadControlGroup',
                'KeyboardControlGroup',
                'SystemStatusControlGroup',
                'AboutPageGroup',
                'PanelSetupGroup',
                'RefButton', 
                'ExButton', 
                'ExLabel', 
                'ExLevel', 
                'ExSlider', 
                'ExKnob')

UI_HOSTS =    Union['ExUIDevice', 
                    'ExEBUSDevice', 
                    'ExProcessorDevice', 
                    'ExSPDevice']
UI_HOSTS_MATCH =   ('ExUIDevice', 
                    'ExEBUSDevice', 
                    'ExProcessorDevice', 
                    'ExSPDevice')