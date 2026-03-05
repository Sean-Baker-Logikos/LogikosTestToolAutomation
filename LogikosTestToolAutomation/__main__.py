import argparse
from .UDP3305S import UDP3305S
from .SDS1104X import SDS1104X
from .DL3021A import DL3021A

def main():
    parser = argparse.ArgumentParser(
        prog="LogikosTestToolAutomation",
        description="Logikos Test Tool Automation"
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0"
    )
    parser.add_argument(
        "tool",
        help="Automation tool to use ('UDP3305S', 'SDS1104X', 'DL3021A')"
    )
    parser.add_argument(
        "command",
        help="Command to execute ('list' to list available commands)",
        nargs="+"
    )

    args = parser.parse_args()

    print(args.tool)
    print(args.command)

    match args.tool:
        case "UDP3305S":
            tool = UDP3305S()
        case "SDS1104X":
            tool = SDS1104X()
        case "DL3021A":
            tool = DL3021A()

    if tool:
        tool.execute_command(args.command)
    else:
        print(f"Tool '{args.tool}' not found.")

if __name__ == "__main__":
    main()
