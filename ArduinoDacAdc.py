import qcodes as qc
from qcodes import Instrument
from qcodes.parameters import Parameter
from qcodes.instrument.visa import VisaInstrument, VisaInstrumentKWArgs
import serial
import time

class ArduinoDacAdc(Instrument):
    def __init__(self, name: str, port: str, baudrate: int = 115200, timeout: float = 0.5, 
                 **kwargs):
        super().__init__(name, **kwargs)

        #Initialize
        print("All DAC channels set to 0V")
        self._set_all_dac_zero()

        dac_voltages = {0:0.0, 1:0.0, 2:0.0, 3:0.0}

        self.ser = serial.Serial(port, baudrate=baudrate, timeout=timeout)
        print("Identifying...")
        self._board_identify()
        print("Ready?")
        self._board_ready()

    def _set_all_dac_zero(self):
        for i in range(0,4):
            self._set_dac_voltage(i, 0.0)
            self.dac_voltges[i] = 0.0

    def _set_dac_voltage(self, channel: int, voltage: float):
        cmd = f"SET,{channel},{voltage} r\n"
        counter = 0
        while counter !=3:
            self.ser.write(bytes(cmd, 'utf-8'))
            time.sleep(0.05)  
            response = self.ser.readline().strip()
            counter += 1
        self.dac_voltages[channel] = voltage
        print(f"DAC Response: {response}")

    def _get_dac_voltage(self, channel:int):
        return self.dac_voltages[channel]

    def _get_adc_voltage(self, channel: int):
        cmd = f"GET_ADC,{channel} r\n"
        counter = 0
        while counter !=3:
            self.ser.write(bytes(cmd, 'utf-8'))
            time.sleep(0.05)
            response = self.ser.readline().strip()
            counter +=1
        print(f"ADC Response: {response}")
        return str(response)
    
    # To ramp up a DAC Channel 2 from -8.5V to +4.8V in 1000 steps with a delay
    # of 30 microseconds per step RAMP1,2,-8.5,4.8,1000,30 r
    def _ramp1(self, channel: int, v_initial: float, v_final: float, steps: int, delay: int):
        cmd = f"RAMP1,{channel},{v_initial},{v_final},{steps},{delay} r\n"
        counter = 0
        while counter !=3:
            self.ser.write(bytes(cmd, 'utf-8'))
            time.sleep(0.05)
            response = self.ser.readline().strip()
            counter +=1
        print(f"Response: {response}")
        return str(response)

        
    def _board_ready(self):
        cmd = f"*RDY? r\n"
        counter = 0
        while counter !=3:
            self.ser.write(bytes(cmd, 'utf-8'))
            time.sleep(0.05)
            response = self.ser.readline().strip()
            counter +=1
        print(f"Response: {response}")

    def _board_identify(self):
        cmd = f"*IDN? r\n"
        counter = 0
        while counter !=3:
            self.ser.write(bytes(cmd, 'utf-8'))
            time.sleep(0.05)
            response = self.ser.readline().strip()
            counter +=1
        print(f"Response: {response}")
        

    def close(self):
        self.ser.close()
        super().close()
