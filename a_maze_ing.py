import argparse
import signal
import sys

from src.controller import run_app


def main() -> int:
    """Parse the config_file argument and run application generating a maze.

    Returns:
        Application exit code, or 130 when interrupted with Ctrl+C.
    """
    parser = argparse.ArgumentParser(
        description="Generate and display maze using config from a file"
    )
    parser.add_argument("config_file", type=str, help="Path to config file.")
    args = parser.parse_args()

    try:
        return run_app(args.config_file)
    except KeyboardInterrupt:
        return 128 + signal.SIGINT


if __name__ == "__main__":
    sys.exit(main())
