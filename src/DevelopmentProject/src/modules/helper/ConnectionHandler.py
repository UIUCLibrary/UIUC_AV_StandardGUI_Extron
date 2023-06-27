"""
Connection Handler module

Copyright 2018-2022, Extron. All rights reserved.
"""

## Begin ControlScript Import -------------------------------------------------
from extronlib.interface import (EthernetClientInterface,
                                 EthernetServerInterfaceEx, SerialInterface,
                                 SPInterface)
from extronlib.software import SummitConnect
from extronlib.system import Wait, Timer

# Platform Specific imports
from extronlib import Platform
if Platform() == 'Pro xi':
    from extronlib.interface import DanteInterface
## End ControlScript Import ---------------------------------------------------

from collections import deque
from time import monotonic

__version__ = '2.3.0'


def ModuleVersion():
    """The ConnectionHandler Module version.

    :rtype: string
    """
    return __version__


DEBUG = False


def _trace(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)


def GetConnectionHandler(Interface, keepAliveQuery=None,
                         keepAliveQueryQualifier=None, DisconnectLimit=15,
                         pollFrequency=1, connectRetryTime=5,
                         serverTimeout=5*60):
    """
    Creates a new connection handler instance tailored to the object instance
    passed in the Interface argument.

    .. code-block:: python

        Server = GetConnectionHandler(EthernetServerInterfaceEx(9000),
                                      serverTimeout=30)

        # The connection handler will use the Global Scripter Module's Video
        # Mute query function to keep the connection alive.
        Dvs605 = GetConnectionHandler(DvsModule.EthernetClass('192.168.1.1',
                                      9000, Model='DVS 605'), 'VideoMute',
                                      DisconnectLimit=5)

        # MlcKeepAlive in this example is a function that sends a programmer-
        # specified query string.
        Mlc206 = GetConnectionHandler(SerialInterface(MainProcessor, 'COM2'),
                                      MlcKeepAlive)

    :param Interface: The extronlib.interface for which to create a connection
                      handler.
    :type Interface: One of the interface types in the table below or a
                     derivative of one of these types.
    :param keepAliveQuery: A function name as a string or reference to a
                           callable used to execute the keep alive query.
    :type keepAliveQuery: string, callable
    :param keepAliveQueryQualifier: When Interface is a Global Scripter Module,
                                    any qualifiers needed by the update
                                    function.
    :type keepAliveQueryQualifier: dict
    :param DisconnectLimit: Maximum number of missed responses that indicates
                            a disconnected device. Defaults to 15.
    :type DisconnectLimit: int
    :param pollFrequency: How often to send the keep alive query in seconds.
                          Defaults to 1.
    :type pollFrequency: float
    :param connectRetryTime: Number of seconds to wait before attempting to
                             reconnect after disconnect.
    :type connectRetryTime: float
    :param serverTimeout: For server Interfaces, maximum time in seconds to
                          allow before disconnecing idle clients. Defaults to 5
                          minutes.
    :type serverTimeout: float.
    :returns: An object instance with an API similar to an extronlib.interface
              object.
    :raises TypeError: if Interface is an `EthernetServerInferface` (non-Ex) or
                       is a UDP `EthernetServerInferfaceEx`.
    :raises ValueError: if Interface is an `EthernetClientInterface` and its
                        Protocol type is not TCP, UDP, or SSH.

    The returned object instance depends on the instance type passed in
    Interface.

    .. list-table::
        :widths: auto

        * - **Interface**
          - **Returned Instance**
        * - DanteInterface
          - :py:class:`RawTcpHandler`
        * - EthernetClientInterface - SSH
          - :py:class:`RawTcpHandler`
        * - EthernetClientInterface - TCP
          - :py:class:`RawTcpHandler`
        * - EthernetClientInterface - UDP
          - :py:class:`RawSimplePipeHandler`
        * - EthernetServerInterfaceEx
          - :py:class:`ServerExHandler`
        * - Global Scripter Module - Dante
          - :py:class:`ModuleTcpHandler`
        * - Global Scripter Module - HTTP
          - :py:class:`ModuleSimplePipeHandler`
        * - Global Scripter Module - Serial
          - :py:class:`ModuleSimplePipeHandler`
        * - Global Scripter Module - Serial-Over-Ethernet
          - :py:class:`ModuleTcpHandler`
        * - Global Scripter Module - SPInterface
          - :py:class:`ModuleSimplePipeHandler`
        * - Global Scripter Module - SSH
          - :py:class:`ModuleTcpHandler`
        * - Global Scripter Module - TCP
          - :py:class:`ModuleTcpHandler`
        * - Global Scripter Module - UDP
          - :py:class:`ModuleSimplePipeHandler`
        * - SerialInterface
          - :py:class:`RawSimplePipeHandler`
        * - SPInterface
          - :py:class:`RawSimplePipeHandler`

    .. note::
        * Only TCP EthernetServerInterfaceEx instances are supported.
        * DanteInterface does not have a *SendAndWait* method.
        * DanteInterface is only available in ControlScript Pro xi.
    """
    if isinstance(Interface, EthernetServerInterfaceEx):
        if Interface.Protocol == 'UDP':
            raise TypeError('UDP is not a supported protocol type. Use '
                            'EthernetServerInterfaceEx without the Universal '
                            'Connection Handler.')
        return ServerExHandler(Interface, serverTimeout, connectRetryTime)

    # Look for signs Interface is a Global Scripter Module. We will assume
    # Interface is a Global Scripter Module if it has a callable (i.e. acts
    # like a Python function) attribute with a name matching 'Update' +
    # keepAliveQuery and a callable SubscribeStatus attribute.

    # Connection handler classes for Global Scripter Modules use the module's
    # built-in Update facility whereas the others treat keepAliveQuery as a
    # user function that sends a query string the controlled device.

    if isinstance(keepAliveQuery, str):
        UpdateAttr = getattr(Interface, 'Update' + keepAliveQuery, None)
        SubscribeAttr = getattr(Interface, 'SubscribeStatus', None)
        if callable(UpdateAttr) and callable(SubscribeAttr):
            IsGSModule = True
        else:
            IsGSModule = False
    elif callable(keepAliveQuery):
        IsGSModule = False
    else:
        raise ValueError('keepAliveQuery must be the name of an Update '
                         'function in a Global Scripter Module or a reference '
                         'to a callable function.')

    if IsGSModule:
        if isinstance(Interface, SerialInterface):
            return ModuleSimplePipeHandler(Interface, DisconnectLimit,
                                           pollFrequency, keepAliveQuery,
                                           keepAliveQueryQualifier)

        if isinstance(Interface, EthernetClientInterface):
            if Interface.Protocol in ['TCP', 'SSH']:
                return ModuleTcpHandler(Interface, DisconnectLimit,
                                        pollFrequency, keepAliveQuery,
                                        keepAliveQueryQualifier,
                                        connectRetryTime)
            elif Interface.Protocol == 'UDP':
                return ModuleSimplePipeHandler(Interface, DisconnectLimit,
                                               pollFrequency, keepAliveQuery,
                                               keepAliveQueryQualifier)
            else:
                raise ValueError('Unsupported Ethernet protocol '
                                 'type: {}.'.format(Interface.Protocol))

        if Platform() == 'Pro xi' and isinstance(Interface, DanteInterface):
            if Interface.Protocol in ['Extron']:
                return ModuleTcpHandler(Interface, DisconnectLimit,
                                        pollFrequency, keepAliveQuery,
                                        keepAliveQueryQualifier,
                                        connectRetryTime)

        if isinstance(Interface, SPInterface):
            return ModuleSimplePipeHandler(Interface, DisconnectLimit,
                                           pollFrequency, keepAliveQuery,
                                           keepAliveQueryQualifier)

        if Interface.ConnectionType == 'HTTP':
            return ModuleSimplePipeHandler(Interface, DisconnectLimit,
                                           pollFrequency, keepAliveQuery,
                                           keepAliveQueryQualifier)

        if isinstance(Interface, SummitConnect):
            return ModuleTcpHandler(Interface, DisconnectLimit,
                                    pollFrequency, keepAliveQuery,
                                    keepAliveQueryQualifier,
                                    connectRetryTime)
    else:
        if isinstance(Interface, SerialInterface):
            return RawSimplePipeHandler(Interface, DisconnectLimit,
                                        pollFrequency, keepAliveQuery)

        if isinstance(Interface, EthernetClientInterface):
            if Interface.Protocol in ['TCP', 'SSH']:
                return RawTcpHandler(Interface, DisconnectLimit, pollFrequency,
                                     keepAliveQuery, connectRetryTime)
            elif Interface.Protocol == 'UDP':
                return RawSimplePipeHandler(Interface, DisconnectLimit,
                                            pollFrequency, keepAliveQuery)
            else:
                raise ValueError('Unsupported Ethernet protocol '
                                 'type: {}.'.format(Interface.Protocol))

        if Platform() == 'Pro xi' and isinstance(Interface, DanteInterface):
            if Interface.Protocol in ['Extron']:
                return RawTcpHandler(Interface, DisconnectLimit, pollFrequency,
                                     keepAliveQuery, connectRetryTime)

        if isinstance(Interface, SPInterface):
            return RawSimplePipeHandler(Interface, DisconnectLimit,
                                        pollFrequency, keepAliveQuery)

    raise TypeError('"{}" is not a supported interface type.'.format(type(Interface)))


