# This is a dummy module for unit testing extron control script code files

from typing import Dict, Tuple, List, Union, re
import extronlib.device
import extronlib.software

## CLASS DEFINITIONS +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class CircuitBreakerInterface:
    def __init__(self,
                 Host: Union[extronlib.device.ProcessorDevice,
                             extronlib.device.UIDevice,
                             extronlib.device.AdapterDevice,
                             extronlib.device.SPDevice],
                 Port: str) -> None:
        """This class provides a common interface to a circuit breaker on an Extron product (extronlib.device). The user can instantiate the class directly or create a subclass to add, remove, or alter behavior for different types of devices.

        Parameters: 
            Host (extronlib.device) - handle to Extron device class that instantiated this interface class\n
            Port (string) - port name (e.g. 'CBR1')
        """
        ## Untracked Events
        # Offline
        # Online
        # StateChanged
        
        self.Host = Host
        self.Port = Port
        self.State = 'Closed'
    
class ClientObject:
    def __init__(self) -> None:
        """This class provides a handle to connected clients to an EthernetServerInterfaceEx.

        Note - This class cannot be instantiated by the programmer. It is only created by the EthernetServerInterfaceEx object.
        """
        self.Hostname = None
        self.IPAddress = None
        self.ServicePort = None
        
    def Disconnect(self) -> None:
        """Closes the connection gracefully on the client."""
        pass
    
    def Send(data: Union[bytes, str]) -> None:
        """Send string to the client.

        Parameters: data (bytes, string) - string to send out
        Raise: TypeError, IOError
        """
    
class ContactInterface:
    def __init__(self,
                 Host: Union[extronlib.device.ProcessorDevice,
                             extronlib.device.UIDevice,
                             extronlib.device.AdapterDevice,
                             extronlib.device.SPDevice],
                 Port: str) -> None:
        """This class will provide a common interface for controlling and collecting data from Contact Input ports on Extron devices (extronlib.device). The user can instantiate the class directly or create a subclass to add, remove, or alter behavior for different types of devices.

        Parameters: 
            Host (extronlib.device) - handle to Extron device class that instantiated this interface class\n
            Port (string) - port name (e.g. 'CII1')
        """
        ## Untracked Events
        # Offline
        # Online
        # StateChanged
        
        self.Host = Host
        self.Port = Port
        self.State = 'Off'
    
class DanteInterface:
    _valid_interface = ['LAN', 'AVLAN']
    _interface = 'LAN'
    def __init__(self,
                 DeviceName: str, 
                 Protocol: str='Extron', 
                 DanteDomainManager: extronlib.software.DanteDomainManager=None,
                 Domain: str=None) -> None:
        """This class provides an interface to Dante controlled devices.

        New in version 1.2.

        Parameters: 
            DeviceName (string) - Device name of the Dante controlled device.\n
            Protocol (string) - Protocol type used. (‘Extron’ is the only supported protocol at this time)\n
            DanteDomainManager (DanteDomainManager) - Dante Domain Manager of the Dante controlled device.\n
            Domain (string) - Dante domain this device is assigned to.
        """
        
        ## Untracked Events
        # Connected
        # Disconnected
        # ReceiveData
        
        self.DanteDomainManager = DanteDomainManager
        self.DeviceName = DeviceName
        self.Domain = Domain
        if Protocol != 'Extron':
            raise ValueError("'Extron' is currently the only valid protocol")
        self.Protocol = Protocol
        self._connected = False
    
    @classmethod
    def StartService(cls, interface='LAN') -> str:
        if interface not in cls._valid_interface:
            raise ValueError('Interface value not valid')
        cls._interface = interface
        return "ServiceStarted"
    
    def Connect(self, timeout: float=None) -> str:
        if self._connected:
            return 'ConnectedAlready'
        else:
            return 'Connected'
    
    def Disconnect(self) -> None:
        pass
    
    def Send(self, data: Union[bytes, str]) -> None:
        pass
    
    
class DigitalInputInterface:
    def __init__(self,
                 Host: Union[extronlib.device.ProcessorDevice,
                             extronlib.device.UIDevice,
                             extronlib.device.AdapterDevice,
                             extronlib.device.SPDevice],
                 Port: str,
                 Pullup: bool=False) -> None:
        """This class will provide a common interface for collecting data from Digital Input ports on Extron devices (extronlib.device). The user can instantiate the class directly or create a subclass to add, remove, or alter behavior for different types of devices.

        Parameters: 
            Host (extronlib.device) - handle to Extron device class that instantiated this interface class\n
            Port (string) - port name (e.g. 'DII1')\n
            Pullup (bool) - pull-up state on the port
        """
        ## Untracted Events
        # Online
        # Offline
        # StateChanged
        
        self.Host = Host
        self.Port = Port
        self.Pullup = Pullup
        self.State = 'Off'
        
    def Initialize(self, Pullup: bool=None) -> None:
        """Initializes Digital Input port to given values. User may provide any or all of the parameters. None leaves property unmodified.

        Parameters: Pullup (bool) - pull-up state on the port
        """
        if Pullup != None:
            self.Pullup = Pullup
    
