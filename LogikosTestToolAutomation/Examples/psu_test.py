from LogikosTestToolAutomation.UDP3305S import UDP3305S
import time

psu = UDP3305S()

# Configure channel 1

psu.set_mode(UDP3305S.Mode.NORM)
psu.ch1.set_voltage(12.0)
psu.ch1.set_current(3.0)

# Turn on channel 1

psu.ch1.on()

# Read channel 1 output values

time.sleep(2)
r = psu.ch1.read_all()
print(f"CH1 - {r[0]}V {r[1]}A {r[2]}W")