def _UnassignedEvent(*args, **kwargs):
    pass


class ScripterModuleMixin:
    """
    The ScripterModuleMixin adds methods to a ConnectionHandler subclass to
    facilitate intercepting features built into Global Scripter Modules such as
    status subscription.
    """
    def _AddStatusSubscriber(self):
        # Check for a 'SubscribeStatus' method on the wrapped interface. If one
        # exists, add the interceptor for it.
        if hasattr(self._WrappedInterface, 'SubscribeStatus'):
            self.SubscribeStatus = self._SubscribeStatus

            # Add a subscription for ConnectionStatus routed to our handler.
            self._WrappedInterface.SubscribeStatus('ConnectionStatus', None,
                                                   self._NewConnectionStatus)

    def _SubscribeStatus(self, command, qualifier, callback):
        # Passes status subscriptions down to the wrapped interface except for
        # ConnectionStatus. ConnectionStatus subscription is instead handled in
        # this class.
        if command == 'ConnectionStatus':
            self._Subscriptions[command] = callback
        else:
            self._WrappedInterface.SubscribeStatus(command, qualifier, callback)


class ConnectionHandler:
    """
    Base class for all client-type connection handlers.

    This class is not intended to be used directly as it is the base class for
    all connection handlers. Rather, use :py:meth:`GetConnectionHandler` to
    instantiate the correct handler for your interface type.
    """
    def __init__(self, Interface, pollFrequency):
        self._WrappedInterface = Interface
        self._PollTimer = Timer(pollFrequency, self._PollTriggered)
        self._PollTimer.Pause()

        # Common Event Handlers
        self._Connected = _UnassignedEvent
        self._Disconnected = _UnassignedEvent

        self._ConnectionStatus = 'Unknown'

    @property
    def Connected(self):
        """
        ``Event:`` Triggers when the underlying interface instance connects.

        The callback function must accept two parameters. The first is the
        ConnectionHandler instance triggering the event and the second is the
        string 'Connected'.
        """
        return self._Connected

    @Connected.setter
    def Connected(self, handler):
        _trace('set Connected handler.', handler)
        if callable(handler):
            self._Connected = handler
        else:
            raise TypeError("'handler' is not callable")

    @property
    def ConnectionStatus(self):
        """
        Returns the current connection state: ``Connected``, ``Disconnected``,
        or ``Unknown``.
        """
        return self._ConnectionStatus

    @property
    def Disconnected(self):
        """
        ``Event:`` Triggers when the underlying interface instance disconnects.

        The callback function must accept two parameters. The first is the
        ConnectionHandlerinstance triggering the event and the second is the
        string 'Disconnected'.
        """
        return self._Disconnected

    @Disconnected.setter
    def Disconnected(self, handler):
        _trace('set Disconnected handler.', handler)
        if callable(handler):
            self._Disconnected = handler
        else:
            raise TypeError("'handler' is not callable")

    @property
    def DisconnectLimit(self):
        """
        :returns: the value set as the maximum number of missed responses
            that indicates a disconnected device.
        :rtype: int
        """
        return self._DisconnectLimit

    @property
    def Interface(self):
        """
        :returns: the interface instance for which this instance is handling
            connection.
        :rtype: an extronlib interface or a Global Scripter Module
        """
        return self._WrappedInterface

    @property
    def PollTimer(self):
        """
        :returns: the timer instance used to schedule keep alive polling.
        :rtype: extronlib.system.Timer
        """
        return self._PollTimer

    def __getattr__(self, name):
        # This function overrides the Python-supplied version of __getattr__.
        # Under the covers, accessing obj.name causes Python to first call
        # __getattribute__ on obj to lookup 'name'. If that fails Python then
        # calls __getattr__, which we can hook to implement fall-through to the
        # underlying interface instance for methods not implemented by this
        # class.
        try:
            return self._WrappedInterface.__getattribute__(name)
        except AttributeError:
            SelfName = self.__class__.__name__
            WrappedName = self._WrappedInterface.__class__.__name__

            raise AttributeError("'{}' object has no attribute '{}' nor was "
                                 "one found in the underlying '{}' "
                                 "object.".format(SelfName, name, WrappedName))


