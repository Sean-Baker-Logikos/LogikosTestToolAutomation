from turtle import mode
import pyvisa
from LogikosTestToolAutomation import test_tool_common
from typing import Optional, Union
from dataclasses import dataclass
from enum import Enum
import sys

"""
Controlling a DG4062 Function/Arbitrary Waveform Generator

Note: Many functions are not implemented! See:
      https://www.rigolna.com/products/waveform-generators/dg4000/
      DG4000 Programming Manual
"""

class DG4062:
    """
    RIGOL DG4062 Function/Arbitrary Waveform Generator
    """

    class Function(Enum):
        SIN = 0, # Sine
        SQU = 1, # Square
        RAMP = 2, # Ramp
        PULSE = 3, # Pulse
        NOISE = 4, # Noise
        SINC = 5, # Arb
        HARMONIC = 6, # Harmonic
        CUSTOM = 7 # User

    class SystemState(Enum):
        DEF = 0, # Default
        USER1 = 1,
        USER2 = 2,
        USER3 = 3,
        USER4 = 4,
        USER5 = 5,
        USER6 = 6,
        USER7 = 7,
        USER8 = 8,
        USER9 = 9,
        USER10 = 10,
    
    class HarmonicType(Enum):
        EVEN = 0,
        ODD = 1,
        ALL = 2,
        USER = 3

    class TriggerSource(Enum):
        INT = 0, #Internal
        EXT = 1, #External
        MAN = 2  #Manual

    def __init__(self, RID : str = ""):
        """
        Initialize DG4062 instance

        RID : pyVISA resource identifier. If not specified, the first DG4062 found will be connected.

        See pyVISA documentation for details.
        https://pyvisa.readthedocs.io/en/latest/introduction/communication.html
        """
        self.models = ["DG4062"]
        self.rid = RID

        rm = pyvisa.ResourceManager()
        (self.connection, self.idn, self.rid) = test_tool_common.connect_pyvisa_device(rm, RID, self.models)

        if not self.connection:
            raise RuntimeError(f"Instrument {self.models} not found." )
        
        self.ch1 = DG4062_channel('1', self.connection)
        self.ch2 = DG4062_channel('2', self.connection)

    def __del__(self):
        if self.connection:
            self.connection.close()
    

    # SYST:RESTART
    def restart(self):
        """
        The REBOOT command restarts the instrument.
        """
        return self.connection.write(f":SYST:RESTART")
    
    
    # SYST:PRES
    def reset(self, state: 'DG4062.SystemState'):
        """
        The RESET command restores the system to its default state (DEFault) or user-defined state (USER1, USER2, USER3, USER4, USER5, USER6, USER7, USER8, USER9 or USER10)..
        """
        return self.connection.write(f":SYST:PRES {state.name}")

    # *SAV USER1
    def save_state(self, state: 'DG4062.SystemState'):
        """
        The SAVE_STATE command restores the system to user-defined state (USER1, USER2, USER3, USER4, USER5, USER6, USER7, USER8, USER9 or USER10)..
        """
        return self.connection.write(f"*SAV {state.name}")
    
    # *TRG
    def trigger(self):
        """
        Trigger the instrument to generate an output
        """
        return self.connection.write(f"*TRG")

