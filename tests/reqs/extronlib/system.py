import sys
TESTING = ('unittest' in sys.modules.keys())

from typing import Dict, Tuple, List, NamedTuple, Union, Callable, Any
from datetime import datetime
import re
import os
import extronlib.ui
import extronlib.interface

## CLASS DEFINITIONS +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
class Clock:
    WEEKDAYS = {'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3, 'Friday': 4, 'Saturday': 5, 'Sunday': 6}
    def __init__(self, Times: List[str], Days: List[str]=None, Function=None) -> None:
        self.Days = Days
        self.Function = Function
        self.State = 'enabled'
        self.Times = Times
        
    def Disable(self) -> None:
        self.State = 'disabled'
        
    def Enable(self) -> None:
        self.State = 'enabled'
        
    def SetDays(self, Days: List[str]):
        self.Days = Days
        
    def SetTimes(self, Times: List[str]):
        self.Times = Times

class Email:
    def __init__(self, smtpServer: str=None, port: int=None, username: str=None, password: str=None, sslEnabled: bool=None) -> None:
        self._smtpServer = smtpServer
        self._port = port
        self._username = username
        self._password = password
        self._sslEnabled = sslEnabled
        self._to = None
        self._cc = None
        self._from = 'no-reply@extron.com'
        self._subject = ''
        
    def Receiver(self, receiver: List[str]=None, cc: bool=False) -> None:
        if not cc:
            self._to = receiver
        else:
            self._cc = receiver
            
    def SendMessage(self, msg: str) -> None:
        pass
    
    def Sender(self, sender: str) -> None:
        self._from = sender
    
    def Subject(self, subject: str) -> None:
        self._subject = subject

class File:
    _pathroot = './tests/reqs/emFS/SFTP'
    _path = '/'
    
    def __init__(self, Filename: str, mode: str='r', encoding: str=None, newline: str=None) -> None:
        self.FileName = Filename
        
        re_str = r'[rwax]{1}\+?([bt]?)'
        re_match = re.match(re_str, mode)
        if not re_match:
            raise ValueError("Open mode ({}) is not a valid value".format(mode))

        if re_match.group(1) == '':
            self._binary = False
            self._mode = '{m}t'.format(m=mode)
        elif re_match.group(1) == 'b':
            self._binary = True
            self._mode = mode
        else:
            self._binary = False
            self._mode = mode
        
        if encoding != None:
            self._enc = encoding
        else:
            self._enc = 'ascii'
        self._new_line = newline
        
        if self.FileName.startswith('/'):
            self._file_object = open('{path}{file}'.format(path=self._pathroot, file=self.FileName),
                                     mode= self._mode,
                                     encoding= self._enc,
                                     newline= self._new_line)
        elif self.FileName.startswith('../'):
            pass
            # TODO: figure out going up a level when possible
        elif self.FileName.startswith('./'):
            self._file_object = open('{path}{file}'.format(path=self._get_path(), file=self.FileName[2:]),
                                     mode= self._mode,
                                     encoding= self._enc,
                                     newline= self._new_line)
        
    
    @classmethod
    def _get_path(cls) -> None:
        return cls._pathroot + cls._path
    
    @classmethod
    def ChangeDir(cls, path: str) -> None:
        if not path.startswith('/'):
            path = '/{p}'.format(p = path)
            
        if not path.endswith('/'):
            path = '{p}/'.format(p = path)
            
        cls._path = path
    
    @classmethod
    def DeleteDir(cls, path: str) -> None:
        if not path.startswith('/'):
            path = '/{p}'.format(p = path)
            
        if not path.endswith('/'):
            path = '{p}/'.format(p = path)
        os.rmdir(cls._pathroot+path)
    
    @classmethod
    def DeleteFile(cls, path: str) -> None:
        if not path.startswith('/'):
            path = '/{p}'.format(p = path)
        os.remove(cls._pathroot+path)
    
    @classmethod
    def Exists(cls, path: str) -> bool:
        if not path.startswith('/'):
            path = '/{p}'.format(p = path)
        fullpath = cls._pathroot+path
        #winpath = fullpath.replace('/','\\')
        #print(winpath)
        return os.path.exists(fullpath)
    
    @classmethod
    def GetCurrentDir(cls) -> str:
        return cls._path
    
    @classmethod
    def ListDir(cls, path: str=None) -> List[str]:
        if not path:
            path = cls._path
            
        if not path.startswith('/'):
            path = '/{p}'.format(p = path)
            
        if not path.endswith('/'):
            path = '{p}/'.format(p = path)
            
        os.listdir(cls._pathroot+path)
    
    @classmethod
    def MakeDir(cls, path: str) -> None:
        if not path.startswith('/'):
            path = '/{p}'.format(p = path)
            
        if not path.endswith('/'):
            path = '{p}/'.format(p = path)
            
        os.mkdir(cls._pathroot+path)
    
    @classmethod
    def RenameFile(cls, oldname, newname) -> None:
        os.rename(cls._get_path()+oldname, cls._get_path()+newname)
    
    def close(self) -> None:
        self._file_object.close()
    
    def read(self, size: int=-1) -> bytes:
        return self._file_object.read(size)
    
    def readline(self) -> bytes:
        return self._file_object.readline()
    
    def seek(self, offset, whence: int=0) -> None:
        if whence >= 0 and whence <= 2:
            self._file_object.seek(offset, whence)
        else:
            raise ValueError('Whence may only be 0, 1, or 2')
    
    def tell(self) -> int:
        return self._file_object.tell()
    
    def write(self, data: Union[str, bytes]) -> None:
        self._file_object.write(data)
    
    def writelines(self, seq: List[str]) -> None:
        self._file_object.writelines(seq)
        
class RFile:
    _pathroot = './tests/reqs/emFS/Restricted'
    _path = '/'
    
    def __init__(self, Filename: str, mode: str='r', encoding: str=None, newline: str=None) -> None:
        self.FileName = Filename
        
        re_str = r"[rwa]{1}\+?([bt]?)"
        re_match = re.match(re_str, mode)
        if not re_match:
            raise ValueError("Open mode is not a valid value")
        if re_match.group(1) == '':
            self._binary = False
            self._mode = '{m}t'.format(m=mode)
        elif re_match.group(1) == 'b':
            self._binary = True
            self._mode = mode
        else:
            self._binary = False
            self._mode = mode
        
        if encoding != None:
            self._enc = encoding
        else:
            self._enc = 'ascii'
        self._new_line = newline
        
        self._file_object = open('{path}{file}'.format(path=self._get_path(), file=self.FileName),
                  mode= self._mode,
                  encoding= self._enc,
                  newline= self._new_line)
        
    
    @classmethod
    def _get_path(cls) -> None:
        return cls._pathroot + cls._path
    
    @classmethod
    def ChangeDir(cls, path: str) -> None:
        if not path.startswith('/'):
            path = '/{p}'.format(p = path)
            
        if not path.endswith('/'):
            path = '{p}/'.format(p = path)
            
        cls._path = path
    
    @classmethod
    def DeleteDir(cls, path: str) -> None:
        if not path.startswith('/'):
            path = '/{p}'.format(p = path)
            
        if not path.endswith('/'):
            path = '{p}/'.format(p = path)
        os.rmdir(cls._pathroot+path)
    
    @classmethod
    def DeleteFile(cls, path: str) -> None:
        if not path.startswith('/'):
            path = '/{p}'.format(p = path)
        os.remove(cls._pathroot+path)
    
    @classmethod
    def Exists(cls, path: str) -> bool:
        os.path.exists(cls._pathroot+path)
    
    @classmethod
    def GetCurrentDir(cls) -> str:
        return cls._path
    
    @classmethod
    def ListDir(cls, path: str=None) -> List[str]:
        if not path:
            path = cls._path
            
        if not path.startswith('/'):
            path = '/{p}'.format(p = path)
            
        if not path.endswith('/'):
            path = '{p}/'.format(p = path)
            
        os.listdir(cls._pathroot+path)
    
    @classmethod
    def MakeDir(cls, path: str) -> None:
        if not path.startswith('/'):
            path = '/{p}'.format(p = path)
            
        if not path.endswith('/'):
            path = '{p}/'.format(p = path)
            
        os.mkdir(cls._pathroot+path)
    
    @classmethod
    def RenameFile(cls, oldname, newname) -> None:
        os.rename(cls._get_path()+oldname, cls._get_path()+newname)
    
    def close(self) -> None:
        self._file_object.close()
    
    def read(self, size: int=-1) -> bytes:
        return self._file_object.read(size)
    
    def readline(self) -> bytes:
        return self._file_object.readline()
    
    def seek(self, offset, whence: int=0) -> None:
        if whence >= 0 and whence <= 2:
            self._file_object.seek(offset, whence)
        else:
            raise ValueError('Whence may only be 0, 1, or 2')
    
    def tell(self) -> int:
        return self._file_object.tell()
    
    def write(self, data: Union[str, bytes]) -> None:
        self._file_object.write(data)
    
    def writelines(self, seq: List[str]) -> None:
        self._file_object.writelines(seq)
        
class MESet:
    def __init__(self, Objects: List[Union[extronlib.ui.Button,
                                           extronlib.interface.DigitalIOInterface,
                                           extronlib.interface.FlexIOInterface,
                                           extronlib.interface.PoEInterface,
                                           extronlib.interface.RelayInterface,
                                           extronlib.interface.SWACReceptacleInterface,
                                           extronlib.interface.SWPowerInterface,
                                           extronlib.interface.TallyInterface]]) -> None:
        self.Objects = Objects
        self._activeIndex = 0
        self._states = []
        for o in self.Objects:
            self._states.append([0,1])

    def Append(self, obj: Union[extronlib.ui.Button,
                                extronlib.interface.DigitalIOInterface,
                                extronlib.interface.FlexIOInterface,
                                extronlib.interface.PoEInterface,
                                extronlib.interface.RelayInterface,
                                extronlib.interface.SWACReceptacleInterface,
                                extronlib.interface.SWPowerInterface,
                                extronlib.interface.TallyInterface]) -> None:
        self.Objects.append(obj)
        self._states.append([0, 1])
        
    def GetCurrent(self) -> Union[extronlib.ui.Button,
                                    extronlib.interface.DigitalIOInterface,
                                    extronlib.interface.FlexIOInterface,
                                    extronlib.interface.PoEInterface,
                                    extronlib.interface.RelayInterface,
                                    extronlib.interface.SWACReceptacleInterface,
                                    extronlib.interface.SWPowerInterface,
                                    extronlib.interface.TallyInterface]:
        if self._activeIndex is None:
            return None
        else:
            return self.Objects[self._activeIndex]
    
    def Remove(self, obj: Union[extronlib.ui.Button,
                                extronlib.interface.DigitalIOInterface,
                                extronlib.interface.FlexIOInterface,
                                extronlib.interface.PoEInterface,
                                extronlib.interface.RelayInterface,
                                extronlib.interface.SWACReceptacleInterface,
                                extronlib.interface.SWPowerInterface,
                                extronlib.interface.TallyInterface]) -> None:
        if type(obj) == 'int':
            self.Objects.pop(obj)
            self._states.pop(obj)
        else:
            index = self.Objects.index(obj)
            self.Objects.remove(obj)
            self._states.pop(index)
        
    def SetCurrent(self, obj: Union[extronlib.ui.Button,
                                    extronlib.interface.DigitalIOInterface,
                                    extronlib.interface.FlexIOInterface,
                                    extronlib.interface.PoEInterface,
                                    extronlib.interface.RelayInterface,
                                    extronlib.interface.SWACReceptacleInterface,
                                    extronlib.interface.SWPowerInterface,
                                    extronlib.interface.TallyInterface]) -> None:
        if obj is None:
            self._activeIndex = None
        elif type(obj) is int:
            self._activeIndex = obj
        else:
            self._activeIndex = self.Objects.index(obj)
        
    def SetStates(self,
                  obj: Union[extronlib.ui.Button,
                             extronlib.interface.DigitalIOInterface,
                             extronlib.interface.FlexIOInterface,
                             extronlib.interface.PoEInterface,
                             extronlib.interface.RelayInterface,
                             extronlib.interface.SWACReceptacleInterface,
                             extronlib.interface.SWPowerInterface,
                             extronlib.interface.TallyInterface],
                  offState: int,
                  onState: int) -> None:
        if type(obj) == 'int':
            self._states[obj][0] = offState
            self._states[obj][1] = onState
        else:
            index = self.Objects.index(obj)
            self._states[index][0] = offState
            self._states[index][1] = onState

class Timer:
    def __init__(self, Interval: float, Function: Callable=None) -> None:
        """The Timer class allows the user to execute programmed actions on a periodic time schedule.

        ```
        @Timer(5)
        def handlePolling(timer, count):
            mainProjector.Send('get Power\r')

            if not count % 20:
                mainProjector.Send('get LampHours\r')
        ```
        
        Note
            - The handler (Function) must accept exactly two parameters, which are the Timer that called it and the Count.
            - If the handler (Function) has not finished by the time the Interval has expired, Function will not be called and Count will not be incremented (i.e. that interval will be skipped).
            - In addition to being used as a decorator, Timer can be named and modified.

        Parameters:	
            - Interval (float) – How often to call the handler in seconds (minimum interval is 0.1s).
            - Function (function) – Handler function to execute each Interval.
        """
        ## Untracked Events
        # StateChanged
        
        self.Count = 0
        self.Function = Function
        self.Interval = Interval
        self.State = 'Running'
        
        def timer_wrapper(func=self.Function):
            func(Timer = self, Count = self.Count)
        
    def Change(self, Interval: float) -> None:
        """Set a new Interval value for future events in this instance.

        Parameters:	Interval (float) – How often to call the handler in seconds.
        ```
        @event(buttonObject, 'Pressed')
        def buttonObjectHandler(button, state):
            DoSomething()
            PollingTimer.Change(60)
        ```
        """
        self.Interval = Interval
        
    def Pause(self) -> None:
        """Pause the timer (i.e. stop calling the Function).

        Note - Does not reset the timer or the Count.

        ```
        @event(mainProjector, 'Offline')
        def handleOfflineEvent(interface, state):
            PollingTimer.Pause()
        ```
        """
        self.State = 'Paused'
        
    def Restart(self) -> None:
        """Restarts the timer – resets the Count and executes the Function in Interval seconds.

        ```
        @event(buttonObject, 'Pressed')
        def buttonObjectHandler(button, state):
            DoSomething()
            PollingTimer.Restart()
        ```
        """
        self.State = 'Running'
        self.Count = 0
        
    def Resume(self) -> None:
        """Resume the timer after being paused or stopped.

        ```
        @event(mainProjector, 'Online')
        def handleOnlineEvent(interface, state):
            PollingTimer.Resume()
        ```
        """
        self.State = 'Running'
        
    def Stop(self) -> None:
        """Stop the timer.

        Note - Resets the timer and the Count.

        ```
        @event(mainProjector, 'Online')
        def handleOfflineEvent(interface, state):
            PollingTimer.Stop()
        ```
        """
        self.State = 'Stopped'
        self.Count = 0

# class Wait:
#     def __init__(self, Time: float, Function: Callable=None) -> None:
#         """The wait class allows the user to execute programmed actions after a desired delay without blocking other processor activity.

#         ---
#         ```
#         @event(PowerOn, 'Pressed')
#         def HandlePowerButton(button, state):
#             mainProjector.Send('Power=On\r')
#             @Wait(30)
#             def CheckPowerState():
#                 mainProjector.Send('get Power\r')
#         ```
#         ---

#         In addition to being used as a one-shot (decorator), Wait can be named and reusable.

#         Parameters:	
#             - Time (float) – Expiration time of the wait in seconds
#             - Function (function) – Code to execute when Time expires
#         ---
        
#         ```
#         closeWait = None    # Delay to hide Setup Page

#         @event(ShowSetup, 'Released')
#         def handleShowSetup(button, state):
#             global closeWait
#             def CloseSetupPage():
#                 ConfRoomWall.ShowPage('Main')
#             closeWait = Wait(60, CloseSetupPage)
#             ConfRoomWall.ShowPage('Setup')
#         ```
#         """
        
#         self.Function = Function
#         self.Time = Time
#         self.Count = 0 # dummy data
#         self._currentTime = Time
    
#         def wait_wrapper(func=self.Function):
#             print(self.Time)
#             print(self.Count)
#             func(Time = self.Time, Count = self.Count)
            
#         self._wait_wrapper = wait_wrapper
            
#     def __call__(self, *args: Any, **kwds: Any) -> Any:
#         self._wait_wrapper()
            
#     def Add(self, Time: float) -> None:
#         """Add time to current interval.

#         Note - Add() does not modify Time.

#         Parameters:	Time (float) – Time in seconds

#         ```
#         QueryDelay = Wait(3)

#         def ErrorRecieved():    # Called by received data handler
#             QueryDelay.Add(1)
#         ```
#         """
#         self._currentTime = self._currentTime + Time
        
#     def Cancel(self) -> None:
#         """Stop Function from executing when the Time expires.

#         ```
#         @event(CloseSetup, 'Released')
#         def CloseSetup(button, state):
#             global closeWait
#             if closeWait:
#                 closeWait.Cancel()
#                 closeWait = None
#             ConfRoomWall.ShowPage('Main')
#         ```
#         """
#         self._currentTime = 0
        
#     def Change(self, Time: float) -> None:
#         """Set a new Time value for current and subsequent runs of this instance.

#         Note - Change() will modify Time.

#         Parameters:	Time (float) – Time in seconds

#         ```
#         @event(buttonObject, 'Pressed')
#         def buttonObjectHandler(button, state):
#             DoSomething()
#             closeWait.Change(60)
#         ```
#         """
#         self.Time = Time
        
#     def Restart(self) -> None:
#         """Restarts the Wait (i.e. executes the Function in Time seconds). If the Wait is active, Restart() cancels that Wait before starting a new one.

#         ```
#         @event(buttonObject, 'Pressed')
#         def buttonObjectHandler(button, state):
#             DoSomething()
#             closeWait.Restart()
#         ```
#         """
#         self._currentTime = self.Time
    
import time, numbers, extronlib.services.WaitService as _ext3969ron__WaitService, threading as _ext3969ron__threading, logging as _ext3969ron__logging #, eup.services.Const as _ext3969ron__Const
import sys, functools
TESTING = ('unittest' in sys.modules.keys())

class Wait:

    def __init__(self, Time, Function=None):
        if TESTING:
            if Function is not None and not callable(Function):
                raise TypeError('Function parameter is not a callable object')
            if not isinstance(Time, numbers.Real) or Time < 0:
                raise TypeError('Invalid Time Type')
            # @functools.wraps(Function)
            # def wrapper(*args, **kwargs):
            #     Function(*args, **kwargs)
                
            # self.wrapper = wrapper
        else:
            if Function is not None and not callable(Function):
                raise TypeError('Function parameter is not a callable object')
            if not isinstance(Time, numbers.Real) or Time < 0:
                _ext3969ron__logging.error('Wrong Time Type')
                raise TypeError('Invalid Time Type')
            self.expireSeconds = Time
            self.currentExpireTime = time.monotonic() + self.expireSeconds
            self.expireCb = None
            self.args = None
            self.rlock = _ext3969ron__threading.RLock()
            self.name = self.__class__.__name__
            self.state = ''
            if Function:
                self.name += '.' + Function.__name__
                self.expireCb = Function
                self._Wait__add()

    @classmethod
    def mro(cls):
        raise NotImplementedError()

    def __call__(self, Function):
        if TESTING:
            return Function
        else:
            self.name += '.' + Function.__name__
            self.expireCb = Function
            self._Wait__add()
            return Function

    def __add(self):
        with self.rlock:
            _ext3969ron__WaitService.AddWaitFunction(self._Wait__callback, self.currentExpireTime, name=self.name)

    def __callback(self):
        with self.rlock:
            try:
                self.expireCb()
            except:
                _ext3969ron__logging.exception('Failed to run wait callback function: ' + self.name)

    def Restart(self):
        with self.rlock:
            self.currentExpireTime = time.monotonic() + self.expireSeconds
            if not _ext3969ron__WaitService.ChgIntervalFunction(self._Wait__callback, self.currentExpireTime):
                self._Wait__add()

    def Cancel(self):
        with self.rlock:
            _ext3969ron__WaitService.DeleteWaitFunction(self._Wait__callback)

    def Add(self, Time):
        if Time < 0:
            return False
        with self.rlock:
            self.currentExpireTime += Time
            return _ext3969ron__WaitService.ChgIntervalFunction(self._Wait__callback, self.currentExpireTime)

    def Change(self, Time):
        with self.rlock:
            self.expireSeconds = Time
            self.currentExpireTime = time.monotonic() + self.expireSeconds
            return _ext3969ron__WaitService.ChgIntervalFunction(self._Wait__callback, self.currentExpireTime)

    @property
    def Time(self):
        return self.expireSeconds

    @property
    def Function(self):
        return self.expireCb

    @Function.setter
    def Function(self, Function):
        if self.expireCb:
            raise RuntimeError('{0} is set to this timer already'.format(self.expireCb))
        else:
            self.name += '.' + Function.__name__
            self.expireCb = Function
    
## +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
##
## SSL METHODS -----------------------------------------------------------------
import ssl

def GetUnverifiedContext() -> ssl.SSLContext:
    """Python 3.4.3 changed the default behavior of the stdlib http clients. They will now verify that “the server presents a certificate which is signed by a CA in the platform trust store and whose hostname matches the hostname being requested by default”. This method returns an unverified context for use when a valid certificate is impossible.

    Returns:	unverified context object compatible with stdlib http clients.
    Return type:	ssl.SSLContext

    ---
    
    ```
    import urllib.request
    from extronlib.system import GetUnverifiedContext

    # This disables all verification
    context = GetUnverifiedContext()

    urllib.request.urlopen("https://invalid-cert", context=context)
    ```
    
    ---

    ***Warning*** - This is a potential security risk. It should only be used when a secure solution is impossible. GetSSLContext should be used whenever possible.
    """
    context = ssl.SSLContext()
    context.verify_mode = ssl.CERT_OPTIONAL
    context.load_default_certs()
    return context

def GetSSLContext(alias: str) -> ssl.SSLContext:
    """Retrieve a Certificate Authority certificate from the Security Store and use it to create an SSL context usable with standard Python http clients.

    Parameters:	alias (string) – name of the CA certificate as it appears in the Security Store.
    Returns:	an SSL context object compatible with stdlib http clients.
    Return type:	ssl.SSLContext

    ---
    
    ```
    import urllib.request
    from extronlib.system import GetSSLContext

    context = GetSSLContext('yourcert')

    urllib.request.urlopen("https://www.example.com", context=context)
    ```
    """
    context = ssl.SSLContext()
    context.verify_mode = ssl.CERT_REQUIRED
    context.load_default_certs()
    
    certs = context.get_ca_certs()
    for c in certs:
        if alias == c['subject'][1][0][1]:
            return context
    raise Exception('CA Cert Alias not found')

## -----------------------------------------------------------------------------
##
## TIME METHODS ----------------------------------------------------------------
from collections import namedtuple
_ntp_server = ''
_TZTuple = namedtuple('_TZTuple', ['id', 'description', 'MSid'])
_tz = _TZTuple('CST','(UTC-06:00/UTC-05:00) Central Time','Central Standard Time')
_tz_list = \
    [
        _TZTuple('GMT-12','(UTC-12:00)','Dateline Standard Time'),
        _TZTuple('GMT-11','(UTC-11:00)','UTC-11'),
        _TZTuple('GMT-10','(UTC-10:00)','Aleutian Standard Time'),
        _TZTuple('HST','(UTC-10:00) Hawaii Time','Hawaiian Standard Time'),
        _TZTuple('MIT','(UTC-09:30) Marquesas Islands Time','Marquesas Standard Time'),
        _TZTuple('GMT-9','(UTC-09:00)','UTC-09'),
        _TZTuple('AKST','(UTC-09:00/UTC-08:00) Alaska Time','Alaskan Standard Time'),
        _TZTuple('GIT','(UTC-09:00) Gambier Islands Time','UTC-09'),
        _TZTuple('GMT-8','(UTC-08:00)','UTC-08'),
        _TZTuple('PST','(UTC-08:00/UTC-07:00) Pacific Time','Pacific Standard Time'),
        _TZTuple('GMT-7','(UTC-07:00)','Mountain Standard Time'),
        _TZTuple('AZT','(UTC-07:00) Arizona','US Mountain Standard Time'),
        _TZTuple('MST','(UTC-07:00/UTC-06:00) Mountain Time','Mountain Standard Time'),
        _TZTuple('GMT-6','(UTC-06:00)','Central America Standard Time'),
        _TZTuple('CST','(UTC-06:00/UTC-05:00) Central Time','Central Standard Time'),
        _TZTuple('GMT-5','(UTC-05:00)','Eastern Standard Time'),
        _TZTuple('PET','(UTC-05:00) Peru Time','SA Pacific Standard Time'),
        _TZTuple('COT','(UTC-05:00) Columbia Time','SA Pacific Standard Time'),
        _TZTuple('EST','(UTC-05:00/UTC-04:00) Eastern Time','Eastern Standard Time'),
        _TZTuple('VET', '(UTC-04:00) Venezuela Time', 'Venezuela Standard Time'),
        _TZTuple('GMT-4', '(UTC-04:00)', 'Atlantic Standard Time'),
        _TZTuple('BOT', '(UTC-04:00) Bolivia Time', 'SA Western Standard Time'),
        _TZTuple('AST', '(UTC-04:00/UTC-03:00) Atlantic Time', 'Atlantic Standard Time'),
        _TZTuple('NT', '(UTC-03:30/UTC-02:30) Newfoundland Time', 'Newfoundland Standard Time'),
        _TZTuple('GMT-3', '(UTC-03:00)', 'SA Eastern Standard Time'),
        _TZTuple('ART', '(UTC-03:00) Argentina Time', 'Argentina Standard Time'),
        _TZTuple('UYT', '(UTC-03:00) Uruguay Time', 'Argentina Standard Time'),
        _TZTuple('BRT', '(UTC-03:00) Brasilia Time', 'E. South America Standard Time'),
        _TZTuple('CLT', '(UTC-03:00/UTC-04:00) Chile Time', 'Magallanes Standard Time'),
        _TZTuple('GMT-2', '(UTC-02:00)', 'UTC-02'),
        _TZTuple('GMT-1', '(UTC-01:00)', 'Cape Verde Standard Time'),
        _TZTuple('AZOST', '(UTC-01:00/UTC+00:00) Azores Time', 'Azores Standard Time'),
        _TZTuple('GMT+0', '(UTC+00:00)', 'GMT Standard Time'),
        _TZTuple('WET', '(UTC+00:00/UTC+01:00) Western European Time', 'W. Europe Standard Time'),
        _TZTuple('GMT+1', '(UTC+01:00)', 'Central Europe Standard Time'),
        _TZTuple('CET', '(UTC+01:00/UTC+02:00) Central European Time', 'Central European Standard Time'),
        _TZTuple('WAT', '(UTC+01:00) West Africa Time', 'W. Central Africa Standard Time'),
        _TZTuple('GMT+2', '(UTC+02:00)', 'E. Europe Standard Time'),
        _TZTuple('EET', '(UTC+02:00/UTC+03:00) Eastern European Time', 'E. Europe Standard Time'),
        _TZTuple('CAT', '(UTC+02:00) Central Africa Time', 'W. Central Africa Standard Time'),
        _TZTuple('GMT+3', '(UTC+03:00)', 'Russian Standard Time'),
        _TZTuple('FET', '(UTC+03:00) Further Eastern European Time', 'Further Eastern European Time'),
        _TZTuple('EAT', '(UTC+03:00) Eastern Africa Time', 'E. Africa Standard Time'),
        _TZTuple('MSK', '(UTC+03:00) Moscow Time', 'Russian Standard Time'),
        _TZTuple('GMT+4', '(UTC+04:00)', 'Russia Time Zone 3'),
        _TZTuple('AFT', '(UTC+04:30) Afghanistan Time', 'Afghanistan Standard Time'),
        _TZTuple('GMT+5', '(UTC+05:00)', 'West Asia Standard Time'),
        _TZTuple('MSK+2', '(UTC+05:00) Yekaterinburg', 'Ekaterinburg Standard Time'),
        _TZTuple('IST', '(UTC+05:30) India Time', 'India Standard Time'),
        _TZTuple('NPT', '(UTC+05:45) Nepal Time', 'Nepal Standard Time'),
        _TZTuple('GMT+6', '(UTC+06:00)', 'Central Asia Standard Time'),
        _TZTuple('MSK+3', '(UTC+06:00) Omsk', 'Omsk Standard Time'),
        _TZTuple('GMT+7', '(UTC+07:00)', 'SE Asia Standard Time'),
        _TZTuple('MSK+4', '(UTC+07:00) Krasnoyarsk', 'North Asia Standard Time'),
        _TZTuple('THA', '(UTC+07:00) Thailand Time', 'SE Asia Standard Time'),
        _TZTuple('GMT+8', '(UTC+08:00)', 'North Asia East Standard Time'),
        _TZTuple('HKT', '(UTC+08:00) Hong Kong Time', 'China Standard Time'),
        _TZTuple('AWST', '(UTC+08:00) Australia Western Time', 'W. Australia Standard Time'),
        _TZTuple('CT', '(UTC+08:00) China Time', 'China Standard Time'),
        _TZTuple('MSK+5', '(UTC+08:00) Irkutsk', 'North Asia East Standard Time'),
        _TZTuple('GMT+9', '(UTC+09:00)', 'Transbaikal Standard Time'),
        _TZTuple('KST', '(UTC+09:00) Korea Time', 'Korea Standard Time'),
        _TZTuple('JST', '(UTC+09:00) Japan Time', 'Tokyo Standard Time'),
        _TZTuple('MSK+6', '(UTC+09:00) Yakutsk', 'Yakutsk Standard Time'),
        _TZTuple('ACST', '(UTC+09:30) Australia Central Time', 'Cen. Australia Standard Time'),
        _TZTuple('ACST+D', '(UTC+09:30) Australia Central Time (DST observed)', 'AUS Central Standard Time'),
        _TZTuple('GMT+10', '(UTC+10:00)', 'West Pacific Standard Time'),
        _TZTuple('AEST', '(UTC+10:00) Australia Eastern Time', 'E. Australia Standard Time'),
        _TZTuple('AEST+D', '(UTC+10:00) Australia Eastern Time (DST observed)', 'AUS Eastern Standard Time'),
        _TZTuple('MSK+7', '(UTC+10:00) Vladivostok', 'Vladivostok Standard Time'),
        _TZTuple('LHST', '(UTC+10:30/UTC+11:00) Lord Howe Time', 'Lord Howe Standard Time'),
        _TZTuple('GMT+11', '(UTC+11:00)', 'Central Pacific Standard Time'),
        _TZTuple('MSK+8', '(UTC+11:00) Magadan', 'Magadan Standard Time'),
        _TZTuple('NFT', '(UTC+12:00/UTC+11:00) Norfolk Time', 'Norfolk Standard Time'),
        _TZTuple('GMT+12', '(UTC+12:00)', 'UTC+12'),
        _TZTuple('NZST', '(UTC+12:00/UTC+13:00) New Zealand Time', 'New Zealand Standard Time'),
        _TZTuple('CHAST', '(UTC+12:45/UTC+13:45) Chatham Time', 'Chatham Islands Standard Time'),
        _TZTuple('GMT+13', '(UTC+13:00)', 'UTC+13'),
        _TZTuple('PHOT', '(UTC+13:00) Phoenix Islands Time', 'UTC+13'),
        _TZTuple('SST', '(UTC+13:00/UTC+14:00) Samoa Time', 'Samoa Standard Time'),
        _TZTuple('GMT+14', '(UTC+14:00)', 'Line Islands Standard Time'),
        _TZTuple('LINT', '(UTC+14:00) Line Islands Time', 'Line Islands Standard Time')
    ]

_system_time = datetime.now() # add a timezone to this

def SetAutomaticTime(Server: str) -> None:
    """Turn on NTP time synchronization using Server as the time source.

    Parameters:	Server (string) – the NTP server to synchronize with
    New in version 1.1.

    ```
    SetAutomaticTime('time.example.com')
    ```
    """
    _ntp_server = Server
    
def SetManualTime(DateAndTime: datetime) -> None:
    """Change the system time. This will turn off NTP synchronization if it is on.

    Parameters:	DateAndTime (datetime) – the new system date and time
    
    New in version 1.1.

    ```
    from datetime import datetime

    # Turn off NTP sync but keep the current system time.
    SetManualTime(datetime.now())

    # Set system time to noon on January 1, 2020
    dt = datetime(2020, 1, 1, 12, 0, 0)
    SetManualTime(dt)
    ```
    """
    _system_time = DateAndTime
    
def GetCurrentTimezone() -> NamedTuple:
    """Returns:	the current time zone of the primary controller
    Return type:	namedtuple
    The returned namedtuple contains three pieces of string data: the time zone id, the time zone description, and MSid which contains a Microsoft-compatible time zone identifier.

    New in version 1.1.
    """
    return _tz

def GetTimezoneList() -> List[NamedTuple]:
    """Returns:	all time zones supported by the system
    Return type:	list of namedtuples

    Each item in the returned list is a namedtuple that contains three pieces of string data: the time zone id, the time zone description, and MSid which contains a Microsoft-compatible time zone identifier.

    New in version 1.1.

    ```
    for zone in GetTimezoneList():
        print(zone.id + ', ' + zone.description)
    ```    
    """
    return _tz_list

def SetTimeZone(id: str) -> None:
    """Change the system time zone. Time zone affects Daylight Saving Time behavior and is used to calculate time of day when NTP time synchronization is turned on.

    Parameters:	id (string) – The new system time zone identifier. Use an item returned by GetTimezoneList to get the time zone id for this parameter.

    New in version 1.1.

    ```
    # Set the system time zone to 'Pacific'.
    for zone in GetTimezoneList():
        if 'Pacific' in zone.description:
            SetTimeZone(zone.id)
            break
    ```        
    """
    for tz in _tz_list:
        if id == tz.id:
            _tz = tz
            return None
    raise LookupError('Timezone with id ({}) not found in available Timezones list'.format(id))

## -----------------------------------------------------------------------------
##
## NETWORK METHODS -------------------------------------------------------------
import subprocess

def Ping(hostname: str='localhost', count: int=5) -> Tuple[int, int, float]:
    """Ping is a network administration utility that’s used to test reachablilty of a remote network host. It achieves this by measuring the round-trip time of messages sent to and echoed back by the remote host.

    This function sends count pings from the control processor and and returns the result in a tuple: (# of successful pings, # of failed pings, avg. round-trip time)

    Parameters:	
        - hostname (string) – IP address or hostname to ping.
        - count (int) – how many times to ping.

    Returns: tuple (# of successes, # of failures, avg. time)

    Return type: (int, int, float)
    """
    ping = subprocess.getoutput('ping -n {c} {h}'.format(c = count, h = hostname))
    # successes, # failure, avg time
    reSucc = r"Received = (\d+)"
    re_match_Succ = re.match(reSucc, ping)
    Succ = int(re_match_Succ.group(1))
    reFail = r"Lost = (\d+)"
    re_match_Fail = re.match(reFail, ping)
    Fail = int(re_match_Fail.group(1))
    reAvg = r"Average = (\d+)ms"
    re_match_Avg = re.match(reAvg, ping)
    Avg = float(re_match_Avg.group(1))
    return (Succ, Fail, Avg)
    
import struct, socket
def WakeOnLan(macAddress: str, port: int=9) -> None:
    """Wake-on-LAN is an computer networking standard that allows a computer to be awakened by a network message. The network message, ‘Magic Packet’, is sent out through UDP broadcast, port 9.

    Parameters:	
        - macAddress (string) – Target device’s MAC address. The format is six groups of two hex digits, separated by hyphens ('01-23-45-67-ab-cd', e.g.).
        - port (int) – Port on which target device is listening.
    
    Note - Typical ports for WakeOnLan are 0, 7 and 9.
    """
    # Construct 6 byte hardware address
    add_oct = macAddress.split('-') # extronlib expects "-" separators
    if len(add_oct) != 6:
        raise ValueError("MAC Address must be provided in six groups of two hex digits, separated by hyphens ('01-23-45-67-ab-cd', e.g.)")
    hwa = struct.pack('BBBBBB', int(add_oct[0],16),
        int(add_oct[1],16),
        int(add_oct[2],16),
        int(add_oct[3],16),
        int(add_oct[4],16),
        int(add_oct[5],16))

    # Build magic packet

    msg = '\xff' * 6 + hwa * 16

    # Send packet to broadcast address using UDP port 9 or provided port

    soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    soc.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    broadcast = ['127.0.0.1']
    for i in broadcast:
        soc.sendto(msg,(i,port))
    soc.close()

## -----------------------------------------------------------------------------
##
## OTHER METHODS ---------------------------------------------------------------

def GetSystemUpTime() -> float:
    """Returns:	system up time in seconds
    Return type:	float
    """
    return 1867.2022

_ProgramLog = ''
def ProgramLog(Entry: str, Severity: str = 'error') -> None:
    """Write entry to program log file.

    Parameters:	
        - Entry (string) – the message to enter into the log
        - Severity (string) – indicates the severity to the log viewer. ('info', 'warning', or 'error')
    
    Note - ProgramLog also generates a trace message.

    ```
    ProgramLog('Projector lamp hours > 3000.', 'warning')
    ```
    """
    global _ProgramLog
    
    dt = datetime.now()
    if Severity == 'error':
        LogStatement = '[{t}] ERROR - {e}\n'.format(t = dt.isoformat(), e=Entry)
    elif Severity == 'warning':
        LogStatement = '[{t}] WARNING - {e}\n'.format(t = dt.isoformat(), e=Entry)
    elif Severity == 'info':
        LogStatement = '[{t}] INFO - {e}\n'.format(t = dt.isoformat(), e=Entry)
    else:
        raise ValueError("Severity must be either 'error', 'warning', or 'info'")

    _ProgramLog += LogStatement
    if TESTING:
        log =  open('.\TEST_LOG.log', 'at')
        log.write(LogStatement)
        log.close()
    else:
        print(LogStatement)
    
def _ReadProgramLog():
    global _ProgramLog
    return _ProgramLog

def _ClearProgramLog():
    global _ProgramLog
    _ProgramLog = ''

def SaveProgramLog(path: Union[File, str]=None) -> None:
    """Save the ProgramLog to the specified User file system location.

    If no path is supplied, the Program Log will be saved in the root of the User file space with the name ‘ProgramLog YYYY-MM-DD HHMMSS.txt’ where ‘YYYY-MM-DD’ will be replaced with the current date and ‘HHMMSS’ will be replaced with the current 24-hour time including seconds.

    If path points to a directory, the log will be saved in that directory using the file name pattern above.

    The file will be overwritten if it already exists.

    Parameters:	path (File or string) – The file path to save the log to.
    """
    global _ProgramLog
    if path == None:
        dt = datetime.now()
        path = 'ProgramLog {year}-{month}-{day} {hr}{min}{sec}.txt'.format(
            year = dt.year,
            month = dt.month,
            day = dt.day,
            hr = str(dt.hour).zfill(2),
            min = str(dt.minute).zfill(2),
            sec = str(dt.second).zfill(2)
        )
    
    if type(path) == 'str':
        f = File(path, 'w')
        f.write(_ProgramLog)
        f.close()
    else:
        path.write(_ProgramLog)
        

def RestartSystem() -> None:
    """Stops the main script running on the primary control processor only then starts it again.

    ```
    from extronlib.system import File, RestartSystem, SaveProgramLog
    from datetime import datetime

    # Save the ProgramLog for later inspection.
    dt = datetime.now()
    filename = 'ProgramLog {}.txt'.format(dt.strftime('%Y-%m-%d %H%M%S'))

    with File(filename, 'w') as f:
        SaveProgramLog(f)

    RestartSystem()
    ```
    """
    pass

## -----------------------------------------------------------------------------
