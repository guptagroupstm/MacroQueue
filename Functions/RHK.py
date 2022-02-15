import numpy as np
import time
import socket

Socket = None
BUFFER_SIZE = None
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


Set_Bias_SettingsInfo = { "Bias":{"DefaultValue":0,"Type":"Numerical"}, }
def Set_Bias(Settings):
    Message = f"SetSWParameter, STM Bias, Value, {Settings['Bias']}\n"
    Socket.send(Message.encode())
    data = Socket.recv(BUFFER_SIZE)


Set_Setpoint_SettingsInfo = { "Setpoint" : {"DefaultValue":0,"Type":"Numerical"}, }
def Set_Setpoint(Settings):
    Message = f"SetHWSubParameter, Z PI Controller 1, Set Point, Value, {Settings['Setpoint']}\n"
    Socket.send(Message.encode())
    data = Socket.recv(BUFFER_SIZE)