class DG4062_channel:
    """
    Waveform generator channel
    """

    def __init__(self, name : str, connection : pyvisa.resources.MessageBasedResource):
        """
        Initialize channel object

        name        name of the channel
        connection  connection object to read/write from/to
        """
        self.connection = connection
        self.name = name


    def set_output(self, value: bool):
        """
        The OUTPUT_SET? command Enable or disable the output of the [Output1] or [Output2] connector at the front panel.
        """
        return self.connection.write(f":OUTP{self.name} {"ON" if value else "OFF"}")
        
        
    def get_output(self) -> bool:
        output = self.connection.query(f":OUTP{self.name}?")
        
        #This query returns two '\n' characters at the end (a bug?),
        #so read the second one as well
        self.connection.read() 
        return output

    # FREQ?
    def set_frequency(self, value : Union[str, float]):
        """
        The FREQUENCY_SET? command sets the frequency of the basic waveform and the default unit is "Hz".
        """
        return self.connection.write(f":SOUR{self.name}:FREQ {value}")
    
    def get_frequency(self):
        return self.connection.query(f":SOUR{self.name}:FREQ?")
    

    # VOLT?

    def set_voltage(self, value : Union[str, float]):
        """
        The VOLTAGE_SET? command set the amplitude of the basic waveform and the default unit is "Vpp".
        """
        return self.connection.write(f":SOUR{self.name}:VOLT {value}")

    def get_voltage(self):
        return self.connection.query(f":SOUR{self.name}:VOLT?")
    
    # VOLT:OFFS?
    def set_offset(self, value : Union[str, float]):
        """
        The OFFSET_SET? command sets the DC offset voltage and the default unit is "VDC".
        """
        return self.connection.write(f":SOUR{self.name}:VOLT:OFFS {value}")

    def get_offset(self):
        return self.connection.query(f":SOUR{self.name}:VOLT:OFFS?")
    
    
    # PHAS?
    def set_phase(self, value : Union[str, float]):
        """
        The PHASE_SET? command sets the start phase of the basic waveform.
        """
        return self.connection.write(f":SOUR{self.name}:PHAS {value}")

    def get_phase(self):
        return self.connection.query(f":SOUR{self.name}:PHAS?")
    

    # FUNC?
    def set_waveform(self, func: DG4062.Function):
        """
        The WAVEFORM_SET? command sets the waveform type.
        """
        return self.connection.write(f":SOUR{self.name}:FUNC {func.name}")

    def get_waveform(self) -> str:
        return self.connection.query(f':SOUR{self.name}:FUNC?')
    
    # MOD?
    def set_modulation(self, value : bool):
        """
        The MODULATION_SET? command enables or disables the modulation function.
        """
        return self.connection.write(f":SOUR{self.name}:MOD {"ON" if value else "OFF"}")

    def get_modulation(self) -> str:
        return self.connection.query(f':SOUR{self.name}:MOD?')
    
    
    # SWE:STAT?
    def set_sweep(self, value : bool):
        """
        The SWEEP_SET? command enables or disables the sweep function.
        """
        return self.connection.write(f":SOUR{self.name}:SWE:STAT {"ON" if value else "OFF"}")

    def get_sweep(self) -> str:
        return self.connection.query(f':SOUR{self.name}:SWE:STAT?')
    

    # BURS?
    def set_burst(self, value : bool):
        """
        The BURST_SET? command enables or disables the burst function.
        """
        return self.connection.write(f":SOUR{self.name}:BURS {"ON" if value else "OFF"}")

    def get_burst(self) -> str:
        return self.connection.query(f':SOUR{self.name}:BURS?')


    # Waveform / Mode specific functions

    # BURS:TRIG:SOUR
    def set_burst_trigger_source(self, value: DG4062.TriggerSource):
        """
        Sets the trigger source of the Burst to internal, external or manual.
        """
        return self.connection.write(f":SOUR{self.name}:BURS:TRIG:SOUR {value.name}")
    def get_burst_trigger_source(self):
        return self.connection.query(f":SOUR{self.name}:BURS:TRIG:SOUR?")
    
    # SWE:TRIG:SOUR
    def set_sweep_trigger_source(self, value: DG4062.TriggerSource):
        """
        Sets the trigger source of the Sweep to internal, external or manual.
        """
        return self.connection.write(f":SOUR{self.name}:SWE:TRIG:SOUR {value.name}")
    def get_sweep_trigger_source(self):
        return self.connection.query(f":SOUR{self.name}:SWE:TRIG:SOUR?")
    
    #HARM:ORDE
    def set_harmonic_order(self, value: int):
        """
        Set the order of the harmonic.
        """
        return self.connection.write(f":SOUR{self.name}:HARM:ORDE {value}")
    
    def get_harmonic_order(self):
        return self.connection.query(f":SOUR{self.name}:HARM:ORDE?")
    
    
    #HARM:TYP
    def set_harmonic_type(self, value: DG4062.HarmonicType):
        """
        Set the harmonic type to EVEN, ODD, ALL or USER.
        """
        return self.connection.write(f":SOUR{self.name}:HARM:TYP {value.name}")
    
    def get_harmonic_type(self):
        return self.connection.query(f":SOUR{self.name}:HARM:TYP?")
    

    #PULS:WIDT
    def set_pulse_width(self, value: float):
        """
        Set the pulse width and the default unit is "s"
        """
        return self.connection.write(f":SOUR{self.name}:PULS:WIDT {value}")
    
    def get_pulse_width(self):
        return self.connection.query(f":SOUR{self.name}:PULS:WIDT?")
    
    #PULS:DCYC
    def set_pulse_duty_cycle(self, value: int):
        """
        The PULSE_DUTY_CYCLE_SET command sets the pulse duty cycle and the unit is %
        """
        return self.connection.write(f":SOUR{self.name}:PULS:DCYCLE {value}")
    
    def get_pulse_duty_cycle(self):
        return self.connection.query(f":SOUR{self.name}:PULS:DCYCLE?")
    

    #:PULS:TRAN:LEAD
    def set_pulse_leading(self, value: float):
        """
        The PULSE_LEADING_SET command sets the leading (rising) edge time of the pulse and the default unit is "s"

        The range available is limited by the pulse width currently specified. The relation fulfills the inequality: leading/falling edge time ≤ 0.625 x pulse width.
        DG4000 will automatically adjust the edge time to match the specified pulse width if the value currently set exceeds the limit value
        """
        return self.connection.write(f":SOUR{self.name}:PULS:TRAN:LEAD {value}")
    
    def get_pulse_leading(self):
        return self.connection.query(f":SOUR{self.name}:PULS:TRAN:LEAD?")
    


    #:PULS:TRAN:TRA
    def set_pulse_trailing(self, value: float):
        """
        The PULSE_TRAILING_SET command sets the trailing (falling) edge time of the pulse and the default unit is "s"

        The range available is limited by the pulse width currently specified. The relation fulfills the inequality: leading/falling edge time ≤ 0.625 x pulse width.
        DG4000 will automatically adjust the edge time to match the specified pulse width if the value currently set exceeds the limit value
        """
        return self.connection.write(f":SOUR{self.name}:PULS:TRAN:TRA {value}")
    
    def get_pulse_trailing(self):
        return self.connection.query(f":SOUR{self.name}:PULS:TRAN:TRA?")
    


    #FUNC:SQU:DCYC
    def set_square_duty_cycle(self, value: int):
        """
        THE SQUARE_DUTY_CYCLE_SET Set the duty cycle of the square waveform and the unit is %
        """
        return self.connection.write(f":SOUR{self.name}:FUNC:SQU:DCYCLE {value}")
    
    def get_square_duty_cycle(self):
        return self.connection.query(f":SOUR{self.name}:FUNC:SQU:DCYCLE?")
    
    
    #FUNC:RAMP:SYMM
    def set_ramp_symmetry(self, value: int):
        """
        The SYMMETRY_SET? command sets the symmetry of the ramp and the unit is %
        """
        return self.connection.write(f":SOUR{self.name}:FUNC:RAMP:SYMM {value}")
    
    def get_ramp_symmetry(self):
        return self.connection.query(f":SOUR{self.name}:FUNC:RAMP:SYMM?")
    