class DigitalIOInterface:
    def __init__(self,
                 Host: Union[extronlib.device.ProcessorDevice,
                             extronlib.device.UIDevice,
                             extronlib.device.AdapterDevice,
                             extronlib.device.SPDevice],
                 Port: str,
                 Mode: str='DigitalInput',
                 Pullup: bool=False) -> None:
        """This class will provide a common interface for controlling and collecting data from Digital IO ports on Extron devices (extronlib.device). The user can instantiate the class directly or create a subclass to add, remove, or alter behavior for different types of devices.

        Parameters: 
            Host (extronlib.device) - handle to Extron device class that instantiated this interface class\n
            Port (string) - port name (e.g. 'DIO1')\n
            Mode (string) - Possible modes are: 'DigitalInput' (default), and 'DigitalOutput'\n
            Pullup (bool) - pull-up state on the port
        """
        ## Untracked Events
        # Online
        # Offline
        # StateChanged
        
        self.Host = Host
        self.Port = Port
        self.Mode = Mode
        self.Pullup = Pullup
        self.State = 'Off'
        
    def Initialize(self, Mode: str=None, Pullup: bool=None) -> None:
        """Initializes Digital IO port to given values. User may provide any or all of the parameters. None leaves property unmodified.

        Parameters: 
            Mode (string) - Possible modes are: 'DigitalInput', and 'DigitalOutput'\n
            Pullup (bool) - pull-up state on the port
        """
        if Mode != None:
            self.Mode = Mode
            
        if Pullup != None:
            self.Pullup = Pullup
            
    def Pulse(self, duration: float) -> None:
        """Turns the port on for the specified time in seconds with 10ms accuracy and a 100ms minimum value.

        Parameters: duration (float) - pulse duration
        """
        pass
    
    def SetState(self, State: Union[int, str]) -> None:
        """Parameters: State (int, string) - output state to be set ('On' or 1, 'Off' or 0)"""
        if State == 0 or State == 'Off':
            self.State = 'Off'
        elif State == 1 or State == 'On':
            self.State = 'On'
            
    def Toggle(self) -> None:
        """Changes the state of the IO Object to the logical opposite of the current state."""
        if self.State == 'On':
            self.State = 'Off'
        else:
            self.State = 'On'
    
