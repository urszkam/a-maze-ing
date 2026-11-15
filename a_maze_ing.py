import argparse
import signal
import sys

from src.controller import run_app


def main() -> int:
    """TODO placeholder.
    """
    parser = argparse.ArgumentParser(description="Parse and validate maze "
                                                 "config file using Pydantic.")
    parser.add_argument("config_file", type=str, help="Path to config file.")
    args = parser.parse_args()

    try:
        return run_app(args.config_file)
    except KeyboardInterrupt:
        return 128 + signal.SIGINT


if __name__ == "__main__":
    sys.exit(main())
