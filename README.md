# LogikosTestToolAutomation
Logikos Test Tool Automation Helper Scripts

# Usage


# Example - SDS1104X

	from SDS1104X import SDS1104X
	import time

	scope = SDS1104X()

	scope.load_state_file("test5_osc_setup.xml")

	s = scope.get_status()
	print(s)
	while s != SDS1104X.Status.NONE:
		time.sleep(1)
		s = scope.get_status()
		print(s)

	print("set_trigger_mode SINGLE")
	scope.set_trigger_mode(SDS1104X.TriggerMode.SINGLE)

	s = scope.get_status()
	print(s)
	while not s & SDS1104X.Status.SIGNAL_ACQUIRED:
		time.sleep(1)
		s = scope.get_status()
		print(s)

	scope.capture_screen("test5_screenshot.bmp")




# Notes

https://dev.to/abdellahhallou/create-and-release-a-private-python-package-on-github-2oae