import socket
class EthernetClientInterface:
    _valid_protocols = ['TCP', 'UDP', 'SSH']
    def __init__(self,
                 Hostname: str, 
                 IPPort: int, 
                 Protocol: str='TCP', 
                 ServicePort: int=0, 
                 Credentials: Tuple=None,
                 bufferSize: int=4096) -> None:
        """This class provides an interface to a client Ethernet socket. This class allows the user to send data over the Ethernet port in a synchronous or asynchronous manner.

        Note
            SendAndWait() can be used to synchronously capture responses.\n
            For asynchronous communication, a handler function is assigned to the ReceiveData event. Then responses and unsolicited messages will be sent to the user’s ReceiveData handler.\n
            SendAndWait cannot be called within the context of a ReceiveData event.\n
            Using SendAndWait while unsolicited data transmission is possible, may cause data loss.\n


        Parameters: 
            Hostname (string) - DNS Name of the connection. Can be an IP Address\n
            IPPort (int) - IP port number of the connection\n
            Protocol (string) - Value for either 'TCP', 'UDP', or 'SSH'\n
            ServicePort (int) - Sets the port on which to listen for response data, UDP only, zero means listen on port OS assigns\n
            Credentials (tuple) - Username and password for SSH connection.\n
            bufferSize (int) - Sets buffer size of ReceiveData (with UDP Protocol).
        """
        ## Untracked Events
        # Disconnected
        # ReceiveData
        
        self.Credentials = Credentials
        self.Hostname = Hostname
        try:
            self.IPAddress = socket.gethostbyname(Hostname)
        except:
            self.IPAddress = '0.0.0.0'
        self.IPPort = IPPort
        if Protocol not in self._valid_protocols:
            raise ValueError('Protocol must be one of TCP, UDP, or SSH')
        self.Protocol = Protocol
        self.ServicePort = ServicePort
        self._buffer_size = bufferSize
        self._timeout = None
        self._connected = False
        
    def Connect(self, timeout: float=None) -> str:
        """Connect to the server

        Parameters: timeout (float) - time in seconds to attempt connection before giving up.
        Returns: 'Connected' or 'ConnectedAlready' or reason for failure
        Return type: string
        
        Note - Does not apply to UDP connections.
        """
        if self.Protocol == 'UDP':
            raise Exception('This method does not apply to UDP clients')
        
        self._timeout = timeout
        
        if self._connected:
            return 'ConnectedAlready'
        else:
            self._connected = True
            return 'Connected'
        
    def Disconnect(self) -> None:
        """Disconnect the socket
        
        Note - Does not apply to UDP connections.
        """
        if self.Protocol == 'UDP':
            raise Exception('This method does not apply to UDP clients')
        
        self._connected = False
        
    def SSLWrap(self, 
                certificate: str=None, 
                cert_reqs: str='CERT_NONE', 
                ssl_version: str='TLSv2', 
                ca_certs: str=None) -> None:
        _valid_cert_reqs = ['CERT_NONE', 'CERT_OPTIONAL', 'CERT_REQUIRED']
        """Wrap this connection in an SSL context.

        Note
            This is almost a direct call to ssl.wrap_socket(). See python documentation for more details. The following changes are applied:
                Property server_side is set to False\n
                Property cert_reqs is a string\n
                Property ssl_version is a string\n
                Property do_handshake_on_connect is set to True\n
                Property suppress_ragged_eofs is set to True\n
                Property ciphers is fixed to the system default\n
                
        Parameters: 
            certificate (string) - alias to a specific keyfile/certificate pair\n
            cert_reqs (string) - specifies whether a certificate is required from the other side of the connection ('CERT_NONE', 'CERT_OPTIONAL', or 'CERT_REQUIRED'). If the value of this parameter is not 'CERT_NONE', then the ca_certs parameter must point to a file of CA certificates.\n
            ssl_version (string) - version from the supported SSL/TLS version table ('TLSv2'). Currently only TLS 1.2 is allowed.\n
            ca_certs (string) - alias to a file that contains a set of concatenated “certification authority” certificates, which are used to validate certificates passed from the other end of the connection.
        
        Note
            Requires protocol 'TCP'.\n
            certificate and ca_certs specify aliases to machine certificate/key pairs and CA certificates uploaded to the processor in Toolbelt.
        """
        if cert_reqs not in _valid_cert_reqs:
            raise ValueError("A valid cert_reqs value must be provided")
        if ssl_version != 'TLSv2':
            raise ValueError('TLSv2 is currently the only supported ssl_version')
        
        self._certificate = certificate
        self._cert_reqs = cert_reqs
        self._ssl_version = ssl_version
        self._ca_certs = ca_certs
        
    def Send(self, data: Union[bytes, str]) -> None:
        """Send string over Ethernet port if it’s open

        Parameters: data (bytes, string) - string to send out
        Raise: TypeError, IOError
        """
        pass
    
    def SendAndWait(self, 
                    data: Union[bytes, str], 
                    timeout: float, 
                    **delimiter: Union[int, bytes, re]) -> bytes:
        """Send data to the controlled device and wait (blocking) for response. It returns after timeout seconds expires or immediately if the optional condition is satisfied.

        Note
            In addition to data and timeout, the method accepts an optional delimiter, which is used to compare against the received response. It supports any one of the following conditions:
                deliLen (int) - length of the response\n
                deliTag (bytes) - suffix of the response\n
                deliRex (regular expression object) - regular expression
                
        Note - The function will return an empty bytes object if timeout expires and nothing is received, or the condition (if provided) is not met.

        Parameters: 
            data (bytes, string) - data to send.\n
            timeout (float) - amount of time to wait for response.\n
            delimiter (see above) - optional conditions to look for in response.\n
            
        Returns: 
            Response received data (may be empty)
            
        Return type: 
            bytes
        """
        bStr = b''
        
        return bStr
    
    def SetBufferSize(self, bufferSize: int) -> None:
        """Sets the size of the RecieveData buffer for UDP communication. This is the largest single packet size that can be received.

        Parameters: bufferSize (int) - Size of the buffer for ReceiveData
        
        Note - Applies to UDP protocol only.
        """
        if self.Protocol != 'UDP':
            raise Exception('This method only applies to UDP connections')
        self._buffer_size = bufferSize
        
    def StartKeepAlive(self, interval: float, data: Union[bytes, str]) -> None:
        """Repeatedly sends data at the given interval

        Parameters: 
            interval (float) - Time in seconds between transmissions\n
            data (bytes, string) - data to send
        """
        
        self._keep_alive = interval
        
    def StopKeepAlive(self) -> None:
        self._keep_alive = None
    