class DG4062_commandline:

    def __init__(self, RID : str = ""):
        self.rid = RID
    
    
    def execute_command(self, command : list):
        if not command:
            print("No command specified.")
            sys.exit(1)
        
        try:
            tool = DG4062(RID=self.rid)
        except RuntimeError as e:
            print("Error: Could not connect to DG4062 waveform generator.")
            sys.exit(1)
        if not tool:
            print("Error: Could not connect to DG4062 waveform generator.")
            sys.exit(1)
        print(tool.rid)

        match command[0]:
            case "list":
                print("Available commands:")
                print("  list - list available commands")
                print("  restart")
                print("  reset")
                print("  save_state")
                print("  trigger")
                print("  ch# <cmd> - execute channel command (ch1, ch2, ch3, ch4)")
                print("      set_output <value> - set channel output")
                print("      set_frequency <value> - set channel frequency")
                print("      set_voltage <value> - set channel voltage")
                print("      set_offset <value> - set channel offset")
                print("      set_phase <value> - set channel phase")
                print("      set_waveform <value> - set channel waveform")
                print("      set_modulation <value> - set channel modulation")
                print("      set_sweep <value> - set channel sweep")
                print("      set_burst <value> - set channel burst")
                print("      set_harmonic_order <value> - set channel harmonic order")
                print("      set_harmonic_type <value> - set channel harmonic type")
                print("      set_pulse_width <value> - set channel pulse width")
                print("      set_pulse_duty_cycle <value> - set channel pulse duty cycle")
                print("      set_pulse_leading <value> - set channel pulse leading")
                print("      set_pulse_trailing <value> - set channel pulse trailing")
                print("      set_square_duty_cycle <value> - set channel square duty cycle")
                print("      set_ramp_symmetry <value> - set channel ramp symmetry")
            case "restart":
                tool.restart()
            case "reset":
                if len(command) < 2:
                    print("Error: Missing filename argument for reset command.")
                    sys.exit(1)
                else:
                    try:
                        state = DG4062.SystemState[command[1].upper()]
                        tool.reset(state)
                    except KeyError:
                        print(f"Error: Invalid state '{command[1]}'. Valid states are: DEF, USER1, USER2, USER3, USER4, USER5, USER6, USER7, USER8, USER9 or USER10.")
                        sys.exit(1)
            case "save_state":
                if len(command) < 2:
                    print("Error: Missing filename argument for save_state command.")
                    sys.exit(1)
                else:
                    try:
                        state = DG4062.SystemState[command[1].upper()]
                        tool.save_state(state)
                    except KeyError:
                        print(f"Error: Invalid state '{command[1]}'. Valid states are: USER1, USER2, USER3, USER4, USER5, USER6, USER7, USER8, USER9 or USER10.")
                        sys.exit(1)
            case "trigger":
                tool.trigger()
            case "ch1" | "ch2":
                channel = getattr(tool, command[0])
                match command[1]:
                    case "set_output":
                        if len(command) < 3:
                            print("Error: Missing value argument for set_output command.")
                            sys.exit(1)
                        else:
                            channel.set_output(command[2].lower() == "on")
                    case "set_frequency":
                        if len(command) < 3:
                            print("Error: Missing value argument for set_frequency command.")
                            sys.exit(1)
                        else:
                            channel.set_frequency(float(command[2]))
                    case "set_voltage":
                        if len(command) < 3:
                            print("Error: Missing value argument for set_voltage command.")
                            sys.exit(1)
                        else:
                            channel.set_voltage(float(command[2]))
                    case "set_offset":
                        if len(command) < 3:
                            print("Error: Missing value argument for set_offset command.")
                            sys.exit(1)
                        else:
                            channel.set_offset(float(command[2]))
                    case "set_phase":
                        if len(command) < 3:
                            print("Error: Missing value argument for set_phase command.")
                            sys.exit(1)
                        else:
                            channel.set_phase(float(command[2]))
                    case "set_waveform":
                        if len(command) < 3:
                            print("Error: Missing unit argument for set_waveform command.")
                            sys.exit(1)
                        else:
                            try:
                                func = DG4062.Function[command[2].upper()]
                                channel.set_waveform(func)
                            except KeyError:
                                print(f"Error: Invalid waveform '{command[2]}'. Valid waveforms are: SIN, SQU, RAMP, PULSE, NOISE, SINC, HARMONIC, CUSTOM.")
                                sys.exit(1)
                    case "set_modulation":
                        if len(command) < 3:
                            print("Error: Missing value argument for set_modulation command.")
                            sys.exit(1)
                        else:
                            channel.set_modulation(command[2].lower() == "on")
                    case "set_sweep":
                        if len(command) < 3:
                            print("Error: Missing value argument for set_sweep command.")
                            sys.exit(1)
                        else:
                            channel.set_sweep(command[2].lower() == "on")
                    case "set_burst":
                        if len(command) < 3:
                            print("Error: Missing value argument for set_burst command.")
                            sys.exit(1)
                        else:
                            channel.set_burst(command[2].lower() == "on")
                    case "set_harmonic_order":
                        if len(command) < 3:
                            print("Error: Missing value argument for set_harmonic_order command.")
                            sys.exit(1)
                        else:
                            channel.set_harmonic_order(int(command[2]))
                    case "set_harmonic_type":
                        if len(command) < 3:
                            print("Error: Missing unit argument for set_harmonic_type command.")
                            sys.exit(1)
                        else:
                            try:
                                htype = DG4062.HarmonicType[command[2].upper()]
                                channel.set_harmonic_type(htype)
                            except KeyError:
                                print(f"Error: Invalid harmonic type '{command[2]}'. Valid harmonic types are: EVEN, ODD, ALL, USER.")
                                sys.exit(1)
                    case "set_pulse_width":
                        if len(command) < 3:
                            print("Error: Missing value argument for set_pulse_width command.")
                            sys.exit(1)
                        else:
                            channel.set_pulse_width(float(command[2]))
                    case "set_pulse_duty_cycle":
                        if len(command) < 3:
                            print("Error: Missing value argument for set_pulse_duty_cycle command.")
                            sys.exit(1)
                        else:
                            channel.set_pulse_duty_cycle(float(command[2]))
                    case "set_pulse_leading":
                        if len(command) < 3:
                            print("Error: Missing value argument for set_pulse_leading command.")
                            sys.exit(1)
                        else:
                            channel.set_pulse_leading(float(command[2]))
                    case "set_pulse_trailing":
                        if len(command) < 3:
                            print("Error: Missing value argument for set_pulse_trailing command.")
                            sys.exit(1)
                        else:
                            channel.set_pulse_trailing(float(command[2]))
                    case "set_square_duty_cycle":
                        if len(command) < 3:
                            print("Error: Missing value argument for set_square_duty_cycle command.")
                            sys.exit(1)
                        else:
                            channel.set_square_duty_cycle(int(command[2]))
                    case "set_ramp_symmetry":
                        if len(command) < 3:
                            print("Error: Missing value argument for set_ramp_symmetry command.")
                            sys.exit(1)
                        else:
                            channel.set_ramp_symmetry(int(command[2]))
                        
            case _:
                print(f"Command '{command}' not found.")
                sys.exit(1)
