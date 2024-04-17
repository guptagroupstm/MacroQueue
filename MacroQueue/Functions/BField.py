import numpy as np
import time
from time import time as timer
import pyvisa
import os
import pandas as pd
from datetime import datetime

from CreaTec import Edit_Memo_Line


CurrentMacro = None
OutgoingQueue = None
Cancel = False
MacroQueueSelf = None


BField = None
BFieldPowerControl = None


def Connect_To_Power_Supply(GPIBaddress = 6):
    rm = pyvisa.ResourceManager()
    instName = f'GPIB0::{GPIBaddress}::INSTR'
    BFieldPowerControl = rm.open_resource(instName)

    BFieldPowerControl.read_termination = '\n'
    BFieldPowerControl.write_termination = '\n'
    BFieldPowerControl.write('OUTPUT OFF')

def OnClose():
    if BField is not None:
        OutgoingQueue.put(("DontClose","The Magnetic Field is not off.  Run the function 'Turn B Field Off'."))
        MacroQueueSelf.Closing=False
        



# {"Name":"B","Units":"T","Min":-1,"Max":1,"Tooltip":"The magnetic field strength in T"}
def Set_B_Field(B=1,LogPath='D:\\LabData\\BFieldLoop.csv'):
    STM = None
    try:
        STM = MacroQueueSelf.Functions[MacroQueueSelf.Software].STM
    finally:
        pass
        
    if B < -1 or B > 1:
        raise Exception(f"Bfield, {B}, out of range. Must be between -1 and 1 T.")
    # Kepco BOP 400W bipolar power supply
    # https://www.kepcopower.com/support/bop-operator-r7.pdf
    global BField, BFieldPowerControl
    Ramp_Interval=0.1
    Ramp_amount=1
    Ramp_amount = np.abs(Ramp_amount)/1000 # so ramp amount is in V

    # Test if connected to the power supply
    if BFieldPowerControl is not None:
        try:
            CurrentCurrent = float(BFieldPowerControl.query('MEAS:CURR?'))
        except Exception:
            BFieldPowerControl=None

    if BFieldPowerControl is None:
        Connect_To_Power_Supply()

    if not eval(BFieldPowerControl.query('OUTPUT?')):
        BFieldPowerControl.write('FUNC:MODE VOLT')
        BFieldPowerControl.write('VOLT 0')
        BFieldPowerControl.write('CURR 10.1')
        BFieldPowerControl.write('OUTPUT ON')


    FinalCurrent = B*10
    CurrentVoltage = float(BFieldPowerControl.query('MEAS:VOLT?'))
    BFieldPowerControl.write(f'VOLT {CurrentVoltage}')
    time.sleep(0.1)
    CurrentCurrent = float(BFieldPowerControl.query('MEAS:CURR?'))
    InitialCurrent = CurrentCurrent
    BField = CurrentCurrent/10

    if STM is not None:
        STM.setp('VERTMAN.MARKER',f'{BField}')
    Increasing = 1 if FinalCurrent > CurrentCurrent else -1

    # CurrentCurrent + Ramp_amount is a somewhat reasonable approximation for the next step
    StartTime = timer()
    # OutgoingQueue.put(("SetStatus",(f"{CurrentCurrent},{FinalCurrent},{Increasing}",4)))
    while ((Increasing*round(CurrentCurrent,3) < Increasing*FinalCurrent - Ramp_amount) or (CurrentVoltage <=  -0.02 and CurrentVoltage >= -0.03)) and not Cancel: 
        CurrentVoltage += Increasing*Ramp_amount
        CurrentVoltage = round(CurrentVoltage,3)
        BFieldPowerControl.write(f'VOLT {CurrentVoltage}')
        StartTime = timer()
        time.sleep(0.01)
        CurrentCurrent = float(BFieldPowerControl.query('MEAS:CURR?'))
        float(BFieldPowerControl.query('MEAS:VOLT?'))
        BField = CurrentCurrent/10
        if STM is not None:
            STM.setp('VERTMAN.MARKER',f'{BField}')
        if Ramp_Interval > (timer() - StartTime):
            time.sleep(Ramp_Interval - (timer() - StartTime))
        Percent = (CurrentCurrent-InitialCurrent)*100/(FinalCurrent-InitialCurrent)
        OutgoingQueue.put(("SetStatus",(f"Ramp {round(Percent,1)}% Complete",2)))

    if Cancel:
        OutgoingQueue.put(("SetStatus",("",2)))
    else:
        OutgoingQueue.put(("SetStatus",("Ramp 100% Complete",2)))
    Log_BField(LogPath)
    if STM is not None:
        Edit_Memo_Line("B",round(BField,2))

# Ramp_speed=s;How often steps are taken in seconds
# Ramp_amount=mV;How much the voltage is changed for a single step
def Turn_B_Field_Off(LogPath='D:\\LabData\\BFieldLoop.csv'):
    try:
        STM = MacroQueueSelf.Functions[MacroQueueSelf.Software].STM
    except Exception:
        STM = None
    Set_B_Field(0,LogPath)
    global BField, BFieldPowerControl
    BFieldPowerControl.write('OUTPUT OFF')
    BField = None
    if STM is not None:
        Edit_Memo_Line("B",0)





ChannelDict = {'Y':0,'X':1,'Z':2}
DirDict = {'p':0,'n':1}
ZZero = None

