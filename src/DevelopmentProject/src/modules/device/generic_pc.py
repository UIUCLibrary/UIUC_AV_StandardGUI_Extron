class PCClass:
    def __init__(self, **kwargs) -> None:
        pass
    
    def OnConnected(self):
        pass

    def OnDisconnected(self):
        pass

    def Set(self, command, value, qualifier=None):
        pass

    def Update(self, command, qualifier=None):
        pass

    def SubscribeStatus(self, command, qualifier, callback):
        pass

    def NewStatus(self, command, value, qualifier):
        pass

    def WriteStatus(self, command, value, qualifier=None):
        pass

    def ReadStatus(self, command, qualifier=None):
        pass