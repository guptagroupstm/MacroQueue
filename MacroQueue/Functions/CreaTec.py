import numpy as np
import time
import win32com.client
from time import time as timer
import pyvisa
import pythoncom
import os
import pandas as pd
from datetime import datetime

CurrentMacro = None
OutgoingQueue = None
Cancel = False
MacroQueueSelf = None

STM = None
RFGenerator = None


def Initialize():
    global STM
    pythoncom.CoInitialize()
    STM = win32com.client.Dispatch("pstmafm.stmafmrem")
    time.sleep(0.3)


# {"Name":"Parameter","Units":"s","Max":10,"Min":-10,"Tooltip":"Example Tooltip"}
# {"Name":"Parameter2","Units":"m","Max":13,"Tooltip":"Example Tooltip"}
# {"Name":"Parameter3","Units":"m","Min":-12,"Tooltip":"Example Tooltip"}
def Test(Parameter=5,Parameter2=3,Parameter3=-2):
    print(Parameter2)
    pass

def OnClose():
    if STM is not None:
        pass




def Clear_Memo():
    STM.setp('MEMO.SET', "")
    time.sleep(0.1)


# Variable;The variable to change in the memo
# Value;The value to change it to
def Edit_Memo_Line(Variable="Power",Value="Off"):
    if STM is not None:
        Memo = STM.getp('MEMO.GET','')
        if len(Memo) > 0:
            if f"{Variable} = " in Memo:
                NewMemo = ""
                for line in Memo.splitlines():
                    NewMemo = f"{NewMemo}{Variable} = {Value}\n" if f"{Variable} = " in line else f"{NewMemo}{line}\n"
                Memo = NewMemo
            else:
                Memo = f'{Memo}\n{Variable} = {Value}'

        else:
            Memo = f'{Variable} = {Value}\n'
        STM.setp('MEMO.SET', Memo)
        time.sleep(0.1)


ChannelDict = {'Y':0,'X':1,'Z':2}
DirDict = {'p':0,'n':1}

# Rectification_Steps=Perform steps to center the Z piezo after approach.
def Approach(Rectification_Steps=True):
    Burst_XY = STM.getp('HVAMPCOARSE.CHK.BURST.XY','')
    Burst_Z = STM.getp('HVAMPCOARSE.CHK.BURST.Z','')
    STM.setp('HVAMPCOARSE.CHK.RETRACT_TIP_AFTER_APPROACH','OFF')

    time.sleep(1)

    STM.setp('HVAMPCOARSE.APPROACH.START','ON')
    while not STM.getp('HVAMPCOARSE.APPROACH.Finished','') and not Cancel:
        time.sleep(0.1)
        pass
    if Cancel:
        STM.setp('HVAMPCOARSE.APPROACH.STOP','ON')
    if not Cancel:
        time.sleep(1)

    if not Cancel:
        if Rectification_Steps:
            time.sleep(1)

            STM.setp('HVAMPCOARSE.CHK.BURST.Z','OFF')

            ZVoltage = STM.signals1data(2,0.1,5)
            while ZVoltage > 350 and not Cancel:
                print(ZVoltage)
                STM.setp('SLIDER.ZLIMIT.ON','ON')
                STM.setp('SLIDER.ZLIMIT.VOLT',-10)
                time.sleep(1)
                STM.slider(ChannelDict['Z'],DirDict['n'],0)
                time.sleep(0.5)
                STM.setp('SLIDER.ZLIMIT.ON','OFF')
                time.sleep(1)
                ZVoltage = STM.signals1data(2,0.1,5)
                time.sleep(0.5)

    if Burst_Z:
        STM.setp('HVAMPCOARSE.CHK.BURST.Z','ON')
    else:
        STM.setp('HVAMPCOARSE.CHK.BURST.Z','OFF')
    if Burst_XY:
        STM.setp('HVAMPCOARSE.CHK.BURST.XY','ON')
    else:
        STM.setp('HVAMPCOARSE.CHK.BURST.XY','OFF')

    

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

# {"Name":"Lockin_Freq","Units":"Hz","Min":0.1,"Max":1500,"Tooltip":"The lock-in frequency in Hz"}
def Set_LockIn_Frequency(Lockin_Freq=877):
    STM.setp('LOCK-IN.FREQ.HZ',Lockin_Freq)
    time.sleep(0.1)

def Set_Spectrum_Mode(Mode=["I(V,z)",'z(V)',"z(V,X:I)"]):
    STM.setp('VERTMAN.VFB_MODE', Mode)

# {"Name":"Lockin_RC","Units":"Hz","Min":0.1,"Max":1000,"Tooltip":"The lock-in time constant in Hz"}
def Set_LockIn_TimeConstant(Lockin_RC=100):
    STM.setp('LOCK-IN.RC.HZ',Lockin_RC)
    time.sleep(0.1)

# {"Name":"Lockin_Amp","Units":"mV","Min":0,"Max":10000,"Tooltip":"The lock-in voltage amplitude in mV"}
def Set_LockIn_Amplitude(Lockin_Amp=100):
    STM.setp('LOCK-IN.AMPLITUDE.MVPP',Lockin_Amp)
    time.sleep(0.1)

# {"Name":"Lockin_RefA","Units":"mV","Min":0,"Max":10000,"Tooltip":"The lock-in reference voltage amplitude in mV"}
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

