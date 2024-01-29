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

STM = None
BField = None
RFGenerator = None

BFieldControlThread = None
BFieldPowerControl = None
OnCloseFunctions = []




def Initialize():
    global STM, OnCloseFunctions
    pythoncom.CoInitialize()
    STM = win32com.client.Dispatch("pstmafm.stmafmrem")
    time.sleep(0.3)
    # OnCloseFunctions.append()


# {"Name":"Parameter","Units":"s","Max":10,"Min":-10,"Tooltip":"Example Tooltip"}
# {"Name":"Parameter2","Units":"m","Max":13,"Tooltip":"Example Tooltip"}
# {"Name":"Parameter3","Units":"m","Min":-12,"Tooltip":"Example Tooltip"}
def Test(Parameter=5,Parameter2=3,Parameter3=-2):
    pass

def OnClose():
    if BField is not None:
        OutgoingQueue.put(("DontClose","The Magnetic Field is not off.  Run the function 'Turn B Field Off'."))
        MacroQueueSelf.Closing=False

    if STM is not None:
        pass





# {"Name":"B","Units":"T","Min":-1,"Max":1,"Tooltip":"The magnetic field strength in T"}
def Set_B_Field(B=1):
    if B < -1 or B > 1:
        raise Exception(f"Bfield, {B}, out of range. Must be between -1 and 1 T.")
    # Kepco BOP 400W bipolar power supply
    # https://www.kepcopower.com/support/bop-operator-r7.pdf
    global BField, BFieldPowerControl, BFieldControlThread
    # Ramp_speed and Ramp_amount used to be parameters.
    # Ramp_speed=s;How often steps are taken in seconds
    # Ramp_amount=mV;How much the voltage is changed for a single step
    Ramp_Interval=0.1
    Ramp_amount=1
    # Make sure current stays below +/- 10 A
    # Hard limit on ramp speed

    # 10 Amps is 1 T

    # if np.abs(Ramp_speed*Ramp_amount) > 0.105:
    #     raise Exception(f"The magnetic field is ramping too much, too fast.  {Ramp_Interval*Ramp_amount} > 0.105.")
    Ramp_amount = np.abs(Ramp_amount)/1000 # so ramp amount is in V

    # Test if connected to the power supply
    if BFieldPowerControl is not None:
        try:
            CurrentCurrent = float(BFieldPowerControl.query('MEAS:CURR?'))
        except:
            BFieldPowerControl=None
    if BFieldPowerControl is None:
        rm = pyvisa.ResourceManager()
        GPIBaddress = 6
        instName = f'GPIB0::{GPIBaddress}::INSTR'
        BFieldPowerControl = rm.open_resource(instName)

        BFieldPowerControl.read_termination = '\n'
        BFieldPowerControl.write_termination = '\n'
        BFieldPowerControl.write('OUTPUT OFF')

    if eval(BFieldPowerControl.query('OUTPUT?'))==False:
        BFieldPowerControl.write('FUNC:MODE VOLT')
        BFieldPowerControl.write('VOLT 0')
        BFieldPowerControl.write('CURR 10.1')
        BFieldPowerControl.write('OUTPUT ON')


    # if BFieldControlThread is None:
    #     def BFieldControlThreadFunction():
    #         pass
    #     # BFieldControlThread = 
    FinalCurrent = B*10
    CurrentVoltage = float(BFieldPowerControl.query('MEAS:VOLT?'))
    BFieldPowerControl.write(f'VOLT {CurrentVoltage}')
    CurrentCurrent = float(BFieldPowerControl.query('MEAS:CURR?'))
    InitialCurrent = CurrentCurrent
    BField = CurrentCurrent/10
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
        CurrentCurrent = float(BFieldPowerControl.query('MEAS:CURR?'))
        MeasuredVoltage = float(BFieldPowerControl.query('MEAS:VOLT?'))
        BField = CurrentCurrent/10
        STM.setp('VERTMAN.MARKER',f'{BField}')
        if Ramp_Interval > (timer() - StartTime):
            time.sleep(Ramp_Interval - (timer() - StartTime))
        Percent = (CurrentCurrent-InitialCurrent)*100/(FinalCurrent-InitialCurrent)
        OutgoingQueue.put(("SetStatus",(f"Ramp {round(Percent,1)}% Complete",2)))


    # Ramp_amount /= 2
    # NOverShoots = 0
    # Increasing = 1 if FinalCurrent > CurrentCurrent else -1
    # while (Increasing*round(CurrentCurrent,5) < Increasing*FinalCurrent - Ramp_amount) and not Cancel and NOverShoots < 5: 
    #     CurrentVoltage += Increasing*Ramp_amount
    #     CurrentVoltage = round(CurrentVoltage,6)
    #     BFieldPowerControl.write(f'VOLT {CurrentVoltage}')
    #     StartTime = timer()
    #     CurrentCurrent = float(BFieldPowerControl.query('MEAS:CURR?'))
    #     MeasuredVoltage = float(BFieldPowerControl.query('MEAS:VOLT?'))
    #     if Ramp_speed > (timer() - StartTime):
    #         time.sleep(Ramp_speed - (timer() - StartTime))
    #     BField = CurrentCurrent/10

    #     OldIncreasing = Increasing
    #     Increasing = 1 if FinalCurrent > CurrentCurrent else -1
    #     if Increasing != OldIncreasing:
    #         Ramp_amount /= 2
    #         NOverShoots += 1



    if Cancel:
        OutgoingQueue.put(("SetStatus",(f"",2)))
    else:
        OutgoingQueue.put(("SetStatus",(f"Ramp 100% Complete",2)))
    if STM is not None:
        STM.setp('MEMO.SET', f"B = {round(BField,1)} T")

