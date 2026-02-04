from LogikosTestToolAutomation.UDP3305S import UDP3305S
import time

psu = UDP3305S()

# Configure channel 1

psu.set_mode(UDP3305S.Mode.PARA)
psu.chPARA.set_voltage(22.0)
psu.chPARA.set_current(9.0)

# Turn on channel 1

time.sleep(2)
psu.chPARA.on()

# Read channel 1 output values

time.sleep(2)
r = psu.chPARA.read_all()
print(f"CH1 - {r[0]}V {r[1]}A {r[2]}W")
