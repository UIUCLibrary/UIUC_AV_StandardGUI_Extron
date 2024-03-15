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
    from modules.project.ExtendedClasses.UI \
        import (ButtonEx_Ref, 
                ButtonEx, 
                LabelEx, 
                LevelEx, 
                SliderEx, 
                KnobEx)
    from modules.project.ExtendedClasses.Device \
        import (ExProcessorDevice,
                ExUIDevice,
                ExSPDevice,
                ExEBUSDevice)
    from modules.project.Collections.UISets \
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
                PanelSetupGroup,
                ScheduleConfigGroup,
                ScheduleEditGroup)

# Python imports

# Project imports
from modules.project.Devices.Classes import BLANK_SOURCE                                # noqa: F401
from modules.helper.CommonUtilities import MergeLists
from modules.project.PrimitiveObjects import ActivityMode, SystemState

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

EVENTS_BUTTON = ['Pressed', 'Released', 'Held', 'Repeated', 'Tapped']
EVENTS_SLIDER = ['Pressed', 'Released', 'Changed']

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
                    'PanelSetupGroup',
                    'ScheduleConfigGroup',
                    'ScheduleEditGroup']
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
                    'PanelSetupGroup',
                    'ScheduleConfigGroup',
                    'ScheduleEditGroup')

UI_OBJECTS =  Union['ButtonEx_Ref', 
                    'ButtonEx', 
                    'LabelEx', 
                    'LevelEx', 
                    'SliderEx', 
                    'KnobEx']
UI_OBJECTS_MATCH = ('ButtonEx_Ref', 
                    'ButtonEx', 
                    'LabelEx', 
                    'LevelEx', 
                    'SliderEx', 
                    'KnobEx')

UI_BUTTONS =  Union['ButtonEx_Ref', 
                    'ButtonEx']
UI_BUTTONS_MATCH = ('ButtonEx_Ref', 
                    'ButtonEx')

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
                'ScheduleConfigGroup',
                'ScheduleEditGroup',
                'ButtonEx_Ref', 
                'ButtonEx', 
                'LabelEx', 
                'LevelEx', 
                'SliderEx', 
                'KnobEx']
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
                'ScheduleConfigGroup',
                'ScheduleEditGroup',
                'ButtonEx_Ref', 
                'ButtonEx', 
                'LabelEx', 
                'LevelEx', 
                'SliderEx', 
                'KnobEx')

UI_HOSTS =    Union['ExUIDevice', 
                    'ExEBUSDevice', 
                    'ExProcessorDevice', 
                    'ExSPDevice']
UI_HOSTS_MATCH =   ('ExUIDevice', 
                    'ExEBUSDevice', 
                    'ExProcessorDevice', 
                    'ExSPDevice')