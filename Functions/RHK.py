import numpy as np
import time
import socket
from time import time as timer

Socket = None
BUFFER_SIZE = None
Cancel = False
OutgoingQueue = None
CourseX = 0
CourseY = 0

def Initialize():
    global Socket, BUFFER_SIZE
    IP_Address_R9_PC   = '127.0.0.1'
    TCP_Port_R9s       = 12600
    BUFFER_SIZE = 1024
    socket.setdefaulttimeout(3)
    Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    Socket.connect((IP_Address_R9_PC, TCP_Port_R9s))
    time.sleep(0.1)


def OnClose():
    if Socket is not None:
        Socket.shutdown(2)
        Socket.close()

# def Approach(Parameter1= 0):
#     Message = f'GetHWSubParameter, Z PI Controller 1, Upper Bound, Value\n'
#     Socket.send(Message.encode())
#     UpperBound = float(Socket.recv(BUFFER_SIZE))
#     Message = f'GetHWSubParameter, Z PI Controller 1, Lower Bound, Value\n'
#     Socket.send(Message.encode())
#     LowerBound = float(Socket.recv(BUFFER_SIZE))
    
#     Message = f'SetHWParameter, Z PI Controller 1, Tip Control, Unlimit\n'
#     Socket.send(Message.encode())
#     data = Socket.recv(BUFFER_SIZE)

#     time.sleep(0.01)
    
#     Message = f'ReadChannelValue, z0-src\n'
#     Socket.send(Message.encode())
#     ZPosition = float(Socket.recv(BUFFER_SIZE))

#     while ZPosition == UpperBound:
#         Message = f"StartProcedure, Pan Single Step In\n"
#         Socket.send(Message.encode())
#         data = Socket.recv(BUFFER_SIZE)
#         # data = Socket.recv(BUFFER_SIZE)
#         # time.sleep(0.1)
#         Message = f'ReadChannelValue, z0-src\n'
#         Socket.send(Message.encode())
#         ZPosition = float(Socket.recv(BUFFER_SIZE))
#     pass
# def Z_Course_Step_Out(Parameter1= 0):
#     pass
# def Z_Course_Step_In(Parameter1= 0):
#     pass
# def Course_Step(X=0,Y=0):
#     pass

# Bias=V;The bias voltage in Volts
def Set_Bias(Bias= 1):
    Message = f"SetSWParameter, STM Bias, Value, {Bias}\n"
    Socket.send(Message.encode())
    data = Socket.recv(BUFFER_SIZE)
    time.sleep(3)
    try:
        data = Socket.recv(BUFFER_SIZE)
        data = Socket.recv(BUFFER_SIZE)
    except:
        pass

# # BiasRate=V/s;The rate the bias changes in Volts per second 
# def Set_Bias_Rate(BiasRate=1):
#     Message = "SetSWParameter, STM Bias, Rate, {BiasRate}\n"
#     Socket.send(Message.encode())
#     data = Socket.recv(BUFFER_SIZE)

# Setpoint=pA;The current setpoint in pA
def Set_Setpoint(Setpoint=100):
    Setpoint *= 1e-12 #Convert from pA to A (RHK uses A)
    Message = f"SetHWSubParameter, Z PI Controller 1, Set Point, Value, {Setpoint}\n"
    Socket.send(Message.encode())
    data = Socket.recv(BUFFER_SIZE)


# XOffset=nm;The X center of the image in nm
# YOffset=nm;The Y center of the image in nm
def Set_Scan_Window_Position(XOffset=0,YOffset=0):
    XOffset *= 1e-9
    YOffset *= 1e-9
    Message = f'SetSWParameter, Scan Area Window, X Offset, {XOffset}\n'
    Socket.send(Message.encode())
    data = Socket.recv(BUFFER_SIZE)
    
    Message = f'SetSWParameter, Scan Area Window, Y Offset, {YOffset}\n'
    Socket.send(Message.encode())
    data = Socket.recv(BUFFER_SIZE)