class RawSimplePipeHandler(ConnectionHandler):
    def __init__(self, Interface, DisconnectLimit, pollFrequency,
                 keepAliveQuery):
        """
        Wraps an instance of extronlib's SerialInterface or UDP
        EthernetClientInterface (or derivative of these types) to provide
        connect and disconnect events and periodic keep alive polling.

        .. note:: Use :py:meth:`GetConnectionHandler` to instantiate the
            correct connection handler rather than instantiating
            :py:class:`RawSimplePipeHandler` directly.

        :param Interface: The interface instance to wrap.
        :type Interface: SerialInterface, EthernetClientInterface, or
                         derivative
        :param DisconnectLimit: Maximum number of missed responses that
                                indicates a disconnected device.
        :type DisconnectLimit: int
        :param pollFrequency: How often in seconds to send the keep alive
                              query.
        :type pollFrequency: float
        :param keepAliveQuery: The callback that will send the appropriate
                               device query. The callback must accept the
                               calling ConnectionHandler instance as an
                               argument.
        :type keepAliveQuery: callable
        """
        super().__init__(Interface, pollFrequency)

        self._keepAliveQuery = keepAliveQuery

        # Event Handlers
        self._ReceiveData = _UnassignedEvent

        self._WrappedInterface.ReceiveData = self._IfaceRxData

        # Bookkeeping
        self._SendCounter = 0
        self._DisconnectLimit = DisconnectLimit

    @property
    def ReceiveData(self):
        """
        ``Event:`` Triggers when data is received by the underlying interface
        instance.

        The callback function must accept two parameters. The first is the
        ConnectionHandler instance triggering the event and the second is the
        received data as a bytes object.
        """
        return self._ReceiveData

    @ReceiveData.setter
    def ReceiveData(self, handler):
        if callable(handler):
            self._ReceiveData = handler
        else:
            raise TypeError("'handler' is not callable")

    def Connect(self):
        '''
        Attempts to connect and starts the polling loop. The keepAliveQuery
        function will be called at the rate set by the PollTimer Interval.
        '''
        if self._PollTimer.State != 'Running':
            self._PollTimer.Restart()

    def ResponseAccepted(self):
        """
        Resets the send counter. Call this function when a valid response has
        been received from the controlled device.

        .. note:: This function must be called whenever your code determines
            that a good keep alive response has been received.

        .. code-block:: python

            @event(SomeDevice, 'ReceiveData')
            def HandleReceiveData(interface, data):
                DataBuffer += data.decode()

                # Parse DataBuffer content.

                if IsGoodResponse:
                    interface.ResponseAccepted()
        """
        self._SendCounter = 0
        self._NewConnectionStatus('Connected')

    def Send(self, data):
        '''
        Send data to the controlled device without waiting for response.

        :param data: string to send out
        :type data: bytes, string
        :raise: TypeError, IOError

        .. code-block:: python

            MainProjector.Send('GET POWER\\r')
        '''
        self._SendCounter += 1
        _trace('Send: data=', data, 'count=', self._SendCounter)

        if self._DisconnectLimitExceeded():
            self._NewConnectionStatus('Disconnected')

        self._WrappedInterface.Send(data)

    def SendAndWait(self, data, timeout, **delimiter):
        '''
        Send data to the controlled device and wait (blocking) for response. It
        returns after *timeout* seconds expires, or returns immediately if the
        optional condition is satisfied.

        .. note:: In addition to *data* and *timeout*, the method accepts an
            optional delimiter, which is used to compare against the received
            response.  It supports any one of the following conditions:

                * *deliLen* (int) - length of the response
                * *deliTag* (byte) - suffix of the response
                * *deliRex* (regular expression object) - regular expression

        .. note:: The function will return an empty byte array if *timeout*
            expires and nothing is received, or the condition (if provided) is
            not met.

        :param data: data to send.
        :type data: bytes, string
        :param timeout: amount of time to wait for response.
        :type timeout: float
        :param delimiter: optional conditions to look for in response.
        :type delimiter: see above
        :return: Response received data (may be empty)
        :rtype: bytes
        '''
        if isinstance(self._WrappedInterface, SPInterface):
            raise AttributeError("'{}' object has no attribute \
                                'SendandWait'.".format(self.__class__.__name__))

        self._SendCounter += 1
        _trace('SendAndWait: data=', data, 'count=', self._SendCounter)

        if self._DisconnectLimitExceeded():
            self._NewConnectionStatus('Disconnected')

        return self._WrappedInterface.SendAndWait(data, timeout, **delimiter)

    def _DisconnectLimitExceeded(self):
        return self._SendCounter > self._DisconnectLimit

    def _IfaceRxData(self, interface, data):
        """
        Intercepts the ReceiveData event emitted by the wrapped interface and
        passes the event up to client code.
        """
        self._ReceiveData(self, data)

    def _NewConnectionStatus(self, value):
        """
        Triggers the Connected or Disconnect event on connection status change.
        """
        if not value == self._ConnectionStatus:
            self._ConnectionStatus = value
            if value == 'Connected':
                self._Connected(self, value)
            elif value == 'Disconnected':
                self._Disconnected(self, value)

    def _PollTriggered(self, timer, count):
        self._keepAliveQuery(self)


