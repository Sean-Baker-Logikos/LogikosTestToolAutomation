from LogikosTestToolAutomation.SigrokLA import SigrokLA
from datetime import timedelta

la = SigrokLA()

# params = SigrokLA.Capture_Raw(format=SigrokLA.Capture_Raw.OutputFormat.HEX, channels=[SigrokLA.Channels.D0, SigrokLA.Channels.D1])

params = SigrokLA.Capture_UART(rx=SigrokLA.Channels.D0, baudrate=115200, format=SigrokLA.Capture_UART.Format.ASCII, rx_packet_len=7)

res = la.start_capture(samplerate=SigrokLA.Samplerate.SR_24MHz, duration=timedelta(seconds=5), params=params)

print(res)



