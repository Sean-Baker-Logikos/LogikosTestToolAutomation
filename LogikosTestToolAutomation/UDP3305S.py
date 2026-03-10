import pyvisa
from LogikosTestToolAutomation import test_tool_common
from enum import Enum
import time
import sys
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
        self.rid = RID

        rm = pyvisa.ResourceManager()
        (self.connection, self.idn, self.rid) = test_tool_common.connect_pyvisa_device(rm, RID, self.models)

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


    def execute_command(self, command : list):
        match command[0]:
            case "on":
                self.on()
            case "off":
                self.off()
            case "voltage":
                if len(command) > 1:
                    self.set_voltage(float(command[1]))
                else:
                    raise ValueError("Voltage value not specified.")
            case "current":
                if len(command) > 1:
                    self.set_current(float(command[1]))
                else:
                    raise ValueError("Current value not specified.")
            case "OVP":
                if len(command) > 1:
                    if command[1].upper() == "OFF":
                        self.set_OVP(0, state=False)
                    else:
                        self.set_OVP(float(command[1]), state=True)
                else:
                    raise ValueError("OVP value not specified.")
            case "OCP":
                if len(command) > 1:
                    if command[1].upper() == "OFF":
                        self.set_OCP(0, state=False)
                    else:
                        self.set_OCP(float(command[1]), state=True)
                else:
                    raise ValueError("OCP value not specified.")
            case "read":
                voltage = self.read_voltage()
                current = self.read_current()
                power = self.read_power()
                print(f"{self.name} Output: {voltage:.2f} V, {current:.2f} A, {power:.2f} W")
            case _:
                print(f"Command '{command}' not found for {self.name}.")



class UDP3305S_commandline:

    def __init__(self, RID : str = ""):
        self.rid = RID

    def execute_command(self, command : list):
        if not command:
            print("No command specified.")
            sys.exit(1)

        if command[0] == "list":
            print("Available commands:")
            print("  list - list available commands")
            print("  on - turn on all outputs")
            print("  off - turn off all outputs")
            print("  ch# <cmd> - channel commands (ch1, ch2, ch3, chSER, chPARA)")
            print("      on - turn on channel output")
            print("      off - turn off channel output")
            print("      voltage <value> - set channel voltage [V]")
            print("      current <value> - set channel current limit [A]")
            print("      OVP <value> - set channel over voltage protection (OVP) value [V] or 'OFF' to disable")
            print("      OCP <value> - set channel over current protection (OCP) value [A] or 'OFF' to disable")
            print("      read - measure channel output voltage, current, and power")
        else:
            
            try:    
                tool = UDP3305S(RID=self.rid)
            except RuntimeError as e:
                print("Error: Could not connect to UDP3305S power supply.")
                sys.exit(1)
            if not tool:
                print("Error: Could not connect to UDP3305S power supply.")
                sys.exit(1)
            print(tool.rid)

            match command[0]:
                case "on":
                    tool.on()
                case "off":
                    tool.off()

                case "ch1" | "ch2" | "ch3" | "chSER" | "chPARA":
                    channel = getattr(tool, command[0])

                    match command[1]:
                        case "on":
                            channel.on()
                        case "off":
                            channel.off()
                        case "voltage":
                            if len(command) < 3:
                                print("Error: Voltage value not specified.")
                                sys.exit(1)
                            else:
                                try:
                                    channel.set_voltage(float(command[2]))
                                except ValueError as e:
                                    print(f"Error: {e}")
                                    sys.exit(1)
                        case "current":
                            if len(command) < 3:
                                print("Error: Current value not specified.")
                                sys.exit(1)
                            else:
                                try:
                                    channel.set_current(float(command[2]))
                                except ValueError as e:
                                    print(f"Error: {e}")
                                    sys.exit(1)
                        case "OVP":
                            if len(command) < 3:
                                print("Error: OVP value not specified.")
                                sys.exit(1)
                            else:
                                if command[2].upper() == "OFF":
                                    channel.set_OVP(0, state=False)
                                else:
                                    try:
                                        channel.set_OVP(float(command[2]), state=True)
                                    except ValueError as e:
                                        print(f"Error: {e}")
                                        sys.exit(1)
                        case "OCP":
                            if len(command) < 3:
                                print("Error: OCP value not specified.")
                                sys.exit(1)
                            else:
                                if command[2].upper() == "OFF":
                                    channel.set_OCP(0, state=False)
                                else:
                                    try:
                                        channel.set_OCP(float(command[2]), state=True)
                                    except ValueError as e:
                                        print(f"Error: {e}")
                                        sys.exit(1)
                        case "read":
                            voltage = channel.read_voltage()
                            current = channel.read_current()
                            power = channel.read_power()
                            print(f"{channel.name} Output: {voltage:.2f} V, {current:.2f} A, {power:.2f} W")

                        case _:
                            print(f"Command '{command}' not found.")
                            sys.exit(1)

                case _:
                    print(f"Command '{command}' not found.")
                    sys.exit(1)
