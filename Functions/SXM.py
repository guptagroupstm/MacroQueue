import SXMRemote
import numpy as np
import time

MySXM = None
Cancel = False
def Initialize():
    global MySXM
    MySXM= SXMRemote.DDEClient("SXM","Remote")


def OnClose():
    if MySXM is not None:
        pass


# Bias=The bias voltage in V
def Set_Bias(Bias= 0):
    MySXM.SendWait(f"FeedPara('Bias',{Bias});")
    NewBias = MySXM.GetFeedbackPara('Bias')

# Setpoint=The current setpoint in Amps
def Set_Setpoint(Setpoint=1e-9):
   MySXM.SendWait(f"FeedPara('ref', {Setpoint});")
   MySXM.SendWait(f"FeedPara('Ref2', {Setpoint});") 


# XOffset=The X center of the image in nm
# YOffset=The Y center of the image in nm
def Set_Scan_Window_Position(XOffset=0,YOffset=0):
    #no case sensitivity (can use x and Y: let's use X and Y to stay consistent)
    MySXM.SendWait(f"ScanPara('X',{XOffset});");
    MySXM.SendWait(f"ScanPara('Y',{YOffset});");
    
# ImageSize=The length of a row and column in nm
def Set_Scan_Image_Size(ImageSize=1e-9):
    MySXM.SendWait(f"ScanPara('Range',{ImageSize});")

# Angle=The angle on the scan in degrees
def Set_Scan_Window_Angle(Angle=0):
    MySXM.SendWait(f"ScanPara('Angle',{Angle});")

# NPixels=The number of pixels in each row and each column
def Set_NPixels(NPixels=512):
    MySXM.SendWait(f"ScanPara('Pixel',{NPixels});")

# LineSpeed=The speed the tip moves in nm/s
def Set_Scan_Speed(LineSpeed=2e-9):
    MySXM.SendWait(f"ScanPara('Speed',{LineSpeed});")

def Scan():
    MySXM.execute("ScanImage")

'''find motion
coarse motion for x,y,z (different command for z)
approach 
spectra
'''
def Scan(Filename="Scan"):
    # Set the filename
    MySXM.execute("ScanImage", 1000)
    while MySXM.NotGotAnswer and not Cancel:
        SXMRemote.loop()
    if Cancel:
        # Is there a way to make it stop scanning?
        pass
