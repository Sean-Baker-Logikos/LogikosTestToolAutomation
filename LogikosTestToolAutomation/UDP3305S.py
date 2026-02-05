import pyvisa
from LogikosTestToolAutomation import test_tool_common
from enum import Enum
import time

"""
Controlling a UNI-T UDP3305S power supply
"""

class UDP3305S:
    """Uni-T UDP3305S Lab power supply

    Features 5 channels:
        ch1     channel1 (max 33V 5.2A)
        ch2     channel2 (max 33V 5.2A)
        ch3     channel3 (max 6.2V 3.2A)
        chSER   virtual channel vor serial mode (max 66V 5.2A)
        chPARA  virtual channel for parallel mode (max 33V 10.4A)
    """

    class Mode(Enum):
        NORM    = 0
        SER     = 1
        PARA    = 2

    def __init__(self, RID : str = ""):
        """
        Initialize UDP3305S instance

        RID : pyVISA resource identifier. If not specified, the first UDP3305S found will be connected.

        See pyVISA documentation for details.
        https://pyvisa.readthedocs.io/en/latest/introduction/communication.html
        """
        self.models = ["UDP3305S", "UDP3305S-E"]

        rm = pyvisa.ResourceManager()
        (self.connection, self.idn) = test_tool_common.connect_pyvisa_device(rm, RID, self.models)

        if not self.connection:
            raise RuntimeError(f"Instrument {self.models} not found." )

        self.ch1 = UDP3305S_channel("CH1", self.connection, V_max=33, A_max=5.2)
        self.ch2 = UDP3305S_channel("CH2", self.connection, V_max=33, A_max=5.2)
        self.ch3 = UDP3305S_channel("CH3", self.connection, V_max=6.2, A_max=3.2)
        self.chSER = UDP3305S_channel("SER", self.connection, V_max=66, A_max=5.2)
        self.chPARA = UDP3305S_channel("PARA", self.connection, V_max=33, A_max=10.4)

    def __del__(self):
        if self.connection:
            self.connection.close()

    def __str__(self):
        return f"{self.idn['model']} 3-channel lab power supply\nSN:{self.idn['SN']}\nFirmware: {self.idn['firmware']}"

    def set_mode(self, mode : Mode):
        """
        Sets the mode of the power supply channels 1 and 2, either normal, serial or parallel.
        mode : UDP3305S.Mode
        """
        self.connection.write(f"SOURCE:MODE {mode.name}")

        # It takes some time for the power supply to switch modes, during this time if executing the commands related
        # to work mode of the power supply, it may cause the command execution to fail. Therefore, after switching
        # work mode of the power supply, a new command is executed after an interval of at least 500 milliseconds.
        time.sleep(0.5)

    def get_mode(self):
        return self.connection.query("SOURCE:MODE?")

    def on(self):
        """
        Turn on all outputs
        """
        self.connection.write(f"OUTPUT:STATE ALL,ON")

    def off(self):
        """
        Turn off all outputs
        """
        self.connection.write(f"OUTPUT:STATE ALL,OFF")

    def lock(self):
        """
        Lock keys on instrument panel
        """
        self.connection.write("LOCK ON")

    def unlock(self):
        """
        Unlock keys on instrument panel
        """
        self.connection.write("LOCK OFF")


class UDP3305S_channel:
    """
    Class representing a single channel of the UDP3305S power supply
    """
    def __init__(self, name : str, connection : pyvisa.resources.MessageBasedResource, V_max : float, A_max : float):
        """
        Initialize channel object
            name        name of the channel
            connection  connection object to read/write from/to
            V_max       max voltage supported
            A_max       max current supported
        """
        self.connection = connection
        self.name = name
        self.V_max = V_max
        self.A_max = A_max

    def set_voltage(self, value : float):
        """
        Set output voltage [V]
        """
        if 0 < value <= self.V_max:
            self.connection.write(f"APPLY {self.name},{value}V")
        else:
            raise ValueError(f"Voltage must be in [0, {self.V_max}] V")

    def get_voltage(self):
        """
        Get output voltage [V]
        """
        return float(self.connection.query(f"APPLY? {self.name},VOLT").split(",")[1])

    def set_current(self, value : float):
        """
        Set current limit [A]

        value: current limit in Amps
        """
        if 0 < value <= self.A_max:
            self.connection.write(f"APPLY {self.name},{value}A")
        else:
            raise ValueError(f"Current must be in [0, {self.A_max}] A")

    def get_current(self):
        """
        Get current limit [A]
        """
        return float(self.connection.query(f"APPLY? {self.name},CURRENT").split(",")[1])

    def set_OVP(self, value : float, state : bool = True):
        """
        set over voltage protection (OVP) value [V]
        """
        if 0 < value <= self.V_max:
            self.connection.write(f"OUTPUT:OVP:VALUE {self.name},{value}")
        else:
            raise ValueError(f"OVP Voltage must be in [0, {self.V_max}] V")

        self.connection.write(f"OUTPUT:OVP:STATE {self.name},{'ON' if state else 'OFF'}")

    def get_OVP(self):
        """
        return over voltage protection (OVP) value [V]
        """
        value = float(self.connection.query(f"OUTPUT:OVP:VALUE? {self.name}"))
        state = self.connection.query(f"OUTPUT:OVP:STATE? {self.name}")
        return (value, state)

    def set_OCP(self, value : float, state : bool = True):
        """
        set over current protection (OCP) value [A]
        """
        if 0 < value <= self.A_max:
            self.connection.write(f"OUTPUT:OCP:VALUE {self.name},{value}")
        else:
            raise ValueError(f"OCP current must be in [0, {self.A_max}] A")

        self.connection.write(f"OUTPUT:OCP:STATE {self.name},{'ON' if state else 'OFF'}")

    def get_OCP(self):
        """
        return over current protection (OCP) value [A]
        """
        value = float(self.connection.query(f"OUTPUT:OCP:VALUE? {self.name}"))
        state = self.connection.query(f"OUTPUT:OCP:STATE? {self.name}")
        return (value, state)

    def read_voltage(self):
        """
        read (measure) output voltage [V]
        """
        return float(self.connection.query(f"MEASURE:VOLT? {self.name}"))

    def read_current(self):
        """
        read (measure) output current [A]
        """
        return float(self.connection.query(f"MEASURE:CURRENT? {self.name}"))

    def read_power(self):
        """
        read (measure) output power [W]
        """
        return float(self.connection.query(f"MEASURE:POWER? {self.name}"))

    def read_all(self):
        """
        read (measure) output values: Volts [V], current [A], Power[W]
        """
        return [float(x) for x in self.connection.query(f"MEASURE:ALL? {self.name}").split(",")]

    def on(self):
        """
        Turn channel on
        """
        self.connection.write(f"OUTPUT:STATE {self.name},ON")

    def off(self):
        """
        Turn channel off
        """
        self.connection.write(f"OUTPUT:STATE {self.name},OFF")