class EthernetServerInterfaceEx:
    _available_protocols = ['TCP', 'UDP']
    _available_interfaces = ['Any', 'LAN', 'AVLAN']
    
    def __init__(self, IPPort: int, Protocol: str='TCP', Interface: str='Any', MaxClients: int=None) -> None:
        """This class provides an interface to an Ethernet server that allows a user-defined amount of client connections. After instantiation, the server is started by calling StartListen(). This class allows the user to send data over the Ethernet port in an asynchronous manner using Send() and ReceiveData after a client has connected.

        Parameters: 
            IPPort (int) - IP port number of the listening service.\n
            Protocol (string) - communication protocol ('TCP' or 'UDP')\n
            Interface (string) - Defines the network interface on which to listen ('Any', 'LAN', or 'AVLAN')\n
            MaxClients (int) - maximum number of client connections to allow (None == Unlimited, 0 == Invalid)
        """
        ## Untracked Events
        # Connected
        # Disconnected
        # ReceiveData
        
        self.Clients = []
        self.IPPort = IPPort
        if Interface not in self._available_interfaces:
            raise ValueError("Interface must be 'Any', 'LAN', or 'AVLAN'")
        self.Interface = Interface
        if MaxClients == 0:
            raise ValueError('Max clients cannot be 0. Use None (default) for unlimted client connections')
        self.MaxClients = MaxClients
        if Protocol not in self._available_protocols:
            raise ValueError("Protocol must either be 'TCP' or 'UDP'")
        self.Protocol = Protocol
        self._connected = False
        self._listening = False
        
    def Disconnect(self, client: ClientObject) -> None:
        """Closes the connection gracefully on specified client.

        Parameters: client (ClientObject) - handle to client object
        """
        # TODO: handle client object
        
    def SSLWrap(self, 
                certificate: str=None, 
                cert_reqs: str='CERT_NONE', 
                ssl_version: str='TLSv2', 
                ca_certs: str=None) -> None:
        _valid_cert_reqs = ['CERT_NONE', 'CERT_OPTIONAL', 'CERT_REQUIRED']
        """Wrap this connection in an SSL context.

        Note
            This is almost a direct call to ssl.wrap_socket(). See python documentation for more details. The following changes are applied:
                Property server_side is set to False\n
                Property cert_reqs is a string\n
                Property ssl_version is a string\n
                Property do_handshake_on_connect is set to True\n
                Property suppress_ragged_eofs is set to True\n
                Property ciphers is fixed to the system default\n
                
        Parameters: 
            certificate (string) - alias to a specific keyfile/certificate pair\n
            cert_reqs (string) - specifies whether a certificate is required from the other side of the connection ('CERT_NONE', 'CERT_OPTIONAL', or 'CERT_REQUIRED'). If the value of this parameter is not 'CERT_NONE', then the ca_certs parameter must point to a file of CA certificates.\n
            ssl_version (string) - version from the supported SSL/TLS version table ('TLSv2'). Currently only TLS 1.2 is allowed.\n
            ca_certs (string) - alias to a file that contains a set of concatenated “certification authority” certificates, which are used to validate certificates passed from the other end of the connection.
        
        Note
            Requires protocol 'TCP'.\n
            certificate and ca_certs specify aliases to machine certificate/key pairs and CA certificates uploaded to the processor in Toolbelt.
        """
        if cert_reqs not in _valid_cert_reqs:
            raise ValueError("A valid cert_reqs value must be provided")
        if ssl_version != 'TLSv2':
            raise ValueError('TLSv2 is currently the only supported ssl_version')
        
        self._certificate = certificate
        self._cert_reqs = cert_reqs
        self._ssl_version = ssl_version
        self._ca_certs = ca_certs
        
    def StartListen(self, timeout: int=0) -> str:
        """Start the listener

        Parameters: timeout (float) - how long to listen for connections
        Returns: 'Listening' or a reason for failure
        Raises: IOError
        """
        self._listening = True
        return 'Listening'
    
    def StopListen(self) -> None:
        self._listening = False
    
class FlexIOInterface:
    _available_modes = ['AnalogInput', 'DigitalInput', 'DigitalOutput']
    def __init__(self,
                 Host: Union[extronlib.device.ProcessorDevice,
                             extronlib.device.UIDevice,
                             extronlib.device.AdapterDevice,
                             extronlib.device.SPDevice],
                 Port: str,
                 Mode: str='DigitalInput',
                 Pullup: bool=False,
                 Upper: float=2.8,
                 Lower: float=2.0) -> None:
        """This class will provide a common interface for controlling and collecting data from Flex IO ports on Extron devices (extronlib.device). The user can instantiate the class directly or create a subclass to add, remove, or alter behavior for different types of devices.

        Parameters: 
            Host (extronlib.device) - handle to Extron device class that instantiated this interface class\n
            Port (string) - port name (e.g. 'FIO1')\n
            Mode (string) - Possible modes are: 'AnalogInput', 'DigitalInput' (default), and 'DigitalOutput'.\n
            Pullup (bool) - pull-up state on the port\n
            Upper (float) - upper threshold in volts\n
            Lower (float) - lower threshold in volts
        """
        ## Untracked Events
        # AnalogVoltageChanged
        # Online
        # Offline
        # StateChanged
        
        self.AnalogVoltage = 0.1
        self.Host = Host
        self.Lower = Lower
        if Mode not in self._available_modes:
            raise ValueError("Mode must be one of 'AnalogInput', 'DigitalInput', or 'DigitalOutput'")
        self.Mode = Mode
        self.Port = Port
        self.Pullup = Pullup
        self.State = 'Off'
        self.Upper = Upper
        
    def Initialize(self, Mode: str=None, Pullup: bool=None, Upper: float=None, Lower: float=None) -> None:
        """Initializes Flex IO port to given values. User may provide any or all of the parameters. None leaves property unmodified.

        Parameters: 
            Mode (string) - Possible modes are: 'AnalogInput', 'DigitalInput', and 'DigitalOutput'.\n
            Pullup (bool) - pull-up state on the port\n
            Upper (float) - upper threshold in volts\n
            Lower (float) - lower threshold in volts
        """
        if Mode not in self._available_modes:
            raise ValueError("Mode must be one of 'AnalogInput', 'DigitalInput', or 'DigitalOutput'")
        if Mode != None:
            self.Mode = Mode
        if Pullup != None:
            self.Pullup = Pullup
        if Upper != None:
            self.Upper = Upper
        if Lower != None:
            self.Lower = Lower
        
    def Pulse(self, duration: float) -> None:
        """Turns the port on for the specified time in seconds with 10ms accuracy and a 100ms minimum value.

        Parameters: duration (float) - pulse duration
        """
        pass
    
    def SetState(self, State: Union[int, str]) -> None:
        """Parameters: State (int, string) - output state to be set ('On' or 1, 'Off' or 0)"""
        if State == 0 or State == 'Off':
            self.State = 'Off'
        elif State == 1 or State == 'On':
            self.State = 'On'
        else:
            raise ValueError("State must be one of 0, 1, 'On', or 'Off'")
        
    def Toggle(self) -> None:
        """Changes the state of the IO Object to the logical opposite of the current state."""
        if self.State == 'On':
            self.State = 'Off'
        else:
            self.State = 'On'
    
