from unittest import case

import pyvisa
from LogikosTestToolAutomation import test_tool_common
from typing import Union
from enum import Enum, Flag

"""
Controlling a SIGLENT SDS 1104X-E Digitial Storage Oscilloscope

Note: Many functions are not implemented! See:
      https://siglentna.com/wp-content/uploads/dlm_uploads/2025/11/SDS1000-SeriesSDS2000XSDS2000X-E_ProgrammingGuide_EN02E.pdf
"""

class SDS1104X:
    """
    SIGLENT SDS 1104X-E Digitial Storage Oscilloscope
    """
    class Status(Flag):
        """
        15  ---     Not used (always 0)
        14  ---     Not used (always 0)
        13  8192    Trigger is ready
        12  4096    Pass/Fail test detected desired outcome
        11  2048    Waveform processing has terminated in Trace D
        10  1024    Waveform processing has terminated in Trace C
        9   512     Waveform processing has terminated in Trace B
        8   256     Waveform processing has terminated in Trace A
        7   128     A memory card, floppy or hard disk exchange has been detected
        6   64      Memory card, floppy or hard disk has become full in “AutoStore Fill” mode
        5   ---     Not use(always 0)
        4   16      A segment of a sequence waveform has been acquired
        3   8       A time-out has occurred in a data block transfer
        2   4       A return to the local state is detected
        1   2       A screen dump has terminated
        0   1       A new signal has been acquired
        """
        TRIGGER_READY           = 8192
        SIGNAL_ACQUIRED         = 1
        NONE                    = 0

    class TriggerMode(Enum):
        AUTO = 0
        NORM = 1
        SINGLE = 2

    class TriggerSlope(Enum):
        NEG = 0     # falling edge
        POS = 1     # rising edge
        WINDOW = 2  # alternating edge

    class Unit(Enum):
        V = 0
        A = 1

    class CouplingMode(Enum):
        A1M = 0
        D1M = 1
        GND = 2

    class CursorMode(Enum):
        OFF = 0
        MANUAL = 1
        TRACK = 2

    class CursorType(Enum):
        X = 0
        Y = 1
        X_Y = 2

    class CursorValueType(Enum):
        HREL = 0
        VREL = 1

    class Cursor(Enum):
        VREF = 0
        VDIF = 1
        TREF = 2
        TDIF = 3
        HREF = 4
        HDIF = 5

    def __init__(self, RID : str = ""):
        """
        Initialize SDS1104X instance

        RID : pyVISA resource identifier. If not specified, the first UDP3305S found will be connected.

        See pyVISA documentation for details.
        https://pyvisa.readthedocs.io/en/latest/introduction/communication.html
        """
        self.models = ["SDS1104X-E"]
        self.rid = RID

        rm = pyvisa.ResourceManager()
        (self.connection, self.idn) = test_tool_common.connect_pyvisa_device(rm, RID, self.models)

        if not self.connection:
            raise RuntimeError(f"Instrument {self.models} not found." )

        self.ch1 = SDS1104X_channel('C1', self.connection)
        self.ch2 = SDS1104X_channel('C2', self.connection)
        self.ch3 = SDS1104X_channel('C3', self.connection)
        self.ch4 = SDS1104X_channel('C4', self.connection)

        self.connection.write('CHDR OFF')
        # pyvisa.errors.VisaIOError

    def __del__(self):
        if self.connection:
            self.connection.close()

    def __str__(self):
        return f"{self.idn['model']} Digital Storage Oscilloscope\nSN:{self.idn['SN']}\nFirmware: {self.idn['firmware']}"

    # STATUS COMMANDS

    def get_status(self) -> Status:
        return SDS1104X.Status(int(self.connection.query("INR?")))

    # COMMON COMMANDS

    def default(self):
        """
        Reset the oscilloscope. This is the same as pressing the "Default" button
        """
        self.connection.write("*RST")

    # AUTOSET COMMANDS

    def auto_setup(self):
        """
        The AUTO_SETUP command attempts to identify the waveform type and automatically adjusts controls to
        produce a usable display of the input signal.
        """
        self.connection.write('ASET')

    # SAVE COMMANDS
    # RECALL COMMANDS

    def write_state_file(self, filename : str):
        """
        Saves the current oscilloscope state into a local XML file.
        filename : path to XML state file
        """
        self.connection.chunk_size = 200000
        self.connection.timeout = 30000

        self.connection.write('CHDR OFF')
        with open(filename, "wb") as datafile:
            self.connection.write('PNSU?')
            while True:
                state_data = self.connection.read_raw()
                if not state_data or state_data == b'\n':
                    break
                datafile.write(state_data)

    def load_state_file(self, filename : str):
        """
        Loads the oscilloscope state from a local XML file.
        filename : path to XML state file
        """
        self.connection.chunk_size = 200000
        self.connection.timeout = 30000

        with open(filename, "r") as datafile:
            state_data = datafile.read()
            command = "PNSU " + state_data
            self.connection.write_raw(command.encode('utf-8'))

    # TIMEBASE COMMANDS

    def set_time_div(self, timediv : Union[str, float]):
        """
        The TIME_DIV command sets the horizontal scale per division for the main window.
        Valid timediv values are: 1NS, 2NS, 5NS, 10NS, 20NS, 50NS, 100NS, 200NS, 500NS,
                                  1US, 2US, 5US, 10US, 20US, 50US, 100US, 200US, 500US,
                                  1MS, 2MS, 5MS, 10MS, 20MS, 50MS, 100MS, 200MS, 500MS,
                                  1S, 2S, 5S, 10S, 20S, 50S, 100S
        timediv : new time division as a string with units (S/mS/uS/nS) or a float in seconds, and will be rounded to the next highest valid value.
        """
        if isinstance(timediv, str):
            self.connection.write(f'TDIV {timediv}')
        else:
            valid_values = []
            for v in [1,2,5,10,20,50,100,200,500]:
                valid_values.append((v / 1000000000, f'{v}NS'))
            for v in [1,2,5,10,20,50,100,200,500]:
                valid_values.append((v / 1000000, f'{v}US'))
            for v in [1,2,5,10,20,50,100,200,500]:
                valid_values.append((v / 1000, f'{v}MS'))
            for v in [1,2,5,10,20,50,100]:
                valid_values.append((v, f'{v}S'))

            for v, s in valid_values:
                if timediv <= v:
                    self.connection.write(f'TDIV {s}')
                    break

    def get_time_div(self) -> str:
        return self.connection.query('TDIV?')

    def set_trig_delay(self, delay : Union[str, float]):
        """
        The TRIG_DELAY command sets the time interval from the trigger event to the horizontal center point on the screen.
        The maximum position value depends on the time/division settings.
        delay : new delay value as a string with units (S/mS/uS/nS) or a float in seconds.
        """
        if isinstance(delay, str):
            self.connection.write(f'TRDL {delay}')
        else:
            self.connection.write(f'TRDL {delay}S')

    def get_trig_delay(self) -> str:
        return self.connection.query('TRDL?')

    # TRIGGER COMMANDS

    def set_trigger_mode(self, mode : TriggerMode):
        self.connection.write(f'TRMD {mode.name}')

    def get_trigger_mode(self) -> str:
        return self.connection.query('TRMD?')

    def set_trigger_slope(self, slope : TriggerSlope):
        self.connection.write(f'TRSL {slope.name}')

    def get_trigger_slope(self) -> str:
        return self.connection.query('TRSL?')

    def set_trigger_level(self, level : Union[str, float]):
        """
        The TRIG_LEVEL command sets the trigger level voltage for the active trigger source.
        level : new trigger level as a string with units (V/mV) or a float in volts.
        """
        if isinstance(level, str):
            self.connection.write(f'TRLV {level}')
        else:
            self.connection.write(f'TRLV {level}V')

    def get_trigger_level(self) -> str:
        return self.connection.query('TRLV?')

    # ACQUIRE COMMANDS

    def arm(self):
        """
        The ARM_ACQUISITION command starts a new signal acquisition.
        """
        self.connection.write('STOP')

    def stop(self):
        """
        The STOP command stops the acquisition.
        """
        self.connection.write('STOP')

    # CURSOR COMMANDS
    # CRMS                                    <<  {OFF,MANUAL,TRACK}

    def set_cursor_measure(self, mode : CursorMode):
        """
        The CURSOR_MEASURE command specifies the type
        of cursor or parameter measurement to be displayed
        """
        self.connection.write(f'CRMS {mode.name}')

    def get_cursor_measure(self) -> str:
        return self.connection.query('CRMS?')

    # CRTY
    #                              <<

    def set_cursor_type(self, type: CursorType):
        """
        The CURSOR_TYPE command specifies the type
        of cursor to be displayed when the cursor mode is manual.
        """
        self.connection.write(f'CRTY {type.name.replace('_','-')}')

    def get_cursor_type(self) -> str:
        return self.connection.query('CRTY?')


    '''
    print(dev.connection.query('CRTY?'))
    X

    >>> print(dev.connection.query('CRMS?'))
    MANUAL
    >>> print(dev.connection.query('C1:CRST? TREF'))
    TREF,1.00E-06
    >>> print(dev.connection.query('C1:CRST? TDIF'))
    TDIF,6.01E-04

    dev.connection.write('CRTY X')
    dev.connection.write('C1:CRST TREF,0,TDIF,0.0006')

    dev.connection.write('CRTY Y')
    dev.connection.write('C1:CRST VREF,-2,VDIF,3')

    dev.connection.write('CRTY X-Y')
    ??
    '''

    # DISPLAY COMMANDS

    def set_menu(self, visible : bool):
        """
        Displays or hides the menu.
        """
        self.connection.write(f'MENU {"ON" if visible else "OFF"}')

    # PRINT COMMANDS

    def capture_screen(self, filename : str):
        """
        Captures the current screen to a bitmap file
        """
        with open(filename, "wb") as bmpfile:
            self.connection.write('SCDP')
            bmp_data = self.connection.read_raw()
            bmpfile.write(bmp_data)

    # SYSTEM COMMANDS

    def set_buzz(self, buzz : bool):
        """
        The BUZZER command enables or disables the buzzer.
        """
        self.connection.write(f'BUZZ {"ON" if buzz else "OFF"}')


