import numpy as np
import time
import win32com.client
from time import time as timer
import pyvisa
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
        if eval(BFieldPowerControl.query('OUTPUT?'))==True:
            BFieldPowerControl.write('OUTPUT OFF')

        BFieldPowerControl.write('FUNC:MODE VOLT')
        BFieldPowerControl.write('VOLT 0')
        BFieldPowerControl.write('CURR 10.1')
        BFieldPowerControl.write('OUTPUT ON')


    if BFieldControlThread is None:
        def BFieldControlThreadFunction():
            pass
        # BFieldControlThread = 
    FinalCurrent = B*10
    CurrentCurrent = float(BFieldPowerControl.query('MEAS:CURR?'))
    CurrentVoltage = float(BFieldPowerControl.query('MEAS:VOLT?'))
    InitialCurrent = CurrentCurrent
    BField = CurrentCurrent/10
    Increasing = 1 if FinalCurrent > CurrentCurrent else -1

    # CurrentCurrent + Ramp_amount is a somewhat reasonable approximation for the next step
    StartTime = timer()
    while Increasing*round(CurrentCurrent,3) < Increasing*FinalCurrent - Ramp_amount and not Cancel: 
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
        # print(CurrentVoltage,MeasuredVoltage,CurrentCurrent,round(Percent,2))
        OutgoingQueue.put(("SetStatus",(f"Ramp {round(Percent,1)}% Complete",2)))



    # # TODO:
    # # Make a thread that keeps it at this current value

    if Cancel:
        OutgoingQueue.put(("SetStatus",(f"",2)))
    if STM is not None:
        STM.setp('MEMO.SET', f"B = {BField} T")

# Ramp_speed=s;How often steps are taken in seconds
# Ramp_amount=mV;How much the voltage is changed for a single step
def Turn_B_Field_Off():
    global BField, BFieldPowerControl
    Set_B_Field(0)
    BFieldPowerControl.write('OUTPUT OFF')
    BField = None
    memo = 'B = 0T; Output Off.'
    STM.setp('MEMO.SET', memo)

# # Ramp_speed=s;How often steps are taken in seconds
# # Ramp_amount=mV;How much the voltage is changed for a single step
# def BField_Spectra(Final_BField=-1,Ramp_speed=0.1,Ramp_amount=1):
#     # OriginalTable = np.array(STM.getp('VERTMAN.IVTABLE',''))
#     # NewTable = OriginalTable.copy()
#     # NewTable[1,2] = 2000
#     # STM.setp('VERTMAN.IVTABLE',tuple(map(tuple,NewTable)))
#     pass

# def Approach(Parameter1= 0):
#     pass

# def Z_Course_Step_Out(Parameter1= 0):
#     pass

# def Z_Course_Step_In(Parameter1= 0):
#     pass

# def Course_Step(X=0,Y=0):
#     pass

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
        # XOffset *= 10
        # YOffset *= 10
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
        Channels.append('TOPOGRAPHY')
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
            time.sleep(0.5)
    if Cancel:
        STM.setp('STMAFM.BTN.STOP',"")
        OutgoingQueue.put(("SetStatus",(f"",2)))

def dIdV_Scan():
    Size = float(STM.getp('SCAN.IMAGESIZE.NM.X',''))
    Lines = float(STM.getp('SCAN.IMAGESIZE.PIXEL.Y',''))
    Speed = float(STM.getp('SCAN.SPEED.NM/SEC',""))
    Time = (np.floor(Lines * Size/Speed)-5)/10
    Time = 0 if Time <= 0 else Time
    # STM.setp('LOCK-IN.CHANNEL','ADC0')
    STM.setp('LOCK-IN.MODE','Internal ')
    # STM.setp('SCAN.CHANNELS',('TOPOGRAPHY','CURRENT','Lock-in X'))
    time.sleep(1)
    STM.setp('STMAFM.BTN.START' ,'')
    Status = STM.getp('STMAFM.SCANSTATUS','')
    while Status == 2 and not Cancel:
        Status = STM.getp('STMAFM.SCANSTATUS','')
        time.sleep(1)
        i = 0
        while not Cancel and i < Time:
            i+=1
            time.sleep(1)
    if Cancel:
        STM.setp('STMAFM.BTN.STOP','')
    STM.setp('LOCK-IN.MODE','Internal + Spectrum only')


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
    Status = STM.getp('STMAFM.SCANSTATUS','')
    print(Status)
    STM.vertspectrum()
    # STM.Setp('VERTMAN.BTN.SINGLE_SPECTRUM','')
    Status = STM.getp('STMAFM.SCANSTATUS','')
    print(Status)


# # B=The magnetic field strength in mT
# def Set_B_Field(B):
#     rm=pyvisa.ResourceManager()
#     instName = 'GPIB0::' + GPIBaddress + '::INSTR'
#     inst=rm.open_resource(instName)
#     inst.read_termination = '\n'
#     inst.write_termination = '\n'
#     if eval(inst.query('OUTPUT?'))==True:
#         inst.query('OUTPUT OFF')

#     inst.write('FUNC:MODE VOLT')
#     inst.write('VOLT 0')
#     inst.write('CURR 10.1')
#     time.sleep(0.1)
#     inst.write('OUTPUT ON')
#     inputString = 'VOLT '+ setValue
#     inst.write(inputString)


if __name__ == "__main__":
    pass
    # Set_BField(0.1)
    # Set_BField(0)
    # Initialize()
    # Scan()
    # Set_Scan_Image_Size('Resolution',1)
    # Set_Scan_Window_Position(XOffset=0,YOffset=0)