# HowToSetSize=Choose to set the Image Size in nm directly or the Resolution in nm/pixel
# ImageSize=nm;The length of a row and column in nm or nm/pixel
def Set_Scan_Image_Size(HowToSetSize=['Image Size','Resolution'],ImageSize=100):
    ImageSize *= 1e-9
    if HowToSetSize == 'Image Size':
        Message = f'SetSWParameter, Scan Area Window, Scan Area Size, {ImageSize}\n'
    elif HowToSetSize == 'Resolution':
        try:
            data = Socket.recv(BUFFER_SIZE)
        except:
            pass
        Message = f"GetSWSubItemParameter, Scan Area Window, Scan Settings, Lines Per Frame\n"
        Socket.send(Message.encode())
        Pixels = Socket.recv(BUFFER_SIZE)
        ImageSize *= Pixels
        Message = f'SetSWParameter, Scan Area Window, Scan Area Size, {ImageSize}\n'
        
    Socket.send(Message.encode())
    data = Socket.recv(BUFFER_SIZE)

# Angle=degrees;The angle on the scan in degrees
def Set_Scan_Window_Angle(Angle=0):
    Message = f"SetSWParameter, Scan Area Window, Rotate Angle, {Angle}\n"
    Socket.send(Message.encode())
    data = Socket.recv(BUFFER_SIZE)

# IntegralGain=um/s;The integral gain of the z piezo.
def Set_Integral_Gain(IntegralGain=1):
    IntegralGain*=1e-6
    Message = f"SetHWSubParameter, Z PI Controller 1, Integral Gain, {IntegralGain}\n"
    Socket.send(Message.encode())
    data = Socket.recv(BUFFER_SIZE)
    
# ProportionalGain=The proportional gain.
def Set_Proportional_Gain(ProportionalGain=1e-17):
    Message = f"SetHWSubParameter, Z PI Controller 1, Proportional Gain, {ProportionalGain}\n"
    Socket.send(Message.encode())
    data = Socket.recv(BUFFER_SIZE)

# NPixels=The number of pixels in each row and each column
def Set_NPixels(NPixels=512):
    Message = f"SetSWSubItemParameter, Scan Area Window, Scan Settings, Lines Per Frame, {NPixels}\n"
    Socket.send(Message.encode())
    data = Socket.recv(BUFFER_SIZE)

# HowToSetSpeed=Choose how the Image Speed is set
# Speed=The speed the tip moves in nm/s, s/line, or ms/pixel
def Set_Scan_Speed(HowToSetSpeed=['nm/s','s/line','ms/pixel'],Speed=2):
    try:
        data = Socket.recv(BUFFER_SIZE)
    except:
        pass
    if HowToSetSpeed == 'nm/s':
        Speed *= 1e-9
        Message = f"SetSWParameter, Scan Area Window, Image Navigation Speed, Tip Speed"
        Socket.send(Message.encode())
        data = Socket.recv(BUFFER_SIZE)
        Message = f"SetSWParameter, Scan Area Window, Scan Speed, {Speed}\n"
        Socket.send(Message.encode())
        data = Socket.recv(BUFFER_SIZE)
    if HowToSetSpeed == 's/line':
        Message = f"SetSWParameter, Scan Area Window, Image Navigation Speed, Image Speed"
        Socket.send(Message.encode())
        data = Socket.recv(BUFFER_SIZE)
        Message = f'GetSWParameter, Scan Area Window, Scan Area Size\n'
        Socket.send(Message.encode())
        Size = float(Socket.recv(BUFFER_SIZE))
        Message = f"SetSWParameter, Scan Area Window, Scan Speed, {Size/Speed}\n"
        # Setting the Line Time only temperorily changes the text in the software.  Doesn't actualy change the speed.
        # Message = f"SetSWParameter, Scan Area Window, Line Time, {Speed}\n"
        Socket.send(Message.encode())
        data = Socket.recv(BUFFER_SIZE)
    if HowToSetSpeed == 'ms/pixel':
        Message = f"SetSWParameter, Scan Area Window, Image Navigation Speed, Image Speed"
        Socket.send(Message.encode())
        data = Socket.recv(BUFFER_SIZE)
        Message = f"GetSWSubItemParameter, Scan Area Window, Scan Settings, Lines Per Frame\n"
        Socket.send(Message.encode())
        NPixels = float(Socket.recv(BUFFER_SIZE))
        Message = f'GetSWParameter, Scan Area Window, Scan Area Size\n'
        Socket.send(Message.encode())
        Size = float(Socket.recv(BUFFER_SIZE))
        Message = f"SetSWParameter, Scan Area Window, Scan Speed, {Size/(NPixels*Speed/1000)}\n"
        # Message = f"SetSWParameter, Scan Area Window, Line Time, {NPixels*Speed/1000}\n"
        Socket.send(Message.encode())
        data = Socket.recv(BUFFER_SIZE)

