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
from typing import TYPE_CHECKING
if TYPE_CHECKING:                                                               # pragma: no cover
    pass

#### Python imports

#### Extron Library Imports

#### Project imports
from modules.helper.Collections import AlertCollection
## End Imports -----------------------------------------------------------------

# Create empty DeviceCollection to populate with system devices below
SystemAlerts = AlertCollection()

################################################################################
################################################################################
## Alert  Documentation                                                       ##
## -------------------------------------------------------------------------- ##
## Name: name for alert                                                       ##
## AlertDeviceId: Device Id or 'sys', determines where alerts are shown       ##
## AlertLevel: 'info', 'warn', 'err', or callable which returns one of these  ##
##             strings                                                        ##
## AlertText: Alert string or callable which returns an alert string          ##
## TestDeviceId: device with interface to test alert status                   ##
## TestCommand: control module command to read status of on TestDeviceID's    ##
##              interface                                                     ##
## TestQualifier: control module qualifier for TestCommand, may be None       ##
## TestOperator: string operator to test device status against TestOperand    ##
##     Valid Options:                                                         ##
##          ==: ['eq', 'equal', 'equals', 'equal to', '=', '==']              ##
##          !=: ['neq', '!eq', 'not equal', 'not equals',                     ##
##               'unequal to', '!=', '!==']                                   ##
##          >:  ['gt', 'greater', 'greater than', '>']                        ##
##          >=: ['gte', 'greater or equal', 'greater than or equal to', '>='] ##
##          <:  ['lt', 'less', 'less than', '<']                              ##
##          <=: ['lte', 'less or equal', 'less than or equal to', '<=']       ##
##          in: ['in', 'in list', 'in object']                                ##
##          not in: ['not in', '!in', 'not in list', 'not in object']         ##
##          is: ['is']                                                        ##
##          is not: ['is not', '!is']                                         ##
## TestOperand: any value to compare against TestDeviceID's test status       ##
##                                                                            ##
## Alerts are active if the test evaluates to True                            ##
## Alerts contain a watch variable .Changed which can be used to update alert ##
##     feedback or otherwise update system information when alert information ##
##     changes.
################################################################################
################################################################################
## ADD ALERT CONFIGS BELOW                                                    ##
## VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV ##

SystemAlerts.AddNewAlert(**{
    'Name': 'PC001 Source Alert',
    'AlertDeviceId': 'PC001',
    'AlertLevel': 'info',
    'AlertText': 'Ensure the PC is awake.',
    'TestDeviceId': 'VMX001',
    'TestCommand': 'InputSignalStatus',
    'TestQualifier': {'Input': 1},
    'TestOperator': '==',
    'TestOperand': 'Not Active'
})

SystemAlerts.AddNewAlert(**{
    'Name': 'WPD001 Source Alert',
    'AlertDeviceId': 'WPD001',
    'AlertLevel': 'info',
    'AlertText': 'Contact Library IT for Assistance with this Wireless Device',
    'TestDeviceId': 'VMX001',
    'TestCommand': 'InputSignalStatus',
    'TestQualifier': {'Input': 2},
    'TestOperator': '==',
    'TestOperand': 'Not Active'
})

SystemAlerts.AddNewAlert(**{
    'Name': 'MON002 Input Source Alert',
    'AlertDeviceId': 'MON002',
    'AlertLevel': 'info',
    'AlertText': 'Contact Library IT for Assistance with Monitor Configuration',
    'TestDeviceId': 'MON002',
    'TestCommand': 'Input',
    'TestOperator': '!=',
    'TestOperand': 'HDMI 1'
})
