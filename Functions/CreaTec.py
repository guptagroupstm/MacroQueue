import numpy as np
import time
import win32com.client
from time import time as timer
import pyvisa

STM = None
CurrentMacro = None
OutgoingQueue = None
Cancel = False
BField = None

OnCloseFunctions = []

def Initialize():
    global STM, OnCloseFunctions
    STM = win32com.client.Dispatch("pstmafm.stmafmrem")
    time.sleep(0.1)
    # OnCloseFunctions.append()


def OnClose():
    # global OnCloseFunctions
    # for f in OnCloseFunctions:
    #     f()
    if STM is not None:
        pass

    if BField is not None:
        pass


def Set_BField(B=1,ramp_spped=0.1):
    global BField
    if BField is not None:
        # ConnectMagneticFieldController()
        pass
    # Make sure current stays below +/- 10 A
    # Hard limit on ramp speed

    # 10 Amps is 1 T
    # Amps or T input parameter

    # Add BField to memo
    pass

# def Turn_BField_Off():
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
        STM.setp('STMAFM.CMD.SETXYOFF.NM',(XOffset,YOffset))
    elif HowToSetPosition == 'Image Coord':
        STM.setp('STMAFM.CMD.SETXYOFF.IMAGECOORD',(XOffset,YOffset))
    elif HowToSetPosition == 'Voltage':
        STM.setp('STMAFM.CMD.SETXYOFF.VOLT',(XOffset,YOffset))

# XOffset=The X position of the tip in nm, or Image Coordinate, or V
# YOffset=The Y X position of the tip in nm, or Image Coordinate, or V
def Fine_Move_Tip(HowToSetPosition=['nm','Image Coord','Voltage'],XOffset=0,YOffset=0):
    if HowToSetPosition == 'nm':
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

def Scan():
    Size = float(STM.getp('SCAN.IMAGESIZE.NM.X',''))
    Lines = float(STM.getp('SCAN.IMAGESIZE.PIXEL.Y',''))
    Speed = float(STM.getp('SCAN.SPEED.NM/SEC',""))
    ScanTime = 2*Lines * Size/Speed
    CheckTime = int(np.ceil(ScanTime/500))
    # Time = 0 if Time <= 0 else Time

    STM.setp('SCAN.CHANNELS',('TOPOGRAPHY','CURRENT'))
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

def dIdV_Scan():
    Size = float(STM.getp('SCAN.IMAGESIZE.NM.X',''))
    Lines = float(STM.getp('SCAN.IMAGESIZE.PIXEL.Y',''))
    Speed = float(STM.getp('SCAN.SPEED.NM/SEC',""))
    Time = (np.floor(Lines * Size/Speed)-5)/10
    Time = 0 if Time <= 0 else Time
    STM.setp('LOCK-IN.CHANNEL','ADC1')
    STM.setp('LOCK-IN.MODE','Internal ')
    STM.setp('SCAN.CHANNELS',('TOPOGRAPHY','CURRENT','Lock-in X'))
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
    Initialize()
    Scan()
    # Set_Scan_Image_Size('Resolution',1)
    # Set_Scan_Window_Position(XOffset=0,YOffset=0)