# XOffset=nm;The X center of the image in nm
# YOffset=nm;The Y center of the image in nm
def Move_Tip(XOffset=0,YOffset=0):
    Message = f"SetSWParameter, Scan Area Window, Tip X in scan coordinates, {XOffset}\n"
    Socket.send(Message.encode())
    data = Socket.recv(BUFFER_SIZE)
    Message = f"SetSWParameter, Scan Area Window, Tip Y in scan coordinates, {YOffset}\n"
    Socket.send(Message.encode())
    data = Socket.recv(BUFFER_SIZE)
    Message = f"StartProcedure, Move Tip\n"
    Socket.send(Message.encode())
    data = Socket.recv(BUFFER_SIZE)

# Wait_Time=s;The time to wait after the tip is moved in seconds.
def Move_To_Image_Start(Wait_Time=10):
    try:
        data = Socket.recv(BUFFER_SIZE)
    except:
        pass
    Message = f"GetSWParameter, Scan Area Window, Rotate Angle\n"
    Socket.send(Message.encode())
    Angle = float(Socket.recv(BUFFER_SIZE))
    Message = f'GetSWParameter, Scan Area Window, Scan Area Size\n'
    Socket.send(Message.encode())
    Size = float(Socket.recv(BUFFER_SIZE))
    Message = f'GetSWParameter, Scan Area Window, X Offset\n'
    Socket.send(Message.encode())
    XOffset = float(Socket.recv(BUFFER_SIZE))
    Message = f'GetSWParameter, Scan Area Window, Y Offset\n'
    Socket.send(Message.encode())
    YOffset = float(Socket.recv(BUFFER_SIZE))
    c, s = np.cos(Angle),np.sin(Angle)
    X = c*Size/2 - s*Size/2
    Y = s*Size/2 + c*Size/2
    X += XOffset
    Y += YOffset
    Message = f"SetSWParameter, Scan Area Window, Tip X in scan coordinates, {X}\n"
    Socket.send(Message.encode())
    data = Socket.recv(BUFFER_SIZE)
    Message = f"SetSWParameter, Scan Area Window, Tip Y in scan coordinates, {Y}\n"
    Socket.send(Message.encode())
    data = Socket.recv(BUFFER_SIZE)
    Message = f"StartProcedure, Move Tip\n"
    Socket.send(Message.encode())
    data = Socket.recv(BUFFER_SIZE)
    while not Cancel:
        try:
            data = Socket.recv(BUFFER_SIZE)
            break
        except Exception as e:
            print(e)
            pass
    time.sleep(Wait_Time)

# def dIdV_Spectra():
#     pass

# def PixelScan():
#     pass
def PixelScan():
    try:
        data = Socket.recv(BUFFER_SIZE)
    except:
        pass
    Message = "SetSWSubItemParameter, Scan Area Window, Scan Settings, Alternate Slow Scan, Top Down Only\n"
    Socket.send(Message.encode())
    data = Socket.recv(BUFFER_SIZE)

    Message = "SetSWSubItemParameter, Scan Area Window, Scan Settings, Scan Count Mode, Single\n"
    Socket.send(Message.encode())
    data = Socket.recv(BUFFER_SIZE)


    Message = f"GetSWSubItemParameter, Scan Area Window, Scan Settings, Lines Per Frame\n"
    Socket.send(Message.encode())
    Lines = float(Socket.recv(BUFFER_SIZE))
    Message = f"GetSWParameter, Scan Area Window, Line Time\n"
    Socket.send(Message.encode())
    LineTime = float(Socket.recv(BUFFER_SIZE))
    Message = f"GetSWSubItemParameter, Scan Area Window, Scan Settings, Over Scan Count\n"
    Socket.send(Message.encode())
    OverScanCount = float(Socket.recv(BUFFER_SIZE))
    ScanTime = 2*(Lines+OverScanCount)*LineTime

    Message = "StartProcedure, Pixel Scan\n"
    Socket.send(Message.encode())
    
    data = Socket.recv(BUFFER_SIZE)
    # data = Socket.recv(BUFFER_SIZE)

    StartTime = timer()
    while not Cancel:
        try:
            data = Socket.recv(BUFFER_SIZE)
            print(f"Scan Data: {data}")
            break
        except Exception as e:
            print(e)
            pass
        Percent = round(100*((timer() - StartTime)/ScanTime),1)
        OutgoingQueue.put(("SetStatus",(f"Scan {Percent}% Complete",2)))
    if Cancel:
        Message = "StopProcedure, Comb Scan\n"
        Socket.send(Message.encode())
        data = Socket.recv(BUFFER_SIZE)

