import sys
sys.path.append("./components/")
import time
import datetime
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg
import numpy as np

TEST = False
try:
    import RPi.GPIO as GPIO
    import AIO
except:
    print("no RPi.GPIO or AIO")
    TEST = True

# must inherit QtCore.QObject in order to use 'connect'
class Worker(QtCore.QObject):

    sigStep = QtCore.pyqtSignal(str, np.ndarray)
    sigDone = QtCore.pyqtSignal(int, str)
    sigMsg = QtCore.pyqtSignal(str)

    def __init__(self, id: int, type: str, app: QtGui.QApplication):
        super().__init__()
        self.__id = id
        self.type = type
        self.__app = app
        self.__abort = False
        self.data = np.zeros(shape=(10, 2))

    @QtCore.pyqtSlot()
    def work(self):
        self.__setThread()
        if TEST:
            if self.type == "Temperature":
                pass
            elif self.type == "Pressure1":
                pass
            elif self.type == "Pressure2":
                pass
            else:
                return
            self.__test()
        else:
            pass

    def abort(self):
        self.sigMsg.emit("Worker #{} aborting acquisition".format(self.__id))
        self.__abort = True

    @QtCore.pyqtSlot()
    def __setThread(self):
        threadName = QtCore.QThread.currentThread().objectName()
        threadId = int(QtCore.QThread.currentThreadId())

        self.sigMsg.emit(
            "Running worker #{} from thread '{}' (#{})".format(self.__id, threadName, threadId)
        )

    @QtCore.pyqtSlot()
    def __test(self):
        startTime = datetime.datetime.now()
        totalStep = 0
        step = 0
        while not (self.__abort):
            time.sleep(0.01)
            currentTime = datetime.datetime.now()
            deltaSeconds = (currentTime - startTime).total_seconds()

            # TODO: 実際のデータをとる
            self.data[step] = [deltaSeconds, np.random.normal()*10]

            if step%9 == 0 and step!=0:
                self.sigStep.emit(self.type, self.data)
                self.data = np.zeros(shape=(10, 2))
                step = 0
            else:
                step += 1
            totalStep += 1

            self.__app.processEvents()

        else:
            if self.data[step][0] == 0.0:
                step -= 1
            if step > -1:
                self.sigStep.emit(self.type, self.data[:step+1, :])
            self.sigMsg.emit(
                "Worker #{} aborting work at step {}".format(self.__id, totalStep)
            )
        self.sigDone.emit(self.__id, self.type)
        return
