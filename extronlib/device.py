# This is a dummy module for unit testing extron control script code files

from typing import Dict, Tuple, List, Union

## CLASS DEFINITIONS +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class ProcessorDevice:
    def __init__(self, DeviceAlias: str, PartNumber: str=None) -> object:
        """This class provides a common interface to a TouchLink Control Adapter. The user can instantiate the class directly or create a subclass to add, remove, or alter behavior for different types of devices.

        Parameters:
            Host (UIDevice) - handle to Extron UIDevice to which the AdapterDevice is connected
            DeviceAlias (string) - Device Alias of the Extron device
        
        Ports on the TouchLink Control Adapter are instantiated and used in the same way as ports built into controllers but using the TouchLink Control Adapter as the Host parameter.
        """
        self.DeviceAlias = DeviceAlias
        if PartNumber == None:
            self.PartNumber = 'dummy Part Number'
        else:
            self.PartNumber = PartNumber
        
        ## Untracked events
        # CombinedCurrentChanged
        # CombinedLoadStateChanged
        # CombinedWattageChanged
        # ExecutiveModeChanged
        # Offline
        # Online
        
        self.CombinedCurrent = None
        self.CombinedLoadState = None
        self.CombinedWattage = None
        self.CurrentLoad = None # This will be removed in future CS releases
        self.ExecutiveMode = 0
        self.FirmwareVersion = 'dummy FW Version'
        self.Hostname = 'dummy Host Name'
        self.IPAddress = '127.0.0.1'
        self.MACAddress = '01:23:45:67:89:ab'
        self.ModelName = 'dummy Model Name'
        self.SerialNumber = 'dummySN'
        self.SystemSettings = \
            {
                'Network': {
                    'LAN': {
                        'DNSServers': ['192.168.1.1',],
                        'Gateway': '192.168.254.1',
                        'Hostname': self.Hostname,
                        'IPAddress': self.IPAddress,
                        'SubnetMask': '255.255.255.0',
                        'SearchDomains': ['extron.com',],
                    },
                    'AVLAN': {
                        'DHCPServer': 'Off',
                        'DNSServers': ['192.168.1.1',],
                        'Hostname': self.Hostname,
                        'IPAddress': '192.168.253.251',
                        'SubnetMask': '255.255.255.0',
                        'SearchDomains': ['extron.com',],
                    },
                },
                'MailServer': {
                    'IPAddress': '192.168.254.100',
                    'SMTPPort': 25,
                    'SSLEnabled': True,
                    'UserID': 'dummy Mail User',
                },
                'DateTime': {
                    'NTPSettings': {
                        'Enabled': True,
                        'Server': '192.168.254.101', 
                    },
                    'TimeZone': '(UTC-08:00/UTC-07:00) Pacific Time',
                },
                'ProgramInformation': {
                    'Author': 'dummyAuthor',
                    'DeviceName': 'dummy device name',
                    'FileLoaded': 'dummyGUI.gs',
                    'LastUpdated': '1/23/2016 9:08:29 AM',
                    'SoftwareVersion': 'dummySWVersion',
                }
            }
        self.UserUsage = (256, 1024)
        
        pass
        
