# SigrokLA Logic Analyzer

## Example Usage

    from LogikosTestToolAutomation.SigrokLA import SigrokLA

    la = SigrokLA()
    la.start_capture()
    status = la.get_status()
    print(status)
    la.stop_capture()
    data = la.read_samples()
    print(data)

## CLI Usage

    python -m LogikosTestToolAutomation SigrokLA list
    python -m LogikosTestToolAutomation SigrokLA start
    python -m LogikosTestToolAutomation SigrokLA status
    python -m LogikosTestToolAutomation SigrokLA read

### Methods

- `SigrokLA(RID='')` connect to the SigrokLA instrument
- `start_capture()` start acquisition
- `stop_capture()` stop acquisition
- `get_status()` query capture state
- `read_samples()` read acquired data
