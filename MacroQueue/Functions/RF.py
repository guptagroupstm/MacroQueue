import pyvisa
import CreaTec

CurrentMacro = None
OutgoingQueue = None
Cancel = False
MacroQueueSelf = None

def Connect_To_RF_Generator():
    global RFGenerator

    rm = pyvisa.ResourceManager()
    # ResourceList = rm.list_resources()
    RFGenerator = rm.open_resource('USB0::0x03EB::0xAFFF::481-34B6D0608-2368::INSTR')
    RFGenerator.write_termination = '\n'
    RFGenerator.read_termination = '\n'
    pass

# Freq=Hz;The RF frequency in Hz
def Set_RF_Freq(Freq=1e9):
    global RFGenerator
    if RFGenerator is None: 
        Connect_To_RF_Generator()
    RFGenerator.write(f'SOUR:FREQ {Freq}')

# Power=dBm;The amount of power for the RF generator in dBm
def Set_RF_Power(Power=0):
    global RFGenerator
    if RFGenerator is None: 
        Connect_To_RF_Generator()
    RFGenerator.write(f'SOUR:POW {Power}')
    print(str(RFGenerator.query(f'SOUR:POW?')))


# Start_Freq=Hz;The frequency to start the RF sweep in Hz
# Stop_Freq=Hz;The frequency to stop the RF sweep in Hz
def StartRFFreqSweep(Start_Freq=1e8,Stop_Frequency=1e9):
    global RFGenerator
    if RFGenerator is None: 
        Connect_To_RF_Generator()
    pass

# Start_power=dBm;The power to start the RF sweep in dBm
# Stop_power=dBm;The power to stop the RF sweep in dBm
def StartRFPowerSweep(Start_power=-10,Stop_power=10):
    global RFGenerator
    if RFGenerator is None: 
        Connect_To_RF_Generator()
    pass

# Path;The path to the excel (.csv) sheet with the power & freq parameters
def StartRFListSweep(Path=""):
    global RFGenerator
    if RFGenerator is None: 
        Connect_To_RF_Generator()
    pass