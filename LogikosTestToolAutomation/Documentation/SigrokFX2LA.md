# SigrokLA Logic Analyzer

# Example Usage

    from LogikosTestToolAutomation.SigrokLA import SigrokLA
    from datetime import timedelta

    la = SigrokLA()
    params = SigrokLA.Capture_UART(rx=SigrokLA.Channels.D0, baudrate=115200, format=SigrokLA.Capture_UART.Format.ASCII)
    triggers = SigrokLA.Triggers([
            SigrokLA.TriggerChannel(channel=SigrokLA.Channels.D0, condition=SigrokLA.TriggerCondition.RISING),
            SigrokLA.TriggerChannel(channel=SigrokLA.Channels.D1, condition=SigrokLA.TriggerCondition.FALLING),
        ], wait=False)

    data = la.start_capture(samplerate=SigrokLA.Samplerate.SR_200kHz, duration=timedelta(seconds=1.5), params=params, triggers=triggers)
    print(data)


# Documentation

### SigrokLA Initilization

    SigrokLA(drivername = "fx2lafw")
        Creates a connection to a SigrokLA Logic Analyzer

        drivername : Select the driver to use for the connected hardware.
            See "sigrok-cli.exe --list-supported" for full list of supported drivers.
            Defaults to "fx2lafw" (generic driver for FX2 based LAs).

### SigrokLA Methods

    start_capture(
        samplerate: SigrokLA.Samplerate,
        duration: timedelta,
        samples: int,
        frames: int,
        params: SigrokLA.CaptureParams,
        triggers: SigrokLA.Triggers) -> str:

        Start data acquisition.

            samplerate : Data aquisition sample rate. See SigrokLA.Samplerate for valid values

            duration : Duration of the data aquisition, given by a timedelta.
                Only one of duration, samples, or frames should be specified.

            samples : Number of samples to be aquired.
                Only one of duration, samples, or frames should be specified.

            frames : Number of frames to be aquired.
                Only one of duration, samples, or frames should be specified.

            params : A SigrokLA.CaptureParams class indicating the parameters of the data aquisition.
                Possible values include:

                    SigrokLA.Capture_Raw(
                        format: SigrokLA.Capture_Raw.Format,
                        channels: list[SigrokLA.Channels])

                    SigrokLA.Capture_CAN(
                        can_rx: SigrokLA.Channels,
                        nominal_bitrate: int,
                        fast_bitrate: int,
                        sample_point: float)

                    SigrokLA.Capture_I2C(
                        scl: SigrokLA.Channels,
                        sda: SigrokLA.Channels,
                        address_format: SigrokLA.Capture_I2C.AddressFormat)

                    SigrokLA.Capture_SPI(
                        clk: SigrokLA.Channels,
                        miso: SigrokLA.Channels,
                        mosi: SigrokLA.Channels,
                        cs: SigrokLA.Channels,
                        cs_polarity: SigrokLA.Capture_SPI.CSPolarity,
                        cpol: int,
                        cpha: int,
                        bitorder: SigrokLA.Capture_SPI.BitOrder,
                        wordsize: int)

                    SigrokLA.Capture_UART(
                        rx : SigrokLA.Channels,
                        tx : SigrokLA.Channels,
                        baudrate: int,
                        data_bits: int,                                  # 5, 6, 7, 8, 9
                        parity: SigrokLA.Capture_UART.Parity,
                        stop_bits: float,                                # 0.0, 0.5, 1.0, 1.5, 2.0
                        bit_order: SigrokLA.Capture_UART.BitOrder,
                        format: SigrokLA.Capture_UART.Format,
                        invert_rx: bool,
                        invert_tx: bool,
                        sample_point: float,
                        rx_packet_delim: int,
                        tx_packet_delim: int,
                        rx_packet_len: int,
                        tx_packet_len: int)


            triggers : Trigger settings controlling the start of the capture.

                SigrokLA.Triggers(
                    triggers: list[SigrokLA.TriggerChannel],
                    wait : bool)

### Data types

    SigrokLA.Samplerate
        SR_20kHz
        SR_25kHz
        SR_50kHz
        SR_100kHz
        SR_200kHz
        SR_250kHz
        SR_500kHz
        SR_1MHz
        SR_2MHz
        SR_3MHz
        SR_4MHz
        SR_6MHz
        SR_8MHz
        SR_12MHz
        SR_16MHz
        SR_24MHz
        SR_48MHz

    SigrokLA.Channels
        D0
        D1
        D2
        D3
        D4
        D5
        D6
        D7




