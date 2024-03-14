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
from typing import TYPE_CHECKING, Dict
if TYPE_CHECKING: # pragma: no cover
    from modules.project.Collections import DeviceCollection

#### Python Imports
from datetime import datetime
import importlib
import importlib.util
import functools
from inspect import getmro

#### Exron Library Imports

#### Project Imports
from modules.helper.ConnectionHandler import GetConnectionHandler
from modules.project.mixins.Interface import InterfaceSystemHost
from modules.helper.CommonUtilities import Logger
from modules.project.Classes import (Source, 
                                    Destination, 
                                    Camera, 
                                    Switch, 
                                    Microphone, 
                                    Screen, 
                                    Light, 
                                    Shade)
from modules.project.mixins import InitializeMixin
import Variables
import System

## End Imports -------------------------------------------------------------
##
## Begin Class Definitions -----------------------------------------------------

class SystemHardwareController(InitializeMixin, object):
    def __init__(self, DeviceCollection: 'DeviceCollection', Id: str, Name: str, Manufacturer: str, Model: str, Interface: Dict, Subscriptions: Dict, Polling: Dict, Options: Dict=None) -> None:
        InitializeMixin.__init__(self, self.__Initialize)
        
        self.Collection = DeviceCollection
        self.Id = Id
        self.Name = Name
        self.Manufacturer = Manufacturer
        self.Model = Model
        self.ConnectionStatus = 'Not Connected'
        self.LastStatusChange = None
        
        self.__Subscriptions = Subscriptions
        self.__Polling = Polling
        
        if Options is not None:
            for key in Options:
                if not hasattr(self, key):
                    setattr(self, key, Options[key])
        
        if Interface is not None:
            # interface data structure example
            # interface = {
            #     "module": module_name,
            #     "interface_class": interface_class,
            #     "ConnectionHandler": {
            #         Connection handler configuration items
            #     }
            #     "interface_configuration": {
            #         interface configuration items
            #     }
            # }
            
            self.__Module = importlib.import_module('modules.device.{}'.format(Interface['module']))
            self.__Constructor = getattr(self.__Module,
                                        Interface['interface_class'])
            
            self.__Interface = Interface
        else:
            self.__Interface = None
    
    def __repr__(self) -> str:
        return 'Device: {} ({}|{})'.format(self.Name, self.Id, self.ConnectionStatus)
    
    def __Initialize(self):
        if self.__Interface is not None:
            if self.__Interface['interface_class'] == 'SerialClass':
                host_id = self.__Interface['interface_configuration']['Host']
                # TODO: this may need to check other collections for host matches if using expansion devices
                self.__Interface['interface_configuration']['Host'] = System.CONTROLLER.Processors.GetProcessorById(host_id)
            
            if 'ConnectionHandler' in self.__Interface and isinstance(self.__Interface['ConnectionHandler'], dict):
                self.interface = GetConnectionHandler(self.__Constructor(**self.__Interface['interface_configuration']),
                                                    **self.__Interface['ConnectionHandler'])
                if not Variables.TESTING:
                    self.interface.Connect()
            else:
                self.interface = self.__Constructor(**self.__Interface['interface_configuration'])
            
            # add mixin(s) to the interface class
            # this prepends 'ex' to the front of the existing class name and adds a tuple of mixin classes to the existing class bases.
            originalClass = type(self.interface)
            exClassName = 'ex{}_{}'.format(str(self.__Interface['module']).capitalize(), self.__Interface['interface_class'])
            
            # check for feedback modules
            # feedbackModule = importlib.util.find_spec('ui.feedback.device.{}'.format(Interface['module']))
            # if feedbackModule is not None:
            #     importlib.import_module('ui.feedback.device.{}'.format(Interface['module']))
            #     feedbackClass = locate('ui.feedback.device.{}.FeedbackClass'.format(Interface['module']))
            #     mixinTuple = (InterfaceSystemHost, feedbackClass)
            # else:
            #     mixinTuple = (InterfaceSystemHost, )
            mixinTuple = (InterfaceSystemHost, )
                
            # get original class bases
            bases = getmro(originalClass)
            exBaseTuple = mixinTuple + bases
            
            # extend class
            self.interface.__class__ = type(exClassName, exBaseTuple, {})
            
            # set interface parameters here
            self.interface.Collection = self.Collection
            
            self.interface.SubscribeStatus('ConnectionStatus', None, self.__ConnectionStatus)
        
        # subscription data structure example
        # subscriptions = [
        #     {
        #         'command': subscription command,
        #         'qualifier': qualifier,
        #         'callback': callback function
        #     },
        #     ...
        # ]
        
        if self.__Subscriptions is not None:
            for sub in self.__Subscriptions:
                qualSub = self.GetQualifierList(sub)
                
                for qp in qualSub:
                    # these subscriptions do not poll for updated statuses and appropriate
                    # Update or Set commands must be sent elsewhere in the program
                    # Use these subscriptions to verify changes or to handle control feedback
                    self.AddSubscription(sub, qp)
        
        # polling data structure example
        # polling = [
        #  {
        #     'command': polling command,
        #     'qualifier': command qualifier, Optional
        #     'callback': polling update command, Optional
        #     'active_int': active polling interval, Optional
        #     'inactive_int': inactive polling interval, Optional
        #  },
        #  ...
        # ]
        
        if self.__Polling is not None:
            for poll in self.__Polling:
                qualPoll = self.GetQualifierList(poll)
                
                if 'active_int' in poll:
                    actInt = poll['active_int']
                else:
                    actInt = None
                if 'inactive_int' in poll:
                    inactInt = poll['inactive_int']
                else:
                    inactInt = None
                
                for qp in qualPoll:
                    self.Collection.AddPolling(self,
                                                poll['command'],
                                                qualifier=qp,
                                                active_duration=actInt,
                                                inactive_duration=inactInt
                                                )
                    
                    # To prevent the need to duplicate polling and subscriptions in settings
                    # if a callback is included in the poll, a subscription will automatically
                    # be created on the interface
                    if 'callback' in poll:
                        self.AddSubscription(poll, qp)
        
        objDict = None
        if hasattr(self, 'Destination'):
            # Logger.Log('Initializing Destination')
            objDict = dict(self.Destination)
            objAttr = 'Destination'
            objClass = Destination
        elif hasattr(self, 'Source'):
            # Logger.Log('Initializing Source')
            objDict = dict(self.Source)
            objAttr = 'Source'
            objClass = Source
        elif hasattr(self, 'Switch'):
            # Logger.Log('Initializing Switch')
            objDict = dict(self.Switch)
            objAttr = 'Switch'
            objClass = Switch
        elif hasattr(self, 'Camera'):
            # Logger.Log('Initializing Camera')
            objDict = dict(self.Camera)
            objAttr = 'Camera'
            objClass = Camera
        elif hasattr(self, 'Microphone'):
            # Logger.Log('Initializing Microphone')
            objDict = dict(self.Microphone)
            objAttr = 'Microphone'
            objClass = Microphone
        elif hasattr(self, 'Screen'):
            # Logger.Log('Initializing Screen')
            objDict = dict(self.Screen)
            objAttr = 'Screen'
            objClass = Screen
        elif hasattr(self, 'Light'):
            # Logger.Log('Initializing Light')
            objDict = dict(self.Light)
            objAttr = 'Light'
            objClass = Light
        elif hasattr(self, 'Shade'):
            # Logger.Log('Initializing Shade')
            objDict = dict(self.Shade)
            objAttr = 'Shade'
            objClass = Shade
        
        if objDict is not None:
            objDict['device'] = self
            setattr(self, objAttr, objClass(**objDict))
    
    # Collection attributes
    @property
    def IsDest(self) -> bool:
        return hasattr(self, 'Destination')
    
    @IsDest.setter
    def IsDest(self, value) -> None:
        raise AttributeError('IsDest property cannot be set, only read')
    
    @property
    def IsSrc(self) -> bool:
        return hasattr(self, 'Source')
    
    @IsSrc.setter
    def IsSrc(self, value) -> None:
        raise AttributeError('IsSrc property cannot be set, only read')
    
    @property
    def IsSwitch(self) -> bool:
        return hasattr(self, 'Switch')
    
    @IsSwitch.setter
    def IsSwitch(self, value) -> None:
        raise AttributeError('IsSwitch property cannot be set, only read')
    
    @property
    def IsCam(self) -> bool:
        return hasattr(self, 'Camera')
    
    @IsCam.setter
    def IsCam(self, value) -> None:
        raise AttributeError('IsCam property cannot be set, only read')
    
    @property
    def IsMic(self) -> bool:
        return hasattr(self, 'Microphone')
    
    @IsMic.setter
    def IsMic(self, value) -> None:
        raise AttributeError('IsMic property cannot be set, only read')
    
    @property
    def IsScn(self) -> bool:
        return hasattr(self, 'Screen')
    
    @IsScn.setter
    def IsScn(self, value) -> None:
        raise AttributeError('IsScn property cannot be set, only read')
    
    @property
    def IsLight(self) -> bool:
        return hasattr(self, 'Light')
    
    @IsLight.setter
    def IsLight(self, value) -> None:
        raise AttributeError('IsLight property cannot be set, only read')
    
    @property
    def IsShade(self) -> bool:
        return hasattr(self, 'Shade')
    
    @IsShade.setter
    def IsShade(self, value) -> None:
        raise AttributeError('IsShade property cannot be set, only read')
    
    # Event Handlers +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    # Private Methods ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    def __ConnectionStatus(self, command, value, qualifier):
        Logger.Log('{} {} Callback; Value: {}; Qualifier {}'.format(self.Name, command, value, qualifier))
        if value != self.ConnectionStatus:
            self.ConnectionStatus = value
            self.LastStatusChange = datetime.now()
    
    # Public Methods +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    def GetQualifierList(self, subscription):
        qualList = [None]
        if 'qualifier' in subscription and subscription['qualifier'] is not None:
            if isinstance(subscription['qualifier'], list):
                for q in subscription['qualifier']:
                    if not isinstance(q, dict):
                        raise TypeError('Qualifier ({}) must be a dictionary'.format(q))
                qualList = subscription['qualifier']
            elif isinstance(subscription['qualifier'], dict):
                qualList = [subscription['qualifier']]
            else:
                raise TypeError('Qualifier must be a dictionary')
        return qualList

    def AddSubscription(self, subscription, qualifier):
        if callable(subscription['callback']):
            if 'tag' in subscription:
                callbackFn = functools.partial(subscription['callback'], hardware=self, tag=subscription['tag'])
            else:
                callbackFn = functools.partial(subscription['callback'], hardware=self)
        elif isinstance(subscription['callback'], str) and hasattr(self.interface, subscription['callback']):
            if 'tag' in subscription:
                callbackFn = functools.partial(getattr(self.interface, subscription['callback']), hardware=self, tag=subscription['tag'])
            else:
                callbackFn = functools.partial(getattr(self.interface, subscription['callback']), hardware=self)
        else:
            raise TypeError('Callback ({}) must either be a callable or a string matching a name of an interface method.'.format(subscription['callback']))
                
        self.interface.SubscribeStatus(subscription['command'],
                                       qualifier,
                                       callbackFn)
    

## End Class Definitions -------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------

## End Function Definitions ----------------------------------------------------