# {"Name":"NPixels","Min":1,"Tooltip":"The number of pixels in each row and each column"}
def Set_NPixels(NPixels=512):
    STM.setp('SCAN.IMAGESIZE.PIXEL', (NPixels, NPixels))
    time.sleep(0.1)

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
    # Calculates how long the scan will take
    Size = float(STM.getp('SCAN.IMAGESIZE.NM.X',''))
    Lines = float(STM.getp('SCAN.IMAGESIZE.PIXEL.Y',''))
    Speed = float(STM.getp('SCAN.SPEED.NM/SEC',""))
    ScanTime = 2*Lines * Size/Speed

    # How often the status bar will be updated.
    CheckTime = int(np.ceil(ScanTime/500))

    # Starts the scan
    STM.setp('STMAFM.BTN.START' ,'')
    time.sleep(0.1)


    StartTime = timer()
    Status = STM.getp('STMAFM.SCANSTATUS','')
    # Keeps scanning until the scan is done (Status == 2) or the user cancelled the macro (Cancel)
    while Status == 2 and not Cancel:
        Status = STM.getp('STMAFM.SCANSTATUS','')
        StartCheckTime = timer()
        # Every {CheckTime} seconds, the status bar is updated.
        while not Cancel and timer() - StartCheckTime < CheckTime:
            Percent = round(100*((timer() - StartTime)/ScanTime),1)
            # Puts f"Scan {Percent}% Complete" in the third spot in the status bar.
            OutgoingQueue.put(("SetStatus",(f"Scan {Percent}% Complete",2)))
            time.sleep(1)
    if Cancel:
        # If the user cancelled the macro, stop the scan.
        STM.setp('STMAFM.BTN.STOP',"")
        time.sleep(0.1)
        OutgoingQueue.put(("SetStatus",(f"",2)))
        while Status != 0:
            Status = STM.getp('STMAFM.SCANSTATUS','')
    else:
        Bias = STM.getp('SCAN.BIASVOLTAGE.VOLT','')
        STM.setp('LOCK-IN.MODE','Internal + Spectrum only')
        STM.setp('SCAN.BIASVOLTAGE.VOLT',Bias)

def dIdV_Scan():
    STM.setp('LOCK-IN.MODE','Internal ')
    Scan()
    

# Inital_Bias=V;The inital bias for the spectrum.  
# Final_Bias=V;The final bias for the spectrum.  
# N_Datapoints=The number of data points for a single direction
def Set_Spectrum_Table(Inital_Bias=-1,Final_Bias=1, N_Datapoints=1024):
    Time = STM.getp('VERTMAN.SPECLENGTH.SEC','')
    OriginalSpectraTable = STM.getp('VERTMAN.IVTABLE','')    
    SpecListGrid = list(map(list,OriginalSpectraTable))
    TableLength = len(SpecListGrid[0])
    for i in range(2):
        SpecListGrid[i] = [0 for j in range(TableLength)]
    SpecListGrid[0][1] = N_Datapoints
    SpecListGrid[1][0] = Inital_Bias
    SpecListGrid[1][1] = Final_Bias
    NewSpecGrid = tuple(map(tuple,SpecListGrid))
    STM.setp('VERTMAN.IVTABLE',NewSpecGrid)    
    STM.setp('VERTMAN.SPECLENGTH.SEC',Time)


def Set_Spectrum_Table_to_Constant_Bias():
    OriginalSpectraTable = STM.getp('VERTMAN.IVTABLE','')    
    SpecListGrid = list(map(list,OriginalSpectraTable))
    Bias = STM.getp('SCAN.BIASVOLTAGE.VOLT','')
    SpecListGrid[1][0] = Bias
    SpecListGrid[1][1] = Bias
    NewSpecGrid = tuple(map(tuple,SpecListGrid))
    STM.setp('VERTMAN.IVTABLE',NewSpecGrid)  
    
    
def Set_Spectrum_Table_Trig_Vaux():  
    OriginalSpectraTable = STM.getp('VERTMAN.IVTABLE','')    
    SpecListGrid = list(map(list,OriginalSpectraTable))
    N_Datapoints = SpecListGrid[0][1]
    SpecListGrid[4][0] = 0
    SpecListGrid[4][1] = 1
    SpecListGrid[4][2] = N_Datapoints-1
    SpecListGrid[4][3] = N_Datapoints

    SpecListGrid[5][0] = 0
    SpecListGrid[5][1] = 10
    SpecListGrid[5][2] = 10
    SpecListGrid[5][3] = 0

    NewSpecGrid = tuple(map(tuple,SpecListGrid))
    STM.setp('VERTMAN.IVTABLE',NewSpecGrid)

# {"Name":"Setpoint","Units":"nA","Max":1e4,"Tooltip":"The setpoint for constant current spectra"}
def Set_Spectrum_Setpoint(Setpoint=1,Use_Scan_Setpoint=True):
    if Use_Scan_Setpoint:
        Setpoint = float(STM.getp('SCAN.SETPOINT.AMPERE',''))
        STM.setp('VERTMAN.VFB_CURRENT.NAMP',Setpoint*1e9)
    else:
        STM.setp('VERTMAN.VFB_CURRENT.NAMP',Setpoint)


# Time=s;The duration of the spectrum for a single direction
def Set_Spectra_Time(Time=60):
    STM.setp('VERTMAN.SPECLENGTH.SEC',Time)


# N=The number of spectra to take and average.  Takes long. reduces noise.
def Set_Spectra_NAveraging(N=1):
    STM.setp('VERTMAN.SPECAVRG.COUNT', N)
    
def Spectrum():
    ImageSize = float(STM.getp('SCAN.IMAGESIZE.NM.X',""))
    STM.setp('SCAN.IMAGESIZE.NM.X',1)
    Pixels = float(STM.getp('SCAN.IMAGESIZE.PIXEL.X',''))
    STM.btn_vertspec(int(Pixels//2)+1,0)
    STM.setp('SCAN.IMAGESIZE.NM.X',ImageSize)


if __name__ == "__main__":
    pass
    # Initialize()
    # Spectrum()
    # Scan()
