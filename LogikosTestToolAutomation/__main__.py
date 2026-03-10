import argparse
from twine.cli import args
from importlib.metadata import version
import sys

from .test_tool_common import list_pyvisa_devices
from .UDP3305S import UDP3305S_commandline
from .SDS1104X import SDS1104X_commandline
from .DL3021A import DL3021A_commandline

# Command line examples:
#   python -m LogikosTestToolAutomation list
#   python -m LogikosTestToolAutomation devices
#   python -m LogikosTestToolAutomation UDP3305S list
#   python -m LogikosTestToolAutomation UDP3305S ch1 voltage 12.0

def main():
    parser = argparse.ArgumentParser(
        prog="LogikosTestToolAutomation",
        description="Logikos Test Tool Automation"
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s " + version("LogikosTestToolAutomation")
    )
    parser.add_argument(
        "--id",
        help="Specify the ID of the tool to connect to. If not specified, the first matching tool will be used."
    )
    parser.add_argument(
        "tool",
        help="Automation tool to use ('list' to list supported tools)"
    )
    parser.add_argument(
        "command",
        help="Command to execute ('list' to list supported commands)",
        nargs="*"
    )

    args = parser.parse_args()
    # print(args.tool)
    # print(args.command)

    match args.tool:
        case "list":
            print("Supported tools:")
            print("  UDP3305S")
            print("  SDS1104X")
            print("  DL3021A")

        case "devices":
            list_pyvisa_devices()

        case _:
            tool = None
            match args.tool:
                case "UDP3305S":
                    tool = UDP3305S_commandline(RID=args.id)
                case "SDS1104X":
                    tool = SDS1104X_commandline(RID=args.id)
                case "DL3021A":
                    tool = DL3021A_commandline(RID=args.id)

            if tool:
                tool.execute_command(args.command)
            else:
                print(f"Tool '{args.tool}' not supported.")
                sys.exit(1)


if __name__ == "__main__":
    main()