# Ramp_speed=s;How often steps are taken in seconds
# Ramp_amount=mV;How much the voltage is changed for a single step
def Turn_B_Field_Off():
    Set_B_Field(0)
    global BField, BFieldPowerControl
    BFieldPowerControl.write('OUTPUT OFF')
    BField = None
    if STM is not None:
        STM.setp('MEMO.SET', 'B = 0T; Output Off.')

# BField_End=T;The final magnetic field strength
# N_Datapoints=The number of datapoints in a single direction of the spectrum
# Backwards=Scan the BField back to it's inital value.
# N_Repeat=The number of times the spectrum will repeat.  Only if Backwards is checked.  Must be an integer.
def BField_Spectrum(BField_End=-1, N_Datapoints=1024, Backwards=True,N_Repeat=0):    
    global BField
    if BField is not None:
        StartingBField =  BField
        Time_Single_Direction = np.abs(BField_End-StartingBField)*1020/1 # Changing 1 T takes 17 minutes (1020 seconds)
    else:
        StartingBField =  0
        Time_Single_Direction = np.abs(BField_End)*1020/1 # Changing 1 T takes 17 minutes (1020 seconds)

    TotalSpectrumTime = Time_Single_Direction
    TotalN_Datapoints = N_Datapoints
    N_Repeat = int(np.floor(N_Repeat))
    if Backwards:
        TotalSpectrumTime*=2
        TotalSpectrumTime+=TotalSpectrumTime*N_Repeat

        TotalN_Datapoints*=2
        TotalN_Datapoints+=TotalN_Datapoints*N_Repeat

    OriginalSpectraTable = STM.getp('VERTMAN.IVTABLE','')    
    SpecListGrid = list(map(list,OriginalSpectraTable))
    TableLength = len(SpecListGrid[0])
    for i in range(5):
        SpecListGrid[i] = [0 for j in range(TableLength)]
    SpecListGrid[0][1] = TotalN_Datapoints
    NewSpecGrid = tuple(map(tuple,SpecListGrid))
    STM.setp('VERTMAN.IVTABLE',NewSpecGrid)    
    OriginalLength = STM.getp('VERTMAN.SPECLENGTH.SEC','')
    STM.setp('VERTMAN.SPECLENGTH.SEC',TotalSpectrumTime)
    OriginalVFBMode = STM.getp('VERTMAN.VFB_MODE','')
    STM.setp('VERTMAN.VFB_MODE',"z(V)")
    OriginalVFBCurrent = STM.getp('VERTMAN.VFB_CURRENT.NAMP' ,'')
    Setpoint = float(STM.getp('SCAN.SETPOINT.AMPERE',''))
    STM.setp('VERTMAN.VFB_CURRENT.NAMP',Setpoint*1e9)
 

    OriginalChannels = STM.getp('VERTMAN.CHANNELS','')
    NewChannels = [channel for channel in OriginalChannels] + ['Lock-in X','Marker']
    STM.setp('VERTMAN.CHANNELS',NewChannels)


    Pixels = float(STM.getp('SCAN.IMAGESIZE.PIXEL.X',''))
    STM.btn_vertspec(int(Pixels//2)+1,0)

    memo = f'BField Spectrum from {StartingBField} T to {BField_End} T'
    STM.setp('MEMO.SET', memo)
    Set_B_Field(BField_End)
    if Backwards:
        Set_B_Field(StartingBField)
        for i in range(N_Repeat):
            Set_B_Field(BField_End)
            Set_B_Field(StartingBField)

    STM.setp('VERTMAN.IVTABLE',OriginalSpectraTable)    
    STM.setp('VERTMAN.CHANNELS',OriginalChannels)
    STM.setp('VERTMAN.SPECLENGTH.SEC',OriginalLength)
    STM.setp('VERTMAN.VFB_MODE',OriginalVFBMode)
    STM.setp('VERTMAN.VFB_CURRENT.NAMP',OriginalVFBCurrent)



# # Ramp_speed=s;How often steps are taken in seconds
# # Ramp_amount=mV;How much the voltage is changed for a single step
# def BField_Spectra(Final_BField=-1,Ramp_speed=0.1,Ramp_amount=1):
#     # OriginalTable = np.array(STM.getp('VERTMAN.IVTABLE',''))
#     # NewTable = OriginalTable.copy()
#     # NewTable[1,2] = 2000
#     # STM.setp('VERTMAN.IVTABLE',tuple(map(tuple,NewTable)))
#     pass

ChannelDict = {'Y':0,'X':1,'Z':2}
DirDict = {'p':0,'n':1}


def Approach():
    STM.setp('HVAMPCOARSE.CHK.BURST.Z','OFF')
    time.sleep(0.1)
    STM.setp('HVAMPCOARSE.CHK.RETRACT_TIP_AFTER_APPROACH','OFF')
    time.sleep(0.1)


    STM.setp('HVAMPCOARSE.APPROACH.START','ON')
    time.sleep(0.1)
    while not STM.getp('HVAMPCOARSE.APPROACH.Finished','') and not Cancel:
        time.sleep(0.01)
        pass
    if Cancel:
        STM.setp('HVAMPCOARSE.APPROACH.STOP','ON')
        time.sleep(0.1)
    if not Cancel:
        time.sleep(1)
    if not Cancel:
        # PulseHeight = STM.getp('HVAMPCOARSE.PULSEHEIGHT.VOLT','')
        # PulseDuration = STM.getp('HVAMPCOARSE.PULSEDURATION.SEC','')
        # STM.setp('HVAMPCOARSE.PULSEHEIGHT.VOLT',35)
        # STM.setp('HVAMPCOARSE.PULSEDURATION.SEC',0.001)
        ZVoltage = STM.signals1data(2,0.1,5)
        if ZVoltage > 300:
            STM.slider(ChannelDict['Z'],DirDict['n'],0)
            ZVoltage = STM.signals1data(2,0.1,5)
        # STM.setp('HVAMPCOARSE.PULSEHEIGHT.VOLT',PulseHeight)
        # STM.setp('HVAMPCOARSE.PULSEDURATION.SEC',PulseDuration)

    

# NBursts=Number of Z steps to retract
def Z_Course_Steps_Out(NBursts = 3):
    STM.setp('HVAMPCOARSE.CHK.BURST.Z','ON')
    time.sleep(0.1)
    for i in range(NBursts):
        STM.slider(ChannelDict['Z'],DirDict['p'],0)
        time.sleep(0.2)

# def Z_Course_Step_In(Parameter1= 0):
#     pass


# Burst_XY=Check Burst XY in the Course Positioning Form
def Burst_XY(Burst_XY=True):    
    if Burst_XY:
        STM.setp('HVAMPCOARSE.CHK.BURST.XY','ON')
        time.sleep(0.1)
    else:
        STM.setp('HVAMPCOARSE.CHK.BURST.XY','OFF')
        time.sleep(0.1)

# Burst_XY=Check Burst Z in the Course Positioning Form
def Burst_Z(Burst_Z=True):
    if Burst_Z:
        STM.setp('HVAMPCOARSE.CHK.BURST.Z','ON')
        time.sleep(0.1)
    else:
        STM.setp('HVAMPCOARSE.CHK.BURST.Z','OFF')
        time.sleep(0.1)


CourseX = 0
CourseY = 0
def Define_as_Course_Origin():
    global CourseX,CourseY
    CourseX = 0
    CourseY = 0

# X_Position=The X position to course move to.
# Y_Position=The Y position to course move to.
# NSteps_Out=The number of Z steps to retract before course moving in X and Y
def XYCourse_Step(NSteps_Out=3,X_Position=0,Y_Position=0):
    STM.setp('HVAMPCOARSE.CHK.BURST.Z','ON')
    time.sleep(0.1)
    for i in range(NSteps_Out):
        STM.slider(ChannelDict['Z'],DirDict['p'],0)
        time.sleep(0.1)
    XSteps = int(X_Position - CourseX)
    if XSteps == 0:
        pass
    elif XSteps > 0:
        for i in range(np.abs(XSteps)):
            STM.slider(ChannelDict['X'],DirDict['p'],0)
            time.sleep(0.1)
    elif XSteps < 0:
        for i in range(np.abs(XSteps)):
            STM.slider(ChannelDict['X'],DirDict['n'],0)
            time.sleep(0.1)

    
    YSteps = int(Y_Position - CourseY)
    if YSteps == 0:
        pass
    elif YSteps > 0:
        for i in range(np.abs(YSteps)):
            STM.slider(ChannelDict['Y'],DirDict['p'],0)
            time.sleep(0.1)
    elif YSteps < 0:
        for i in range(np.abs(YSteps)):
            STM.slider(ChannelDict['Y'],DirDict['n'],0)
            time.sleep(0.1)



def AutoPhase():
    Bias = STM.getp('SCAN.BIASVOLTAGE.VOLT','')
    STM.setp('LOCK-IN.MODE','Internal ')
    time.sleep(0.1)
    STM.setp('SCAN.BIASVOLTAGE.VOLT',Bias)
    time.sleep(3)
    STM.setp('LOCK-IN.BTN.AUTOPHASE','ON')
    time.sleep(1)
    Phase = STM.getp('LOCK-IN.PHASE1.DEG','')
    STM.setp('LOCK-IN.PHASE1.DEG',float(Phase)-90)
    time.sleep(0.1)

    time.sleep(1)
    STM.setp('LOCK-IN.MODE','Internal + Spectrum only')
    time.sleep(0.1)
    STM.setp('SCAN.BIASVOLTAGE.VOLT',Bias)
    time.sleep(0.1)

# Lockin_Freq=Hz;The lock-in frequency in Hz
def Set_LockIn_Frequency(Lockin_Freq=877):
    STM.setp('LOCK-IN.FREQ.HZ',Lockin_Freq)
    time.sleep(0.1)


# Lockin_RC=Hz;The lock-in time constant in Hz
def Set_LockIn_TimeConstant(Lockin_RC=100):
    STM.setp('LOCK-IN.RC.HZ',Lockin_RC)
    time.sleep(0.1)

# Lockin_Amp=mV;The lock-in voltage amplitude in mV
def Set_LockIn_Amplitude(Lockin_Amp=100):
    STM.setp('LOCK-IN.AMPLITUDE.MVPP',Lockin_Amp)
    time.sleep(0.1)

# Lockin_RefA=mV;The lock-in reference voltage amplitude in mV
def Set_LockIn_RefAmplitude(Lockin_RefA=2000):
    STM.setp('LOCK-IN.REFAMPLITUDE.MVPP',Lockin_RefA)
    time.sleep(0.1)


# {"Name":"Bias","Units":"V","Min":-10,"Max":10,"Tooltip":"The bias voltage in V"}
def Set_Bias(Bias= 0):
    STM.setp('SCAN.BIASVOLTAGE.VOLT',Bias)
    time.sleep(0.1)



# {"Name":"Setpoint","Units":"pA","Min":0,"Max":1e6,"Tooltip":"The current setpoint in pA"}
def Set_Setpoint(Setpoint=100):
    Setpoint *= 1e-12 #Convert from pA to A
    STM.setp('SCAN.SETPOINT.AMPERE',Setpoint)
    time.sleep(0.1)


# XOffset=The X center of the image in nm, or Image Coordinate, or V
# YOffset=The Y top of the image in nm, or Image Coordinate, or V
def Set_Scan_Window_Position(HowToSetPosition=['nm','Image Coord','Voltage'],XOffset=0,YOffset=0):
    if HowToSetPosition == 'nm':
        # CreaTec doesn't know what NM means...
        STM.setp('STMAFM.CMD.SETXYOFF.NM',(XOffset,YOffset))
        time.sleep(0.1)
    elif HowToSetPosition == 'Image Coord':
        STM.setp('STMAFM.CMD.SETXYOFF.IMAGECOORD',(XOffset,YOffset))
        time.sleep(0.1)
    elif HowToSetPosition == 'Voltage':
        STM.setp('STMAFM.CMD.SETXYOFF.VOLT',(XOffset,YOffset))
        time.sleep(0.1)

# XOffset=The X position of the tip in nm, or Image Coordinate, or V
# YOffset=The Y X position of the tip in nm, or Image Coordinate, or V
def Fine_Move_Tip(HowToSetPosition=['nm','Image Coord','Voltage'],XOffset=0,YOffset=0):
    if HowToSetPosition == 'nm':
        XOffset *= 10
        YOffset *= 10
        # Not sure if this command actually uses nm
        STM.setp('STMAFM.CMD.SETXYOFF.NM',(XOffset,YOffset))
        time.sleep(0.1)
    elif HowToSetPosition == 'Image Coord':
        STM.setp('STMAFM.CMD.SETXYOFF.IMAGECOORD',(XOffset,YOffset))
        time.sleep(0.1)
    elif HowToSetPosition == 'Voltage':
        STM.setp('STMAFM.CMD.SETXYOFF.VOLT',(XOffset,YOffset))
        time.sleep(0.1)

    
    


# HowToSetSize=Choose to set the Image Size in Å directly or the Resolution in Å/pixel
# ImageSize=Å;The length of a row and column in Å or Å/pixel
def Set_Scan_Image_Size(HowToSetSize=['Image Size','Resolution'],ImageSize=100):
    ImageSize /= 10 # for A
    if HowToSetSize == 'Image Size':
        pass
    if HowToSetSize == 'Resolution':
        Pixels = float(STM.getp('SCAN.IMAGESIZE.PIXEL.X',''))
        ImageSize *= Pixels
    STM.setp('SCAN.IMAGESIZE.NM.X',ImageSize)
    time.sleep(0.1)


# Angle=degrees;The angle on the scan in degrees
def Set_Scan_Window_Angle(Angle=0):
    STM.setp('SCAN.ROTATION.DEG',Angle)
    time.sleep(0.1)

# NPixels=The number of pixels in each row and each column
def Set_NPixels(NPixels=512):
    STM.setp('SCAN.IMAGESIZE.PIXEL', (NPixels, NPixels))
    time.sleep(0.1)

# LineSpeed=nm/s;The speed the tip moves in nm/s
# def Set_Scan_Speed(Speed=2):
    
# HowToSetSpeed=Choose how the Image Speed is set
# Speed=The speed the tip moves in nm/s, s/line, or s/pixel
def Set_Scan_Speed(HowToSetSpeed=['nm/s','s/line','s/pixel'],Speed=2):    
    if HowToSetSpeed == 'nm/s':
        pass
    if HowToSetSpeed == 's/line':
        Size = float(STM.getp('SCAN.IMAGESIZE.NM.X',''))
        Speed = Size/Speed
    if HowToSetSpeed == 's/pixel':
        Size = float(STM.getp('SCAN.IMAGESIZE.NM.X',''))
        Pixels = float(STM.getp('SCAN.IMAGESIZE.PIXEL.X',''))
        Speed = Size/(Speed*Pixels)
    STM.setp('SCAN.SPEED.NM/SEC',Speed)
    time.sleep(0.1)


def Set_Recorded_Channels(Topography=True,Current=True,LockInX=True):
    Channels = []
    if Topography:
        Channels.append('TOPOGRAPHY')
    if Current:
        Channels.append('CURRENT')
    if LockInX:
        Channels.append('Lock-in X')
    Channels = list(Channels)
    STM.setp('SCAN.CHANNELS',Channels)
    time.sleep(0.1)

def Scan():
    Size = float(STM.getp('SCAN.IMAGESIZE.NM.X',''))
    Lines = float(STM.getp('SCAN.IMAGESIZE.PIXEL.Y',''))
    Speed = float(STM.getp('SCAN.SPEED.NM/SEC',""))
    ScanTime = 2*Lines * Size/Speed
    CheckTime = int(np.ceil(ScanTime/500))
    # Time = 0 if Time <= 0 else Time

    # STM.setp('SCAN.CHANNELS',('TOPOGRAPHY','CURRENT'))
    time.sleep(1)
    STM.setp('STMAFM.BTN.START' ,'')
    time.sleep(0.1)
    StartTime = timer()
    Status = STM.getp('STMAFM.SCANSTATUS','')
    while Status == 2 and not Cancel:
        Status = STM.getp('STMAFM.SCANSTATUS','')
        StartCheckTime = timer()
        while not Cancel and timer() - StartCheckTime < CheckTime:
            Percent = round(100*((timer() - StartTime)/ScanTime),1)
            OutgoingQueue.put(("SetStatus",(f"Scan {Percent}% Complete",2)))
            time.sleep(1)
    if Cancel:
        STM.setp('STMAFM.BTN.STOP',"")
        time.sleep(0.1)
        OutgoingQueue.put(("SetStatus",(f"",2)))
        while Status != 0:
            Status = STM.getp('STMAFM.SCANSTATUS','')

def dIdV_Scan():
    Size = float(STM.getp('SCAN.IMAGESIZE.NM.X',''))
    Lines = float(STM.getp('SCAN.IMAGESIZE.PIXEL.Y',''))
    Speed = float(STM.getp('SCAN.SPEED.NM/SEC',""))
    ScanTime = 2*Lines * Size/Speed
    CheckTime = int(np.ceil(ScanTime/500))
    # STM.setp('LOCK-IN.CHANNEL','ADC0')
    STM.setp('LOCK-IN.MODE','Internal ')
    # STM.setp('SCAN.CHANNELS',('TOPOGRAPHY','CURRENT','Lock-in X'))
    time.sleep(1)
    STM.setp('STMAFM.BTN.START' ,'')
    time.sleep(0.1)
    StartTime = timer()
    Status = STM.getp('STMAFM.SCANSTATUS','')
    while Status == 2 and not Cancel:
        Status = STM.getp('STMAFM.SCANSTATUS','')
        StartCheckTime = timer()
        while not Cancel and timer() - StartCheckTime < CheckTime:
            Percent = round(100*((timer() - StartTime)/ScanTime),1)
            OutgoingQueue.put(("SetStatus",(f"Scan {Percent}% Complete",2)))
            time.sleep(1)
    if Cancel:
        STM.setp('STMAFM.BTN.STOP','')
        time.sleep(0.1)
        OutgoingQueue.put(("SetStatus",(f"",2)))
        while Status != 0:
            Status = STM.getp('STMAFM.SCANSTATUS','')
    
    Bias = STM.getp('SCAN.BIASVOLTAGE.VOLT','')
    STM.setp('LOCK-IN.MODE','Internal + Spectrum only')
    time.sleep(0.1)
    STM.setp('SCAN.BIASVOLTAGE.VOLT',Bias)
    time.sleep(0.1)

# FinalBias=V;The final bias for the spectrum.  
# N_Datapoints=The number of data points for a single direction
# Time=s;The duration of the spectrum for a single direction
def Set_Spectrum_Table(Final_Bias=1, N_Datapoints=1024, Time=60):
    OriginalSpectraTable = STM.getp('VERTMAN.IVTABLE','')    
    SpecListGrid = list(map(list,OriginalSpectraTable))
    TableLength = len(SpecListGrid[0])
    for i in range(5):
        SpecListGrid[i] = [0 for j in range(TableLength)]
    SpecListGrid[0][1] = N_Datapoints
    Inital_Bias = STM.getp('SCAN.BIASVOLTAGE.VOLT','')
    SpecListGrid[1][0] = Inital_Bias
    SpecListGrid[1][1] = Final_Bias
    NewSpecGrid = tuple(map(tuple,SpecListGrid))
    STM.setp('VERTMAN.IVTABLE',NewSpecGrid)    
    OriginalLength = STM.getp('VERTMAN.SPECLENGTH.SEC','')
    STM.setp('VERTMAN.SPECLENGTH.SEC',Time)


def Spectrum():
    Pixels = float(STM.getp('SCAN.IMAGESIZE.PIXEL.X',''))
    STM.btn_vertspec(int(Pixels//2)+1,0)
    Status = STM.getp('STMAFM.SCANSTATUS','')

def Test(LogPath='Magnetic.csv'):
    DF = pd.DataFrame({'datetime':[datetime.now()],'bye':[20]})
    if os.path.exists(LogPath):
        DF.to_csv(LogPath, mode='a', header=False)
    else:
        DF.to_csv(LogPath)

if __name__ == "__main__":
    pass
    # Initialize()
    # Spectrum()
    # Scan()
