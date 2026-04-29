# SigrokLA Logic Analyzer

## Example Usage

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


### Methods

- `SigrokLA(drivername="fx2lafw")` connect to the SigrokLA instrument
- `start_capture()` start acquisition