class IRInterface:
    def __init__(self,
                 Host: Union[extronlib.device.ProcessorDevice,
                             extronlib.device.UIDevice,
                             extronlib.device.AdapterDevice,
                             extronlib.device.SPDevice],
                 Port: str,
                 File: str) -> None:
        """This class provides an interface to an IR port. This class allows the user to transmit IR data through an IR or IR/Serial port.

        Note - If an IR/Serial port is passed in and it has already been instantiated as an SerialInterface, an exception will be raised.

        Parameters: 
            Host (extronlib.device) - handle to Extron device class that instantiated this interface class\n
            Port (string) - port name (e.g., 'IRS1', 'IRI1')\n
            File (string) - IR file name (e.g. 'someDevice.eir')
        """
        ## Untracked Events
        # Online
        # Offline
        
        self.File = File
        self.Host = Host
        self.Port = Port
        self._playing = False
    
    def Initialize(self, File: str=None) -> None:
        """Initializes IR port to given file. None leaves property unmodified.

        Parameters: File (string) - IR file name (e.g. 'someDevice.eir')
        """
        if File != None:
            self.File = File
    
    def PlayContinuous(self, irFunction: str) -> None:
        """Begin playback of an IR function. Function will play continuously until stopped. Will complete at least one header, one body, and the current body.

        Parameters: irFunction (string) - function within the driver to play
        """
        self._playing = True
    
    def PlayCount(self, irFunction: str, repeatCount: int=None) -> None:
        """Play an IR function Count times. Function will play the header once and the body 1 + the specified number of repeat times.

        Parameters: 
            irFunction (string) - function within the driver to play\n
            repeatCount (int) - number of times to repeat the body (0-15)
            
        Note
            PlayCount is uninterruptible, except by Stop().\n
            repeatCount of None means play the number defined in the driver.
        """
        if repeatCount < 0 or repeatCount > 15:
            raise ValueError('Repeat count must be between 0 and 15')
        
        self._playing = True
        
    def PlayTime(self, irFunction: str, duration: float) -> None:
        """Play an IR function for the specified length of time. Function will play the header once and the body as many times as it can. Playback will stop when the time runs out. Current body will be completed.

        Parameters: 
            irFunction (string) - function within the driver to play\n
            duration (float) - time in seconds to play the function
        
        Note - PlayTime is uninterruptible, except by Stop().
        """
        if duration < 0:
            raise ValueError("Duration must be positive")
        
        self._playing = True
        
    def Stop(self) -> None:
        """Stop the current playback. Will complete the current body."""
        self._playing = False
    
class PoEInterface:
    def __init__(self,
                 Host: Union[extronlib.device.ProcessorDevice,
                             extronlib.device.AdapterDevice,
                             extronlib.device.SPDevice],
                 Port: str) -> None:
        """This is the interface class for the Power over Ethernet ports on Extron devices (extronlib.device). The user can instantiate the class directly or create a subclass to add, remove, or alter behavior for different types of devices.

        Parameters: 
            Host (extronlib.device) - handle to Extron device class that instantiated this interface class\n
            Port (string) - port name (e.g. 'POE1')
        """
        ## Untracked Events
        # Online
        # Offline
        # PowerStatusChanged
        
        self.CurrentLoad = 0.0
        self.Host = Host
        self.Port = Port
        self.PowerStatus = 'Inactive'
        self.State = 'Off'
        
    def SetState(self, State: Union[int, str]) -> None:
        """Parameters: State (int, string) - output state to be set ('On' or 1, 'Off' or 0)"""
        if State == 0 or State == 'Off':
            self.State = 'Off'
        elif State == 1 or State == 'On':
            self.State = 'On'
        else:
            raise ValueError("State must be one of 0, 1, 'On', or 'Off'")
        
    def Toggle(self) -> None:
        """Changes the state to the logical opposite of the current state."""
        if self.State == 'On':
            self.State = 'Off'
        else:
            self.State = 'On'
    
