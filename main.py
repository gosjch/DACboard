
from qcodes import Instrument
from qcodes.parameters import Parameter
import serial
import time

def main():
    import serial
    ser = serial.Serial('/dev/ttyUSB0')
    print(ser.name)
    ser.write(b'hello')
    ser.close()


class ArduinoDacAdc(Instrument):
    def __init__(self, name: str, port: str, baudrate: int = 115200, timeout: float = 1.0, **kwargs):
        super().__init__(name, **kwargs)
        self.ser = serial.Serial(port, baudrate=baudrate, timeout=timeout)

        # Add DAC voltage setter
        self.add_parameter(
            "dac_voltage",
            label="DAC Voltage",
            unit="V",
            get_cmd=None,  # You can implement later
            set_cmd=self._set_dac_voltage,
        )

        # Add ADC voltage reader
        self.add_parameter(
            "adc_voltage",
            label="ADC Voltage",
            unit="V",
            get_cmd=self._get_adc_voltage,
            set_cmd=None,
        )

    def _set_dac_voltage(self, voltage: float):
        channel = 0 
        cmd = f"SET,{channel},{voltage} r\n"
        self.ser.write(cmd.encode())
        time.sleep(0.05)  
        response = self.ser.readline().decode().strip()
        print(f"DAC Response: {response}")

    def _get_adc_voltage(self):
        channel = 0
        cmd = f"GET_ADC,{channel} r\n"
        self.ser.write(cmd.encode())
        time.sleep(0.05)
        response = self.ser.readline().decode().strip()
        print(f"ADC Response: {response}")
        return float(response)

    def close(self):
        self.ser.close()
        super().close()



if __name__ == "__main__":
    main()
