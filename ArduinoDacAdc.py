import qcodes as qc
from qcodes import Instrument
import serial
import time
import re

class ArduinoDacAdc(Instrument):
    """
    Proper QCoDeS driver for the Arduino DAC/ADC board.
    Provides 4 DAC outputs and 4 ADC inputs as Parameters.
    """

    def __init__(self, name: str, port: str, baudrate: int = 115200, timeout: float = 0.5, **kwargs):
        super().__init__(name, **kwargs)

        # Openign serial connection
        self.ser = serial.Serial(port, baudrate=baudrate, timeout=timeout)
        time.sleep(0.1) 

        # Store last DAC voltages
        self.dac_voltages = {i: 0.0 for i in range(4)}
        self.set_all_dac_zero

        # The DAC channels are now parameters
        for ch in range(4):
            self.add_parameter(
                f"dac{ch}",
                label=f"DAC Channel {ch}",
                unit="V",
                get_cmd=lambda ch=ch: self.dac_voltages[ch],
                set_cmd=lambda v, ch=ch: self.set_dac_voltage(ch, v),
                vals=qc.validators.Numbers(-10, 10)  # Example voltage range
            )

        # ADC channels are read-only parameters
        for ch in range(4):
            self.add_parameter(
                f"adc{ch}",
                label=f"ADC Channel {ch}",
                unit="V",
                get_cmd=lambda ch=ch: self.get_adc_voltage(ch),
                set_cmd=False
            )

        # Helper parameters
        self.add_parameter(
            "identity",
            get_cmd=self.identify,
            set_cmd=False
        )

        self.add_parameter(
            "is_ready",
            get_cmd=self.ready,
            set_cmd=False
        )

        print("Arduino DAC/ADC initialized.")
        self.set_all_dac_zero()
        self.identify()
        self.ready()

    #-------------------------------#

    # For some reason unknown to me, commands seem to work only when sent the 3rd time, so retries are necessary
    def send_command(self, cmd: str, retries: int = 3):
        """Send a command over serial and return response as string."""
        response = b""
        for _ in range(retries):
            self.ser.write(cmd.encode())
            time.sleep(0.05)
            response = self.ser.readline().strip()
        return response.decode(errors="ignore")

    def set_all_dac_zero(self):
        for ch in range(4):
            self.set_dac_voltage(ch, 0.0)

    def set_dac_voltage(self, channel: int, voltage: float):
        cmd = f"SET,{channel},{voltage} r\n"
        response = self.send_command(cmd)
        self.dac_voltages[channel] = voltage
        return response

    # re.search because this one returns weird strings, test if these readings are accurate later
    def get_adc_voltage(self, channel: int):
        cmd = f"GET_ADC,{channel} r\n"
        response = self.send_command(cmd)
        # Extract the last numeric value from the response
        match = re.search(r"[-+]?\d*\.\d+|\d+", response)
        if match:
            return float(match.group())
        return float('nan')

    def identify(self):
        return self.send_command("*IDN? r\n")

    def ready(self):
        return self.send_command("*RDY? r\n")

    def reset(self):
        return self.send_command("RESET r\n")

    def talk(self):
        return self.send_command("TALK r\n")

    def close(self):
        self.ser.close()
        super().close()