class ModuleSimplePipeHandler(ScripterModuleMixin, ConnectionHandler):
    def __init__(self, Interface, DisconnectLimit, pollFrequency,
                 keepAliveQuery, keepAliveQualifiers=None):
        """
        Wraps a Global Scripter Module instance derived from
        extronlib's SerialInterface or UDP EthernetClientInterface to provide
        connect/disconnect events and periodic keep alive polling.

        .. note:: Use :py:meth:`GetConnectionHandler` to instantiate the
            correct connection handler rather than instantiating
            :py:class:`ModuleSimplePipeHandler` directly.

        :param Interface: The interface instance who's connection state will be
                           managed.
        :type Interface: SerialInterface, EthernetClientInterface, or
                         derivative
        :param DisconnectLimit: Maximum number of missed responses that
                                indicates a disconnected device.
        :type DisconnectLimit: int
        :param pollFrequency: How often to send the keep alive query in
                              seconds.
        :type pollFrequency: float
        :param keepAliveQuery: The name of an Update function that will be
                               queried to keep the connection alive.
        :type keepAliveQuery: string
        :param keepAliveQualifiers: Dictionary of parameter and value pairs to
                                    be passed to the  keep-alive function.
        :type keepAliveQualifiers: dict
        """
        super().__init__(Interface, pollFrequency)

        self._keepAliveQuery = keepAliveQuery
        self._keepAliveParams = keepAliveQualifiers

        # Override the module's maximum missed response count.
        self._WrappedInterface.connectionCounter = DisconnectLimit

        # Bookkeeping
        self._DisconnectLimit = DisconnectLimit

        self._AddStatusSubscriber()

        # Maps command names for which the client has status subscriptions to
        # the client's callback function.
        self._Subscriptions = {}

    def Connect(self):
        '''
        Attempts to connect and starts the polling loop. The keepAliveQuery
        function will be called at the rate set by the PollTimer Interval.
        '''
        if self._PollTimer.State != 'Running':
            self._PollTimer.Restart()

    def _NewConnectionStatus(self, command, value, qualifier):
        if not value == self._ConnectionStatus:
            self._ConnectionStatus = value
            if value == 'Connected':
                self._Connected(self, value)
            elif value == 'Disconnected':
                self._Disconnected(self, value)

            # Update the client with new connection status if subscribed.
            client_callback = self._Subscriptions.get('ConnectionStatus', None)
            if callable(client_callback):
                client_callback('ConnectionStatus', value, None)

    def _PollTriggered(self, timer, count):
        self._WrappedInterface.Update(self._keepAliveQuery,
                                      self._keepAliveParams)