class UIDevice:
    def __init__(self, DeviceAlias: str, PartNumber: str=None) -> object:
        """Entity to communicate with Extron Device featuring user interactive input.

        Parameters:	
            DeviceAlias (string) - Device Alias of the Extron device  
            PartNumber (string) - device’s part number  
            
        Note:
            DeviceAlias must be a valid device Device Alias of an Extron device in the system.  
            If the part number is provided, the device will trigger a warning message in the program log if it does not match the connected device.
        """
        self.DeviceAlias = DeviceAlias
        if PartNumber == None:
            self.PartNumber = 'dummy Part Number'
        else:
            self.PartNumber = PartNumber
        
        ### Untracked events
        # BrightnessChanged
        # HDCPStatusChanged
        # InactivityChanged
        # InputPresenceChanged
        # LidChanged
        # LightChanged
        # MotionDetected
        # Offline
        # Online
        # OverTemperatureChaged
        # OverTemperatureWarning
        # OverTemperatureWarningStateChanged
        # SleepChanged
        
        
        self.AmbientLightValue = 0
        self.AutoBrightness = False
        self.Brightness = 100
        self.DisplayState = 'On'
        self.DisplayTimerEnabled = False
        self.DisplayTimer = 180
        self.FirmwareVersion = 'dummy FW'
        self.Hostname = 'dummy hostname'
        self.IPAddress = '127.0.0.1'
        self.InactivityTime = 42 # this dummy data
        self.LidState = 'Open'
        self.LightDetectedState = 'Detected'
        self.LinkLicenses = []
        self.MACAddress = '01:23:45:67:89:ab'
        self.ModelName = 'dummy model name'
        self.MotionDecayTime = 10
        self.MotionState = 'Motion'
        self.OverTemperature = -25
        self.OverTemperatureWarningState = False
        self.SerialNumber = 'dummySN'
        self.SleepState = 'Awake'
        self.SleepTimerEnabled = True
        self.SleepTimer = 600
        self.UserUsage = (256, 1024)
        self.WakeOnMotion = True
        
        self._Input = 'HDMI'
        self._MuteStates = {
            'Master': 'Off',
            'Speaker': 'Off',
            'Line': 'Off',
            'Click': 'Off',
            'Sound': 'Off',
            'HDMI': 'Off',
            'XTP': 'Off'
        }
        self._Volumes = {
            'Master': 100,
            'Click': 100,
            'Sound': 100,
            'HDMI': 100,
            'XTP': 100
        }
        self._LEDs = {
            '65533': {
                "rate": 'Off',
                "state": 'Off'
            }
        }
        self._InactivityTimers = []
        
        self.SystemSettings = \
            {
                'Network': {
                    'LAN': {
                        'DNSServers': ['192.168.1.1',],
                        'Gateway': '192.168.254.1',
                        'Hostname': self.Hostname,
                        'IPAddress': self.IPAddress,
                        'SubnetMask': '255.255.255.0',
                        'SearchDomains': ['extron.com',],
                    },
                },
                'ProgramInformation': {
                    'Author': 'dummyAuthor',
                    'DeviceName': 'dummy device name',
                    'FileLoaded': 'dummyGUI.gs',
                    'LastUpdated': '1/23/2016 9:08:29 AM',
                    'SoftwareVersion': 'dummySWVersion',
                }
            }
        
    def Click(self, count: int=1, interval: float=None) -> None:
        """Play default buzzer sound on applicable device

        Parameters:	
            count (int) - number of buzzer sound to play
            interval (float) - time gap between the starts of consecutive buzzer sounds
            
        Note
            If count is greater than 1, interval must be provided.
        """
        if count > 1 and interval == None:
            raise Exception()
        pass
    
    def GetHDCPStatus(self, videoInput: str) -> bool:
        """Return the current HDCP Status for the given input.

        Parameters: videoInput (string) - input ('HDMI' or 'XTP')
        Returns: True or False
        Return type: bool
        """
        if videoInput != "XTP" and videoInput != "HDMI":
            raise Exception()
        return False
    
    def GetInputPresence(self, videoInput: str) -> bool:
        """Return the current input presence status for the given input.

        Parameters: videoInput (string) - input ('HDMI' or 'XTP')
        Returns: True or False
        Return type: bool
        """
        if videoInput != "XTP" and videoInput != "HDMI":
            raise Exception()
        return False
    
    def GetMute(self, name: str) -> str:
        """Get the mute state for the given channel

        The defined channel names are:
            'Master' - the master volume\n
            'Speaker' - the built-in speakers\n
            'Line' - the line out\n
            'Click' - button click volume\n
            'Sound' - sound track playback volume\n
            'HDMI' - HDMI input volume\n
            'XTP' - XTP input volume
            
        Parameters: name (string) - name of channel.
        Returns: mute state ('On' or 'Off')
        Return type: string
        """
        if name in self._MuteStates.keys():
            return self._MuteStates[name]
        else:
            raise LookupError()
    
    def GetVolume(self, name: str) -> int:
        """Return current volume level for the given channel

        The defined channel names are:
            'Master' - the master volume\n
            'Click' - button click volume\n
            'Sound' - sound track playback volume\n
            'HDMI' - HDMI input volume\n
            'XTP' - XTP input volume\n
        
        Parameters: name (string) - name of volume channel.
        Returns: volume level
        Return type: int
        """
        if name in self._Volumes.keys():
            return self._Volumes[name]
        else:
            raise LookupError()
        
    def HideAllPopups(self) -> None:
        """Dismiss all popup pages"""
        pass
    
    def HidePopup(self, popup: Union[int, str]) -> None:
        """Hide popup page

        Parameters:	popup (int, string) - popup page number or name
        """
        pass
    
    def HidePopupGroup(self, group: int) -> None:
        """Hide all popup pages in a popup group

        Parameters:	group (int) - popup group number
        """
        pass
    
    def PlaySound(self, filename: str) -> None:
        """Play a sound file identified by the filename

        Parameters:	filename (string) - name of sound file
        """
        pass
    
    def Reboot(self) -> None:
        """Performs a soft restart of this device - this is equivalent to rebooting a PC.
        """
        pass
    
    def SetAutoBrightness(self, state: Union[str, bool]) -> None:
        """Set auto brightness state

        Either 'On' or True turns on auto brightness. 'Off' or False turns off auto brightness.

        Parameters:	state (bool, string) - whether to enable auto brightness
        """
        if state == True or state == 'On':
            self.AutoBrightness = True
        elif state == False or state == 'Off':
            self.AutoBrightness = False
        else:
            raise ValueError('Invalid state provided')
            
    def SetBrightness(self, level: int) -> None:
        """Set LCD screen brightness level

        Parameters:	level (int) - brightness level from 0 ~ 100
        """
        if level >= 0 and level <= 100:
            self.Brightness = level
        else:
            raise ValueError('Brightness must be between 0 and 100')
        
    def SetDisplayTimer(self, state: Union[bool, str], timeout: int) -> None:
        """Enable/disable display timer

        Either 'On' or True enables display timer. 'Off' or False disables display timer.

        Parameters:
            state (bool, string) - whether to enable the display timer\n
            timeout (int) - time in seconds before turn off the display
        """
        if state == True or state == 'On':
            self.DisplayTimerEnabled = True
        elif state == False or state == 'Off':
            self.DisplayTimerEnabled = False
        else:
            raise ValueError('Invalid state provided')
        
        if timeout != None:
            self.DisplayTimer = timeout
            
    def SetInactivityTime(self, times: List[int]) -> None:
        """Set the inactivity times of the UIDevice. When each time expires, the InactivityChanged event will be triggered. All times are absolute.

        Parameters: times (list of ints) - list of times. Each time in whole seconds
        """
        self._InactivityTimers = times
        pass
        
    def SetInput(self, videoInput: str) -> None:
        """Sets the input. Inputs must be published for each device.

        Parameters:	videoInput (string) - input to select ('HDMI' or 'XTP')
        """
        if videoInput != "XTP" and videoInput != "HDMI":
            raise Exception()
        
        self._Input = videoInput
        
    def SetLEDBlinking(self, ledId: int, rate: str, stateList: List[str]) -> None:
        """Make the LED cycle, at ADA compliant rates, through each of the states provided.

        Rate - Frequency\n
        Slow - 0.5 Hz\n
        Medium - 1 Hz\n
        Fast - 2 Hz
        
        Note
            Using this function will blink in unison with other LEDs.

        Parameters:	
            ledId (int) - LED id\n
            rate (string) - ADA compliant blink rate. ('Slow', 'Medium', 'Fast')\n
            stateList (list of strings) - List of colors
        
        Note
            Available colors are Red, Green, and Off.
        """
        if str(ledId) not in self._LEDs.keys():
            raise ValueError('ID ({}) does not match available LED IDs'.format(ledId))
        if rate != 'Slow' and rate != 'Medium' and rate != 'Fast':
            raise ValueError('rate ({}) not defined'.format(rate))
        for s in stateList:
            if s != 'Red' and s != 'Green' and s != 'Off':
                raise ValueError('state ({}) not found'.format(s))
        
        self._LEDs[str(ledId)]['rate'] = rate
        self._LEDs[str(ledId)]['state'] = stateList
        
    def SetLEDState(self, ledId: int, state: str) -> None:
        """Drive the LED to the given color

        Parameters:	
            ledId (int) - LED id\n
            state (string) - LED color or ‘Off’.
            
        Note
            Available colors are Red, Green, and Off.
        """
        if str(ledId) not in self._LEDs.keys():
            raise ValueError('ID ({}) does not match available LED IDs'.format(ledId))
        if state != 'Red' and state != 'Green' and state != 'Off':
                raise ValueError('state ({}) not found'.format(state))
        self._LEDs[str(ledId)]['rate'] = 'Off'
        self._LEDs[str(ledId)]['state'] = state
        
    def SetMotionDecayTime(self, duration: float) -> None:
        """Set the period of time to trigger MotionDetected after last motion was detected.

        Parameters:	duration (float) - time in seconds (minimum/default value is 10)
        """
        if duration < 10:
            raise ValueError('Duration must be at least 10 seconds')
        
        self._MotionDecayTime = duration
        
    def SetMute(self, name: str, mute: str) -> None:
        """Set the mute state for the given channel

        The defined channel names are:
            'Master' - the master volume\n
            'Speaker' - the built-in speakers\n
            'Line' - the line out\n
            'Click' - button click volume\n
            'Sound' - sound track playback volume\n
            'HDMI' - HDMI input volume\n
            'XTP' - XTP input volume
        
        Parameters:	
            name (string) - name of channel.\n
            mute (string) - mute state ('On' or 'Off')
        """
        if name not in self._MuteStates.keys():
            raise LookupError('Name ({}) not found'.format(name))
        if mute != 'On' and mute != 'Off':
            raise ValueError('Mute can either be "On" or "Off"')
        
        self._MuteStates[name] = mute
        
    def SetSleepTimer(self, state: Union[bool, str], duration: int=None) -> None:
        """Enable/disable sleep timer. Either 'On' or True enables sleep timer. 'Off' or False disables sleep timer.

        Parameters:	
            state (bool, string) - whether to enable the sleep timer\n
            duration (int) - time in seconds to sleep
        """
        if state == True or state == 'On':
            self.SleepTimerEnabled = True
        elif state == False or state == 'Off':
            self.SleepTimerEnabled = False
        else:
            raise ValueError('Invalid state provided')
        
        if duration is None:
            self.SleepTimer = 0
        elif duration < 0:
            raise ValueError('Duration must be positive')
        else:
            self.SleepTimer = duration
        
    def SetVolume(self, name: str, level: int) -> None:
        """Adjust volume level for the given channel

        The defined channel names are:
            'Master' - the master volume\n
            'Click' - button click volume\n
            'Sound' - sound track playback volume\n
            'HDMI' - HDMI input volume\n
            'XTP' - XTP input volume
        
        Parameters:	
            name (string) - name of channel.\n
            level (int) - volume level 0 ~ 100
        """
        if name not in self._Volumes.keys():
            raise LookupError('Name ({}) not found'.format(name))
        if level < 0 or level > 100:
            raise ValueError('Level must be between 0 and 100')
        self._Volumes[name] = level
        
    def SetWakeOnMotion(self, state: Union[bool, str]) -> None:
        """Enable/disable wake on motion.

        Parameters:	state (bool, string) - True ('On') or False (‘Off’) to enable and disable wake on motion, respectively.
        """
        if state == True or state == 'On':
            self.WakeOnMotion = True
        elif state == False or state == 'Off':
            self.WakeOnMotion = False
        else:
            raise ValueError('Invalid state provided')
        
    def ShowPage(self, page: Union[int, str]) -> None:
        """Show page on the screen

        Parameters:	page (int, string) - absolute page number or name
        """
        pass
    
    def ShowPopup(self, page: Union[int, str], duration: float=0) -> None:
        """Display pop-up page for a period of time.

        Parameters:	
            popup (int, string) - pop-up page number or name\n
            duration (float) - duration (in seconds) the pop-up remains on the screen. 0 means forever.
        
        Note
            If a pop-up is already showing for a finite period of time, calling this method again with the same pop-up will replace the remaining period with the new period.
        """
        pass
    
    def Sleep(self) -> None:
        """Force the device to sleep immediately"""
        pass
    
    def StopSound(self) -> None:
        """Stop playing sound file"""
        pass
    
    def Wake(self) -> None:
        """Force the device to wake up immediately"""
        pass
    
