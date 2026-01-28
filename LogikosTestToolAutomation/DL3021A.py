import pyvisa
from LogikosTestToolAutomation import test_tool_common
from typing import Optional, Union
from dataclasses import dataclass

"""
Controlling a RIGOL DL3021A DC Electronic Load

Note: Many functions are not implemented! See:
      https://www.rigolna.com/products/dc-power-loads/dl3000/
      DL3000 Programming Manual
"""

class DL3021A:
    """
    RIGOL DL3021A DC Electronic Load
    """

    def __init__(self, RID : str = ""):
        """
        Initialize DL3021A instance

        RID : pyVISA resource identifier. If not specified, the first UDP3305S found will be connected.

        See pyVISA documentation for details.
        https://pyvisa.readthedocs.io/en/latest/introduction/communication.html
        """
        self.models = ["DL3021A"]

        rm = pyvisa.ResourceManager()
        (self.connection, self.idn) = test_tool_common.connect_pyvisa_device(rm, RID, self.models)

        if not self.connection:
            raise RuntimeError(f"Instrument {self.models} not found." )

    def __del__(self):
        if self.connection:
            self.connection.close()

    def __str__(self):
        return f"{self.idn['model']} DC Electronic Load\nSN:{self.idn['SN']}\nFirmware: {self.idn['firmware']}"

    def wait(self):
        """
        Configures the instrument to wait for all pending operations to complete before executing any additional commands.
        """
        if not self.connection:
            raise RuntimeError(f"Instrument not connected.")

        self.connection.write("*WAI")

    # :STATUS:QUESTIONABLE:CONDITION?
    # :STATUS:QUESTIONABLE:ENABLE
    # :STATUS:QUESTIONABLE[:EVENT]?
    # :STATUS:PRESET
    # :STATUS:OPERATION:CONDITION?
    # :STATUS:OPERATION:ENABLE
    # :STATUS:OPERATION[:EVENT]?

    # :FETCH:VOLTAGE[:DC]?
    # :MEASURE:VOLTAGE[:DC]?
    # :FETCH:VOLTAGE:MAX?
    # :MEASURE:VOLTAGE:MAX?
    # :FETCH:VOLTAGE:MIN?
    # :MEASURE:VOLTAGE:MIN?
    # :FETCH:CURRENT[:DC]?
    # :MEASURE:CURRENT[:DC]?
    # :FETCH:CURRENT:MAX?
    # :MEASURE:CURRENT:MAX?
    # :FETCH:CURRENT:MIN?
    # :MEASURE:CURRENT:MIN?
    # :FETCH:RESISTANCE[:DC]?
    # :MEASURE:RESISTANCE[:DC]?
    # :FETCH:POWER[:DC]?
    # :MEASURE:POWER[:DC]?
    # :FETCH:CAPABILITY?
    # :MEASURE:CAPABILITY?
    # :FETCH:WATTHOURS?
    # :MEASURE:WATTHOURS?
    # :FETCH:DISCHARGINGTIME?
    # :MEASURE:DISCHARGINGTIME?
    # :FETCH:TIME?
    # :MEASURE:TIME?
    # :FETCH:WAVEDATA?
    # :MEASURE:WAVEDATA?

    # :TRIGGER
    # :TRIGGER:SOURCE


    def get_state(self):
        """
        Queries whether the input of the electronic load is on or off.
        """
        return self.connection.query(":SOURCE:INPUT:STATE?")

    def set_state(self, state):
        """
        Sets the input of the electronic load to be on or off.
        state: {0|1|ON|OFF}
        """

        if state == 0 or state == 1 or state.upper() in ("ON", "OFF"):
            self.connection.write(f":SOURCE:INPUT:STATE {state}")
        else:
            raise ValueError(f"'{state}' is not a valid state")

    def on(self):
        self.set_state("ON")

    def off(self):
        self.set_state("OFF")

    def get_function(self):
        """
        Queries the static operation mode of the electronic load.
        """
        return self.connection.query(":SOURCE:FUNC?")

    def set_function(self, fn):
        """
        Sets the static operation mode of the electronic load.
        fn: {CURR|RES|VOLT|POW}
        """

        if fn.upper() in ("CURR", "RES", "VOLT", "POW"):
            self.connection.write(f":SOURCE:FUNC {fn}")
        else:
            raise ValueError(f"'{fn}' is not a valid function")

    def get_mode(self):
        """
        Queries what controls the input regulation mode.

        FIXed: indicates that the input regulation mode is determined by the FUNCtion command.
        LIST: indicates that the input regulation mode is determined by the activated list command.
        WAVe: indicates that the input regulation mode is determined by the waveform display command.
        BATTery: indicates that the input regulation mode is determined by the battery discharge command.
        OCP: indicates that the input regulation mode is determined by the OCP command.
        OPP: indicates that the input regulation mode is determined by the OPP command.

        The query returns LIST in List mode; returns WAV in waveform display interface;
        returns BATT in battery discharge mode; returns OCP in OCP mode; returns OPP in
        OPP mode; returns FIX in other modes.
        """
        return self.connection.query(":SOURCE:FUNCTION:MODE?")

    def set_mode(self, mode):
        """
        The input regulation mode setting is controlled by the FUNCtion command, the list command,
        the waveform display command, the battery discharge command, the OCP command, or the OPP command.
        mode: {FIX|LIST|WAV|BATT|OCP|OPP}
        """

        if mode.upper() in ("FIX", "LIST", "WAV", "BATT", "OCP", "OPP"):
            self.connection.write(f":SOURCE:FUNCTION:MODE {mode}")
        else:
            raise ValueError(f"'{mode}' is not a valid input regulation mode")

    @dataclass
    class const_current_values:
        current : float = 0
        range : float = 0
        slew : float = 0
        von : float = 0
        v_limit : float = 0
        i_limit : float = 0

    def setup_const_current(self,
            current: Optional[Union[float, str]] = None,
            range: Optional[Union[float, str]] = None,
            slew: Optional[Union[float, str]] = None,
            von: Optional[Union[float, str]] = None,
            v_limit: Optional[Union[float, str]] = None,
            c_limit: Optional[Union[float, str]] = None):
        """
        Sets the load's regulated current, current range, slew, starting voltage, voltage limit,
        and current limit in CC mode.
        Only parameters specified will be set.
        'MIN', 'MAX', and 'DEF' can also be passed to any parameter
        """
        self.connection.write(":SOURCE:FUNC CURR")

        if current:
            self.connection.write(f":SOURCE:CURRENT:LEVEL {current}")

        if range:
            self.connection.write(f":SOURCE:CURRENT:RANGE {range}")

        if slew:
            self.connection.write(f":SOURCE:CURRENT:SLEW {slew}")

        if von:
            self.connection.write(f":SOURCE:CURRENT:VON {von}")

        if v_limit:
            self.connection.write(f":SOURCE:CURRENT:VLIMT {v_limit}")

        if c_limit:
            self.connection.write(f":SOURCE:CURRENT:ILIMT {c_limit}")

    def query_const_current(self) -> const_current_values:
        """
        Queries the load's regulated current, current range, slew, starting voltage, voltage limit,
        and current limit set in CC mode.
        """
        current = float(self.connection.query(":SOURCE:CURRENT:LEVEL?"))
        range = float(self.connection.query(":SOURCE:CURRENT:RANGE?"))
        slew = float(self.connection.query(":SOURCE:CURRENT:SLEW?"))
        von = float(self.connection.query(":SOURCE:CURRENT:VON?"))
        v_limit = float(self.connection.query(":SOURCE:CURRENT:VLIMT?"))
        i_limit = float(self.connection.query(":SOURCE:CURRENT:ILIMT?"))

        return DL3021A.const_current_values(current, range, slew, von, v_limit, i_limit)

    @dataclass
    class const_voltage_values:
        voltage : float = 0
        range : float = 0
        v_limit : float = 0
        i_limit : float = 0

    def setup_const_voltage(self,
            voltage: Optional[Union[float, str]] = None,
            range: Optional[Union[float, str]] = None,
            v_limit: Optional[Union[float, str]] = None,
            c_limit: Optional[Union[float, str]] = None):
        """
        Sets the load voltage, voltage range, voltage limit, and current limit set in CV mode.
        Only parameters specified will be set.
        'MIN', 'MAX', and 'DEF' can also be passed to any parameter
        """
        self.connection.write(":SOURCE:FUNC VOLT")

        if voltage:
            self.connection.write(f":SOURCE:VOLTAGE:LEVEL {voltage}")

        if range:
            self.connection.write(f":SOURCE:VOLTAGE:RANGE {range}")

        if v_limit:
            self.connection.write(f":SOURCE:VOLTAGE:VLIMT {v_limit}")

        if c_limit:
            self.connection.write(f":SOURCE:VOLTAGE:ILIMT {c_limit}")

    def query_const_voltage(self) -> const_voltage_values:
        """
        Queries the load voltage, voltage range, voltage limit, and current limit set in CV mode.
        """
        voltage = float(self.connection.query(":SOURCE:VOLTAGE:LEVEL?"))
        range = float(self.connection.query(":SOURCE:VOLTAGE:RANGE?"))
        v_limit = float(self.connection.query(":SOURCE:VOLTAGE:VLIMT?"))
        i_limit = float(self.connection.query(":SOURCE:VOLTAGE:ILIMT?"))

        return DL3021A.const_voltage_values(voltage, range, v_limit, i_limit)

    @dataclass
    class const_resistance_values:
        resistance : float = 0
        range : float = 0
        v_limit : float = 0
        i_limit : float = 0

    def setup_const_resistance(self,
            resistance: Optional[Union[float, str]] = None,
            range: Optional[Union[float, str]] = None,
            v_limit: Optional[Union[float, str]] = None,
            c_limit: Optional[Union[float, str]] = None):
        """
        Sets the load resistance, resistance range, voltage limit, and current limit in CR mode.
        Only parameters specified will be set.
        'MIN', 'MAX', and 'DEF' can also be passed to any parameter
        """
        self.connection.write(":SOURCE:FUNC RES")

        if resistance:
            self.connection.write(f":SOURCE:RESISTANCE:LEVEL {resistance}")

        if range:
            self.connection.write(f":SOURCE:RESISTANCE:RANGE {range}")

        if v_limit:
            self.connection.write(f":SOURCE:RESISTANCE:VLIMT {v_limit}")

        if c_limit:
            self.connection.write(f":SOURCE:RESISTANCE:ILIMT {c_limit}")

    def query_const_resistance(self) -> const_resistance_values:
        """
        Queries the load resistance, resistance range, voltage limit, and current limit in CR mode.
        """
        resistance = float(self.connection.query(":SOURCE:RESISTANCE:LEVEL?"))
        range = float(self.connection.query(":SOURCE:RESISTANCE:RANGE?"))
        v_limit = float(self.connection.query(":SOURCE:RESISTANCE:VLIMT?"))
        i_limit = float(self.connection.query(":SOURCE:RESISTANCE:ILIMT?"))

        return DL3021A.const_resistance_values(resistance, range, v_limit, i_limit)

    @dataclass
    class const_power_values:
        power : float = 0
        v_limit : float = 0
        i_limit : float = 0

    def setup_const_power(self,
            power: Optional[Union[float, str]] = None,
            v_limit: Optional[Union[float, str]] = None,
            c_limit: Optional[Union[float, str]] = None):
        """
        Sets the load power, voltage limit, and current limit in CP mode.
        Only parameters specified will be set.
        'MIN', 'MAX', and 'DEF' can also be passed to any parameter
        """
        self.connection.write(":SOURCE:FUNC POW")

        if power:
            self.connection.write(f":SOURCE:POWER:LEVEL {power}")

        if v_limit:
            self.connection.write(f":SOURCE:POWER:VLIMT {v_limit}")

        if c_limit:
            self.connection.write(f":SOURCE:POWER:ILIMT {c_limit}")

    def query_const_power(self) -> const_power_values:
        """
        Queries the load power, voltage limit, and current limit in CP mode.
        """
        power = float(self.connection.query(":SOURCE:POWER:LEVEL?"))
        v_limit = float(self.connection.query(":SOURCE:POWER:VLIMT?"))
        i_limit = float(self.connection.query(":SOURCE:POWER:ILIMT?"))

        return DL3021A.const_power_values(power, v_limit, i_limit)









    # :SOURCE:CURRENT:SLEW:POSITIVE
    # :SOURCE:CURRENT:SLEW:NEGATIVE

    # :SOURCE:CURRENT:TRANSIENT:MODE
    # :SOURCE:CURRENT:TRANSIENT:ALEVEL
    # :SOURCE:CURRENT:TRANSIENT:BLEVEL
    # :SOURCE:CURRENT:TRANSIENT:AWIDTH
    # :SOURCE:CURRENT:TRANSIENT:BWIDTH
    # :SOURCE:CURRENT:TRANSIENT:FREQUENCY
    # :SOURCE:CURRENT:TRANSIENT:PERIOD
    # :SOURCE:CURRENT:TRANSIENT:ADUTY




    # :SOURCE:LIST:MODE
    # :SOURCE:LIST:RANGE
    # :SOURCE:LIST:COUNT
    # :SOURCE:LIST:STEP
    # :SOURCE:LIST:LEVEL
    # :SOURCE:LIST:WIDTH
    # :SOURCE:LIST:SLEW
    # :SOURCE:LIST:END
    # :SOURCE:BATTARY:RANGE
    # :SOURCE:BATTARY:LEVEL
    # :SOURCE:BATTARY:VSTOP
    # :SOURCE:BATTARY:CSTOP
    # :SOURCE:BATTARY:TIMESTOP
    # :SOURCE:BATTARY:VON
    # :SOURCE:BATTARY:VENABSTOP
    # :SOURCE:BATTARY:CENABSTOP
    # :SOURCE:BATTARY:TENABSTOP
    # :SOURCE:OCP:RANGE
    # :SOURCE:OCP:VON
    # :SOURCE:OCP:VONDELAY
    # :SOURCE:OCP:ISET
    # :SOURCE:OCP:ISTEP
    # :SOURCE:OCP:IDELAYSTEP
    # :SOURCE:OCP:IMAX
    # :SOURCE:OCP:IMIN
    # :SOURCE:OCP:VOCP
    # :SOURCE:OCP:TOCP
    # :SOURCE:OPP:VON
    # :SOURCE:OPP:VONDELAY
    # :SOURCE:OPP:PSET
    # :SOURCE:OPP:PSTEP
    # :SOURCE:OPP:PDELAYSTEP
    # :SOURCE:OPP:PMAX
    # :SOURCE:OPP:PMIN
    # :SOURCE:OPP:VOPP
    # :SOURCE:OPP:TOPP
    # :SOURCE:WAVE:TIME
    # :SOURCE:WAVE:TSTEP
    # :SOURCE:SENSE

    # :SYSTEM:KEY
    # :SYSTEM:ERROR?
    # :SYSTEM:VERSION?
    # :SYSTEM:IDN

    # LXI:IDENTIFY:STATE
    # LXI:MDNS:ENABLE
    # LXI:RESET
    # LXI:RESTART

    # :LIC:SET

