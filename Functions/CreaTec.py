import numpy as np
import time
import win32com.client
from time import time as timer
import pyvisa
import pythoncom
import wx
import threading

STM = None
CurrentMacro = None
OutgoingQueue = None
Cancel = False
BField = None
BFieldControlThread = None
BFieldPowerControl = None
MacroQueueSelf = None
OnCloseFunctions = []

def Initialize():
    global STM, OnCloseFunctions
    pythoncom.CoInitialize()
    STM = win32com.client.Dispatch("pstmafm.stmafmrem")
    time.sleep(0.1)
    # OnCloseFunctions.append()


def OnClose():
    # STM.release()
    # global OnCloseFunctions
    # for f in OnCloseFunctions:
    #     f()
    
    if BField is not None:
        OutgoingQueue.put(("DontClose","The Magnetic Field is not off.  Run the function 'Turn B Field Off'."))
        MacroQueueSelf.Closing=False

    if STM is not None:
        pass


# B=T;The magnetic field strength in T
def Set_B_Field(B=1):
    # Kepco BOP 400W bipolar power supply
    # https://www.kepcopower.com/support/bop-operator-r7.pdf
    global BField, BFieldPowerControl, BFieldControlThread
    # Ramp_speed and Ramp_amount used to be parameters.
    # Ramp_speed=s;How often steps are taken in seconds
    # Ramp_amount=mV;How much the voltage is changed for a single step
    Ramp_speed=0.1
    Ramp_amount=1
    # Make sure current stays below +/- 10 A
    # Hard limit on ramp speed

    # 10 Amps is 1 T

    # if np.abs(Ramp_speed*Ramp_amount) > 0.105:
    #     raise Exception(f"The magnetic field is ramping too much, too fast.  {Ramp_speed*Ramp_amount} > 0.105.")
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
        if Ramp_speed > (timer() - StartTime):
            time.sleep(Ramp_speed - (timer() - StartTime))
        BField = CurrentCurrent/10
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
    STM.setp('HVAMPCOARSE.CHK.RETRACT_TIP_AFTER_APPROACH','OFF')


    STM.setp('HVAMPCOARSE.APPROACH.START','ON')
    while not STM.getp('HVAMPCOARSE.APPROACH.Finished','') and not Cancel:
        time.sleep(0.01)
        pass
    if Cancel:
        STM.setp('HVAMPCOARSE.APPROACH.STOP','ON')
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
    for i in range(NBursts):
        STM.slider(ChannelDict['Z'],DirDict['p'],0)

# def Z_Course_Step_In(Parameter1= 0):
#     pass


# Burst_XY=Check Burst XY in the Course Positioning Form
def Burst_XY(Burst_XY=True):    
    if Burst_XY:
        STM.setp('HVAMPCOARSE.CHK.BURST.XY','ON')
    else:
        STM.setp('HVAMPCOARSE.CHK.BURST.XY','OFF')

# Burst_XY=Check Burst Z in the Course Positioning Form
def Burst_Z(Burst_Z=True):
    if Burst_Z:
        STM.setp('HVAMPCOARSE.CHK.BURST.Z','ON')
    else:
        STM.setp('HVAMPCOARSE.CHK.BURST.Z','OFF')


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
    for i in range(NSteps_Out):
        STM.slider(ChannelDict['Z'],DirDict['p'],0)
    XSteps = int(X_Position - CourseX)
    if XSteps == 0:
        pass
    elif XSteps > 0:
        for i in range(np.abs(XSteps)):
            STM.slider(ChannelDict['X'],DirDict['p'],0)
    elif XSteps < 0:
        for i in range(np.abs(XSteps)):
            STM.slider(ChannelDict['X'],DirDict['n'],0)

    
    YSteps = int(Y_Position - CourseY)
    if YSteps == 0:
        pass
    elif YSteps > 0:
        for i in range(np.abs(YSteps)):
            STM.slider(ChannelDict['Y'],DirDict['p'],0)
    elif YSteps < 0:
        for i in range(np.abs(YSteps)):
            STM.slider(ChannelDict['Y'],DirDict['n'],0)



def AutoPhase():
    Bias = STM.getp('SCAN.BIASVOLTAGE.VOLT','')
    STM.setp('LOCK-IN.MODE','Internal ')
    STM.setp('SCAN.BIASVOLTAGE.VOLT',Bias)
    time.sleep(3)
    STM.setp('LOCK-IN.BTN.AUTOPHASE','ON')
    time.sleep(1)
    Phase = STM.getp('LOCK-IN.PHASE1.DEG','')
    STM.setp('LOCK-IN.PHASE1.DEG',float(Phase)-90)

    time.sleep(1)
    STM.setp('LOCK-IN.MODE','Internal + Spectrum only')
    STM.setp('SCAN.BIASVOLTAGE.VOLT',Bias)