# {"Name":"B","Units":"T","Min":-1,"Max":1,"Tooltip":"The magnetic field strength in T"}
def Set_B_Field_Keep_Tip_Away(B=1,LogPath='D:\\LabData\\BFieldLoop.csv'):
    try:
        STM = MacroQueueSelf.Functions[MacroQueueSelf.Software].STM
    except Exception:
        STM = None
    global BField, BFieldPowerControl, Ramping, ZZero
    if BField is None:
        BField = 0
    if B > BField:
        BSteps = np.arange(BField,B,0.005)
    else:
        BSteps = np.arange(BField,B,-0.005)

    if ZZero is None:
        ZZero = STM.signals1data(2,0.1,5)
    for BStep in BSteps:
        if np.abs(BStep) >= 0.01:
            STM.setp('SLIDER.ZLIMIT.ON','ON')
            STM.setp('SLIDER.ZLIMIT.VOLT',-10)
            time.sleep(0.1)
            Set_B_Field(BStep)
            print(BStep, BField)
            time.sleep(0.1)
            STM.setp('SLIDER.ZLIMIT.ON','OFF')


            time.sleep(0.7)
            ZVoltage = STM.signals1data(2,0.1,5)
            ZNotZero = ZVoltage
            while ZVoltage > 600 and not Cancel:
                STM.setp('SLIDER.ZLIMIT.ON','ON')
                STM.setp('SLIDER.ZLIMIT.VOLT',-10)
                time.sleep(0.2)
                STM.slider(ChannelDict['Z'],DirDict['n'],0)
                time.sleep(0.5)
                STM.setp('SLIDER.ZLIMIT.ON','OFF')
                time.sleep(0.5)
                ZVoltage = STM.signals1data(2,0.1,5)
                time.sleep(0.1)
                if not ZVoltage > 600:    
                    time.sleep(5)
                    ZVoltage = STM.signals1data(2,0.1,5)
                    ZZero = ZZero + (ZVoltage - ZNotZero)
            while ZVoltage < -500 and not Cancel:
                STM.setp('SLIDER.ZLIMIT.ON','ON')
                STM.setp('SLIDER.ZLIMIT.VOLT',-10)
                time.sleep(0.2)
                STM.slider(ChannelDict['Z'],DirDict['p'],0)
                time.sleep(0.5)
                STM.setp('SLIDER.ZLIMIT.ON','OFF')
                time.sleep(0.5)
                ZVoltage = STM.signals1data(2,0.1,5)
                time.sleep(0.1)
                if not ZVoltage < -500:    
                    time.sleep(5)
                    ZVoltage = STM.signals1data(2,0.1,5)
                    ZZero = ZZero + (ZVoltage - ZNotZero)
            time.sleep(2)
            ZVoltage = STM.signals1data(2,0.1,5)
            Log_BField(LogPath)
            if Cancel:
                break
            
def Log_BField(LogPath='D:\\LabData\\BFieldLoop.csv'):    
    CurrentCurrent = float(BFieldPowerControl.query('MEAS:CURR?'))
    BField = CurrentCurrent/10
    DF = pd.DataFrame({'datetime':[datetime.now()],'BField':[BField]})
    if os.path.exists(LogPath):
        DF.to_csv(LogPath, mode='a', header=False)
    else:
        DF.to_csv(LogPath)


    


# BField_End=T;The final magnetic field strength
# Backwards=Scan the BField back to it's inital value.
# N_Repeat=The number of times the spectrum will repeat.  Only if Backwards is checked.  Must be an integer.
def BField_Spectrum(BField_End=-1, Backwards=True,N_Repeat=0):    
    global BField, Ramping
    try:
        STM = MacroQueueSelf.Functions[MacroQueueSelf.Software].STM
    except Exception:
        STM = None
        
    if BField is not None:
        StartingBField =  BField
        Time_Single_Direction = np.abs(BField_End-StartingBField)*1040/1 # Changing 1 T takes 17 minutes (1020 seconds)
    else:
        StartingBField =  0
        Time_Single_Direction = np.abs(BField_End)*1040/1 # Changing 1 T takes 17 minutes (1020 seconds)

    TotalSpectrumTime = Time_Single_Direction+2
    N_Repeat = int(np.floor(N_Repeat))
    if Backwards:
        TotalSpectrumTime*=2
        TotalSpectrumTime+=TotalSpectrumTime*N_Repeat


    STM.getp('VERTMAN.SPECLENGTH.SEC','')
    STM.setp('VERTMAN.SPECLENGTH.SEC',TotalSpectrumTime)
 

    OriginalChannels = STM.getp('VERTMAN.CHANNELS','')
    NewChannels = [channel for channel in OriginalChannels] + ['Lock-in X','Marker']
    STM.setp('VERTMAN.CHANNELS',NewChannels)

    Ramping = True

    Edit_Memo_Line("B",'Ramping')


    ImageSize = float(STM.getp('SCAN.IMAGESIZE.NM.X',""))
    STM.setp('SCAN.IMAGESIZE.NM.X',1)
    Pixels = float(STM.getp('SCAN.IMAGESIZE.PIXEL.X',''))
    STM.btn_vertspec(int(Pixels//2)+1,0)

    Set_B_Field(BField_End)
    if Backwards:
        Set_B_Field(StartingBField)
        for i in range(N_Repeat):
            Set_B_Field(BField_End)
            Set_B_Field(StartingBField)



    STM.setp('SCAN.IMAGESIZE.NM.X',ImageSize)
    Ramping = False