class SDS1104X_channel:
    """
    Oscilloscope channel
    """

    def __init__(self, name : str, connection : pyvisa.resources.MessageBasedResource):
        """
        Initialize channel object

        name        name of the channel
        connection  connection object to read/write from/to
        """
        self.connection = connection
        self.name = name

    # ATTN
    def set_attenuation(self, value : Union[str, float]):
        """
        The ATTENUATION command specifies the probe attenuation factor for the selected channel. The probe
        attenuation factor may be 0.1 to 10000. This command does not change the actual input sensitivity of the
        oscilloscope. It changes the reference constants for scaling the display factors, for making automatic
        measurements, and for setting trigger levels.

        Valid attenuation values are: {0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000}
        The attenuation parameter passed will be rounded to the nearest valid value.
        """
        valid_values = [0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000]
        closest_value = 0
        value_diff = float('inf')

        for v in valid_values:
            d = abs(value - v)
            if d < value_diff:
                closest_value = v
                value_diff = d

        self.connection.write(f'{self.name}:ATTENUATION {closest_value}')

    def get_attenuation(self) -> str:
        return self.connection.query(f'{self.name}:ATTENUATION?')

    # BWL
    def set_bandwidth(self, bandwidth:Union[str, bool]):
        """
        The BANDWIDTH_LIMIT enables or disables the bandwidth-limiting low-pass filter.
        """
        self.connection.write(f'BWL {self.name},{"ON" if bandwidth else "OFF"}')

    def get_bandwidth(self) -> str:
        return self.connection.query(f'{self.name}:BWL?')

    # CPL
    def set_coupling(self, coupling : SDS1104X.CouplingMode):
        """
        The COUPLING command selects the coupling mode of the specified input channel
        Valid coupling values are A1M, D1M, or GND
            A — alternating current.
            D — direct current.
            1M — 1MΩ input impedance.
            GND — Ground

            Note: Other models have additional modes for 50Ω input impedance which this model does not use
        """
        self.connection.write(f'{self.name}:CPL {coupling.name}')

    def get_coupling(self) -> str:
        return self.connection.query(f'{self.name}:CPL?')

    # OFST
    def set_offset(self, offset : Union[str, float]):
        """
        The OFFSET command allows adjustment of the vertical offset of the specified input channel.
        The maximum ranges depend on the fixed sensitivity setting.

        offset : new offset as a string with units (V/mV/uV) or a float in volts.
        """
        self.connection.write(f'{self.name}:OFFSET {offset}')

    def get_offset(self) -> str:
        return self.connection.query(f'{self.name}:OFFSET?')

    # SKEW
    def set_skew(self, skew : float):
        """
        The SKEW command sets the channel-to-channel skew factor for the specified channel.
        Each analog channel can be adjusted + or -100 ns for a total of 200 ns difference between channels.
        You can use the oscilloscope's skew control to remove cable-delay errors between channels.

        skew : new skew value in nanoseconds
        """
        if skew >= -100 and skew <= 100:
            self.connection.write(f'{self.name}:SKEW {skew}ns')
        else:
            raise ValueError('Skew nanoseconds must be between -100 and 100')

    def get_skew(self) -> str:
        return self.connection.query(f'{self.name}:SKEW?')

    # TRA
    def set_trace(self, display : bool):
        """
        Turn the display of the specified channel on or off.
        """
        if display:
            self.connection.write(f'{self.name}:TRA ON')
        else:
            self.connection.write(f'{self.name}:TRA OFF')

    def get_trace(self) -> str:
        return self.connection.query(f'{self.name}:TRA?')

    # UNIT
    def set_unit(self, unit : SDS1104X.Unit):
        """
        The UNIT command sets the unit of the specified trace. Measurement results, channel sensitivity,
        and trigger level will reflect the measurement units you select.
        """
        self.connection.write(f'{self.name}:UNIT {unit.name}')

    def get_unit(self) -> str:
        return self.connection.query(f'{self.name}:UNIT?')

    # VDIV
    def set_volt_div(self, v_gain : float):
        """
        The VOLT_DIV command sets the vertical sensitivity in Volts/div.
        If the probe attenuation is changed, the scale value is multiplied by the probe's attenuation factor.
        """
        self.connection.write(f'{self.name}:VOLT_DIV {v_gain}')

    def get_volt_div(self) -> str:
        return self.connection.query(f'{self.name}:VOLT_DIV?')

    # INVS
    def set_invert_trace(self, invert : bool):
        """
        The INVERTSET command mathematically inverts the specified traces or the math waveform.
        """
        self.connection.write(f'{self.name}:INVERTSET {"ON" if invert else "OFF"}')

    def get_invert_trace(self) -> str:
        return self.connection.query(f'{self.name}:INVERTSET?')

    # CRVA?                                   <<  C1:CRVA? VREL

    def get_cursor_value(self, value: SDS1104X.CursorValueType) -> str:
        """
        The CURSOR_VALUE? query returns the values
        measured by the specified cursors for a given trace.
        """
        return self.connection.query(f'{self.name}:CRVA? {value.name}')


    # CRST                                    << ??

    def set_cursor_position(self, cursor: SDS1104X.Cursor, value: Union[str, float]):
        """
        The CURSOR_SET command allows the user to position
        any one of the four independent cursors at a given
        screen location, regardless of whether the cursor
        is currently displayed
            VREF — The voltage-value of Y1 (curA) under
            manual mode.
            VDIF — The voltage-value of Y2 (curB) under
            manual mode.
            TREF — The time value of X1 (curA) under manual
            mode.
            TDIF — The time value of X2 (curB) under manual
            mode.
            HREF — The time value of X1 (curA) under track
            mode.
            HDIF — The time value of X2 (curB) under track
            mode.

        value: The value of the cursor position as a string with units or a float
        using the default unit, with different valid units based on the cursor being set.

            VREF, VDIF: Valid units are V/mV and default unit is volts.

            TREF,TDIF,HREF,HDIF: Valid units are S/mS/uS/nS and the
            default unit is seconds.

        """

        self.connection.write(f'{self.name}:CRST {cursor.name},{value}')

    def get_cursor_position(self, cursor: SDS1104X.Cursor) -> str:
        return self.connection.query(f'{self.name}:CRST? {cursor.name}')