class RelayInterface:
    def __init__(self,
                 Host: Union[extronlib.device.ProcessorDevice,
                             extronlib.device.UIDevice,
                             extronlib.device.AdapterDevice,
                             extronlib.device.SPDevice],
                 Port: str) -> None:
        """This class provides a common interface for controlling relays on Extron devices (extronlib.device). The user can instantiate the class directly or create a subclass to add, remove, or alter behavior for different types of devices.

        Parameters: 
            Host (extronlib.device) - handle to Extron device class that instantiated this interface class\n
            Port (string) - port name (e.g. 'RLY1')
        """
        ## Untracked Events
        # Online
        # Offline
        
        self.Host = Host
        self.Port = Port
        self.State = 'Open'
        
    def Pulse(self, duration: float) -> None:
        """Turns the port on for the specified time in seconds with 10ms accuracy and a 100ms minimum value.

        Parameters: duration (float) - pulse duration
        """
        pass
    
    def SetState(self, State: Union[int, str]) -> None:
        """Parameters: State (int, string) - output state to be set ('Close' or 1, 'Open' or 0)"""
        if State == 0 or State == 'Open':
            self.State == 'Open'
        elif State == 1 or State == 'Closed':
            self.State == 'Closed'
        else:
            raise ValueError("State must be one of 0, 1, 'On', or 'Off'")
        
    def Toggle(self) -> None:
        """Changes the state of the IO Object to the logical opposite of the current state."""
        if self.State == 'Open':
            self.State == 'Closed'
        else:
            self.State == 'Open'
    
class SerialInterface:
    _available_parity = ['None', 'Odd', 'Even']
    _available_flow_control = ['HW', 'SW', 'Off']
    _available_mode = ['RS232', 'RS422', 'RS485']
    def __init__(self,
                 Host: Union[extronlib.device.ProcessorDevice,
                             extronlib.device.UIDevice,
                             extronlib.device.AdapterDevice,
                             extronlib.device.SPDevice],
                 Port: str,
                 Baud: int=9600,
                 Data: int=8,
                 Parity: str='None',
                 Stop: int=1,
                 FlowControl: str='Off',
                 CharDelay: float=0.0,
                 Mode: str='RS232') -> None:
        """This class provides an interface to a serial port. This class allows the user to send data over the serial port in a synchronous or asynchronous manner. This class is used for all ports capable of serial communication (e.g., Serial Ports, IR Serial Ports).

        Note
            SendAndWait() can be used to synchronously capture responses.\n
            For asynchronous communication, a handler function is assigned to the ReceiveData event. Then responses and unsolicited messages will be sent to the user’s ReceiveData handler.\n
            SendAndWait cannot be called within the context of a ReceiveData event.\n
            Using SendAndWait while unsolicited data transmission is possible, may cause data loss.\n
            If an IR/Serial port is passed in and it has already been instantiated as an IRInterface, an exception will be raised.\n
        
        Parameters: 
            Host (extronlib.device) - handle to Extron device class that instantiated this interface class\n
            Port (string) - port name (e.g., 'COM1', 'IRS1')\n
            Baud (int) - baudrate\n
            Data (int) - number of data bits\n
            Parity (string) - 'None', 'Odd' or 'Even'\n
            Stop (int) - number of stop bits\n
            FlowControl (string) - 'HW', 'SW', or 'Off'\n
            CharDelay (float) - time between each character sent to the connected device\n
            Mode (string) - mode of the port, 'RS232', 'RS422' or 'RS485'\n
        """
        ## Untracked Events
        # Online
        # Offline
        # ReceiveData
        
        self.Baud = Baud
        self.CharDelay = CharDelay
        self.Data = Data
        if FlowControl not in self._available_flow_control:
            raise ValueError("FlowControl must be one of 'HW', 'SW', or 'Off'")
        self.FlowControl = FlowControl
        self.Host = Host
        if Mode not in self._available_mode:
            raise ValueError("Mode must be one of 'RS232', 'RS422', or 'RS485'")
        self.Mode = Mode
        if Parity not in self._available_parity:
            raise ValueError("Partity must be one of 'None', 'Odd', or 'Even'")
        self.Parity = Parity
        self.Port = Port
        self.Stop = Stop
        self._keep_alive = False
        
    def Initialize(self, 
                   Baud: int=None, 
                   Data: int=None, 
                   Parity: str=None, 
                   Stop: int=None, 
                   FlowControl: str=None, 
                   CharDelay: float=None, 
                   Mode: str=None) -> None:
        """Initializes Serial port to given values. User may provide any or all of the parameters. None leaves property unmodified.

        Parameters: 
            Baud (int) - baudrate\n
            Data (int) - number of data bits\n
            Parity (string) - 'None', 'Odd' or 'Even'\n
            Stop (int) - number of stop bits\n
            FlowControl (string) - 'HW', 'SW', or 'Off'\n
            CharDelay (float) - time between each character sent to the connected device\n
            Mode (string) - mode of the port, 'RS232', 'RS422' or 'RS485'
        """
        if Baud != None:
            self.Baud = Baud
        if Data != None:
            self.Data = Data
        if Parity != None:
            if Parity not in self._available_parity:
                raise ValueError("Partity must be one of 'None', 'Odd', or 'Even'")
            self.Parity = Parity
        if Stop != None:
            self.Stop = Stop
        if FlowControl != None:
            if FlowControl not in self._available_flow_control:
                raise ValueError("FlowControl must be one of 'HW', 'SW', or 'Off'")
            self.FlowControl = FlowControl
        if CharDelay != None:
            self.CharDelay = CharDelay
        if Mode != None:
            if Mode not in self._available_mode:
                raise ValueError("Mode must be one of 'RS232', 'RS422', or 'RS485'")
            self.Mode = Mode
    
    def Send(self, data: Union[bytes, str]) -> None:
        """Send string over serial port if it’s open"""
        pass
    
    def SendAndWait(self, data: Union[bytes, str], timeout: float, delimiter: Union[int, bytes, re]) -> None:
        """Send data to the controlled device and wait (blocking) for response

        Note
            In addition to data and timeout, the method accepts an optional delimiter, which is used to compare against the received response. It supports any one of the following conditions:
                deliLen (int) - length of the response\n
                deliTag (bytes) - suffix of the response\n
                deliRex (regular expression object) - regular expression\n
            It returns after timeout seconds expires, or returns immediately if the optional condition is satisfied.

        Note - The function will return an empty bytes object if timeout expires and nothing is received, or the condition (if provided) is not met.

        Parameters: 
            data (bytes, string) - data to send.\n
            timeout (float) - amount of time to wait for response.\n
            delimiter (see above) - optional conditions to look for in response.\n
        
        Returns: Response received data (may be empty)

        Return type: bytes
        """
        return b''
    
    def StartKeepAlive(self, interval: float, data: Union[bytes, str]) -> None:
        """Repeatedly sends data at the given interval

        Parameters: 
            interval (float) - Time in seconds between transmissions\n
            data (bytes, string) - data to send
        """
        self._keep_alive = True
        
    def StopKeepAlive(self) -> None:
        """Stop the currently running keep alive routine"""
        self._keep_alive = False
    