class RawTcpHandler(ConnectionHandler):
    def __init__(self, Interface, DisconnectLimit, pollFrequency,
                 keepAliveQuery, connectRetryTime):
        """
        Wraps an extronlib EthernetClientInterface instance using TCP
        or SSH protocol to provide connect/disconnect events and periodic keep
        alive polling.

        .. note:: Use :py:meth:`GetConnectionHandler` to instantiate the
            correct connection handler rather than instantiating
            :py:class:`RawTcpHandler` directly.

        :param Interface: The interface to wrap.
        :type Interface: extronlib.EthernetClientInterface
        :param DisconnectLimit: Maximum number of missed responses that
                                indicates a disconnected device.
        :type DisconnectLimit: int
        :param pollFrequency: How often to send the keep alive query in
                              seconds.
        :type pollFrequency: float
        :param keepAliveQuery: The callback that will send the appropriate
                               device query. The callback must accept the
                               calling ConnectionHandler instance as an
                               argument.
        :type keepAliveQuery: callable
        :param connectRetryTime: Time in seconds to wait before attempting to
                                 reconnect to the remote host.
        :type connectRetryTime: float
        """
        super().__init__(Interface, pollFrequency)

        self._keepAliveQuery = keepAliveQuery

        # Event Handlers
        self._ConnectFailed = _UnassignedEvent
        self._ReceiveData = _UnassignedEvent

        # Capture interface events
        self._WrappedInterface.ReceiveData = self._IfaceRxData
        self._WrappedInterface.Connected = self._IfaceConnected
        self._WrappedInterface.Disconnected = self._IfaceDisconnected

        # Bookkeeping
        self._SendCounter = 0
        self._DisconnectLimit = DisconnectLimit
        self._ReconnectTime = connectRetryTime
        self._ReconnectTimer = Timer(self._ReconnectTime,
                                     self._AttemptReconnect)
        self._ReconnectTimer.Stop()
        self._AttemptingConnect = False

        self._ConnectTimeout = None
        self._AutoReconnect = True

    @property
    def AutoReconnect(self):
        """
        Controls whether or not the connection handler attempts to reconnect
        after disconnect.

        :return: The auto reconnect state.
        :rtype: bool
        """
        return self._AutoReconnect

    @AutoReconnect.setter
    def AutoReconnect(self, value):
        if value:
            self._AutoReconnect = True
        else:
            self._AutoReconnect = False

    @property
    def ConnectFailed(self):
        """
        ``Event:`` Triggers when a TCP connect attempt fails.

        The callback function must accept two parameters. The first is the
        ConnectionHandler instance triggering the event and the second is the
        failure reason as a string.

        .. code-block:: python

            @event(SomeInterface, 'ConnectFailed')
            def HandleConnectFailed(interface, reason):
                print('Connect failure:', reason)
        """
        return self._ConnectFailed

    @ConnectFailed.setter
    def ConnectFailed(self, handler):
        if callable(handler):
            self._ConnectFailed = handler
        else:
            raise TypeError("'handler' is not callable")

    @property
    def ReceiveData(self):
        """
        ``Event:`` Triggers when data is received by the underlying interface
        instance.

        The callback function must accept two parameters. The first is the
        ConnectionHandler instance triggering the event and the second is the
        received data as a bytes object.
        """
        return self._ReceiveData

    @ReceiveData.setter
    def ReceiveData(self, handler):
        if callable(handler):
            self._ReceiveData = handler
        else:
            raise TypeError("'handler' is not callable")

    def Connect(self, timeout=None):
        '''
        Attempt to connect to the server and starts the polling loop. The
        keepAliveQuery function will be called at the rate set by PollTimer
        Interval.

        The connection will be attempted only once unless AutoReconnect is
        True.

        :param timeout: optional time in seconds to attempt connection before
                        giving up.
        :type timeout: float
        '''
        self._ConnectTimeout = timeout
        self._AttemptReconnect()

        if self._PollTimer.State != 'Running':
            self._PollTimer.Restart()

    def ResponseAccepted(self):
        """
        Resets the send counter. Call this function when a valid response has
        been received from the controlled device.

        .. note:: This function must be called whenever your code determines
            that a good keep alive response has been received.

        .. code-block:: python

            @event(SomeDevice, 'ReceiveData')
            def HandleReceiveData(interface, data):
                global DataBuffer
                DataBuffer += data.decode()

                # Parse DataBuffer content.

                if IsGoodResponse:
                    interface.ResponseAccepted()
        """
        self._SendCounter = 0
        self._NewConnectionStatus('Connected')

    def Send(self, data):
        '''
        Send data to the controlled device without waiting for response.

        :param data: string to send out
        :type data: bytes, string
        :raise: TypeError, IOError

        .. code-block:: python

            MainProjector.Send('GET POWER\\r')
        '''
        self._SendCounter += 1
        _trace('Send: data=', data, 'count=', self._SendCounter)

        if self._DisconnectLimitExceeded():
            self._WrappedInterface.Disconnect()
        else:
            self._WrappedInterface.Send(data)

    def SendAndWait(self, data, timeout, **delimiter):
        '''
        Send data to the controlled device and wait (blocking) for response. It
        returns after *timeout* seconds expires, or returns immediately if the
        optional condition is satisfied.

        .. note:: In addition to *data* and *timeout*, the method accepts an
            optional delimiter, which is used to compare against the received
            response.  It supports any one of the following conditions:

                * *deliLen* (int) - length of the response
                * *deliTag* (byte) - suffix of the response
                * *deliRex* (regular expression object) - regular expression

        .. note:: The function will return an empty byte array if *timeout*
            expires and nothing is received, or the condition (if provided) is
            not met.

        :param data: data to send.
        :type data: bytes, string
        :param timeout: amount of time to wait for response.
        :type timeout: float
        :param delimiter: optional conditions to look for in response.
        :type delimiter: see above
        :return: Response received data (may be empty)
        :rtype: bytes
        '''
        self._SendCounter += 1
        _trace('SendAndWait: data=', data, 'count=', self._SendCounter)

        if not self._DisconnectLimitExceeded():
            res = self._WrappedInterface.SendAndWait(data, timeout,
                                                     **delimiter)
            return res

        self._WrappedInterface.Disconnect()

    def _AttemptReconnect(self, timer=None, count=0):
        self._AttemptingConnect = True

        connect_res = self._WrappedInterface.Connect(self._ConnectTimeout)
        if connect_res not in ['Connected', 'ConnectedAlready']:
            self._ConnectFailed(self, connect_res)
            self._SendCounter = self._DisconnectLimit + 1

            if self._AutoReconnect and self._ReconnectTimer.State != 'Running':
                self._ReconnectTimer.Resume()

    def _DisconnectLimitExceeded(self):
        return self._SendCounter > self._DisconnectLimit

    def _IfaceConnected(self, interface, state):
        self._SendCounter = 0
        self._AttemptingConnect = False
        if self._ReconnectTimer.State != 'Stopped':
            self._ReconnectTimer.Stop()

    def _IfaceDisconnected(self, interface, state):
        if self._AutoReconnect:
            if self._ReconnectTimer.State != 'Running':
                self._ReconnectTimer.Resume()

        self._NewConnectionStatus('Disconnected')

    def _IfaceRxData(self, interface, data):
        self._ReceiveData(self, data)

    def _NewConnectionStatus(self, value):
        if not value == self._ConnectionStatus:
            self._ConnectionStatus = value
            if value == 'Connected':
                self._Connected(self, value)
            elif value == 'Disconnected':
                self._Disconnected(self, value)

    def _PollTriggered(self, timer, count):
        if not self._AttemptingConnect:
            self._keepAliveQuery(self)


