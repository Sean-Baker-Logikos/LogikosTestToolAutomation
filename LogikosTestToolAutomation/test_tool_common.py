import pyvisa
from typing import List, Optional

def connect_pyvisa_device(rm,   # pyvisa.ResourceManager()
                          RID : str = "",
                          models : List[str] = []):
    """
    If RID is specified, connect to the specified device and verifiy that the model matches a string from the list.
    If RID is not specified, each device will be queried and the first one with a matching model will be retureed.
    """
    connection = None
    idn = dict()

    if RID:
        try:
            connection = rm.open_resource(RID, read_termination='\n', write_termination='\n')
            if connection:
                (idn['manufacturer'], idn['model'], idn['SN'], idn['firmware']) = connection.query("*IDN?").split(",")
                if idn["model"] not in models:
                    connection.close()
                    connection = None
        except pyvisa.errors.VisaIOError:
            connection = None

    else:
        all_resources = rm.list_resources()

        for r in all_resources:
            try:
                connection = rm.open_resource(r, read_termination='\n', write_termination='\n')
                if connection:
                    (idn['manufacturer'], idn['model'], idn['SN'], idn['firmware']) = connection.query("*IDN?").split(",")
                    if not idn['model'] or idn['model'] not in models:
                        connection.close()
                        connection = None
                    else:
                        break
            except pyvisa.errors.VisaIOError:
                connection = None

    return (connection, idn)
