import numpy as np
import time
import socket

Socket = None
BUFFER_SIZE = None
Cancel = False
def Initialize():
    global Socket, BUFFER_SIZE
    IP_Address_R9_PC   = '127.0.0.1'
    TCP_Port_R9s       = 12600
    BUFFER_SIZE = 1024
    Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    Socket.connect((IP_Address_R9_PC, TCP_Port_R9s))
    time.sleep(0.1)


def OnClose():
    if Socket is not None:
        Socket.shutdown(2)
        Socket.close()


# Bias=The bias voltage in V
def Set_Bias(Bias= 0):
    Message = f"SetSWParameter, STM Bias, Value, {Bias}\n"
    Socket.send(Message.encode())
    data = Socket.recv(BUFFER_SIZE)
    time.sleep(0.5)
    data = Socket.recv(BUFFER_SIZE)

# BiasRate=The rate the bias changes in V/s 
def Set_Bias_Rate(BiasRate=1):
    Message = "SetSWParameter, STM Bias, Rate, {BiasRate}\n"
    Socket.send(Message.encode())
    data = Socket.recv(BUFFER_SIZE)

# Setpoint=The current setpoint in Amps
def Set_Setpoint(Setpoint=1e-9):
    Message = f"SetHWSubParameter, Z PI Controller 1, Set Point, Value, {Setpoint}\n"
    Socket.send(Message.encode())
    data = Socket.recv(BUFFER_SIZE)


# XOffset=The X center of the image in nm
# YOffset=The Y center of the image in nm
def Set_Scan_Window_Position(XOffset=0,YOffset=0):
    Message = f'SetSWParameter, Scan Area Window, X Offset, {XOffset}\n'
    Socket.send(Message.encode())
    data = Socket.recv(BUFFER_SIZE)
    
    Message = f'SetSWParameter, Scan Area Window, Y Offset, {YOffset}\n'
    Socket.send(Message.encode())
    data = Socket.recv(BUFFER_SIZE)
    
# ImageSize=The length of a row and column in nm
def Set_Scan_Image_Size(ImageSize=1e-9):
    Message = f'SetSWParameter, Scan Area Window, Scan Area Size, {ImageSize}\n'
    Socket.send(Message.encode())
    data = Socket.recv(BUFFER_SIZE)

# Angle=The angle on the scan in degrees
def Set_Scan_Window_Angle(Angle=0):
    Message = f"SetSWParameter, Scan Area Window, Rotate Angle, {Angle}\n"
    Socket.send(Message.encode())
    data = Socket.recv(BUFFER_SIZE)

# NPixels=The number of pixels in each row and each column
def Set_NPixels(NPixels=512):
    Message = f"SetSWSubItemParameter, Scan Area Window, Scan Settings, Lines Per Frame, {NPixels}\n"
    Socket.send(Message.encode())
    data = Socket.recv(BUFFER_SIZE)

# LineSpeed=The speed the tip moves in nm/s
def Set_Scan_Speed(LineSpeed=2e-9):
    Message = f"SetSWParameter, Scan Area Window, Scan Speed, {LineSpeed}\n"
    Socket.send(Message.encode())
    data = Socket.recv(BUFFER_SIZE)

# WaitTime=The time to wait in s
def Wait(WaitTime=10):
    time.sleep(WaitTime)

def Scan():
    print ("Received data:", data)
    Message = "SetSWSubItemParameter, Scan Area Window, Scan Settings, Scan Count Mode, Single\n"
    Socket.send(Message.encode())
    data = Socket.recv(BUFFER_SIZE)

    Message = "StartProcedure, Comb Scan\n"
    Socket.send(Message.encode())
    data = Socket.recv(BUFFER_SIZE)
    data = Socket.recv(BUFFER_SIZE)