class SDS1104X_commandline:

    def __init__(self, RID : str = ""):
        self.rid = RID

    def execute_command(self, command : list):
        if not command:
            print("No command specified.")
            return

        if command[0] == "list":
                print("Available commands:")
                print("  list - list available commands")
                print("  default - reset oscilloscope to default settings")
                print("  auto_setup - automatically adjust controls for input signal")
                print("  write_state_file <filename> - save current oscilloscope state to XML file")
                print("  load_state_file <filename> - load oscilloscope state from XML file")
                print("  capture_screen <filename> - capture current screen to bitmap file")
                print("  ch# <cmd> - execute channel command (ch1, ch2, ch3, ch4)")
                print("      set_attenuation <value> - set channel attenuation")
                print("      set_bandwidth <on/off> - set channel bandwidth limit")
                print("      set_coupling <A1M/D1M/GND> - set channel coupling mode")
                print("      set_offset <value> - set channel offset")
                print("      set_skew <value> - set channel skew")
                print("      set_trace <on/off> - set channel trace display")
                print("      set_unit <V/A> - set channel unit")
                print("      set_volt_div <value> - set channel volts/div")
                print("      set_invert_trace <on/off> - set channel invert trace")
                print("      set_cursor_position <cursor> <value> - set channel cursor position")
        
        else:
            try:
                tool = SDS1104X(RID=self.rid)
            except RuntimeError as e:
                print("Error: Could not connect to SDS1104X oscilloscope.")
                return
            if not tool:
                print("Error: Could not connect to SDS1104X oscilloscope.")
                return
            print(tool.rid)

            match command[0]:
                case "default":
                    tool.default()
                case "auto_setup":
                    tool.auto_setup()
                case "write_state_file":
                    if len(command) < 2:
                        print("Error: Missing filename argument for write_state_file command.")
                    else:
                        tool.write_state_file(command[1])
                case "load_state_file":
                    if len(command) < 2:
                        print("Error: Missing filename argument for load_state_file command.")
                    else:
                        tool.load_state_file(command[1])
                case "capture_screen":
                    if len(command) < 2:
                        print("Error: Missing filename argument for capture_screen command.")
                    else:
                        tool.capture_screen(command[1])

                case "ch1" | "ch2" | "ch3" | "ch4":
                    channel = getattr(tool, command[0])

                    match command[1]:
                        case "set_attenuation":
                            if len(command) < 3:
                                print("Error: Missing value argument for set_attenuation command.")
                            else:
                                channel.set_attenuation(float(command[2]))
                        case "set_bandwidth":
                            if len(command) < 3:
                                print("Error: Missing on/off argument for set_bandwidth command.")
                            else:
                                channel.set_bandwidth(command[2].lower() == "on")
                        case "set_coupling":
                            if len(command) < 3:
                                print("Error: Missing coupling mode argument for set_coupling command.")
                            else:
                                try:
                                    coupling_mode = SDS1104X.CouplingMode[command[2].upper()]
                                    channel.set_coupling(coupling_mode)
                                except KeyError:
                                    print(f"Error: Invalid coupling mode '{command[2]}'. Valid modes are: A1M, D1M, GND.")
                        case "set_offset":
                            if len(command) < 3:
                                print("Error: Missing value argument for set_offset command.")
                            else:
                                channel.set_offset(float(command[2]))
                        case "set_skew":
                            if len(command) < 3:
                                print("Error: Missing value argument for set_skew command.")
                            else:
                                channel.set_skew(float(command[2]))
                        case "set_trace":
                            if len(command) < 3:
                                print("Error: Missing on/off argument for set_trace command.")
                            else:
                                channel.set_trace(command[2].lower() == "on")
                        case "set_unit":
                            if len(command) < 3:
                                print("Error: Missing unit argument for set_unit command.")
                            else:
                                try:
                                    unit = SDS1104X.Unit[command[2].upper()]
                                    channel.set_unit(unit)
                                except KeyError:
                                    print(f"Error: Invalid unit '{command[2]}'. Valid units are: V, A.")
                        case "set_volt_div":
                            if len(command) < 3:
                                print("Error: Missing value argument for set_volt_div command.")
                            else:
                                channel.set_volt_div(float(command[2]))
                        case "set_invert_trace":
                            if len(command) < 3:    
                                print("Error: Missing on/off argument for set_invert_trace command.")
                            else:
                                channel.set_invert_trace(command[2].lower() == "on")
                        case "set_cursor_position":
                            if len(command) < 4:
                                print("Error: Missing cursor and value arguments for set_cursor_position command.")
                            else:
                                try:
                                    cursor = SDS1104X.Cursor[command[2].upper()]
                                    channel.set_cursor_position(cursor, float(command[3]))
                                except KeyError:
                                    print(f"Error: Invalid cursor '{command[2]}'. Valid cursors are: VREF, VDIF, TREF, TDIF, HREF, HDIF.")
                        case _:
                            print(f"Command '{command}' not found.")

                case _:
                    print(f"Command '{command}' not found.")
