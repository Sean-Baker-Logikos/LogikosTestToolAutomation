import sys
import os
import subprocess
from enum import Enum
from typing import Optional, Union
from datetime import timedelta
#from sigrok import Sigrok, ConfigKey
r"""
Sigrok-compatible Logic Analyzer.
sigrok-cli must be installed at "C:\Program Files\sigrok\sigrok-cli\sigrok-cli.exe".
"""

class SigrokLA:

    sigrok_dir = r"C:\Program Files\sigrok\sigrok-cli"
    sigrok_exe = "sigrok-cli.exe"

    class Samplerate(Enum):
        SR_20kHz = "20 kHz"
        SR_25kHz = "25 kHz"
        SR_50kHz = "50 kHz"
        SR_100kHz = "100 kHz"
        SR_200kHz = "200 kHz"
        SR_250kHz = "250 kHz"
        SR_500kHz = "500 kHz"
        SR_1MHz = "1 MHz"
        SR_2MHz = "2 MHz"
        SR_3MHz = "3 MHz"
        SR_4MHz = "4 MHz"
        SR_6MHz = "6 MHz"
        SR_8MHz = "8 MHz"
        SR_12MHz = "12 MHz"
        SR_16MHz = "16 MHz"
        SR_24MHz = "24 MHz"
        SR_48MHz = "48 MHz"

    class Channels(Enum):
        D0 = "D0"
        D1 = "D1"
        D2 = "D2"
        D3 = "D3"
        D4 = "D4"
        D5 = "D5"
        D6 = "D6"
        D7 = "D7"

    class CaptureParams:
        pass

    class Capture_Raw(CaptureParams):

        class Format(Enum):
            ANALOG = "analog"   #  ASCII analog data values and units
            BINARY = "binary"   #  Raw binary logic data
            BITS = "bits"       #  0/1 digits logic data
            CSV = "csv"         #  Comma-separated values
            HEX = "hex"         #  Hexadecimal digits logic data
            VCD = "vcd"         #  Value Change Dump data

        def __init__(self, 
                format: 'SigrokLA.Capture_Raw.Format',
                channels: Optional[list['SigrokLA.Channels']] = None):
            self.format = format
            self.channels = channels

        def __str__(self) -> str:
            str = f"--output-format {self.format.value}:header=false"
            if self.channels:
                str += " --channels " + ",".join([ch.value for ch in self.channels])
            return str


    class Capture_CAN(CaptureParams):
        """Controller Area Network"""

        default_nominal_bitrate = 1000000
        default_fast_bitrate = 2000000
        default_sample_point = 70.0

        def __init__(self,
                can_rx: 'SigrokLA.Channels',
                nominal_bitrate: int = default_nominal_bitrate,
                fast_bitrate: int = default_fast_bitrate,
                sample_point: float = default_sample_point):
            self.can_rx = can_rx
            self.nominal_bitrate = nominal_bitrate
            self.fast_bitrate = fast_bitrate
            self.sample_point = sample_point

        def __str__(self) -> str:
            str = f"--protocol-decoders can:can_rx={self.can_rx.value}"
            if self.nominal_bitrate != self.default_nominal_bitrate:
                str += f":nominal_bitrate={self.nominal_bitrate}"
            if self.fast_bitrate != self.default_fast_bitrate:
                str += f":fast_bitrate={self.fast_bitrate}"
            if self.sample_point != self.default_sample_point:
                str += f":sample_point={self.sample_point}"
            return str


    class Capture_I2C(CaptureParams):
        """Inter-Integrated Circuit"""

        class AddressFormat(Enum):
            SHIFTED = "shifted"
            UNSHIFTED = "unshifted"

        default_address_format = AddressFormat.SHIFTED

        def __init__(self,
                scl: 'SigrokLA.Channels',
                sda: 'SigrokLA.Channels',
                address_format: 'SigrokLA.Capture_I2C.AddressFormat' = default_address_format):
            self.scl = scl
            self.sda = sda
            self.address_format = address_format

        def __str__(self) -> str:
            str = f"--protocol-decoders i2c:scl={self.scl.value}:sda={self.sda.value}"
            if self.address_format != self.default_address_format:
                str += f":address_format={self.address_format.value}"
            return str


    class Capture_SPI(CaptureParams):
        """Serial Peripheral Interface"""

        class CSPolarity(Enum):
            ACTIVE_LOW = "active-low"
            ACTIVE_HIGH = "active-high"

        class BitOrder(Enum):
            MSB_FIRST = "msb-first"
            LSB_FIRST = "lsb-first"

        default_cs_polarity = CSPolarity.ACTIVE_LOW
        default_cpol = 0
        default_cpha = 0
        default_bitorder = BitOrder.MSB_FIRST
        default_wordsize = 8

        def __init__(self,
                clk: 'SigrokLA.Channels',
                miso: Optional['SigrokLA.Channels'] = None,
                mosi: Optional['SigrokLA.Channels'] = None,
                cs: Optional['SigrokLA.Channels'] = None,
                cs_polarity: 'SigrokLA.Capture_SPI.CSPolarity' = default_cs_polarity,
                cpol: int = default_cpol,
                cpha: int = default_cpha,
                bitorder: 'SigrokLA.Capture_SPI.BitOrder' = default_bitorder,
                wordsize: int = default_wordsize):
            self.clk = clk
            self.miso = miso
            self.mosi = mosi
            self.cs = cs
            self.cs_polarity = cs_polarity
            self.cpol = cpol
            self.cpha = cpha
            self.bitorder = bitorder
            self.wordsize = wordsize

        def __str__(self) -> str:
            str = f"--protocol-decoders spi:clk={self.clk.value}"
            if self.miso:
                str += f":miso={self.miso.value}"
            if self.mosi:
                str += f":mosi={self.mosi.value}"
            if self.cs:
                str += f":cs={self.cs.value}"
            if self.cs_polarity != self.default_cs_polarity:
                str += f":cs_polarity={self.cs_polarity.value}"
            if self.cpol != self.default_cpol:
                str += f":cpol={self.cpol}"
            if self.cpha != self.default_cpha:
                str += f":cpha={self.cpha}"
            if self.bitorder != self.default_bitorder:
                str += f":bitorder={self.bitorder.value}"
            if self.wordsize != self.default_wordsize:
                str += f":wordsize={self.wordsize}"
            return str


    class Capture_UART(CaptureParams):
        """Universal Asynchronous Receiver/Transmitter"""

        class Parity(Enum):
            NONE = "none"
            ODD = "odd"
            EVEN = "even"
            ZERO = "zero"
            ONE = "one"
            IGNORE = "ignore"

        class BitOrder(Enum):
            LSB_FIRST = "lsb-first"
            MSB_FIRST = "msb-first"

        class Format(Enum):
            ASCII = "ascii"
            DEC = "dec"
            HEX = "hex"
            OCT = "oct"
            BIN = "bin"

        default_baudrate = 115200
        default_data_bits = 8
        default_parity = Parity.NONE
        default_stop_bits = 1.0
        default_bit_order = BitOrder.LSB_FIRST
        default_format = Format.HEX
        default_invert_rx = False
        default_invert_tx = False
        default_sample_point = 50.0
        default_rx_packet_delim = -1
        default_tx_packet_delim = -1
        default_rx_packet_len = -1
        default_tx_packet_len = -1

        def __init__(self, 
                rx : Optional['SigrokLA.Channels'] = None,
                tx : Optional['SigrokLA.Channels'] = None,
                baudrate: int = default_baudrate,
                data_bits: int = default_data_bits,                                  # 5, 6, 7, 8, 9
                parity: 'SigrokLA.Capture_UART.Parity' = default_parity,
                stop_bits: float = default_stop_bits,                                # 0.0, 0.5, 1.0, 1.5, 2.0
                bit_order: 'SigrokLA.Capture_UART.BitOrder' = default_bit_order,
                format: 'SigrokLA.Capture_UART.Format' = default_format,
                invert_rx: bool = default_invert_rx,
                invert_tx: bool = default_invert_tx,
                sample_point: float = default_sample_point,
                rx_packet_delim: int = default_rx_packet_delim,
                tx_packet_delim: int = default_tx_packet_delim,
                rx_packet_len: int = default_rx_packet_len,
                tx_packet_len: int = default_tx_packet_len):
            self.rx = rx
            self.tx = tx
            self.baudrate = baudrate
            self.data_bits = data_bits
            self.parity = parity
            self.stop_bits = stop_bits
            self.bit_order = bit_order
            self.format = format
            self.invert_rx = invert_rx
            self.invert_tx = invert_tx
            self.sample_point = sample_point
            self.rx_packet_delim = rx_packet_delim
            self.tx_packet_delim = tx_packet_delim
            self.rx_packet_len = rx_packet_len
            self.tx_packet_len = tx_packet_len

        def __str__(self) -> str:
            str = "--protocol-decoders uart"
            if self.rx:
                str += f":rx={self.rx.value}"
            if self.tx:
                str += f":tx={self.tx.value}"
            if self.baudrate != self.default_baudrate:
                str += f":baudrate={self.baudrate}"
            if self.data_bits != self.default_data_bits:
                if self.data_bits not in [5, 6, 7, 8, 9]:
                    raise ValueError("Invalid data_bits value. Must be one of: 5, 6, 7, 8, 9.")
                str += f":data_bits={self.data_bits}"
            if self.parity != self.default_parity:
                str += f":parity={self.parity.value}"
            if self.stop_bits != self.default_stop_bits:
                if self.stop_bits not in [0.0, 0.5, 1.0, 1.5, 2.0]:
                    raise ValueError("Invalid stop_bits value. Must be one of: 0.0, 0.5, 1.0, 1.5, 2.0.")
                str += f":stop_bits={self.stop_bits}"
            if self.bit_order != self.default_bit_order:
                str += f":bit_order={self.bit_order.value}"
            if self.format != self.default_format:
                str += f":format={self.format.value}"
            if self.invert_rx != self.default_invert_rx:
                str += f":invert_rx={'yes' if self.invert_rx else 'no'}"
            if self.invert_tx != self.default_invert_tx:
                str += f":invert_tx={'yes' if self.invert_tx else 'no'}"
            if self.sample_point != self.default_sample_point:
                str += f":sample_point={self.sample_point}"
            if self.rx_packet_delim != self.default_rx_packet_delim:
                str += f":rx_packet_delim={self.rx_packet_delim}"
            if self.tx_packet_delim != self.default_tx_packet_delim:
                str += f":tx_packet_delim={self.tx_packet_delim}"
            if self.rx_packet_len != self.default_rx_packet_len:
                str += f":rx_packet_len={self.rx_packet_len}"
            if self.tx_packet_len != self.default_tx_packet_len:
                str += f":tx_packet_len={self.tx_packet_len}"
            return str

    class TriggerCondition(Enum):
        ZERO = "0"
        ONE = "1"
        RISING = "r"
        FALLING = "f"
        EITHER = "e"

    class TriggerChannel:
        def __init__(self,
                channel: 'SigrokLA.Channels',
                condition: 'SigrokLA.TriggerCondition'):
            self.channel = channel
            self.condition = condition

        def __str__(self) -> str:
            return f"{self.channel.value}={self.condition.value}"

    class Triggers:
        def __init__(self,
                triggers: list['SigrokLA.TriggerChannel'],
                wait = False):
            self.triggers = triggers
            self.wait = wait

        def __str__(self) -> str:
            return "--triggers " + ",".join([str(trigger) for trigger in self.triggers]) + (" --wait-trigger" if self.wait else "")


    # SigrokLA class methods

    def __init__(self,
            drivername: str = "fx2lafw"):
        self.drivername = drivername

    def start_capture(self, 
            samplerate: Samplerate,
            duration: Optional[timedelta] = None,
            samples: int = 0,
            frames: int = 0,
            params: Optional[CaptureParams] = None,
            triggers: Optional[Triggers] = None) -> str:
        """Start data capture with specified parameters"""
        sigrok_cmd = f"{self.sigrok_exe} --driver {self.drivername} --config samplerate=\"{samplerate.value}\""

        if duration:
            if duration.total_seconds() > 3600.0:
                sigrok_cmd += f" --time {int(duration.total_seconds())}s"
            else:
                sigrok_cmd += f" --time {int(duration.total_seconds() * 1000)}"
        elif samples:
            sigrok_cmd += f" --samples {samples}"
        elif frames:
            sigrok_cmd += f" --frames {frames}"
        else:
            raise ValueError('Either duration, samples, or frames must be specified."')

        if params:
            sigrok_cmd += " " + str(params)

        if triggers:
            sigrok_cmd += " " + str(triggers)

        print(f"Executing command: {sigrok_cmd}")

        os.chdir(self.sigrok_dir)
        output = subprocess.run(sigrok_cmd, shell=True, check=True, capture_output=True, text=True) # open a new process, send the command and return the data
        raw_data = output.stdout

        return raw_data
