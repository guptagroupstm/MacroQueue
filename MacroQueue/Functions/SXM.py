import MacroQueue.Functions.SXMRemote
import numpy as np
import time
import os

OutgoingQueue = None
MySXM = None
Cancel = False
def Initialize():
    global MySXM
    MySXM= SXMRemote.DDEClient("SXM","Remote")


def OnClose():
    if MySXM is not None:
        pass


# Bias=mV;The bias voltage in mV
def Set_Bias(Bias= 1000):
    MySXM.SendWait(f"FeedPara('Bias',{Bias});")
    time.sleep(0.1)

# Setpoint=pA;The current setpoint in pA
def Set_Setpoint(Setpoint=100):
   MySXM.SendWait(f"FeedPara('ref', {Setpoint});")
   MySXM.SendWait(f"FeedPara('Ref2', {Setpoint});") 
   time.sleep(0.1)



# XOffset=nm;The X center of the image in nm
# YOffset=nm;The Y center of the image in nm
def Set_Scan_Window_Position(XOffset=0,YOffset=0):
    #no case sensitivity (can use x and Y: let's use X and Y to stay consistent)
    MySXM.SendWait(f"ScanPara('X',{XOffset});");
    MySXM.SendWait(f"ScanPara('Y',{YOffset});");
    time.sleep(0.1)
    
# ImageSize=nm;The length of a row and column in nm
def Set_Scan_Image_Size(ImageSize=50):
    MySXM.SendWait(f"ScanPara('Range',{ImageSize});")
    time.sleep(0.1)

# Angle=The angle on the scan in degrees
def Set_Scan_Window_Angle(Angle=0):
    MySXM.SendWait(f"ScanPara('Angle',{Angle});")
    time.sleep(0.1)

# NPixels=The number of pixels in each row and each column
def Set_NPixels(NPixels=512):
    MySXM.SendWait(f"ScanPara('Pixel',{NPixels});")
    time.sleep(0.1)

# LineSpeed=line/s;The speed the tip moves in line/s
def Set_Scan_Speed(LineSpeed=2):
    MySXM.SendWait(f"ScanPara('Speed',{LineSpeed});")
    time.sleep(0.1)


# # coarse motion: X,Y = number of steps in x and y direction
# def Course_Step(X=0,Y=0):
#     MySXM.SendWait(f"Move('CX',{X});")
#     MySXM.SendWait(f"Move('CY',{Y});")

# #coarse.py has different modes to approach
# def Approach(Mode= 0):
#     MySXM.SendWait(f"Move('Approach',{Mode});")

# #this retracts the tip with different modes (0=piezo, 1 = step approach)
# def Z_Course_Step_Out(Mode = 0):
#     MySXM.SendWait(f"Move('Retract',{Mode});")

# #can use -1000000 to 1000000 steps where negative is down, positive is up
# def Z_Course_Step_In(Steps = 0):
#     MySXM.SendWait(f"Move('CZ',{Steps});")

def Scan(FolderPath="C:\\Users\\Supervisor\\Desktop\\Data"):
    MySXM.SendWait("ScanPara('AUTOSAVE', 1);")
    MySXM.SendWait("ScanPara('Repeat', 0);")

    time.sleep(1)

    MySXM.SendWait("ScanPara('Scan',1);") #<>0 = start
    OutgoingQueue.put(("SetStatus",(f"The scan has started",2)))  
    time.sleep(1)

    # NFiles = len(os.listdir(FolderPath))
    NFiles = 0
    for root, dirs, files in os.walk(FolderPath):
        NFiles += len(files)
    NFilesNow = NFiles
    while not Cancel and NFiles == NFilesNow:
        NFilesNow = 0
        for root, dirs, files in os.walk(FolderPath):
            NFilesNow += len(files)
        time.sleep(1)
    if Cancel:
        MySXM.SendWait("ScanPara('Scan',0);") #=0 = stop