# Lockin_Freq=Hz;The lock-in frequency in Hz
def Set_LockIn_Frequency(Lockin_Freq=877):
    STM.setp('LOCK-IN.FREQ.HZ',Lockin_Freq)


# Lockin_RC=Hz;The lock-in time constant in Hz
def Set_LockIn_TimeConstant(Lockin_RC=100):
    STM.setp('LOCK-IN.RC.HZ',Lockin_RC)

# Lockin_Amp=mV;The lock-in voltage amplitude in mV
def Set_LockIn_Amplitude(Lockin_Amp=100):
    STM.setp('LOCK-IN.AMPLITUDE.MVPP',Lockin_Amp)

# Lockin_RefA=mV;The lock-in reference voltage amplitude in mV
def Set_LockIn_RefAmplitude(Lockin_RefA=2000):
    STM.setp('LOCK-IN.REFAMPLITUDE.MVPP',Lockin_RefA)

# Bias=V;The bias voltage in V
def Set_Bias(Bias= 0):
    STM.setp('SCAN.BIASVOLTAGE.VOLT',Bias)



# Setpoint=pA;The current setpoint in pA
def Set_Setpoint(Setpoint=100):
    Setpoint *= 1e-12 #Convert from pA to A
    STM.setp('SCAN.SETPOINT.AMPERE',Setpoint)


# XOffset=The X center of the image in nm, or Image Coordinate, or V
# YOffset=The Y top of the image in nm, or Image Coordinate, or V
def Set_Scan_Window_Position(HowToSetPosition=['nm','Image Coord','Voltage'],XOffset=0,YOffset=0):
    if HowToSetPosition == 'nm':
        XOffset *= 10
        YOffset *= 10
        # CreaTec doesn't know what NM means...
        STM.setp('STMAFM.CMD.SETXYOFF.NM',(XOffset,YOffset))
    elif HowToSetPosition == 'Image Coord':
        STM.setp('STMAFM.CMD.SETXYOFF.IMAGECOORD',(XOffset,YOffset))
    elif HowToSetPosition == 'Voltage':
        STM.setp('STMAFM.CMD.SETXYOFF.VOLT',(XOffset,YOffset))

# XOffset=The X position of the tip in nm, or Image Coordinate, or V
# YOffset=The Y X position of the tip in nm, or Image Coordinate, or V
def Fine_Move_Tip(HowToSetPosition=['nm','Image Coord','Voltage'],XOffset=0,YOffset=0):
    if HowToSetPosition == 'nm':
        XOffset *= 10
        YOffset *= 10
        # Not sure if this command actually uses nm
        STM.setp('STMAFM.CMD.SETXYOFF.NM',(XOffset,YOffset))
    elif HowToSetPosition == 'Image Coord':
        STM.setp('STMAFM.CMD.SETXYOFF.IMAGECOORD',(XOffset,YOffset))
    elif HowToSetPosition == 'Voltage':
        STM.setp('STMAFM.CMD.SETXYOFF.VOLT',(XOffset,YOffset))

    
    


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


# Angle=degrees;The angle on the scan in degrees
def Set_Scan_Window_Angle(Angle=0):
    STM.setp('SCAN.ROTATION.DEG',Angle)

# NPixels=The number of pixels in each row and each column
def Set_NPixels(NPixels=512):
    STM.setp('SCAN.IMAGESIZE.PIXEL', (NPixels, NPixels))

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
        OutgoingQueue.put(("SetStatus",(f"",2)))
        while Status != 0:
            Status = STM.getp('STMAFM.SCANSTATUS','')
    
    Bias = STM.getp('SCAN.BIASVOLTAGE.VOLT','')
    STM.setp('LOCK-IN.MODE','Internal + Spectrum only')
    STM.setp('SCAN.BIASVOLTAGE.VOLT',Bias)


# # Initial_Voltage=V;The starting voltage in V
# # Final_Voltage=V;The final voltage in V
# # Stabilize_Time=s;The time to wait before starting a spectrum.
# # Total_Spectrum_Time=s;The time a single spectrum will take.
# # NDatapoints;The number of datapoints to record
# def Set_Spectrum_Voltage(Initial_Voltage=1,Final_Voltage=-1,Stabilize_Time=1,Total_Spectrum_Time=60,NDatapoints=1000):
#     pass

# # Spectrum_Backwards;  *****
# # Spectrum_Repeat;The number of times to repeat the spectrum.
# # SpectrumAverage;The number of spectra to take and average to reduce noise.
# def Set_Spectrum_Settings(Spectrum_Backwards=1,Spectrum_Repeat=1,SpectrumAverage=1):
#     pass

def Spectrum():
    # Status = STM.getp('STMAFM.SCANSTATUS','')
    # print(Status)
    STM.vertspectrum()
    # STM.Setp('VERTMAN.BTN.SINGLE_SPECTRUM','')
    # Status = STM.getp('STMAFM.SCANSTATUS','')
    # print(Status)



if __name__ == "__main__":
    pass
    # Initialize()
    # Scan()
