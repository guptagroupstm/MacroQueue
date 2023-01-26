import SXMRemote
import numpy as np
import time

OutgoingQueue = None
MySXM = None
Cancel = False
def Initialize():
    global MySXM
    MySXM= SXMRemote.DDEClient("SXM","Remote")


def OnClose():
    if MySXM is not None:
        pass


# Bias=V;The bias voltage in V
def Set_Bias(Bias= 0):
    MySXM.SendWait(f"FeedPara('Bias',{Bias*1000});")
    NewBias = MySXM.GetFeedbackPara('Bias')

# Setpoint=pA;The current setpoint in pA
def Set_Setpoint(Setpoint=100):
   MySXM.SendWait(f"FeedPara('ref', {Setpoint*1e+3});")
   MySXM.SendWait(f"FeedPara('Ref2', {Setpoint*1e+3});") 


# XOffset=nm;The X center of the image in nm
# YOffset=nm;The Y center of the image in nm
def Set_Scan_Window_Position(XOffset=0,YOffset=0):
    #no case sensitivity (can use x and Y: let's use X and Y to stay consistent)
    MySXM.SendWait(f"ScanPara('X',{XOffset});");
    MySXM.SendWait(f"ScanPara('Y',{YOffset});");
    
# ImageSize=nm;The length of a row and column in nm
def Set_Scan_Image_Size(ImageSize=1e-9):
    MySXM.SendWait(f"ScanPara('Range',{ImageSize});")

# Angle=The angle on the scan in degrees
def Set_Scan_Window_Angle(Angle=0):
    MySXM.SendWait(f"ScanPara('Angle',{Angle});")

# NPixels=The number of pixels in each row and each column
def Set_NPixels(NPixels=512):
    MySXM.SendWait(f"ScanPara('Pixel',{NPixels});")

# LineSpeed=s/line;The speed the tip moves in s/line
def Set_Scan_Speed(LineSpeed=2e-9):
    MySXM.SendWait(f"ScanPara('Speed',{LineSpeed});")

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

def Scan():
    MySXM.SendWait("ScanPara('AUTOSAVE', 1);")
    MySXM.SendWait("ScanPara('Repeat', 0);")

    global Scanning
    Scanning = True
    def MyNewFileIsWritten(FileName):
        global Scanning
        OutgoingQueue.put(("SetStatus",(f"The scan has finished",2)))  
        Scanning = False
    Scanning = 5
    MySXM.SaveIsDone=MyNewFileIsWritten

    MySXM.SendWait("ScanPara('Scan',1);") #<>0 = start
    OutgoingQueue.put(("SetStatus",(f"The scan has started",2)))  

    while not Cancel and Scanning:
        time.sleep(1)
    if Cancel:
        MySXM.SendWait("ScanPara('Scan',0);") #=0 = stop


# def Scan(Filename="Scan"):
#     # Set the filename
#     MySXM.execute("ScanImage", 1000)
#     while MySXM.NotGotAnswer and not Cancel:
#         SXMRemote.loop()
#     if Cancel:
#         # Is there a way to make it stop scanning?
#         pass

'''things to add
spectra'''