# X(z) = 0                      X(t) U-step = 5
# X(U,z) = 1                    X(t) U-step CL = 6
# X(U) CL = 2                   cmAFM X(U) = 7
# X(t) z-step = 3               X(t) noise = 8
# X(t) z-step CL = 4            X(x,y) = 9
# Mode=The spectra mode
def Set_Spectra_Mode(Mode=["X(z)","X(U)","Feenstra","X(U) CL","X(t) z-step","X(t) z-step CL","X(t) U-step","X(t) U-step CL","cmAFM X(U)","X(t) noise","X(x,y)"]):
    ModeList=["X(z)","X(U)","Feenstra","X(U) CL","X(t) z-step","X(t) z-step CL","X(t) U-step","X(t) U-step CL","cmAFM X(U)","X(t) noise","X(x,y)"]
    ModeIndex = 0
    for i,thisMode in enumerate(ModeList):
        if thisMode == Mode:
            ModeIndex = i
    MySXM.SendWait("SpectPara(0, "+str(ModeIndex)+");") 
    time.sleep(0.1)

# X=nm;The X position of the spectra
def Set_Spectra_XPosition(X=0):
    MySXM.SendWait("SpectPara(1, "+str(X)+");") 
    time.sleep(0.1)

# Y=nm;The Y position of the spectra
def Set_Spectra_YPosition(Y=0):
    MySXM.SendWait("SpectPara(2, "+str(Y)+");") 
    time.sleep(0.1)

    
# Delay1=ms;The delay after the tip has arrived in position
def Set_Spectra_Delay(Delay1=100):
    MySXM.SendWait("SpectPara(3, "+str(Delay1)+");") 
    time.sleep(0.1)
    
# AquT=ms;The time for one data point
def Set_Spectra_Delay(AquT=50):
    MySXM.SendWait("SpectPara(4, "+str(AquT)+");") 
    time.sleep(0.1)

# dz=nm;The amount to retract before starting the spectra relative to the position that was stablized during the delay1
def Set_Spectra_Starting_Height(dz=0):
    MySXM.SendWait("SpectPara(5, "+str(dz)+");") 
    time.sleep(0.1)

# dz=nm;The position to ramp to during spectra relative to the position that was stablized during the delay1
def Set_Spectra_Final_Height(dz=0):
    MySXM.SendWait("SpectPara(6, "+str(dz)+");") 
    time.sleep(0.1)

# U1=mV;The inital bias for the spectra
def Set_Spectra_Inital_Bias(U1=1000):
    MySXM.SendWait("SpectPara(7, "+str(U1)+");")
    time.sleep(0.1)

# U2=mV;The final bias for the spectra
def Set_Spectra_Final_Bias(U2=-1000):
    MySXM.SendWait("SpectPara(8, "+str(U2)+");")
    time.sleep(0.1)

# NDataPoints=The number of datapoints in a spectrum
def Set_Spectra_NDataPoints(NDataPoints=1024):
    MySXM.SendWait("SpectPara('Points', "+str(NDataPoints)+");")
    time.sleep(0.1)

def Start_Spectra(FolderPath="C:\\Users\\Supervisor\\Desktop\\Data"):
    MySXM.SendWait("SpectPara('AUTOSAVE', 1);")
    time.sleep(0.1)
    MySXM.SendWait("SpectPara('Repeat', 0);")
    time.sleep(0.1)
    MySXM.SendWait("SpectStart;")
    time.sleep(0.1)
    OutgoingQueue.put(("SetStatus",(f"The Spectrum has started",2)))  
    time.sleep(1)

    NFiles = 0
    for root, dirs, files in os.walk(FolderPath):
        NFiles += len(files)
    NFilesNow = NFiles
    while not Cancel and NFiles == NFilesNow:
        NFilesNow = 0
        for root, dirs, files in os.walk(FolderPath):
            NFilesNow += len(files)
        time.sleep(1)
    time.sleep(1)
    