class SPInterface:
    def __init__(self, Host: extronlib.device.SPDevice) -> None:
        """This class will provide a common interface for controlling and collecting data from AV components on Extron devices (extronlib.device) and Extron Secure Platform devices (SPDevice). The user can instantiate the class directly or create a subclass to add, remove, or alter behavior for different types of devices.
        
        Parameters: Host (extronlib.device) - handle to Extron device class that instantiated this interface class
        """
        ## Untracked Events
        # Online
        # Offline
        # ReceiveData
        
        self.Host = Host
        
    def Send(self, data: Union[bytes, str]) -> None:
        pass
    
class SWACReceptacleInterface:
    def __init__(self,
                 Host: Union[extronlib.device.ProcessorDevice,
                             extronlib.device.UIDevice,
                             extronlib.device.AdapterDevice,
                             extronlib.device.SPDevice],
                 Port: str) -> None:
        """This class provides a common interface to a switched AC power receptacle on an Extron product (extronlib.device). The user can instantiate the class directly or create a subclass to add, remove, or alter behavior for different types of devices.

        Parameters: 
            Host (extronlib.device) - handle to Extron device class that instantiated this interface class\n
            Port (string) - port name (e.g. 'SAC1')
        """
        ## Untracked Events
        # CurrentChanged
        # Online
        # Offline
        # StateChanged
        
        self.Host = Host
        self.Port = Port
        self.State = 'Off'
        
    def SetState(self, State: Union[int, str]) -> None:
        """Parameters: State (int, string) - output state to be set ('On' or 1, 'Off' or 0)"""
        if State == 0 or State == 'Off':
            self.State = 'Off'
        elif State == 1 or State == 'On':
            self.State = 'On'
        else:
            raise ValueError("State must be one of 0, 1, 'Off', or 'On'")
        
    def Toggle(self) -> None:
        """Changes the state of the receptacle to the logical opposite of the current state."""
        if self.State == 'Off':
            self.State = 'On'
        else:
            self.State = 'Off'
    