def Scan():
    try:
        data = Socket.recv(BUFFER_SIZE)
    except:
        pass
    Message = "SetSWSubItemParameter, Scan Area Window, Scan Settings, Alternate Slow Scan, Top Down Only\n"
    Socket.send(Message.encode())
    data = Socket.recv(BUFFER_SIZE)

    Message = "SetSWSubItemParameter, Scan Area Window, Scan Settings, Scan Count Mode, Single\n"
    Socket.send(Message.encode())
    data = Socket.recv(BUFFER_SIZE)


    Message = f"GetSWSubItemParameter, Scan Area Window, Scan Settings, Lines Per Frame\n"
    Socket.send(Message.encode())
    Lines = float(Socket.recv(BUFFER_SIZE))
    Message = f"GetSWParameter, Scan Area Window, Line Time\n"
    Socket.send(Message.encode())
    LineTime = float(Socket.recv(BUFFER_SIZE))
    Message = f"GetSWSubItemParameter, Scan Area Window, Scan Settings, Over Scan Count\n"
    Socket.send(Message.encode())
    OverScanCount = float(Socket.recv(BUFFER_SIZE))
    ScanTime = 2*(Lines+OverScanCount)*LineTime

    Message = "StartProcedure, Comb Scan\n"
    Socket.send(Message.encode())
    
    data = Socket.recv(BUFFER_SIZE)
    # data = Socket.recv(BUFFER_SIZE)

    StartTime = timer()
    while not Cancel:
        try:
            data = Socket.recv(BUFFER_SIZE)
            print(f"Scan Data: {data}")
            break
        except Exception as e:
            print(e)
            pass
        Percent = round(100*((timer() - StartTime)/ScanTime),1)
        OutgoingQueue.put(("SetStatus",(f"Scan {Percent}% Complete",2)))
    if Cancel:
        Message = "StopProcedure, Comb Scan\n"
        Socket.send(Message.encode())
        data = Socket.recv(BUFFER_SIZE)

def dIdV_Scan():
    try:
        data = Socket.recv(BUFFER_SIZE)
    except:
        pass
    Message = "SetSWSubItemParameter, Scan Area Window, Scan Settings, Alternate Slow Scan, Top Down Only\n"
    Socket.send(Message.encode())
    data = Socket.recv(BUFFER_SIZE)

    Message = "SetSWSubItemParameter, Scan Area Window, Scan Settings, Scan Count Mode, Single\n"
    Socket.send(Message.encode())
    data = Socket.recv(BUFFER_SIZE)

    Message = f"GetSWSubItemParameter, Scan Area Window, Scan Settings, Lines Per Frame\n"
    Socket.send(Message.encode())
    Lines = float(Socket.recv(BUFFER_SIZE))
    Message = f"GetSWParameter, Scan Area Window, Line Time\n"
    Socket.send(Message.encode())
    LineTime = float(Socket.recv(BUFFER_SIZE))
    Message = f"GetSWSubItemParameter, Scan Area Window, Scan Settings, Over Scan Count\n"
    Socket.send(Message.encode())
    OverScanCount = float(Socket.recv(BUFFER_SIZE))
    ScanTime = 2*(Lines+OverScanCount)*LineTime

    Message = "StartProcedure, dI-dV Map Scan Speed\n"
    Socket.send(Message.encode())
    
    data = Socket.recv(BUFFER_SIZE)
    # data = Socket.recv(BUFFER_SIZE)

    StartTime = timer()
    while not Cancel:
        try:
            data = Socket.recv(BUFFER_SIZE)
            print(f"Scan Data: {data}")
            break
        except Exception as e:
            print(e)
            pass
        Percent = round(100*((timer() - StartTime)/ScanTime),1)
        OutgoingQueue.put(("SetStatus",(f"Scan {Percent}% Complete",2)))
    if Cancel:
        Message = "StopProcedure, dI-dV Map Scan Speed\n"
        Socket.send(Message.encode())
        data = Socket.recv(BUFFER_SIZE)
    Message = f"SetHWParameter, Drive CH1, Modulation, Disable\n"
    Socket.send(Message.encode())
    data = Socket.recv(BUFFER_SIZE)
# def Spectra():
#     pass