class eBUSDevice:
    def __init__(self, Host: ProcessorDevice, DeviceAlias: str):
        """Defines common interface to Extron eBUS panels

        Parameters:	
            Host (ProcessorDevice) - handle to Extron ProcessorDevice to which the eBUSDevice is connected\n
            DeviceAlias (string) - Device Alias of the Extron device
        """
        self.DeviceAlias = DeviceAlias
        self.Host = Host
        
        ### Untracked events
        # InactivityChanged
        # Lid changed
        # Offline
        # Online
        # ReceiveResponse
        # SleepChanged
        
        
        self.ID = 8
        self.InactivityTime = 42
        self.LidState = 'Opened'
        self.ModelName = 'dummy Model name'
        self.PartNumber = 'dummy part number'
        self.SleepState = 'Awake'
        self.SleepTimer = 600
        self.SleepTimerEnabled = True
        
        self._MuteStates = {
            'Click': 'Off'
        }
    
    def Click(self, count: int=1, interval: int=None) -> None:
        """Play default buzzer sound on applicable device

        Parameters:	
            count (int) - number of buzzer sound to play\n
            interval (int) - time gap in millisecond between consecutive sounds
        
        Note
            If count is greater than 1, interval must be provided to indicate the time gap in ms between consecutive buzzer sounds.
        """
        if count > 1 and interval == None:
            raise Exception()
        pass
    
    def GetMute(self, name: str) -> str:
        """Get the mute state for the given channel

        The defined channel names are:
            'Click' - button click volume
        
        Parameters: name (string) - name of channel.
        Returns: mute state ('On' or 'Off')
        Return type: string
        """
        if name in self._MuteStates.keys():
            return self._MuteStates[name]
        else:
            raise LookupError()
        
    def Reboot(self) -> None:
        """Performs a soft restart of this device - this is equivalent to rebooting a PC."""
        pass
    
    def SendCommand(self, command, value: Union[int, Tuple[int]] = None) -> None:
        """Send command to eBUSDevice.

        Parameters:	
            command (string) - command name to issue\n
            value (int, tuple of ints) - command specific value to pass with commend
            
        Note
            For supported eBUS devices.\n
            See device documentation for supported commands.
        """
        pass
    
    def SetInactivityTime(self, times: List[int]) -> None:
        """Set the inactivity times of the eBUSDevice. When each time expires, the InactivityChanged event will be triggered. All times are absolute.

        Parameters:	times (list of ints) - list of times. Each time in whole seconds
        
        Note - Applies to EBP models only.
        """
        self._InactivityTimers = times
        pass
    
    def SetMute(self, name: str, mute: str) -> None:
        """Set the mute state for the given channel

        The defined channel names are:
            'Click' - button click volume
        
        Parameters:	
            name (string) - name of channel.\n
            mute (string) - mute state ('On' or 'Off')
        """
        if name not in self._MuteStates.keys():
            raise LookupError('Name ({}) not found'.format(name))
        if mute != 'On' and mute != 'Off':
            raise ValueError('Mute can either be "On" or "Off"')
        
        self._MuteStates[name] = mute
        
    def SetSleepTimer(self, state: Union[bool, str], duration: int=None) -> None:
        """Enable/disable sleep timer. Either 'On' or True enables sleep timer. 'Off' or False disables sleep timer.

        Parameters:	
            state (bool, string) - whether to enable the sleep timer\n
            duration (int) - time in seconds to sleep
        """
        if state == True or state == 'On':
            self.SleepTimerEnabled = True
        elif state == False or state == 'Off':
            self.SleepTimerEnabled = False
        else:
            raise ValueError('Invalid state provided')
        
        if int < 0:
            raise ValueError('Duration must be positive')
        
        self.SleepTimer = duration
        
    def Sleep(self) -> None:
        """Force the device to sleep immediately"""
        pass
    
    def Wake(self) -> None:
        """Force the device to wake up immediately"""
        pass
    
