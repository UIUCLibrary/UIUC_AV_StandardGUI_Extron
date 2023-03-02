# uncompyle6 version 3.9.0
# Python bytecode version base 3.5 (3350)
# Decompiled from: Python 3.5.4 (v3.5.4:3f56838, Aug  8 2017, 02:17:05) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: services/WaitService.py
# Compiled at: 2022-08-22 12:44:46
# Size of source mod 2**32: 3178 bytes
import threading, logging, time
from collections import OrderedDict

class WaitService(threading.Thread):

    def __init__(self):
        super().__init__()
        self._WaitService__kill = threading.Event()
        self._WaitService__mutex = threading.RLock()
        self._WaitService__callbacks = {}
        self._WaitService__removeCBList = []

    def stopProcess(self):
        self._WaitService__kill.set()

    def setInterval(self, callback, newTime):
        with self._WaitService__mutex:
            if callback in self._WaitService__callbacks:
                self._WaitService__callbacks[callback]['cbTime'] = newTime
                return True
            else:
                return False

    def run(self):
        while not self._WaitService__kill.is_set():
            ts = time.monotonic()
            try:
                self.processEvent(ts)
            except Exception as e:
                logging.error(e)

            te = time.monotonic()
            st = 0.01 - (te - ts)
            if st <= 0:
                pass
            else:
                time.sleep(0.01 - (te - ts))

    def processEvent(self, ts):
        with self._WaitService__mutex:
            while self._WaitService__removeCBList:
                cb_item = self._WaitService__removeCBList.pop()
                if ts >= self._WaitService__callbacks[cb_item]['cbTime']:
                    self._WaitService__callbacks.pop(cb_item)

            for callback, args in self._WaitService__callbacks.items():
                if ts >= args['cbTime']:
                    try:
                        thread = threading.Thread(target=callback, name=args['name'])
                        args['cbThread'] = thread
                        thread.start()
                        self._WaitService__removeCBList.append(callback)
                    except Exception as e:
                        logging.error(e)

    def addCallback(self, callback, cbTime, name):
        with self._WaitService__mutex:
            self._WaitService__callbacks[callback] = {'cbTime': cbTime, 'name': name}

    def delCallback(self, callback):
        with self._WaitService__mutex:
            if callback in self._WaitService__callbacks:
                self._WaitService__callbacks.pop(callback)

    @property
    def ActiveCallbacks(self):
        return len(self._WaitService__callbacks) != 0


waitService = None

def GetWaitService():
    global waitService
    if waitService is None:
        waitService = WaitService()
        waitService.start()
    return waitService


def AddWaitFunction(callback, cbTime, name):
    GetWaitService().addCallback(callback, cbTime, name)


def DeleteWaitFunction(callback):
    global waitService
    service = GetWaitService()
    service.delCallback(callback)
    if not service.ActiveCallbacks and waitService is not None:
        waitService.stopProcess()
        waitService = None


def ChgIntervalFunction(callback, newTime):
    return GetWaitService().setInterval(callback, newTime)