class ModuleTcpHandler(ScripterModuleMixin, ConnectionHandler):
    def __init__(self, Interface, DisconnectLimit, pollFrequency,
                 keepAliveQuery, keepAliveQualifiers, reconnectTime):
        """
        Wraps a Global Scripter Module instance derived from
        extronlib's EthernetClientInterface to provide connect/disconnect
        events and periodic keep alive polling.

        .. note:: Use :py:meth:`GetConnectionHandler` to instantiate the
            correct connection handler rather than instantiating
            :py:class:`ModuleTcpHandler` directly.

        :param Interface: The interface instance who's connection state will be
                          managed.
        :type Interface: A Global Scripter Module instance derived from
                         EthernetClientInterface
        :param DisconnectLimit: Maximum number of missed responses that
                                indicates a disconnected device.
        :type DisconnectLimit: int
        :param PollTimer: A Timer instance used to schedule keep alive queries.
        :type PollTimer: extronlib.system.Timer
        :param keepAliveQuery: The name of an Update function that will be
                               queried to keep the connection alive.
        :type keepAliveQuery: string
        :param keepAliveQualifiers: parameter and value pairs to be passed to
                                    the keep-alive function.
        :type keepAliveQualifiers: dict
        """
        super().__init__(Interface, pollFrequency)

        self._keepAliveQuery = keepAliveQuery
        self._keepAliveParams = keepAliveQualifiers

        # Override the module's maximum missed response count.
        self._DisconnectLimit = DisconnectLimit
        self._WrappedInterface.connectionCounter = DisconnectLimit

        # Event Handlers
        self._ConnectFailed = _UnassignedEvent

        # Capture interface events
        self._WrappedInterface.Connected = self._IfaceConnected
        self._WrappedInterface.Disconnected = self._IfaceDisconnected

        # Bookkeeping
        self._MaxHistory = DisconnectLimit
        self._reconnectTime = reconnectTime
        self._ReconnectTimer = Timer(self._reconnectTime,
                                     self._AttemptReconnect)
        self._ReconnectTimer.Stop()
        self._AttemptingConnect = False
        self._ConnectHistory = deque(maxlen=self._MaxHistory)

        self._AddStatusSubscriber()

        # Maps command names for which the client has status subscriptions to
        # the client's callback function.
        self._Subscriptions = {}
        self._ConnectTimeout = 3
        self._AutoReconnect = True

    @property
    def AutoReconnect(self):
        """
        Enable or disable auto reconnect.

        :type value: boolean
        """
        return self._AutoReconnect

    @AutoReconnect.setter
    def AutoReconnect(self, value):
        if value:
            self._AutoReconnect = True
        else:
            self._AutoReconnect = False

    @property
    def ConnectFailed(self):
        """
        ``Event:`` Triggers when a TCP connect attempt fails.

        The callback function must accept two parameters. The first is the
        ConnectionHandler instance  triggering the event and the second is the
        failure reason as a string.

        .. code-block:: python

            @event(SomeInterface, 'ConnectFailed')
            def HandleConnectFailed(interface, reason):
                print('Connect failure:', reason)
        """
        return self._ConnectFailed

    @ConnectFailed.setter
    def ConnectFailed(self, handler):
        if callable(handler):
            self._ConnectFailed = handler
        else:
            raise TypeError("'handler' is not callable")

    def Connect(self, timeout=None):
        """
        Attempt to connect to the server and starts the polling loop. The
        keepAliveQuery function will be called at the rate set by PollTimer
        Interval.

        The connection will be attempted only once unless AutoReconnect is
        True.

        :param timeout: optional time in seconds to attempt connection before
                        giving up.
        :type timeout: float
        """
        self._ConnectTimeout = timeout

        if not self._AttemptingConnect and \
                self._ConnectionStatus != 'Connected':
            self._AttemptReconnect()

        if self._PollTimer.State != 'Running':
            self._PollTimer.Restart()

    def _AttemptReconnect(self, timer=None, count=0):
        self._AttemptingConnect = True

        connect_res = self._WrappedInterface.Connect(self._ConnectTimeout)
        if connect_res not in ['Connected', 'ConnectedAlready']:
            self._ConnectFailed(self, connect_res)

            # Force disconnected state
            self._WrappedInterface.counter = self._DisconnectLimit + 1

            if self._AutoReconnect and self._ReconnectTimer.State != 'Running':
                self._ReconnectTimer.Resume()

    def _HasBeenConnected(self):
        if len(self._ConnectHistory) >= self._ConnectHistory.maxlen:
            return self._ConnectHistory.count('Connected') > 0
        else:
            # Return True so that we don't trigger a reconnect attempt without
            # first collecting enough history.
            return True

    def _IfaceConnected(self, interface, state):
        self._ConnectHistory.append('Connected')
        self._AttemptingConnect = False
        if self._ReconnectTimer.State != 'Stopped':
            self._ReconnectTimer.Stop()

    def _IfaceDisconnected(self, interface, state):
        if self._AutoReconnect:
            if self._ReconnectTimer.State != 'Running':
                self._ReconnectTimer.Resume()
                self._AttemptingConnect = True

        self._WrappedInterface.OnDisconnected()

    def _PollTriggered(self, timer, count):
        if not self._AttemptingConnect:
            self._WrappedInterface.Update(self._keepAliveQuery,
                                          self._keepAliveParams)

            self._ConnectHistory.append(self._ConnectionStatus)
            if not self._HasBeenConnected():
                self._WrappedInterface.connectionFlag = True
                self._WrappedInterface.Disconnect()

    def _NewConnectionStatus(self, command, value, qualifier):
        if not value == self._ConnectionStatus:
            self._ConnectionStatus = value
            if value == 'Connected':
                self._Connected(self, value)
            elif value == 'Disconnected':
                self._Disconnected(self, value)

            # Update the client with new connection status if subscribed.
            client_callback = self._Subscriptions.get('ConnectionStatus', None)
            if callable(client_callback):
                client_callback('ConnectionStatus', value, None)