class SPDevice: 
    def __init__(self, DeviceAlias: str, PartNumber: str=None) -> None:
        """Defines a common interface to Extron Secure Platform Products

        Parameters:	
            DeviceAlias (string) - Device Alias of the Extron device\n
            PartNumber (string) - device’s part number
        
        Note
            DeviceAlias must be a valid device Device Alias of an Extron device in the system.\n
            If the part number is provided, the device will trigger a warning message in the program log if it does not match the connected device.
        """
        self.DeviceAlias = DeviceAlias
        if PartNumber == None:
            self.PartNumber = 'dummy Part Number'
        else:
            self.PartNumber = PartNumber
        
        ### Untracked Events
        # CombinedCurrentChanged
        # CombinedWattageChanged
        # Offline
        # Online
        
        self.CombinedCurrent = None
        self.CombinedLoadState = None
        self.CombinedWattage = None
        self.FirmwareVersion = 'dummyFW'
        self.Hostname = 'dummy Hostname'
        self.IPAddress = '127.0.0.1'
        self.LinkLicenses = []
        self.MACAddress = '01:23:45:67:89:ab'
        self.ModelName = 'dummy Model Name'
        self.SerialNumber = 'dummySN'
        self.SystemSettings = \
            {
                'Network': {
                    'LAN': {
                        'DNSServers': ['192.168.1.1',],
                        'Gateway': '192.168.254.1',
                        'Hostname': self.Hostname,
                        'IPAddress': self.IPAddress,
                        'SubnetMask': '255.255.255.0',
                        'SearchDomains': ['extron.com',],
                    },
                },
                'ProgramInformation': {
                    'Author': 'dummyAuthor',
                    'DeviceName': 'dummy device name',
                    'FileLoaded': 'dummyGUI.gs',
                    'LastUpdated': '1/23/2016 9:08:29 AM',
                    'SoftwareVersion': 'dummySWVersion',
                }
            }
    
    def Reboot(self) -> None:
        """Performs a soft restart of this device - this is equivalent to rebooting a PC."""
        pass
    
class AdapterDevice:
    def __init__(self, Host: UIDevice, DeviceAlias: str):
        """This class provides a common interface to a TouchLink Control Adapter. The user can instantiate the class directly or create a subclass to add, remove, or alter behavior for different types of devices.

        Parameters:	
            Host (UIDevice) - handle to Extron UIDevice to which the AdapterDevice is connected\n
            DeviceAlias (string) - Device Alias of the Extron device

        Ports on the TouchLink Control Adapter are instantiated and used in the same way as ports built into controllers but using the TouchLink Control Adapter as the Host parameter.
        """
        self.DeviceAlias = DeviceAlias
        self.ModelName = "Dummy Adapter Device"
        self.PartNumber = "Dummy Part Number"