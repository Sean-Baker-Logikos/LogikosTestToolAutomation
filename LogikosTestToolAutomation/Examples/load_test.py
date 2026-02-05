from LogikosTestToolAutomation.DL3021A import DL3021A
import time

load = DL3021A()

load.set_mode(DL3021A.Mode.FIX)
load.set_function(DL3021A.Function.CURR)

load.setup_const_current(0.5)
print(load.query_const_current())

load.on()

time.sleep(5)
voltage = load.get_voltage()
current = load.get_current()
print(f"{voltage}V {current}A")

load.off()
