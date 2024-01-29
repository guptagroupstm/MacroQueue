import numpy as np
import time
import win32com.client
from time import time as timer
import pyvisa
import pythoncom
import wx
import threading
import os
import pandas as pd
from datetime import datetime

CurrentMacro = None
OutgoingQueue = None
Cancel = False
MacroQueueSelf = None

BField = None
STM = None
BFieldPowerControl = None
MacroQueueSelf = None

def OnClose():
    if BField is not None:
        OutgoingQueue.put(("DontClose","The Magnetic Field is not off.  Run the function 'Turn B Field Off'."))
        MacroQueueSelf.Closing=False


def BFTest():
    global STM
    if BFieldPowerControl is None:
        rm = pyvisa.ResourceManager()
        GPIBaddress = 6
        instName = f'GPIB0::{GPIBaddress}::INSTR'
        BFieldPowerControl = rm.open_resource(instName)

        BFieldPowerControl.read_termination = '\n'
        BFieldPowerControl.write_termination = '\n'
        BFieldPowerControl.write('OUTPUT OFF')
        STM = MacroQueueSelf.Functions[MacroQueueSelf.Software].STM