class ServerExHandler:
    def __init__(self, Interface, clientIdleTimeout, listenRetryTime):
        """
        Wraps an EthernetServerInterfaceEx instance to provide automatic
        disconnection of idle clients.

        .. note:: Use :py:meth:`GetConnectionHandler` to instantiate the
            correct connection handler rather than instantiating
            :py:class:`ServerExHandler` directly.

        :param Interface: The interface to wrap.
        :param clientIdleTimeout: Time in seconds to allow clients to be idle
                                  before disconnecting them.
        :type clientIdleTimeout: float
        :param listenRetryTime: If StartListen fails, length of time in seconds
                                to wait before re-attempting.
        :type listenRetryTime: float
        """
        self._WrappedInterface = Interface
        self._ClientIdleTimeout = clientIdleTimeout
        self._ListenRetryTime = listenRetryTime
        self._StartListenTimeout = 0

        self._IdleScanTimer = Timer(1, self._ScanClients)
        self._IdleScanTimer.Pause()

        self._RelistenWait = Wait(self._ListenRetryTime, self._StartListen)
        self._RelistenWait.Cancel()

        self._Connected = _UnassignedEvent
        self._Disconnected = _UnassignedEvent
        self._ListenFailed = _UnassignedEvent
        self._ReceiveData = _UnassignedEvent

        # Capture interface events.
        self._WrappedInterface.Connected = self._ClientConnect
        self._WrappedInterface.Disconnected = self._ClientDisconnect
        self._WrappedInterface.ReceiveData = self._IfaceReceiveData

        # ClientObject: last_activity
        self._Clients = {}

    @property
    def Connected(self):
        """
        ``Event:`` Triggers when a socket connection is established.

        The callback function must accept two parameters. The first is the
        ConnectionHandler instance triggering the event and the second is the
        string 'Connected'.
        """
        return self._Connected

    @Connected.setter
    def Connected(self, handler):
        if callable(handler):
            self._Connected = handler
        else:
            raise TypeError("'handler' is not callable")

    @property
    def Disconnected(self):
        """
        ``Event:`` Triggers when a socket connection is broken.

        The callback function must accept two parameters. The first is the
        ConnectionHandler instance triggering the event and the second is the
        string 'Disconnected'.
        """
        return self._Disconnected

    @Disconnected.setter
    def Disconnected(self, handler):
        if callable(handler):
            self._Disconnected = handler
        else:
            raise TypeError("'handler' is not callable")

    @property
    def Interface(self):
        """
        :returns: the interface instance for which this instance is handling
            connection.
        :rtype: extronlib.interface.EthernetServerInterfaceEx
        """
        return self._WrappedInterface

    @property
    def ListenFailed(self):
        """
        ``Event:`` Triggers when StartListen fails.

        The callback function must accept two parameters. The first is the
        ConnectionHandler instance  triggering the event and the second is the
        failure reason as a string.
        """
        return self._ListenFailed

    @ListenFailed.setter
    def ListenFailed(self, handler):
        if callable(handler):
            self._ListenFailed = handler
        else:
            raise TypeError("'handler' is not callable")

    @property
    def ReceiveData(self):
        """
        ``Event:`` Triggers when data is received by the underlying interface
        instance.

        The callback function must accept two parameters. The first is the
        ClientObject instance triggering the event and the second is the
        received data as a bytes object.

        .. code-block:: python

            @event(SomeServer, 'ReceiveData')
            def HandleClientData(client, data):
                ProcessClientData(data)
        """
        return self._ReceiveData

    @ReceiveData.setter
    def ReceiveData(self, handler):
        if callable(handler):
            self._ReceiveData = handler
        else:
            raise TypeError("'handler' is not callable")

    def StartListen(self, timeout=0):
        '''
        Start the listener.

        :param timeout: length of time, in seconds, to listen for connections.
        :type timeout: float
        '''
        self._StartListenTimeout = timeout
        self._StartListen()

    def _ClientConnect(self, client, state):
        self._Clients[client] = monotonic()
        self._Connected(client, state)

        if len(self._WrappedInterface.Clients) > 0:
            self._IdleScanTimer.Restart()

    def _ClientDisconnect(self, client, state):
        del self._Clients[client]
        self._Disconnected(client, state)

        if len(self._WrappedInterface.Clients) == 0:
            self._IdleScanTimer.Pause()

    def _IfaceReceiveData(self, client, data):
        self._Clients[client] = monotonic()
        self._ReceiveData(client, data)

    def _ScanClients(self, timer, count):
        # Finding and disconnecting idle clients occurs in two steps because
        # collections can not be modified during iteration. Disconnecting a
        # client causes self._Clients to be modified in _ClientDisconnect.
        drop_list = []
        for client, last_activity in self._Clients.items():
            if (monotonic() - last_activity) > self._ClientIdleTimeout:
                drop_list.append(client)

        for client in drop_list:
            _trace('disconnecting idle client:', client.IPAddress)
            client.Disconnect()

    def _StartListen(self):
        result = self._WrappedInterface.StartListen(self._StartListenTimeout)
        if result != 'Listening':
            self._ListenFailed(self, result)
            self._RelistenWait.Restart()

    def __getattr__(self, name):
        # This function overrides the Python-supplied version of __getattr__.
        # Under the covers, accessing obj.name causes Python to first call
        # __getattribute__ on obj to lookup 'name'. If that fails Python then
        # calls __getattr__, which we can hook to implement fall-through to the
        # underlying interface instance for methods not implemented by this
        # class.
        try:
            _trace('__getattr__ trying', name)
            return self._WrappedInterface.__getattribute__(name)
        except AttributeError:
            SelfName = self.__class__.__name__
            WrappedName = self._WrappedInterface.__class__.__name__

            raise AttributeError("'{}' object has no attribute '{}' nor was "
                                 "one found in the underlying '{}' "
                                 "object.".format(SelfName, name, WrappedName))

    def __str__(self):
        listeningon = self._WrappedInterface.Interface
        return 'ConnectionHandler: Connected to Interface ' + str(listeningon)
