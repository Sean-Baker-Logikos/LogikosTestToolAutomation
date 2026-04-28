from LogikosTestToolAutomation.SigrokLA import SigrokLA
from datetime import timedelta

la = SigrokLA()

# params = SigrokLA.Capture_Raw(format=SigrokLA.Capture_Raw.OutputFormat.HEX, channels=[SigrokLA.Channels.D0, SigrokLA.Channels.D1])

params = SigrokLA.Capture_UART(rx = SigrokLA.Channels.D0, baudrate=9600, format=SigrokLA.Capture_UART.Format.ASCII)

# triggers = SigrokLA.Triggers(triggers=[
#         SigrokLA.TriggerChannel(channel=SigrokLA.Channels.D0, condition=SigrokLA.TriggerCondition.RISING),
#         SigrokLA.TriggerChannel(channel=SigrokLA.Channels.D1, condition=SigrokLA.TriggerCondition.FALLING),
#     ],
#     wait=False)
triggers = None

res = la.start_capture(samplerate=SigrokLA.Samplerate.SR_200kHz, duration=timedelta(seconds=1.5), params=params, triggers=triggers)

print(res)



