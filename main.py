import qcodes as qc
from qcodes import Instrument
from qcodes.parameters import Parameter
from qcodes.instrument.visa import VisaInstrument, VisaInstrumentKWArgs
import serial
import time


def main():
    b = ArduinoDacAdc('DACBoard', 'COM8')
    #b._board_ready()
    b._set_dac_voltage(0,0.1)
    b.close()

class ArduinoDacAdc(Instrument):
    def __init__(self, name: str, port: str, baudrate: int = 115200, timeout: float = 0.5,
                 **kwargs):
        super().__init__(name, **kwargs)
        self.ser = serial.Serial(port, baudrate=baudrate, timeout=timeout)

    def _set_dac_voltage(self, channel: int, voltage: float):
        cmd = f"SET,{channel},{voltage} r\n"
        counter = 0
        while counter !=3:
            self.ser.write(bytes(cmd, 'utf-8'))
            time.sleep(0.05)
            response = self.ser.readline().strip()
            counter += 1
        print(f"DAC Response: {response}")

    def _get_adc_voltage(self, channel: int):
        cmd = f"GET_ADC,{channel} r\n"
        counter = 0
        while counter !=3:
            self.ser.write(bytes(cmd, 'utf-8'))
            time.sleep(0.05)
            response = self.ser.readline().strip()
            counter +=1
        print(f"ADC Response: {response}")
        return float(response)
    
    def _board_ready(self):
        cmd = f"*RDY? r\n"
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

if __name__ == "__main__":
    main()