class SWPowerInterface:
    def __init__(self,
                 Host: Union[extronlib.device.ProcessorDevice,
                             extronlib.device.UIDevice,
                             extronlib.device.AdapterDevice,
                             extronlib.device.SPDevice],
                 Port: str) -> None:
        """This is the interface class for the Switched Power ports on Extron devices (extronlib.device). The user can instantiate the class directly or create a subclass to add, remove, or alter behavior for different types of devices.

        Parameters: 
            Host (extronlib.device) - handle to Extron device class that instantiated this interface class\n
            Port (string) - port name (e.g. 'SPI1')
        """
        ## Untracked Events
        # Offline
        # Online
        
        self.Host = Host
        self.Port = Port
        self.State = 'Off'
        
    def Pulse(self, duration: float) -> None:
        """Turns the port on for the specified time in seconds with 10ms accuracy and a 100ms minimum value.

        Parameters: duration (float) - pulse duration
        """
        pass
    
    def SetState(self, State: Union[int, str]) -> None:
        """Parameters: State (int, string) - output state to be set ('On' or 1, 'Off' or 0)"""
        if State == 0 or State == 'Off':
            self.State = 'Off'
        elif State == 1 or State == 'On':
            self.State = 'On'
        else:
            raise ValueError("State must be one of 0, 1, 'Off', or 'On'")
        
    def Toggle(self) -> None:
        """Changes the state of the IO Object to the logical opposite of the current state."""
        if self.State == 'On':
            self.State = 'Off'
        else:
            self.State = 'On'
    
class TallyInterface:
    def __init__(self,
                 Host: Union[extronlib.device.ProcessorDevice,
                             extronlib.device.UIDevice,
                             extronlib.device.AdapterDevice,
                             extronlib.device.SPDevice],
                 Port: str) -> None:
        """This class will provide a common interface for controlling and collecting data from Tally ports on Extron devices (extronlib.device). The user can instantiate the class directly or create a subclass to add, remove, or alter behavior for different types of devices.

        Parameters: 
            Host (extronlib.device) - handle to Extron device class that instantiated this interface class\n
            Port (string) - port name (e.g. 'TAL1')
        """
        ## Untracked Events
        # Online
        # Offline
        
        self.Host = Host
        self.Port = Port
        self.State = 'Off'
        
    def Pulse(self, duration: float) -> None:
        """Turns the port on for the specified time in seconds with 10ms accuracy and a 100ms minimum value.

        Parameters: duration (float) - pulse duration
        """
        pass
    
    def SetState(self, State: Union[int, str]) -> None:
        """Parameters: State (int, string) - output state to be set ('On' or 1, 'Off' or 0)"""
        if State == 0 or State == 'Off':
            self.State = 'Off'
        elif State == 1 or State == 'On':
            self.State = 'On'
        else:
            raise ValueError("State must be one of 0, 1, 'Off', or 'On'")
        
    def Toggle(self) -> None:
        """Changes the state of the Tally port to the logical opposite of the current state."""
        if self.State == 'On':
            self.State = 'Off'
        else:
            self.State = 'On'
    
class VolumeInterface:
    def __init__(self,
                 Host: Union[extronlib.device.ProcessorDevice,
                             extronlib.device.UIDevice,
                             extronlib.device.AdapterDevice,
                             extronlib.device.SPDevice],
                 Port: str) -> None:
        """This class will provide a common interface for controlling and collecting data from Volume Ports on Extron devices (extronlib.device). The user can instantiate the class directly or create a subclass to add, remove, or alter behavior for different types of devices.

        Parameters: 
            Host (extronlib.device) - handle to Extron device class that instantiated this interface class\n
            Port (string) - port name (e.g. 'VOL1')
        """
        ## Untracked Events
        # Online
        # Offline
        
        self.Host = Host
        self.Level = 100
        self.Max = 10.0
        self.Min = 0.0
        self.Mute = 'Off'
        self.Port = Port
        self.SoftStart = 'Enabled'
        
    def SetLevel(self, Level: int) -> None:
        """Sets Level of volume control port

        Parameters: Level (int) - Level (0 % <= Value <= 100 %).
        """
        if Level >= 0 and Level <= 100:
            self.Level = Level
        else:
            raise ValueError('Level must be an integer from 0-100')
        
    def SetMute(self, Mute: str) -> None:
        """Sets the mute state.

        Parameters: Mute (string) - mute state ('On', 'Off').
        """
        if Mute == 'On' or Mute == 'Off':
            self.Mute = Mute
        else:
            raise ValueError("Mute must be either 'On' or 'Off'")
        
    def SetRange(self, Min: float, Max: float) -> None:
        """Set volume control object’s voltage range.

        Parameters: 
            Min (float) - minimum voltage\n
            Max (float) - maximum voltage
        """
        if Min >= 0.0 and Min < 10:
            self.Min = Min
        else:
            raise ValueError("Min must be a floating point number >= 0.0 and < 10.0")
        if Max > 0.0 and Max <= 10:
            self.Max = Max
        else:
            raise ValueError("Max must be a floating point number > 0.0 and <= 10.0")
        
    def SetSoftStart(self, SoftStart: str) -> None:
        """Enable or Disable Soft Start.

        Parameters: SoftStart (string) - Soft Start state ('Enabled', 'Disabled').
        """
        if SoftStart == 'Enabled' or SoftStart == 'Disabled':
            self.SoftStart = SoftStart
        else:
            raise ValueError("SoftStart must either be 'Enabled' or 'Disabled'")
        
## +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++